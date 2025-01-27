import os

from dotenv import load_dotenv

load_dotenv()

host = os.getenv("POSTGRES_HOST", "localhost")
user = os.getenv("POSTGRES_USER", "postgres")
password = os.getenv("POSTGRES_PASSWORD", "root")
port = os.getenv("POSTGRES_PORT", "5432")
name = os.getenv("POSTGRES_DB", "fastapi")

ssl_mode = os.getenv("SSL_MODE", "require")

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{user}:{password}@{host}:{port}/"
