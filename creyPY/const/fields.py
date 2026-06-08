from sqlalchemy import types


class LowerCaseString(types.TypeDecorator):
    """Converts strings to lower case on the way in."""

    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return value.lower()

    @property
    def python_type(self):
        return str
