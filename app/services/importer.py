import logging
from sqlalchemy import select, delete
from ..core.db import engine
from ..utils import *
from ..models.models import*
from ..models.db_operations import *
from ..core.logging_conf import configure_logging

log = logging.getLogger(__name__)

def import_feed(csv_path: str):
    configure_logging()
    log.info("Importing feed: %s", csv_path)

    try:
        df = split_stores(read_csv(csv_path))
    except Exception as e:
        log.error(f"Error reading or processing CSV: {csv_path}, Error: {e}")
        raise 

    try:
        with engine.begin() as conn:
            #Para cada fila del csv
            for fila in df.to_dict(orient="records"):
                pid = int(fila["product_id"])
                sid = int(fila["store_id"])
                title = str(fila["title"])
                price = float(fila["price"])

                #Update/Insert 
                upsert_all(conn, pid, sid, title, price)

            # Reasignación de tiendas por producto
            for pid, group in df.groupby("product_id"):
                allowed_store_ids = set(group["store_id"].astype(int)) 
                store_ids_to_remove = get_store_ids(conn, pid) - allowed_store_ids
                if store_ids_to_remove:
                    # Creamos una lista de tuplas (pid, sid) para eliminar en bloque
                    to_delete = [(pid, sid) for sid in store_ids_to_remove]
                    delete_listings(conn, to_delete)

        log.info("Importing finished.")

    except Exception as e:
        log.error(f"Error during database transaction: {e}")
        raise 



