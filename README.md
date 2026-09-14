# Tarea 1 - Sistemas Distribuidos

## All You Can Cache: Plataforma distribuida del fútbol chileno

Proyecto correspondiente a la **Tarea 1 del curso Sistemas Distribuidos**.

El objetivo es implementar una plataforma distribuida para procesar consultas relacionadas con la **Liga de Primera de Chile**, utilizando Redis como sistema de caché para disminuir consultas repetidas, reducir la latencia y analizar el comportamiento del sistema bajo diferentes patrones de tráfico y configuraciones de caché.

---

## Arquitectura del sistema

La solución está compuesta por cuatro servicios principales y una instancia de Redis:

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

---

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

---

### 3. Scraper Service

Obtiene y procesa información de la Liga de Primera de Chile desde Soccerway.

Debido a que parte del contenido del sitio se carga dinámicamente mediante JavaScript, el servicio utiliza:

- Playwright.
- Chromium.
- BeautifulSoup.

La información se obtiene y procesa al iniciar el servicio y posteriormente queda precargada en memoria para responder las consultas.

Consultas implementadas:

- **Q1:** próximos partidos de un equipo.
- **Q2:** últimos partidos de un equipo.
- **Q3:** enfrentamientos entre dos equipos.
- **Q4:** partidos dentro de un período de fechas.
- **Q5:** tabla completa de posiciones.

---

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