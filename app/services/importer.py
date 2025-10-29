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

    with engine.begin() as conn:
        for fila in df.to_dict(orient="records"):
            pid = int(fila["product_id"])
            sid = int(fila["store_id"])
            title = str(fila["title"])
            price = float(fila["price"])

            upsert_all(conn, pid, sid, title, price)

        for pid, group in df.groupby("product_id"):
            allowed_store_ids = set(group["store_id"].astype(int)) 
            store_ids_to_remove = get_store_ids(conn, pid) - allowed_store_ids
            if store_ids_to_remove:
                for sid in store_ids_to_remove:
                    remove_listing(conn, pid, sid)

    log.info("Importing finished.")



