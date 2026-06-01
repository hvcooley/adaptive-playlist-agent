from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = (
    "postgresql://postgres:postgres@localhost:5433/postgres"
)
#"postgresql+psycopg2://postgres:postgres@localhost:5433/playlist_agent"

engine = create_engine(DATABASE_URL)

Base = declarative_base()