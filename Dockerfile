# 1. Imagen base: Python oficial, variante slim y con versión fija
FROM python:3.12-slim

# 2. Carpeta de trabajo dentro de la imagen
WORKDIR /app

# 3. Primero SOLO las dependencias -> esta capa queda cacheada
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Después el código (cambia seguido, no invalida la capa de pip)
COPY src/ ./src/
#COPY data/raw/ ./data/raw/

# 5. Configuración por defecto (se puede pisar con -e / env_file)
ENV INPUT_PATH=/app/data/raw/ventas.csv \
    OUTPUT_DIR=/app/data/output \
    PYTHONUNBUFFERED=1

# 6. Comando que corre al iniciar el contenedor
CMD ["python", "src/etl.py"]
