import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import sys

# Download Electric Vehicle Population Data

#Para el dockerFile usar
# Build the Docker image
#docker build -t ev-data-loader .


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
   with engine.connect() as conn:
        print("✅ Conexión a PostgreSQL exitosa")
except OperationalError as e:
    print("❌ Error al conectar a PostgreSQL:", e)
    sys.exit(1)
# ========================================
# 2. Borrar tablas (orden inverso de dependencias)
# ========================================
try:
  with engine.begin() as conn:
    print("🧹 Borrando tablas previas...")
    conn.execute(text("TRUNCATE TABLE electric_vehicles CASCADE;"))
    conn.execute(text("TRUNCATE TABLE models CASCADE;"))
    conn.execute(text("TRUNCATE TABLE makes CASCADE;"))
    conn.execute(text("TRUNCATE TABLE regions CASCADE;"))
    conn.execute(text("TRUNCATE TABLE vehicle_types CASCADE;"))
    conn.execute(text("TRUNCATE TABLE stagingev CASCADE;"))
  print("✅ Tablas borradas correctamente.")
except SQLAlchemyError as e:
    print("⚠️ Advertencia: No se pudieron truncar algunas tablas:", e)


url = "https://data.wa.gov/api/views/f6w7-q2d2/rows.csv?accessType=DOWNLOAD"
try:
 df = pd.read_csv(url)
 print("✅ Dataset descargado correctamente.")
except Exception as e:
    print("❌ Error al descargar el dataset:", e)
    sys.exit(1)

# ========================================
# 3. Renombrar columnas a las de StagingEV
# ========================================
try:
  df = df.rename(columns={
    "VIN (1-10)": "vin",
    "County": "county",
    "City": "city",
    "State": "state",
    "Postal Code": "zipcode",
    "Model Year": "modelyear",
    "Make": "make",
    "Model": "model",
    "Electric Vehicle Type": "electricvehicletype",
    "CAFV Eligibility": "cafv_eligibility",
    "Electric Range": "electricrange",
    "Base MSRP": "basemsrp",
    "Legislative District": "legislativedistrict",
    "DOL Vehicle ID": "dolvehicleid",
    "Vehicle Location": "vehiclelocation",
    "Electric Utility": "electricutility",
    "Census Tract 2020": "censustract"
  })
  print("✅ Columnas renombradas correctamente.")
except Exception as e:
    print("❌ Error al renombrar columnas:", e)
    sys.exit(1)


# ========================================
# 4. Insertar en tabla staging
# ========================================
try:
   print("⬆️ Subiendo datos a tabla staging...")
   df.to_sql("stagingev", engine, if_exists="append", index=False)
   print("✅ Datos cargados en stagingev.")
except SQLAlchemyError as e:
    print("❌ Error al cargar datos en stagingev:", e)
    sys.exit(1)

# ========================================
# 5. Poblar tablas normalizadas
# ========================================
try:
  with engine.begin() as conn:
    print("📌 Insertando en Makes...")
    conn.execute(text("""
        INSERT INTO Makes (make_name)
        SELECT DISTINCT Make FROM stagingev
        WHERE Make IS NOT NULL
        ON CONFLICT (make_name) DO NOTHING;
    """))

    print("📌 Insertando en Models...")
    conn.execute(text("""
        INSERT INTO Models (make_id, model_name)
        SELECT DISTINCT m.make_id, s.Model
        FROM StagingEV s
        JOIN Makes m ON m.Make_Name = s.Make
        WHERE s.Model IS NOT NULL
        ON CONFLICT DO NOTHING;
    """))

    
    print("📌 Insertando en Regions...")
    conn.execute(text("""
        INSERT INTO Regions (City, County, ZIPCode, State)
        SELECT DISTINCT City, County, ZIPCode, State
        FROM StagingEV
        ON CONFLICT DO NOTHING;
    """))

    print("📌 Insertando en Vehicle_Types...")
    conn.execute(text("""
        INSERT INTO Vehicle_Types (Fuel_Type, Vehicle_Class)
        SELECT DISTINCT ElectricVehicleType, NULL
        FROM StagingEV
        ON CONFLICT DO NOTHING;
    """))

    print("📌 Insertando en Electric_Vehicles...")
    conn.execute(text("""
					 INSERT INTO Electric_Vehicles (
								VIN, Model_Year, Electric_Range, Registration_Date,
								Electric_Utility, Make_ID, Model_ID, Region_ID, Type_ID
							) 
					 SELECT DISTINCT
								s.VIN,
								s.ModelYear,
								NULLIF(s.ElectricRange, 0),
								CURRENT_DATE,
								s.ElectricUtility,
								m.Make_ID,
								mo.Model_ID,
								r.Region_ID,
								t.Type_ID
							FROM StagingEV s
							JOIN Makes m ON m.Make_Name = s.Make
							JOIN Models mo ON mo.Model_Name = s.Model AND mo.Make_ID = m.Make_ID
							JOIN Regions r ON r.ZIPCode = s.ZIPCode::CHAR(5)
							JOIN Vehicle_Types t ON t.Fuel_Type = s.ElectricVehicleType
		                    ON CONFLICT (vin) DO NOTHING;
	    """))
except SQLAlchemyError as e:
    print("❌ Error al poblar tablas normalizadas:", e)
    sys.exit(1)

print(f"Dataset downloaded successfully. Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(df.head())