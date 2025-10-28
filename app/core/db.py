from sqlalchemy import create_engine
from app.core.config import DATABASE_URL

# Crear el engine
engine = create_engine(DATABASE_URL)