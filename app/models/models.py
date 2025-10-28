import logging
from sqlalchemy import (
    Table, Column, Integer, String, Numeric, DateTime, MetaData, text, create_engine,
    ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import insert
from ..core.config import DATABASE_URL
from ..core.logging_conf import configure_logging

log = logging.getLogger(__name__)

metadata = MetaData()

#Tablas (productos, tiendas y listas)
products = Table(
    "products",
    metadata,
    Column("product_id", Integer, primary_key=True),
    Column("title", String, nullable=False), 
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
)

stores = Table(
    "stores",
    metadata,
    Column("store_id", Integer, primary_key=True),
    Column("name", String, nullable=False), 
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
)

listings = Table(
    "listings",
    metadata,
    Column("product_id", Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False),
    Column("store_id", Integer, ForeignKey("stores.store_id", ondelete="CASCADE"), nullable=False),
    Column("title", String, nullable=False),          
    Column("price", Numeric, nullable=False),   
    Column("created_at", DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
    Column("updated_at", DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False),
)

#Indices de la tabla listings para las consultas
Index("pk_listings", listings.c.product_id, listings.c.store_id, unique=True)
Index("ix_listings_store", listings.c.store_id)
Index("ix_listings_product", listings.c.product_id)


def init_db():
    configure_logging()
    engine = create_engine(DATABASE_URL, future=True)
    metadata.create_all(engine)
    log.info("Tables created.")