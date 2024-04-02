# creyPY

My collection of Python and FastAPI shortcuts etc.

## Installation

```bash
pip install creyPY -U
```

## Versioning

This library uses [Semantic Versioning](https://semver.org/).

## FastAPI

This library installes fastapi and pydantic, as well as sqlalchemy for you. It also provides a sqlalchemy base class and companion pydantic schemas. Also there are some helper functions for FastAPI in `creyPY.fastapi.app` like `generate_unique_id` to generate unique operation IDs for the OpenAPI schema to work with code generators.

### Database connection

The `creyPY.fastapi.db` module provides a `Session` class that can be used as a context manager to connect to a database. It exposes the `SQLALCHEMY_DATABASE_URL` variable for you to use. It uses the following environment variables:

- `POSTGRES_HOST`: The host of the database
- `POSTGRES_PORT`: The port of the database
- `POSTGRES_USER`: The user of the database
- `POSTGRES_PASSWORD`: The password of the database
- `POSTGRES_DB`: The database name

Currently only PostgreSQL is supported. It creates a sync session, it is planned to add async support in the future. You can use this like this:

```python
from creyPY.fastapi.db.session import get_db

async def test_endpoint(
    db: Session = Depends(get_db),
) -> Any:
    pass
```

## Constants

The constants module contains a few enums that I use in my projects. The best way to understand this library is to look at the code (it's not that much). However for simplicity, here is a brief overview:

- LanguageEnum: Contains all languages according to ISO 639
- CountryEnum: Contains all countries according to ISO 3166
- CurrencyEnum: Contains all accepted stripe currencies (Commented out are the Zero-decimal currencies, to avoid custom implementation)
- StripeStatus: Contains all stripe payment statuses
- GroupMode: Contains time group modes (e.g. day, week, month, year)

### Usage example

```python
from creyPY.const import LanguageEnum

print(LanguageEnum.EN) # Output: LanguageEnum.EN
print(LanguageEnum.EN.value) # Output: English
``` 

## TODO

- Add async support for database connection
- Add version without postgresql dependency
