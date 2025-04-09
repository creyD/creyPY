from typing import Optional, Type, Union, get_args, get_origin, get_type_hints

from pydantic import BaseModel, create_model


def optional_fields(cls: Type[BaseModel]) -> Type[BaseModel]:
    fields = {}
    for name, hint in get_type_hints(cls).items():
        if name.startswith("_"):
            continue

        if get_origin(hint) is not Union or type(None) not in get_args(hint):
            hint = Optional[hint]

        fields[name] = (hint, None)

    new_model = create_model(cls.__name__, __base__=cls, **fields)

    return new_model
