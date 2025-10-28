Prueba Técnica: Sincronización de Catálogo de Productos


Objetivo


El objetivo es evaluar la capacidad para:

- Procesar y validar archivos CSV.
- Interactuar con una base de datos PostgreSQL (insertar, actualizar, eliminar registros).
- Implementar la lógica de sincronización (detección de cambios, nuevos registros y eliminaciones).
- Aplicar buenas prácticas en el manejo de errores, logging, organización modular del código y uso de control de versiones.

-------------------------------------------------------------------
-------------------------------------------------------------------

Contexto

Nuestra aplicación realiza dos tareas principales:

1) Importación y parseo del catálogo: Se recibe un feed CSV del cliente, que se procesa para almacenar o actualizar productos en la base de datos, incluyendo la asignación de productos a cuentas de portales (un cliente puede tener varias cuentas).
2) Sincronización con portales externos: Se comparan los datos almacenados en db con la información actual de los portales (simulada con otro CSV) y se realizan:
	- Eliminaciones: se borran productos que ya no figuran en el feed.
	- Actualizaciones: se modifican los productos cuyos datos han cambiado.
	- Inserciones: se agregan los nuevos productos.

-------------------------------------------------------------------
-------------------------------------------------------------------

Parte 1: Importación del Feed CSV

Requisitos:
Entrada: Un archivo CSV (feed_items.csv) con las columnas:
- product_id
- title
- price
- store_id

Tareas a realizar:

1) Leer y validar el formato del CSV.
2) Parsear los datos y, utilizando PostgreSQL, insertar o actualizar los registros en una tabla que almacene la información de los productos.
	- Si un producto ya existe, se debe actualizar la información.
	- Si es nuevo, se inserta en la base de datos.
	- Si el producto cambia de store/cuenta, realizar la reasignación.
3) Registrar (mediante logging) las acciones realizadas: inserciones, actualizaciones y cualquier error durante el proceso.


Parte 2: Sincronización con los Portales Externos

Requisitos:

- Entrada: Un segundo archivo CSV (portal_items.csv) que simula los datos actuales del portal externo. Este CSV tendrá la misma estructura que el anterior (product_id, title, price, store_id).
- Tareas a realizar:
	1) Leer el CSV del portal y obtener la lista actual de productos.
	2) Comparar los datos obtenidos con los que ya están almacenados en la base de datos.
	3) Ejecutar la siguiente lógica de sincronización:
		- Eliminación: Si un producto está en la base de datos pero no aparece en el CSV del portal, eliminarlo de la base de datos.
		- Actualización: Si un producto existe en ambos pero sus datos (por ejemplo, name o price) han cambiado, actualizar el registro en la base de datos.
		- Inserción: Si un producto está en el CSV del portal pero no en la base de datos, insertarlo.
	4) Registrar con logging cada acción (qué productos se actualizan, eliminan o insertan) y manejar posibles errores (p. ej., problemas de conexión a la base de datos o formato inválido en el CSV).


Sugerencias Técnicas:

- Puedes usar la biblioteca estándar csv o alguna externa como pandas.
- Elabora una estructura de datos en base de datos que soporte este flujo.
- Para la interacción con PostgreSQL, es recomendable usar un ORM (por ejemplo, SQLAlchemy) o la librería psycopg2.
- Se valorará una buena estructura modular del código (por ejemplo, separar funciones de lectura, validación, persistencia, etc.).
- La comparación puede hacerse utilizando claves únicas.
- Es recomendable implementar funciones reutilizables para comparar registros y determinar qué cambios aplicar.


Requisitos Adicionales y Opcionales

- Manejo de Errores y Logging:
	Implementa un sistema de logging que permita rastrear las operaciones (por ejemplo, utilizando el módulo logging de Python). Asegúrate de capturar y registrar excepciones relevantes.
- Organización y Documentación:
	- Estructura el código de manera modular y legible.
	- Incluye un archivo README.md en el repositorio con instrucciones claras sobre cómo configurar y ejecutar la aplicación (por ejemplo, utilizando Docker para levantar la base de datos PostgreSQL).
	- Utiliza un fichero de dependencias (requirements.txt).
- Control de Versiones:
	- Utiliza Git (preferentemente en GitHub) para versionar el proyecto. Se valorará la claridad en los commits y la organización del repositorio.
- Opcional:
	Si el tiempo lo permite, implementa una pequeña API usando FastAPI que exponga un endpoint para consultar el catálogo de productos actual.


Entrega

- Repositorio GitHub:
		Sube el proyecto a GitHub y proporciona instrucciones para clonar, configurar y ejecutar la aplicación.
- Documentación:
	Incluye un README.md con:
		- Descripción general del proyecto.
		- Instrucciones de instalación y configuración (incluyendo la base de datos, por ejemplo, mediante Docker).
		- Ejemplos de ejecución y detalles sobre la estructura del código.
- Código:
	Se valorará la calidad del código, la modularidad y la correcta implementación de la lógica de sincronización.
