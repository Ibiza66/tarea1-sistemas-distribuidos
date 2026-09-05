# Imagen base liviana de Python.
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor.
WORKDIR /app

# Se copian e instalan primero las dependencias para aprovechar
# la caché de construcción de Docker.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Instala Chromium y las dependencias necesarias para Playwright.
RUN python -m playwright install --with-deps chromium

# Se copia el código fuente del servicio.
COPY src/ .

# Puerto utilizado por la API del scraper.
EXPOSE 8001

# Se inicia FastAPI mediante Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]