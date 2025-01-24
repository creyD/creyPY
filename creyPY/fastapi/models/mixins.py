from sqlalchemy import Column
from sqlalchemy.orm import Mapped


class AutoAnnotateMixin:
    @classmethod
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        annotations = {}
        for key, value in cls.__dict__.items():
            if isinstance(value, Column):
                annotations[key] = Mapped[value.type.python_type]
        cls.__annotations__ = annotations


class AutoInitMixin:
    @classmethod
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        init_params = []
        for key, value in cls.__dict__.items():
            if isinstance(value, Column):
                if not value.nullable and not value.default and not value.server_default:
                    init_params.append((key, value.type.python_type))

        def __init__(self, **kwargs):
            super(cls, self).__init__()
            for key, _ in init_params:
                if key not in kwargs:
                    raise TypeError(f"Missing required argument: {key}")
                setattr(self, key, kwargs[key])
            for key, value in kwargs.items():
                if key not in init_params and hasattr(self.__class__, key):
                    setattr(self, key, value)

        cls.__init__ = __init__
