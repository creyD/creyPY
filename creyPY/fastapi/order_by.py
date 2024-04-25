from typing import Callable

from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import String, asc, cast, desc
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.selectable import Select


def order_by(order_by: str | SkipJsonSchema[None] = None) -> Callable[[Select], Select]:
    def _order_by(query: Select) -> Select:
        if order_by:
            direction = desc if order_by.startswith("-") else asc
            column_name = order_by.lstrip("-")

            # Get the column from the query
            for column in query.inner_columns:
                if column.key == column_name:
                    # If the column is a UUID, cast it to a string
                    if isinstance(column.type, UUID):
                        column = cast(column, String)
                    query = query.order_by(direction(column))
                    break
        return query

    return _order_by
