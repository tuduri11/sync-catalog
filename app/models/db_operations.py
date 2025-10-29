import logging
from sqlalchemy import (
    Table, Column, Integer, String, Numeric, DateTime, MetaData, text, create_engine,
    ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import delete, select, func
from .models import products, listings

log = logging.getLogger(__name__)

#Insertar o actualizar producto. Si existe, actualizar sus datos
def insert_or_update_product(conn, product_id, title):
    try:
        stmt = (
            insert(products)
            .values(
                product_id=product_id,
                title=title,
            )
            .on_conflict_do_update(
                index_elements=[products.c.product_id],
                set_={
                    "title": stmt_excluded(products, "title"),
                    "updated_at": text("CURRENT_TIMESTAMP"),
                },
                where=products.c.title.is_distinct_from(
                    stmt_excluded(products, "title")
                ),
            )
            .returning(text("(xmax = 0) AS inserted"))
        )

        row = conn.execute(stmt).fetchone()
        if row is None:
            return
        
        inserted = row.inserted 
        if inserted:
            log.info(f"New product with product_id={product_id}, title: {title}")
        else:
            log.info(f"Updated product with product_id={product_id} updated, title: {title}")

    except Exception as e:
        log.error(f"Error inserting or updating product with product_id={product_id}: {e}")
        raise

# Inserta o actualiza un producto en la tabla 'listings'. Si el producto ya está asociado con una tienda, se actualiza el precio, título y la fecha de actualización.
def insert_or_update_listing(conn, item: dict):
    try:
        stmt = insert(listings).values(**item).on_conflict_do_update(
            index_elements=[listings.c.product_id, listings.c.store_id],
            set_={
                "title": stmt_excluded(listings, "title"),
                "price": stmt_excluded(listings, "price"),
                "updated_at": text("CURRENT_TIMESTAMP"),
            },
            where=(
                    listings.c.title.is_distinct_from(stmt_excluded(listings, "title"))
                    | listings.c.price.is_distinct_from(stmt_excluded(listings, "price"))
                ),
        ).returning(
                text("(xmax = 0) AS inserted"))
        
        row = conn.execute(stmt).fetchone()
        if row is None:
            return
        inserted = row.inserted 


        if inserted: 
            log.info(f"Listing inserted for product_id={item['product_id']} and store_id={item['store_id']}. Price: {item['price']}")
        else:  
            log.info(f"Listing updated for product_id={item['product_id']} and store_id={item['store_id']}. Price: {item['price']}")

    except Exception as e:
        log.error(f"Error inserting or updating listing for product_id={item['product_id']} and store_id={item['store_id']}: {e}")
        raise 

# Función auxiliar para obtener el valor de la columna excluida cuando llamamos a inser_or_update (si tenemos conflicto)
def stmt_excluded(table: Table, colname: str):
    try:
        return insert(table).excluded.__getattr__(colname)
    except Exception as e:
        log.error(f"Error in stmt_excluded for table {table.name} and column {colname}: {e}")
        raise


# Función para realizar todos los upserts: producto y listado
def upsert_all(conn, pid, sid, title, price):
    insert_or_update_product(conn, pid, title)
    insert_or_update_listing(conn, {"product_id": pid,"store_id": sid,"title": title,"price": price,})

#Elimina la relación entre un producto y una tienda (store_id) de la base de datos.
def delete_listing(conn, pid, sid):
    try:
        res = conn.execute(
            delete(listings)
            .where(listings.c.product_id == pid)
            .where(listings.c.store_id == sid)
        )
        if res.rowcount > 0:
            log.info(f"Relation between product_id={pid} and store_id={sid} deleted.")

    except Exception as e:
        log.error(f"Error deleting listing for product_id={pid} and store_id={sid}: {e}")
        raise

#Obtener store_id existentes de un producto
def get_store_ids(conn, product_id):
    try:
        existing_store_ids = conn.execute(select(listings.c.store_id).where(listings.c.product_id == product_id)).scalars().all()
        return set(existing_store_ids)
    
    except Exception as e:
        log.error(f"Error getting store_ids for product_id={product_id}: {e}")
        raise


def get_listings(conn):
    try:
        db_rows = conn.execute(
            select(
                listings.c.product_id,
                listings.c.store_id,
                listings.c.title,
                listings.c.price,
            )
        ).mappings().all()
        db_map = {(r["product_id"], r["store_id"]): r for r in db_rows}
        return db_map
    
    except Exception as e:
        log.error(f"Error retrieving listings from database: {e}")
        raise

#Eliminación de productos de una lista
def delete_products(conn,product_ids):
    try:
        res = conn.execute(delete(products).where(products.c.product_id.in_(product_ids)))
        if res.rowcount > 0:
            for pid in product_ids:
                log.info(f"Deleted product with product_id={pid}.")

    except Exception as e:
        log.error(f"Error deleting products {product_ids}: {e}")
        raise

#Se eliminan los listings de una lista y los productos si se quedan sin tiendas
def delete_listings(conn, items):
    try:
        if items:
            for pid, sid in items:
                delete_listing(conn,pid,sid)

            #Si eliminamos TODOS los listings de un producto, eliminamos a ese producto:
            orphan_products = get_products_without_stores(conn)

            if orphan_products:
                delete_products(conn,orphan_products)

    except Exception as e:
        log.error(f"Error deleting listings: {e}")
        raise

def get_products_without_stores(conn):
    return conn.execute(
                select(products.c.product_id)
                .join(listings, listings.c.product_id == products.c.product_id, isouter=True)
                .group_by(products.c.product_id)
                .having(func.count(listings.c.product_id) == 0)
            ).scalars().all()