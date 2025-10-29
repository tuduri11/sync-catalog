import logging
from sqlalchemy import select, delete
from ..core.db import engine
from ..utils import *
from ..models.models import *
from ..models.db_operations import *
from ..core.logging_conf import configure_logging

log = logging.getLogger(__name__)

def sync(csv_path):
    configure_logging()
    log.info("Portal sync: %s", csv_path)

    try:
        df = split_stores(read_csv(csv_path))
    except Exception as e:
        log.error(f"Error reading or processing CSV: {csv_path}, Error: {e}")
        raise 

    portal_map = {(int(r.product_id), int(r.store_id)): r for r in df.itertuples()}

    try:
        with engine.begin() as conn:
            #Todas las listings de la BD
            listings = get_listings(conn)

            db_pairs = set(listings.keys())
            portal_pairs = set(portal_map.keys())
            
            # Eliminaciones
            to_delete = db_pairs - portal_pairs
            if to_delete:
                delete_listings(conn,to_delete)


            # Inserciones / Actualizaciones de la importación
            for key, r in portal_map.items():
                pid, sid = key
                title = str(r.title)
                price = float(r.price)
                
                # Si el producto no existe en la base de datos, lo insertamos
                if key not in listings:
                    insert_or_update_product(conn, pid, title)
                    insert_or_update_listing(conn, {"product_id": pid, "store_id": sid, "title": title, "price": price})
                else:
                    db_r = listings[key]
                    if str(db_r["title"]) != title or float(db_r["price"]) != price:
                        insert_or_update_listing(conn, {"product_id": pid, "store_id": sid, "title": title, "price": price})

        log.info("Sync completed.")

    except Exception as e:
        log.error(f"Error during sync process: {e}")
        raise