**Prueba técnica – Sincronización de Catálogo de Productos**

Este proyecto implementa un sistema completo para importar, validar y sincronizar catálogos de productos a partir de feeds CSV, almacenarlos en una base de datos PostgreSQL y exponer una API REST para consultar los datos.

## Características principales

- Procesamiento y validación de archivos CSV.
- Sincronización automática de productos:
  - Inserciones.
  - Actualizaciones.
  - Eliminaciones.
- Base de datos PostgreSQL gestionada por Docker.
- Logging.
- API REST con FastAPI.
- Despliegue completo con Docker Compose.


## Tecnologías utilizadas

- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL 15
- Docker / Docker Compose
- Logging (nativo Python)
- Pandas / CSV

### Requisitos previos

- Docker ≥ 27.x
- Docker Compose ≥ 2.x

### Configuración e instalación

1. Clonar repositorio:
- git clone https://github.com/tu-usuario/sync-catalog.git
- cd sync-catalog

2. Copiar el archivo de entorno:
- cp .env.example .env

3. Construir e iniciar el sistema:
- docker compose up --build

Esto levantará tres contenedores:

- Un contenedor PostgreSQL.
- Un contenedor app que:
    - Crea las tablas.
    - Importa automáticamente data/feed_items.csv.
    - Sincroniza con data/portal_items.csv.
- Un contenedor api con FastAPI en http://localhost:8000

Se realiza todo de manera automática. También es posible ejecutar cada fase de forma independiente usando la CLI interna (lo explico en el siguiente punto)

### Uso manual (CLI)
El modo manual permite repetir procesos de importación o sincronización sin reiniciar los contenedores:

- Inicializar la base de datos: docker compose exec app python -m app.cli initdb
- Importar feed CSV: docker compose exec app python -m app.cli import data/feed_items.csv
- Sincronizar con portal externo: docker compose exec app python -m app.cli sync data/portal_items.csv


### API REST
Endpoints principales: 
- GET	/products	Lista todos los productos con sus diferentes tiendas y precios

Exemple: http://localhost:8000/products

### FLUJO DE TRABAJO: IMPORTACIÓN Y SINCRONIZACIÓN

El sistema trabaja en dos fases principales, totalmente automatizadas (y también ejecutables manualmente mediante CLI).

1. Importación del feed (importer.py):
  - Leemos y validamos CSV (omitiendo filas inválidas)
  - Insertamos o actualizamos los productos en la base de datos.
  - Si el product_id ya existe, actualizamos title si ha cambiado.
  - Si el producto es nuevo, lo insertamos.
  - Si cambia de tienda, actualiza la asignación (store_id).
  - Si un producto aparece en el feed, se eliminan únicamente los listings que ya no están asociados a ese producto.
  - Los productos o tiendas que no aparecen en el CSV no se eliminan, para evitar borrar información si el feed es parcial.
  - Los registros inválidos se omiten y se registran en los logs.
  - Resultado: la base de datos queda actualizada y coherente con el CSV importado, sin afectar productos ajenos al feed actual.

2. Sincronización con el portal (sync.py):
  - Lee el CSV del portal y obtiene su estado actual.
  - Compara producto a producto con la base de datos.
  - Ejecuta la lógica de sincronización: eliminaciones, actualizaciones e inserciones.
  - Resultado: la base de datos queda sincronizada con la información del portal.


### BASE DE DATOS
- La base de datos está compuesta por dos tablas principales: products y listings:
    - Products almacena la información global del producto (por ejemplo, el título). Representa el catálogo central de artículos, independientemente de las tiendas.
    - Listings almacena la relación entre cada producto y las distintas tiendas (store_id), junto con el precio y los datos específicos de cada una.

- De esta forma, un mismo producto puede aparecer en múltiples tiendas con precios o condiciones diferentes.
- Esta separación permite:
    - Actualizar o eliminar productos sin afectar todas las tiendas manualmente.
    - Añadir nuevas tiendas o precios sin duplicar información.
    - Escalar fácilmente si en el futuro se añaden más atributos por tienda (stock, disponibilidad, promociones, etc.).


### LOGS
Todos los eventos de importación, sincronización y API se registran en: logs/app.log


###  AUTOR
- Antoni Tudurí Morente
- toni.t.m@hotmail.com
- github.com/tuduri11