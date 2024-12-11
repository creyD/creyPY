from sqlalchemy_utils import create_database, database_exists


def create_if_not_exists(db_name: str):
    from .common import SQLALCHEMY_DATABASE_URL

    if not database_exists(SQLALCHEMY_DATABASE_URL + db_name):
        create_database(SQLALCHEMY_DATABASE_URL + db_name)
