from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.VentaTienda_repository import VentaTienda_Repository  # Cabecera
from app.repositories.VentaDetalle_repository import VentaDetalle_Repository # Detalles
from app.repositories.Producto_repository import Producto_Repository         # Inventario
from app.schemas.VentaTienda_schema import VentaTienda_Create
from app.schemas.VentaDetalle_schema import VentaDetalle_Create
from app.models.VentaTienda_model import VentaTienda
from app.models.VentaDetalle_model import VentaDetalle
from app.core.errors import NotFound_Exception, Conflict_Exception
from datetime import date
from typing import List

class Venta_Service:
    """
    Servicio encargado del procesamiento de ventas de la tienda del gimnasio.
    Cumple estrictamente con la Regla de Negocio 6 (Control de Stock).
    """
    def __init__(self, session: AsyncSession):
        self.venta_repo = VentaTienda_Repository(session)
        self.detalle_repo = VentaDetalle_Repository(session)
        self.producto_repo = Producto_Repository(session)

    async def procesar_venta_tienda(
        self, 
        venta_in: VentaTienda_Create, 
        detalles_in: List[VentaDetalle_Create]
    ) -> VentaTienda:
        """
        Procesa una venta completa de la tienda. Verifica que haya stock de cada 
        producto (Regla 6), descuenta el inventario y guarda la transacción de forma atómica.
        """
        if not detalles_in:
            raise Conflict_Exception(message="No se puede procesar una venta sin productos en el carrito.")

        # =========================================================================
        # 1. PRE-VALIDACIÓN DE STOCK LÍNEA POR LÍNEA (Regla de Negocio 6)
        # =========================================================================
        # Hacemos una primera pasada de verificación antes de modificar nada en la BD
        productos_a_actualizar = []
        
        for item in detalles_in:
            producto = await self.producto_repo.get_by_id(item.id_producto)
            if not producto:
                raise NotFound_Exception(
                    message=f"El producto con ID {item.id_producto} no existe en el catálogo."
                )

            # REGLA 6: Comprobar que la cantidad disponible en stock sea suficiente
            if producto.stock_actual <= 0:
                raise Conflict_Exception(
                    message=f"El producto '{producto.nombre_prod}' está completamente agotado."
                )
                
            if producto.stock_actual < item.cantidad:
                raise Conflict_Exception(
                    message=f"Stock insuficiente para '{producto.nombre_prod}'. "
                            f"Disponibles: {producto.stock_actual}, Solicitados: {item.cantidad}."
                )
            
            # Guardamos la referencia del objeto del ORM y la cantidad a restar para el paso posterior
            productos_a_actualizar.append((producto, item.cantidad))

        # =========================================================================
        # 2. CREACIÓN DE LA CABECERA DE LA VENTA
        # =========================================================================
        nueva_venta = VentaTienda(
            cedula_cliente=venta_in.cedula_cliente,
            fecha_venta=venta_in.fecha_venta if venta_in.fecha_venta else date.today(),
            monto_venta=venta_in.monto_venta,
            status_venta=True
        )
        self.venta_repo.session.add(nueva_venta)
        
        # Hacemos un flush para que SQLAlchemy genere el ID de la venta sin cerrar la transacción
        await self.venta_repo.session.flush()

        # =========================================================================
        # 3. APLICACIÓN DE CAMBIOS: RESTAR STOCK Y CREAR DETALLES
        # =========================================================================
        # Pasada final: Como ya sabemos que todo tiene stock, aplicamos los cambios con seguridad
        for producto, cantidad_comprada in productos_a_actualizar:
            # A) Restamos la cantidad del stock del producto
            producto.stock_actual -= cantidad_comprada
            
            # Buscamos los datos del esquema correspondiente
            item_esquema = next(d for d in detalles_in if d.id_producto == producto.id_producto)

            # B) Creamos la línea de detalle de la venta (Congelando el precio histórico)
            nuevo_detalle = VentaDetalle(
                id_venta=nueva_venta.id_venta,
                id_producto=producto.id_producto,
                cantidad=item_esquema.cantidad,
                precio_unitario=item_esquema.precio_unitario, # Precio acordado al momento de la venta
                status_detalle=True
            )
            self.detalle_repo.session.add(nuevo_detalle)

        # =========================================================================
        # 4. CONFIRMACIÓN ATÓMICA DE LA TRANSACCIÓN (ACID)
        # =========================================================================
        # Si un solo producto fallaba en el paso 1, la ejecución nunca llegaba aquí,
        # evitando ventas parciales corruptas o descuadres de caja.
        await self.venta_repo.session.commit()
        await self.venta_repo.session.refresh(nueva_venta)

        return nueva_venta