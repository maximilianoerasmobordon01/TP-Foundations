#  Trabajo Práctico Fundamentals - ITBA Cloud Data Engineering

**Alumno:** Maximiliano Bordón 

## Descripción del dataset seleccionado

El dataset [Electric Vehicle Population Data](https://catalog.data.gov/dataset/electric-vehicle-population-data). del Estado de Washington proporciona información detallada sobre los vehículos eléctricos registrados en el estado, específicamente sobre los vehículos eléctricos de batería (BEVs) y los híbridos enchufables (PHEVs). Estos datos son gestionados por el Departamento de Licencias del Estado de Washington (DOL) y se actualizan periódicamente para reflejar la adopción de vehículos eléctricos en la región.  

## Preguntas de Negocio

1. ¿ Cuál es el total de vehículos registrados?
2. ¿ Cuáles son las marcas más populares?
3. ¿ Cuál es la evolución de registros por año de modelo?
4. ¿ Cuál es el rango eléctrico promedio por marca?
5. ¿ Cuál es la distribución de vehículos por condado?

## Resolución de ejercicios y ejecución end2end

### Ejercicio 1

Consiste en la generación del presente archivo README.md.

### Ejercicio 2

Se generó un archivo docker-compose.yaml en donde se especifica el servicio de base datos postgresql con sus datos asociados.

Para bajar el servicio de base de datos deberá ejecutarse en la línea de comandos: 
```bin/sh
docker-compose down 
```
Para levantar el servicio de base datos deberá considerarse el siguiente comando.
```bin/sh
docker-compose up -d 
```
El flag -d corresponde a --detach, esto implica que el contenedor se ejecutará en segundo plano.

### Ejercicio 3

Para este punto se generaron dos archivos:

**create_tables.sql**: Que contiene las instrucciones DDL (Lenguaje de definición de datos) para la creación de las tablas y sus restricciones asociadas. 

**runsql.sh**: Se trata de un script que recibe archivos sql y los ejecuta. El prerrequisito para su exitosa ejecución es que el servicio de base de datos se encuentre operativo. Se ejecuta desde línea de comandos de la siguiente manera:

```bin/sh
sh -x runsql.sh create_tables.sql
```
### Ejercicio 4

Para la carga de la base de datos, deben considerarse dos archivos:

**load_data.py**: Se trata de un script python 
que descarga de Internet el dataset [Electric Vehicle Population Data](https://catalog.data.gov/dataset/electric-vehicle-population-data), volcandolo en una tabla staging sin restricciones para luego ir cargando los registros en la tablas de negocio. 

**Dockerfile.ev-data.loader**: Se trata del Dockerfile asociado para construir el contenedor. Su código es el siguiente:

```bin/sh
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY load_data.py .

ENV DB_HOST=postgres
ENV DB_USER=postgres
ENV DB_PASS=postgres
ENV DB_NAME=mydb
ENV DB_PORT=5432

CMD ["python", "load_data.py"]
```
Para construir la imagen del contenedor debe ejecutarse lo siguiente:
```bin/sh
docker build -f Dockerfile.ev-data-loader -t ev-data-loader .
```
Para ejecutar el contenedor se ejecutará la siguiente línea de comandos
```bin/sh
docker run --network tp-foundations_my_personal_network ev-data-loader
```

### Ejercicio 5

Para la generación de reportes, deben considerarse dos archivos:

**reporting.py**: Se trata de un script python que se conecta a la base de datos que se encuentra operativa y ejecuta las siguientes consultas, para luego informar por pantalla los resultados a modo de reporte:

#### Total de vehículos eléctricos registrados
```sql
SELECT COUNT(*) AS total_vehiculos
FROM Electric_Vehicles;
```
#### Evolución de registros por año de modelo
```sql
SELECT ev.Model_Year, COUNT(*) AS total
FROM Electric_Vehicles ev
GROUP BY ev.Model_Year
ORDER BY ev.Model_Year;
```
#### Marcas con más registros (top 10)
```sql
SELECT m.Make_Name, COUNT(*) AS cantidad
FROM Electric_Vehicles ev
JOIN Makes m ON ev.Make_ID = m.Make_ID
GROUP BY m.Make_Name
ORDER BY cantidad DESC
LIMIT 10;
```
#### Distribución de vehículos por condado (top 10)
```sql
SELECT r.County, COUNT(*) AS total
FROM Electric_Vehicles ev
JOIN Regions r ON ev.Region_ID = r.Region_ID
GROUP BY r.County
ORDER BY total DESC
LIMIT 10;
```
#### Rango eléctrico promedio por marca (top 10)
```sql
SELECT m.Make_Name, ROUND(AVG(ev.Electric_Range),1) AS rango_promedio
FROM Electric_Vehicles ev
JOIN Makes m ON ev.Make_ID = m.Make_ID
WHERE ev.Electric_Range IS NOT NULL
GROUP BY m.Make_Name
ORDER BY rango_promedio DESC
LIMIT 10;
```

**Dockerfile.reporting**:  Se trata del Dockerfile asociado para construir el contenedor para reportes. Su código es el siguiente:
```bin/sh
FROM python:3.11-slim


WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY reporting.py .

ENV DB_HOST=postgres
ENV DB_USER=postgres
ENV DB_PASS=postgres
ENV DB_NAME=mydb
ENV DB_PORT=5432


CMD ["python", "reporting.py"]

```
Para construir la imagen del contenedor debe ejecutarse lo siguiente:
```bin/sh
docker build -f Dockerfile.reporting -t reporting .
```
Para ejecutar el contenedor se ejecutará la siguiente línea de comandos
```bin/sh
docker run --network tp-foundations_my_personal_network reporting
```

### Ejercicio 6 

Finalmente se generó un script llamando main.sh que ejecuta todos los pasos solicitados en el TP de forma idempotente. El mismo debe ejecutarse desde linea de comandos de la siguiente forma: 
```bin/sh
sh -x main.sh 
```
Su código asociado es el siguiente:
```bin/sh
#!/bin/bash
# Modo de ejecución: sh -x main.sh

# === Variables ===
NETWORK="tp-foundations_my_personal_network"
DB_COMPOSE_FILE="docker-compose.yml"
EV_IMAGE="ev-data-loader"
EV_DOCKERFILE="Dockerfile.ev-data-loader"
REPORT_IMAGE="reporting"
REPORT_DOCKERFILE="Dockerfile.reporting"
CREATE_SCRIPT="create_tables.sql"

# === Colores para mensajes ===
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"
RESET="\e[0m"

# === Funciones ===
check_command() {
  command -v "$1" >/dev/null 2>&1 || {
    echo -e "${RED}❌ Error: $1 no está instalado o en PATH.${RESET}"
    exit 1
  }
}

msg() {
  echo -e "${YELLOW}▶ $1${RESET}"
}

ok() {
  echo -e "${GREEN}✔ $1${RESET}"
}

start_db() {
  msg "Bajando base de datos..."
  docker compose -f "$DB_COMPOSE_FILE" down

  msg "Subiendo base de datos..."
  docker compose -f "$DB_COMPOSE_FILE" up -d
  ok "Base de datos levantada."
}

create_tables() {
  msg "Ejecutando creación de tablas..."
  sh -x runsql.sh "$CREATE_SCRIPT"
  ok "Tablas creadas."
}

load_data() {
  msg "Creando imagen del contenedor para carga de datos..."
  docker build -f "$EV_DOCKERFILE" -t "$EV_IMAGE" .
  ok "Imagen $EV_IMAGE creada."

  msg "Lanzando contenedor para carga de datos..."
  docker run --rm --network "$NETWORK" "$EV_IMAGE"
  ok "Carga de datos finalizada."
}

generate_reports() {
  msg "Creando imagen del contenedor para reportes..."
  docker build -f "$REPORT_DOCKERFILE" -t "$REPORT_IMAGE" .
  ok "Imagen $REPORT_IMAGE creada."

  msg "Ejecutando consultas y generando reporte..."
  docker run --rm --network "$NETWORK" "$REPORT_IMAGE"
  ok "Reporte generado."
}

# === Main ===
check_command docker
check_command docker compose

start_db
create_tables
load_data
generate_reports

```