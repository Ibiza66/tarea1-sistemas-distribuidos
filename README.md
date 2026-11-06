# Sistemas Distribuidos

Repositorio correspondiente a las Tareas 1 y 2 del curso **Sistemas Distribuidos**.

El proyecto trabaja con información de la **Liga de Primera de Chile** obtenida desde Soccerway y utiliza una arquitectura basada en servicios Docker.

---

# Tarea 1 - All You Can Cache

## Plataforma distribuida del fútbol chileno

La Tarea 1 consiste en implementar una plataforma distribuida para procesar consultas relacionadas con la Liga de Primera de Chile, utilizando Redis como sistema de caché para disminuir consultas repetidas, reducir la latencia y analizar el comportamiento del sistema bajo diferentes patrones de tráfico y configuraciones de caché.

## Arquitectura del sistema

La solución está compuesta por cuatro servicios principales y una instancia de Redis.

### 1. Traffic Generator

Genera solicitudes sintéticas hacia el sistema.

Características principales:

- Consultas Q1 a Q5.
- Distribución Uniforme.
- Distribución Zipf.
- Semilla aleatoria configurable.
- Cantidad de solicitudes configurable.
- Tasa de arribo configurable.
- Parámetro `s` de Zipf configurable.

### 2. Cache Service

Recibe las solicitudes generadas y determina si la respuesta se encuentra almacenada en Redis.

#### Cache Hit

Si la clave ya existe en Redis, la respuesta almacenada se retorna directamente.

#### Cache Miss

Si la clave no existe:

1. Se solicita la información al `Scraper Service`.
2. La respuesta se almacena en Redis.
3. Se aplica un TTL configurable.
4. Se retorna la respuesta al generador.
5. Se registran las métricas correspondientes.

La caché permite modificar:

- TTL.
- Tamaño máximo de memoria.
- Política de reemplazo.

### 3. Scraper Service

Obtiene y procesa información de la Liga de Primera de Chile desde Soccerway.

Debido a que parte del contenido del sitio se carga dinámicamente mediante JavaScript, el servicio utiliza:

- Playwright.
- Chromium.
- BeautifulSoup.

La información se obtiene y procesa al iniciar el servicio y posteriormente queda disponible para responder las consultas.

Consultas implementadas:

- **Q1:** próximos partidos de un equipo.
- **Q2:** últimos partidos de un equipo.
- **Q3:** enfrentamientos entre dos equipos.
- **Q4:** partidos dentro de un período de fechas.
- **Q5:** tabla completa de posiciones.

### 4. Metrics Service

Servicio independiente encargado de registrar y calcular métricas del comportamiento del sistema.

Métricas implementadas:

- Cache hits.
- Cache misses.
- Hit rate.
- Miss rate.
- Latencia promedio.
- Latencia p50.
- Latencia p95.
- Throughput.
- Tiempo de acceso al Scraper Service.
- Errores.
- Evictions.
- Evictions por minuto.

Endpoints principales:

```text
GET  /health
POST /evento
GET  /metrics
POST /reset
```

---

# Tarea 2 - Procesamiento Distribuido de Datos

La Tarea 2 extiende la arquitectura desarrollada en la Tarea 1 incorporando persistencia en **MongoDB** y procesamiento de datos mediante **Apache Spark**.

El sistema utiliza datos de partidos de la Liga de Primera de Chile obtenidos desde Soccerway. Los partidos son almacenados en MongoDB y posteriormente procesados mediante RDD de Spark para calcular estadísticas y ejecutar experimentos de rendimiento.

## Componentes utilizados

- MongoDB 7.0 para almacenamiento persistente.
- Scraper Service para obtención y almacenamiento de partidos.
- Apache Spark mediante PySpark para procesamiento y análisis.
- Docker y Docker Compose para ejecutar el sistema de forma reproducible.

## Base de datos

La base de datos utilizada es:

```text
futbol_chileno
```

La colección que contiene los partidos originales es:

```text
raw_matches
```

Los resultados generados por Spark se almacenan en:

```text
estadisticas
```

MongoDB utiliza un índice único sobre:

```text
match_id
```

Este índice permite evitar la duplicación de partidos durante la ingesta.

