from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from ..core.db import SessionLocal
from ..models.models import products,listings
from ..core.logging_conf import configure_logging
import logging

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Catalog Sync API", version="1.0")

#Endpoint para ver los productos con sus tiendas y sus respectivos precios
@app.get("/products")
def list_products():
    with SessionLocal() as session:
        #Unir cada producto con sus tiendas (si un producto está sin tiendas, sale igual)
        q = select(
            products.c.product_id, products.c.title,
            listings.c.store_id, listings.c.price
        ).join(listings, listings.c.product_id == products.c.product_id, isouter=True)

        rows = session.execute(q).all()
        #Crear diccionario con cada product_id y devolverlo en formato JSON
        out = {}
        for pid, title, store_id, price in rows:
            item = out.setdefault(pid, {"product_id": pid, "title": title, "stores": []})
            if store_id is not None:
                item["stores"].append({"store_id": store_id, "price": float(price)})
        return list(out.values())