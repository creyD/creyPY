from typing import Callable, Optional

from sqlalchemy import asc, desc
from sqlalchemy.sql.selectable import Select


def order_by(order_by: Optional[str] = None) -> Callable[[Select], Select]:
    def _order_by(query: Select) -> Select:
        if order_by:
            direction = desc if order_by.startswith("-") else asc
            query = query.order_by(direction(order_by.lstrip("-")))
        return query

    return _order_by