---

# Requisitos

Para ejecutar el proyecto se requiere:

- Docker Desktop.
- Docker Compose.
- Git.

No es necesario instalar MongoDB, Apache Spark ni Python directamente en el equipo, ya que estos componentes se ejecutan dentro de contenedores Docker.

---

# Construcción del proyecto

Desde la raíz del repositorio ejecutar:

```bash
docker compose --profile analytics build
```

Esto construye los servicios utilizados tanto por la Tarea 1 como por la Tarea 2.

---

# Levantar MongoDB y Scraper Service

Para iniciar MongoDB y el servicio encargado de obtener y almacenar los partidos:

```bash
docker compose up -d mongodb scraper-service
```

MongoDB utiliza un volumen persistente llamado:

```text
mongodb-data
```

Por lo tanto, los datos almacenados se mantienen aunque los contenedores sean detenidos.

---

# Procesamiento principal con Spark

Para ejecutar el procesamiento completo del dataset y las ocho consultas analíticas:

```bash
docker compose --profile analytics run --rm spark-metrics python main.py
```

El servicio `spark-metrics` utiliza las siguientes variables de configuración:

```text
MONGO_URI=mongodb://mongodb:27017
MONGO_DB=futbol_chileno
COLECCION_PARTIDOS=raw_matches
MONGO_OUTPUT_COLLECTION=estadisticas
SPARK_MASTER=local[*]
```

El procesamiento realiza la limpieza de los registros, normalización de los partidos, generación de contribuciones por equipo y cálculo de las estadísticas.

---

# Consultas analíticas implementadas

Se implementaron ocho consultas utilizando Spark RDD:

1. Estadísticas por equipo: partidos jugados, victorias, empates y derrotas.
2. Goles a favor, goles en contra y diferencia de goles.
3. Puntos, porcentaje de victorias y promedio de puntos por partido.
4. Distribución de victorias locales, victorias visitantes y empates.
5. Promedio de goles por partido.
6. Cantidad de partidos por mes, año y temporada.
7. Equipos con mayor rendimiento ofensivo.
8. Partidos con mayor cantidad de goles.

Los resultados obtenidos se almacenan posteriormente en la colección:

```text
estadisticas
```

---

# Validación con conjunto pequeño

Para validar el funcionamiento del procesamiento utilizando un conjunto pequeño de partidos con resultados conocidos:

```bash
docker compose --profile analytics run --rm spark-metrics python test.py
```

Esta prueba permite verificar que las estadísticas calculadas por Spark correspondan con los valores esperados.

---

# Benchmark de escritura en MongoDB

Para medir el rendimiento de escritura del dataset completo en MongoDB:

```bash
docker compose run --rm scraper-service python mongo_benchmark.py
```

El experimento ejecuta tres repeticiones.

En cada repetición se utiliza una colección temporal independiente para no modificar la colección original `raw_matches`.

El índice único sobre `match_id` está activo durante la inserción, por lo que el costo de mantenimiento del índice forma parte del tiempo medido.

El programa informa:

- Cantidad de documentos insertados.
- Tiempo total de escritura.
- Tiempo promedio por documento.
- Promedio de las tres repeticiones.

Los resultados se almacenan en:

```text
experiments/tarea2/mongo_escritura.csv
experiments/tarea2/mongo_escritura_resumen.json
```

---

# Benchmark de lectura MongoDB hacia Spark

Para medir la lectura del dataset completo desde MongoDB hacia Spark:

```bash
docker compose --profile analytics run --rm spark-metrics python benchmark_lectura.py
```

El experimento realiza un calentamiento previo de Spark y posteriormente ejecuta tres repeticiones.

La medición incluye la lectura desde MongoDB, la creación del RDD y su materialización.

La creación inicial de la `SparkSession` se mantiene fuera del intervalo medido.

---

# Experimento de escalamiento por volumen

Para ejecutar las ocho consultas utilizando distintos tamaños del dataset:

```bash
docker compose --profile analytics run --rm spark-metrics python benchmark_volumen.py
```

Se utilizan los siguientes tamaños:

```text
N   = 1157 partidos
N/2 = 578 partidos
N/4 = 289 partidos
```

