Base de datos (PostgreSQL):
    - Tabla products (product_id, title, price, store_id)
    - Tabla stores (store_id, name)
    - Tabla listings (product_id,store_id,title, price)

Docker:
    - PostgreSQL
    - La app en si
    - API (si llego)

Import feed csv:
    - Leer archivo
    - Validar CSV
    - Insertar o actualizar datos de BD

Sincro con Portal:
    - Leer archivo (en teoria portal externo)
    - Comparar con BD y sincronizar (eliminar, actualizar e insertar)

Logging:
    - Registrar cualquier acción
OPCIONAL:
    - CLI (Comandos)
    - API REST (Fast api)