import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import os 
import sys

#docker build -t reporting .

# ========================================
# 1. Conexión a PostgreSQL
# ========================================
import os

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


try:
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(engine)
    with engine.connect() as conn:
        print("✅ Conexión a PostgreSQL exitosa")
except OperationalError as e:
    print("❌ Error al conectar a PostgreSQL:", e)
    sys.exit(1)
# ========================================
# Función auxiliar para ejecutar consultas
# ========================================
def run_query(query, title):
    print(f"\n📊 {title}")
    try:
       df = pd.read_sql(query, engine)
       if df.empty:
            print("⚠️ La consulta no devolvió resultados.")
       else:
            print(df.to_string(index=False))
    except SQLAlchemyError as e:
        print(f"❌ Error al ejecutar la consulta '{title}':", e)
# 1. Total de vehículos eléctricos registrados
q1 = """
SELECT COUNT(*) AS total_vehiculos
FROM Electric_Vehicles;
"""

q2 = """
SELECT ev.Model_Year, COUNT(*) AS total
FROM Electric_Vehicles ev
GROUP BY ev.Model_Year
ORDER BY ev.Model_Year;
"""

q3= """
SELECT m.Make_Name, COUNT(*) AS cantidad
FROM Electric_Vehicles ev
JOIN Makes m ON ev.Make_ID = m.Make_ID
GROUP BY m.Make_Name
ORDER BY cantidad DESC
LIMIT 10;
"""

q4="""
SELECT r.County, COUNT(*) AS total
FROM Electric_Vehicles ev
JOIN Regions r ON ev.Region_ID = r.Region_ID
GROUP BY r.County
ORDER BY total DESC
LIMIT 10;
"""

q5="""
SELECT m.Make_Name, ROUND(AVG(ev.Electric_Range),1) AS rango_promedio
FROM Electric_Vehicles ev
JOIN Makes m ON ev.Make_ID = m.Make_ID
WHERE ev.Electric_Range IS NOT NULL
GROUP BY m.Make_Name
ORDER BY rango_promedio DESC
LIMIT 10;
"""
# ========================================
# Ejecutar reportes
# ========================================
if __name__ == "__main__":
    run_query(q1, "Total de vehículos eléctricos registrados")
    run_query(q2, "Evolución de registros por año de modelo")
    run_query(q3, "Marcas con mas registros (top 10)")
    run_query(q4, " Distribución de vehículos por condado (top 10)")
    run_query(q5, "Rango eléctrico promedio por marca (top 10)")