import logging
from sqlalchemy import (
    Table, Column, Integer, String, Numeric, DateTime, MetaData, text, create_engine,
    ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete, select
from .models import products, listings

log = logging.getLogger(__name__)

#Insertar o actualizar producto. Si existe, actualizar sus datos
def insert_or_update_product(conn, product_id, title):
    stmt = insert(products).values(
        product_id=product_id,
        title=title,
    ).on_conflict_do_update(
        index_elements=[products.c.product_id],
        set_={
            "title": stmt_excluded(products, "title"),
            "updated_at": text("CURRENT_TIMESTAMP"),
        },
    )
    result = conn.execute(stmt)
    if result.rowcount > 0:
        log.info(f"Product with product_id={product_id} {'updated' if result.rowcount > 1 else 'inserted'}, title: {title}")

# Inserta o actualiza un producto en la tabla 'listings'. Si el producto ya está asociado con una tienda, se actualiza el precio, título y la fecha de actualización.
def insert_or_update_listing(conn, item: dict):
    stmt = insert(listings).values(**item).on_conflict_do_update(
        index_elements=[listings.c.product_id, listings.c.store_id],
        set_={
            "title": stmt_excluded(listings, "title"),
            "price": stmt_excluded(listings, "price"),
            "updated_at": text("CURRENT_TIMESTAMP"),
        },
    )
    result = conn.execute(stmt)
    if result.rowcount > 0:
        if result.inserted_primary_key: 
            log.info(f"Listing inserted for product_id={item['product_id']} and store_id={item['store_id']}. Price: {item['price']}")
        else:  
            log.info(f"Listing updated for product_id={item['product_id']} and store_id={item['store_id']}. Price: {item['price']}")

# Función auxiliar para obtener el valor de la columna excluida cuando llamamos a inser_or_update (si tenemos conflicto)
def stmt_excluded(table: Table, colname: str):
    return insert(table).excluded.__getattr__(colname)


# Función para realizar todos los upserts: producto y listado
def upsert_all(conn, pid, sid, title, price):
    insert_or_update_product(conn, pid, title)
    insert_or_update_listing(conn, {"product_id": pid,"store_id": sid,"title": title,"price": price,})

#Elimina la relación entre un producto y una tienda (store_id) de la base de datos.
def remove_listing(conn, pid, sid):
    res = conn.execute(
        delete(listings)
        .where(listings.c.product_id == pid)
        .where(listings.c.store_id == sid)
    )
    if res.rowcount > 0:
        log.info(f"Relation between product_id={pid} and store_id={sid} deleted.")

#Obtener store_id existentes de un producto
def get_existing_store_ids(conn, product_id):
    existing_store_ids = conn.execute(select(listings.c.store_id).where(listings.c.product_id == product_id)).scalars().all()
    return set(existing_store_ids)