Para este experimento se mantiene fija una sola partición de Spark.

El conjunto completo se carga desde MongoDB y se ordena por `match_id`.

Posteriormente, el submuestreo se realiza en memoria sobre la lista de Python antes de construir el RDD.

Los subconjuntos se construyen seleccionando los primeros registros según el orden establecido:

```text
N/2 -> primeros 578 registros
N/4 -> primeros 289 registros
```

Este procedimiento permite utilizar exactamente los mismos subconjuntos en cada ejecución y evita depender de una selección aleatoria.

Cada una de las ocho consultas se ejecuta tres veces y se informa su tiempo promedio.

---

# Experimento de particionamiento

Para evaluar el efecto de la cantidad de particiones de Spark:

```bash
docker compose --profile analytics run --rm spark-metrics python benchmark_particiones.py
```

El experimento utiliza el dataset completo de 1157 partidos con:

```text
1 partición
2 particiones
4 particiones
```

El volumen de entrada se mantiene constante y únicamente cambia el nivel de particionamiento.

Las ocho consultas se ejecutan tres veces para cada configuración y se calcula el tiempo promedio.

---

# Validación de resultados entre particiones

Para comprobar que modificar el número de particiones no altere los resultados de las consultas:

```bash
docker compose --profile analytics run --rm spark-metrics python validar_particiones.py
```

El programa ejecuta las ocho consultas utilizando:

```text
1 partición
2 particiones
4 particiones
```

Posteriormente compara los resultados obtenidos.

La validación permite comprobar que el particionamiento puede modificar los tiempos de ejecución, pero no las estadísticas calculadas.

---

# Manejo de partidos definidos por penales

El sistema considera tanto partidos con estado:

```text
finalizado
```

como partidos con estado:

```text
finalizado_tras_penales
```

En los encuentros definidos mediante tanda de penales, los goles del partido se mantienen como goles a favor y goles en contra.

La tanda de penales se utiliza únicamente para determinar qué equipo obtiene la victoria y cuál obtiene la derrota.

De esta forma, los goles de la tanda no se incorporan al total de goles anotados durante el partido.

---

# Persistencia y deduplicación

Los partidos originales se almacenan en:

```text
futbol_chileno.raw_matches
```

Cada partido posee un `match_id` único.

MongoDB mantiene un índice único sobre este campo para impedir la inserción de registros duplicados.

Los datos persisten mediante el volumen Docker:

```text
mongodb-data
```

---

# Archivos principales de Spark

Los archivos relacionados con el procesamiento de la Tarea 2 se encuentran en:

```text
spark-metrics/src/
```

Archivos principales:

```text
main.py
analytics.py
preprocessing.py
transformation.py
mongo_reader.py
mongo_writer.py
config.py
test.py
benchmark_lectura.py
benchmark_volumen.py
benchmark_particiones.py
validar_particiones.py
```

---

# Detener los servicios

Para detener los contenedores:

```bash
docker compose --profile analytics down
```

Este comando mantiene el volumen de MongoDB y, por lo tanto, conserva los datos.

Para eliminar también el volumen persistente y comenzar nuevamente con una base de datos vacía:

```bash
docker compose --profile analytics down -v
```

**Advertencia:** el uso de `-v` elimina los datos almacenados en el volumen `mongodb-data`.

---

# Reproducir los experimentos de la Tarea 2

Una vez que MongoDB contiene el dataset, los experimentos pueden reproducirse ejecutando:

```bash
docker compose --profile analytics run --rm spark-metrics python main.py

docker compose run --rm scraper-service python mongo_benchmark.py

docker compose --profile analytics run --rm spark-metrics python benchmark_lectura.py

docker compose --profile analytics run --rm spark-metrics python benchmark_volumen.py

docker compose --profile analytics run --rm spark-metrics python benchmark_particiones.py

docker compose --profile analytics run --rm spark-metrics python validar_particiones.py

docker compose --profile analytics run --rm spark-metrics python test.py
```

Los tiempos obtenidos pueden variar entre ejecuciones debido a las condiciones de ejecución del sistema, pero los resultados analíticos deben mantenerse consistentes.
