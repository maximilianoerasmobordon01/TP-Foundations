#!/bin/bash

#Hay que darle permisos de ejecución primeramente al script: chmod +x run-sql.sh
#La ejecución será ./run-sql.sh create_tables.sql
CONTAINER_NAME=postgres_12_7
# Nombre de la base de datos
DB_NAME=mydb
# Usuario de PostgreSQL
DB_USER=postgres

# Validar que se pasaron archivos SQL
if [ $# -eq 0 ]; then
  echo "Uso: $0 script1.sql"
  exit 1
fi

# Ejecutar cada script en orden
for sql_file in "$@"; do
  if [ -f "$sql_file" ]; then
    echo "Ejecutando $sql_file..."
    docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$sql_file"
  else
    echo "Archivo no encontrado: $sql_file"
  fi
done

echo "Todos los scripts fueron ejecutados."