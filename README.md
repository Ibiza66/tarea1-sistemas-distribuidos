# Tarea 1 - Sistemas Distribuidos

## All You Can Cache: Plataforma distribuida del fútbol chileno

Proyecto correspondiente a la Tarea 1 del curso **Sistemas Distribuidos**.

El objetivo del proyecto es implementar una plataforma distribuida que permita procesar consultas relacionadas con la **Liga de Primera de Chile**, utilizando un sistema de caché para reducir accesos innecesarios a la fuente externa y mejorar los tiempos de respuesta.

## Arquitectura del sistema

El sistema se divide en cuatro servicios principales:

### 1. Traffic Generator

Genera solicitudes sintéticas hacia el sistema.

Actualmente permite:

- Generar consultas Q1 a Q5.
- Utilizar distribución Uniforme.
- Utilizar distribución Zipf.
- Configurar la cantidad de solicitudes.
- Configurar la tasa de arribo.
- Configurar la semilla aleatoria.
- Configurar el parámetro de Zipf.
- Seleccionar los tipos de consulta habilitados.
- Enviar consultas mediante HTTP al servicio de caché.

### 2. Cache Service

Recibe las consultas provenientes del generador de tráfico y utiliza Redis para determinar si la respuesta se encuentra almacenada.

Flujo esperado:

- **Cache hit:** retorna directamente la respuesta almacenada.
- **Cache miss:** envía la consulta al Scraper Service, almacena la respuesta obtenida y posteriormente la retorna al generador.

Este servicio debe permitir experimentar con distintos tamaños de caché, TTL y políticas de reemplazo.

> Estado actual: pendiente de implementación.

### 3. Scraper Service

Obtiene información actualizada de la **Liga de Primera de Chile** desde Soccerway.

Debido a que parte de la información de Soccerway es cargada dinámicamente mediante JavaScript, el servicio utiliza **Playwright y Chromium** para renderizar las páginas antes de procesarlas.

Los datos obtenidos son procesados y precargados en memoria al iniciar el servicio.

Actualmente soporta:

- **Q1:** próximos partidos de un equipo.
- **Q2:** últimos partidos de un equipo.
- **Q3:** historial de enfrentamientos entre dos equipos.
- **Q4:** partidos dentro de un período de fechas.
- **Q5:** tabla completa de posiciones.

La tabla de posiciones incluye:

- Posición.
- Equipo.
- Partidos jugados.
- Partidos ganados.
- Partidos empatados.
- Partidos perdidos.
- Goles a favor.
- Goles en contra.
- Diferencia de gol.
- Puntos.

El servicio expone una API HTTP mediante FastAPI.

#### Endpoint de estado

```http
GET /health