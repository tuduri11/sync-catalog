from sqlalchemy import (
    Table, Column, Integer, String, Numeric, DateTime, MetaData, text, create_engine,
    ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import insert
from .models import products, stores, listings

def insert_or_update_product(conn, product_id: int, title: str):
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
    conn.execute(stmt)

def insert_or_update_store(conn, store_id: int, name: str):
    stmt = insert(stores).values(
        store_id=store_id,
        name=name,
    ).on_conflict_do_update(
        index_elements=[stores.c.store_id],
        set_={
            "name": stmt_excluded(stores, "name"),
            "updated_at": text("CURRENT_TIMESTAMP"),
        },
    )
    conn.execute(stmt)

def insert_or_update_listing(conn, item: dict):
    stmt = insert(listings).values(**item).on_conflict_do_update(
        index_elements=[listings.c.product_id, listings.c.store_id],
        set_={
            "title": stmt_excluded(listings, "title"),
            "price": stmt_excluded(listings, "price"),
            "updated_at": text("CURRENT_TIMESTAMP"),
        },
    )
    conn.execute(stmt)


# Función auxiliar para obtener el valor de la columna excluida cuando llamamos a inser_or_update (si tenemos conflicto)
def stmt_excluded(table: Table, colname: str):
    return insert(table).excluded.__getattr__(colname)