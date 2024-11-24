from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from .common import SQLALCHEMY_DATABASE_URL, name

engine = create_engine(SQLALCHEMY_DATABASE_URL + name, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db
