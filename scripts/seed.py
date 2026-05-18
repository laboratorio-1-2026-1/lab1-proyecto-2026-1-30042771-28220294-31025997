import os        #sirve para manejar rutas de archivos
import asyncio   #funciones asíncronas
import sys       #Controla configuraciones del sistema de Python

# Agregamos la raíz del proyecto para que Python encuentre la carpeta 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database.session import get_session_db

async def run_seed():
    print("Iniciando el proceso de carga de datos ...")
    
    # 1. Rutas de los archivos
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(base_dir, "seed_data.sql")
    
    if not os.path.exists(sql_file_path):
        print(f"❌ Error: No se encontró el archivo SQL en {sql_file_path}")
        return

    # 2. Leer las sentencias del archivo SQL
    print("Leyendo las sentencias de scripts/seed_data.sql...")
    with open(sql_file_path, "r", encoding="utf-8") as file:
        sql_lines = file.readlines()

    # 3. Limpiar los comentarios línea por línea y reconstruir el SQL 
    cleaned_sql = ""
    for line in sql_lines:
        # Si la línea tiene un comentario '--', nos quedamos solo con lo que está antes
        if "--" in line:
            line = line.split("--")[0]
        cleaned_sql += line

    # 4. Romper el texto limpio en sentencias individuales usando el punto y coma ';'
    statements = [stmt.strip() for stmt in cleaned_sql.split(";") if stmt.strip()]

    # 5. Conectarse de forma asíncrona usando la sesión del proyecto
    session_generator = get_session_db()
    session = await anext(session_generator)

    try:
        print(f"Ejecutando {len(statements)} bloques de sentencias en PostgreSQL de uno en uno...")
        
        # Ejecutamos cada orden de manera de manera individual dentro de la misma transacción
        for statement in statements:
            await session.execute(text(statement))
            
        await session.commit()
        print("✅ ¡Éxito rotundo! Todos los datos base se cargaron correctamente en la base de datos.")
        
    except Exception as e:
        await session.rollback()
        print(f"❌ Ocurrió un error al cargar los datos: {e}")
        print("Nos regresamos (ningún cambio fue guardado).")
        
    finally:
        # Cerramos la sesión 
        await session.close()

if __name__ == "__main__":
    asyncio.run(run_seed()) 