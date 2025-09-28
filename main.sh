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