# Tarea 1 - Sistemas Distribuidos

## All You Can Cache: Plataforma distribuida del fútbol chileno

Proyecto correspondiente a la Tarea 1 del curso Sistemas Distribuidos.

El objetivo del proyecto es implementar una plataforma distribuida que permita
procesar consultas relacionadas con la Liga de Primera de Chile, utilizando un
sistema de caché para reducir accesos innecesarios a la fuente externa y mejorar
el tiempo de respuesta.

## Arquitectura inicial

El sistema se divide en los siguientes servicios:

### 1. Traffic Generator
Genera solicitudes sintéticas al sistema utilizando distribuciones de tráfico
Uniforme y Zipf.

### 2. Cache Service
Recibe las consultas del generador y utiliza Redis para determinar si la respuesta
se encuentra almacenada.

- Cache hit: retorna directamente la respuesta almacenada.
- Cache miss: solicita la información al Scraper.

### 3. Scraper Service
Obtiene información desde Soccerway cuando la respuesta no se encuentra en caché.

### 4. Metrics Service
Registra métricas del comportamiento del sistema, como:

- Cache hits
- Cache misses
- Latencia
- Throughput
- Tiempo de scraping
- Errores
- Evictions

## Flujo general

Traffic Generator -> Cache Service -> Scraper Service

En paralelo, los distintos componentes registran información en el servicio
de métricas.

## Tecnologías

- Docker
- Docker Compose
- Redis
- Git / GitLab

## Estado del proyecto

- [x] Inicialización del repositorio Git
- [x] Creación de la estructura base
- [ ] Configuración inicial de Docker Compose
- [ ] Implementación del generador de tráfico
- [ ] Implementación del servicio de caché
- [ ] Implementación del scraper
- [ ] Implementación del sistema de métricas
- [ ] Experimentos y análisis