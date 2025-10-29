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
- CLI para ejecución manual de procesos.


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

**MUY IMPORTANTE**: Si no se desea la ejecución automática de los dos ejercicios, en ".env", cambiar AUTO_RUN a false.

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

Se puede ir viendo los cambios en la base de datos gracias al endpoint  http://localhost:8000/products


### Uso manual (CLI)
El modo manual permite ejecutar los procesos de importación o sincronización sin reiniciar los contenedores:

- Inicializar la base de datos: docker compose exec app python -m app.cli initdb
- Importar feed CSV: docker compose exec app python -m app.cli import data/feed_items.csv
- Sincronizar con portal externo: docker compose exec app python -m app.cli sync data/portal_items.csv


### API REST
Endpoints principales: 
- GET	/products	Lista todos los productos con sus diferentes tiendas y precios : http://localhost:8000/products

### FLUJO DE TRABAJO: IMPORTACIÓN Y SINCRONIZACIÓN

El sistema trabaja en dos fases principales, totalmente automatizadas (y también ejecutables manualmente mediante CLI).

1. Importación del feed (importer.py):
  - Leemos y validamos CSV (omitiendo filas inválidas o vacías)
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
    - Products almacena la información global del producto. Representa el catálogo central de artículos, independientemente de las tiendas.
    - Listings almacena la relación entre cada producto y las distintas tiendas (store_id), junto con el precio y los datos específicos de cada una.

- De esta forma, un mismo producto puede aparecer en múltiples tiendas con precios o condiciones diferentes.
- Esta separación permite:
    - Actualizar o eliminar productos sin afectar todas las tiendas manualmente.
    - Añadir nuevas tiendas o precios sin duplicar información.
    - Escalar fácilmente si en el futuro se añaden más atributos por tienda (stock, disponibilidad, promociones, etc.).


### LOGS
Todos los eventos de importación, sincronización y API se registran en: logs/app.log mediante el módulo logging de Python


### ESTRUCTURA DEL PROYECTO

sync-catalog/
├── app/
│ ├── api/
│ │ └── api.py → Definición de la API REST con FastAPI (endpoints principales).
│ │
│ ├── core/
│ │ ├── config.py → Configuración general de la aplicación
│ │ ├── db.py → Conexión y sesión con la base de datos PostgreSQL.
│ │ └── logging_conf.py → Configuración de logging del sistema.
│ │
│ ├── models/
│ │ ├── db_operations.py → Funciones de persistencia y consultas a la base de datos.
│ │ └── models.py → Definición de modelos ORM (tablas products, listings).
│ │
│ ├── services/
│ │ ├── importer.py → Ejercicio 1
│ │ └── sync.py → Ejercicio 2
│ │
│ ├── cli.py → CLI para ejecutar comandos (initdb, import, sync).
│ └── utils.py → Funciones auxiliares
│
├── data/
│ ├── feed_items.csv → Archivo CSV de productos del feed.
│ └── portal_items.csv → Archivo CSV simulado del portal externo.
│
├── logs/
│ └── app.log → Archivo de registro de eventos y operaciones.
│
├── docker-compose.yml → Orquestación de servicios Docker (DB, app, API).
├── Dockerfile → Imagen base de la aplicación (Python + dependencias).
├── README.md → Documentación principal del proyecto.
└── requirements.txt → Dependencias del entorno Python.


### EJEMPLOS DE EJECUCIÓN

Cuando ejecutamos la importación del feed CSV (Ejercicio 1), tanto en la terminal como en el archivo de logs app.log, se registra el feedback de las operaciones realizadas sobre la base de datos. Aquí algunos ejemplos de mensajes de éxito que podrías ver:

2025-10-29 08:52:19,304 | INFO | app.models.db_operations | Relation between product_id=2735 and store_id=3 deleted.
2025-10-29 08:52:19,306 | INFO | app.models.db_operations | Deleted product with product_id=2735.
2025-10-29 08:52:19,308 | INFO | app.models.db_operations | Listing updated for product_id=1084 and store_id=1. Price: 406.15

En caso de errores al intentar escribir o actualizar los datos en la base de datos, el sistema también los registra. Un error típico podría ser:

2025-10-29 08:56:05,512 | ERROR | app.models.db_operations | Error inserting or updating product with product_id=A123: Invalid price format



###  AUTOR
- Antoni Tudurí Morente
- toni.t.m@hotmail.com
- github.com/tuduri11