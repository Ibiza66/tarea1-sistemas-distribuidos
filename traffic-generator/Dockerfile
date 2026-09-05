# Imagen base liviana con Python.
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copiamos primero las dependencias para aprovechar la caché de Docker.
COPY requirements.txt .

# Instalamos las dependencias del servicio.
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente.
COPY src/ .

# Comando ejecutado cuando inicia el contenedor.
CMD ["python", "main.py"]