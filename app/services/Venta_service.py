from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime,timezone, timedelta
from typing import List
   
from app.schemas.VentaTienda_schema import Registrar_Venta_In
from app.schemas.Producto_schema import Producto_Create, Producto_Update
from app.repositories.VentaDetalle_repository import VentaDetalle_Repository 
from app.repositories.VentaTienda_repository import VentaTienda_Repository 
from app.repositories.Producto_repository import Producto_Repository 
from app.models.VentaTienda_model import VentaTienda
from app.models.VentaDetalle_model import VentaDetalle
from app.models.Producto_model import Producto
from app.core.errors import NotFound_Exception, Conflict_Exception

class Venta_Service:
    """
    Servicio encargado del procesamiento de ventas de la tienda del gimnasio.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        self.producto_repo = Producto_Repository(session)
        self.venta_repo = VentaTienda_Repository(session)
        self.detalle_repo = VentaDetalle_Repository(session)
        self.tz_venezuela = timezone(timedelta(hours=-4))

    async def listar_productos(self, page: int, size: int, filter: dict | None = None) -> List[Producto]:
        """
        Lista el catálogo de productos aplicando paginación y filtros.
        """
        results = await self.producto_repo.get_all(page=page, size=size, filter=filter)
        if not results:
            raise NotFound_Exception(
                message="No se encontraron productos registrados que coincidan con los criterios de búsqueda.",
                internal_code="BUSQUEDA_PRODUCTOS_SIN_RESULTADOS"
            )
        return results
    
    async def crear_producto(self, prod_in: Producto_Create) -> Producto:
        """
        Registra un nuevo producto verificando duplicados por descripción.
        """
        existente = await self.producto_repo.get_by_nombre(prod_in.descripcion_produ)
        if existente:
            raise Conflict_Exception(
                message="Ya existe un producto registrado con esa misma descripción.",
                internal_code="ERROR_PRODUCTO_DUPLICADO"
            )
        return await self.producto_repo.create(prod_in.model_dump(exclude_unset=True))
    
    async def actualizar_producto(self, id_producto: int, datos: Producto_Update) -> Producto:
        """
        Actualizaciones a un producto existente.
        """
        db_prod = await self.producto_repo.get_by_id(id_producto)
        if not db_prod:
            raise NotFound_Exception(
                message="El producto buscado no existe.",
                internal_code="ERROR_PRODUCTO_NO_ENCONTRADO"
            )
        
        if datos.descripcion_produ is not None:
            existente = await self.producto_repo.get_by_nombre(datos.descripcion_produ)
            if existente and existente.id_producto != id_producto:
                raise Conflict_Exception(
                    message="Ya existe otro producto registrado con esa misma descripción.",
                    internal_code="ERROR_PRODUCTO_DUPLICADO"
                )

        return await self.producto_repo.update(id_producto, datos.model_dump(exclude_unset=True))
    
    async def registrar_venta(self, venta_in: Registrar_Venta_In) -> VentaTienda:
        """
        Procesa de manera atómica el carrito de compras, valida el stock actual y
        descuenta las unidades correspondientes dentro de una sola transacción.
        """
        monto_total = 0.0
        productos_a_descontar = []

        for item in venta_in.productos:
            producto = await self.producto_repo.get_by_id(item.id_producto)
            if not producto:
                raise NotFound_Exception(
                    message=f"El producto con ID {item.id_producto} no se encuentra registrado en el inventario.",
                    internal_code="ERROR_PRODUCTO_VENTA_INEXISTENTE"
                )
            
            if not producto.status_producto:
                raise Conflict_Exception(
                    message=f"El producto '{producto.descripcion_produ}' se encuentra inactivo y no puede ser vendido.",
                    internal_code="ERROR_PRODUCTO_INACTIVO"
                )

            if producto.stock < item.cantidad:
                raise Conflict_Exception(
                    message=f"Stock insuficiente para '{producto.descripcion_produ}'. Disponible: {producto.stock}, Solicitado: {item.cantidad}.",
                    internal_code="STOCK_INSUFICIENTE"  
                )
            
            monto_total += producto.precio_actual * item.cantidad
            productos_a_descontar.append((producto, item.cantidad))

        # zona horaria local de Venezuela
        fecha_actual_venezuela = datetime.now(self.tz_venezuela)
        
        # Generación del Encabezado de la factura
        nueva_venta = VentaTienda(
            cedula_cliente=venta_in.cedula_cliente,
            fecha_venta=fecha_actual_venezuela,
            monto_venta=monto_total,
            status_venta=True
        )
        self.session.add(nueva_venta)
        await self.session.flush() 

        # Registro de detalles y reducción física de inventario
        for producto, cantidad in productos_a_descontar:
            producto.stock -= cantidad  
            
            nuevo_detalle = VentaDetalle(
                id_venta=nueva_venta.id_venta,
                id_producto=producto.id_producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_actual,
                status_detalle=True
            )
            self.session.add(nuevo_detalle)

        await self.session.commit() 

        detalles_factura = await self.detalle_repo.get_by_venta(nueva_venta.id_venta)
        
        #fecha "YYYY-MM-DD"
        fecha_formateada = nueva_venta.fecha_venta.strftime("%Y-%m-%d") if hasattr(nueva_venta.fecha_venta, "strftime") else nueva_venta.fecha_venta

        return {
            "id_venta": nueva_venta.id_venta,
            "cedula_cliente": nueva_venta.cedula_cliente,
            "fecha_venta": fecha_formateada,
            "monto_venta": nueva_venta.monto_venta,
            "status_venta": nueva_venta.status_venta,
            "detalles": detalles_factura 
        }