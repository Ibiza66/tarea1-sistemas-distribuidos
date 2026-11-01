# Imagen base liviana con Python.
FROM python:3.12-slim

# Directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copiamos primero las dependencias para aprovechar la caché de Docker.
COPY requirements.txt .

# Instalar Java
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-21-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configurar Java
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt
    
# Copiamos el código fuente.
COPY src/ .

# Puerto utilizado por la API de Apache-Spark.
EXPOSE 8008

# Comando ejecutado cuando inicia el contenedor.
CMD ["python", "test.py"]