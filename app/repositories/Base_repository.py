from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Con esta linea y el valor que toma Base_Repository, se indica algo como:
# "Esta clase trabajara con un modelo de tabla, pero solo se sabra cual cuando otra clase herede suyo".
Model_Table = TypeVar("Model_Table")

class Base_Repository(Generic[Model_Table]):
    """
    Clase generica que contiene las principales operaciones CRUD para la base de datos. Permite 
    que cada clase 'repository' adapte solo las operaciones necesarias para consultar los datos 
    de su respectiva tabla en base de datos (por ej.: filtrar usuarios por correo, roles por 
    descripcion, membresias por su estado activo o inactivo, etc.), siguiendo el 'Patron
    Repositorio'.
    
    El resto de clases de '/repositories' deben heredar de ella las operaciones fundamentales, 
    evitando asi la repeticion de codigo. 
    """
    def __init__(self, model_repo: Type[Model_Table], session: AsyncSession):
        """Instanciacion de la clase base, con el modelo y sesion asincrona a utilizar."""
        self.model_repo = model_repo
        self.session = session

    async def get_by_id(self, id: Any) -> Optional[Model_Table]:
        """Obtener un registro por su ID."""
        result = await self.session.get(self.model_repo, id)
        return result
    
    async def get_all(self, page: int = 1, size: int = 10, filter: dict | None = None) -> List[Model_Table]:
        """
        Obtener todos los registros de una tabla. Puede especificarse un diccionario para filtrar la
        busqueda por el valor de campos determinados.
        """
        query = select(self.model_repo) # Consulta basica a la tabla de destino.

        # Con este bloque se filtra la busqueda por el valor de los campos. Primero se verifica
        # que el campo dado realmente exista en el modelo/tabla y que su valor sea no nulo.
        if filter:
            for key in filter:
                if filter[key] is not None and hasattr(self.model_repo, key):
                    if isinstance(filter[key], str):
                        # Esta línea permite filtrar campos utilizando strings sin importar si el texto posee mayúsculas o minúsculas.
                        query = query.where(getattr(self.model_repo, key).ilike(f"%{filter[key]}%"))
                    else:
                        query = query.where(getattr(self.model_repo, key) == filter[key])

        # Cálculo de la paginación basado en page y size 
        offset_value = (page - 1) * size
        query = query.offset(offset_value).limit(size)

        results = await self.session.execute(query)
        return list(results.scalars().all()) # Se retorna una lista de registros encontrados (puede ser vacia).
    
    async def create(self, obj_data: dict) -> Model_Table:
        """Crear un nuevo registro en la base de datos."""
        new_obj = self.model_repo(**obj_data) # Se desempaquetan los valores dados para la creacion.
        self.session.add(new_obj)
        await self.session.commit()
        await self.session.refresh(new_obj) # Se "refresca" el objeto en memoria con los datos que haya podido crear la base de datos.
        return new_obj
    
    async def update(self, id_obj_db: Any, obj_data_update: dict) -> Model_Table:
        """Actualizar los datos de un registro en la base de datos."""
        obj_db = await self.get_by_id(id_obj_db) # Buscamos el registro especifico a modificar.

        # En este bloque se actualizan sus campos con los datos nuevos, segun el caso.
        for atribute in obj_data_update:
            if hasattr(obj_db, atribute):
                setattr(obj_db, atribute, obj_data_update[atribute])

        self.session.add(obj_db)
        await self.session.commit()
        await self.session.refresh(obj_db)
        return obj_db
    
    async def detele(self, id: Any) -> bool:
        """Metodo para eliminar registros de la base de datos"""
        obj_to_delete = await self.get_by_id(id) # Se busca el registro especifico a eliminar.

        # En este bloque se devuelve True o False dependiendo de si la eliminacion fue exitosa.
        if obj_to_delete:
            await self.session.delete(obj_to_delete)
            await self.session.commit()
            return True
        else:
            return False
