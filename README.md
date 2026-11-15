# docker-data-demo

Práctica de la clase 6 (Docker para Data Applications) — Diplomatura en Cloud Data Engineering.

Un ETL chico en Python (pandas) que lee ventas crudas, las limpia, agrega por día y sucursal,
escribe un Parquet y, si hay base configurada, carga el resultado en Postgres.

```
.
├── src/etl.py              # el pipeline (config por variables de entorno)
├── data/raw/ventas.csv     # datos de entrada (con duplicados y suciedad a propósito)
├── data/output/            # salida (se monta como volumen)
├── requirements.txt
├── Dockerfile              # versión recomendada (aprovecha la caché)
├── Dockerfile.lento        # versión "mala" para comparar tiempos de build
├── .dockerignore
├── .env.example            # copiar a .env
├── docker-compose.yml      # db (Postgres) + etl + adminer
└── sql/consultas.sql
```

## Requisitos

- Docker Desktop (Mac / Windows) o Docker Engine (Linux)
- Verificar: `docker version` y `docker compose version`

## 1. Correr el ETL en un contenedor

```bash
docker build -t ventas-etl:0.1 .
docker run --rm ventas-etl:0.1
```

## 2. Guardar la salida en tu máquina (bind mount)

```bash
# Mac / Linux
docker run --rm -v "$(pwd)/data/output:/app/data/output" ventas-etl:0.1
# Windows PowerShell
docker run --rm -v "${PWD}/data/output:/app/data/output" ventas-etl:0.1
```

## 3. Cambiar la configuración sin reconstruir

```bash
docker run --rm -e LOG_LEVEL=DEBUG -v "$(pwd)/data/output:/app/data/output" ventas-etl:0.1
```

## 4. Stack completo con Docker Compose

```bash
cp .env.example .env
docker compose up --build        # levanta db, corre el etl y deja adminer
```

- Adminer: http://localhost:8080 (Sistema: PostgreSQL · Servidor: `db` · Usuario/clave: `etl` · Base: `ventas`)
- Consola SQL: `docker compose exec db psql -U etl -d ventas`
- Volver a correr solo el ETL: `docker compose run --rm etl`
- Apagar: `docker compose down` (agregar `-v` borra también los datos de Postgres)
