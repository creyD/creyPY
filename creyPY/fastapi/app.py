import re

from fastapi.routing import APIRoute


# Swagger operation ID config
def generate_unique_id(route: APIRoute) -> str:
    op_id = re.sub(r"{.*?}", "", route.path_format)  # remove path parameters
    operation_id = re.sub(r"\W", "_", op_id.replace("//", "/"))[
        1:
    ]  # replace non-alphanumeric characters with underscores
    assert route.methods
    # if the route doesn't end with an underscore we should add one
    if operation_id[-1] != "_":
        operation_id += "_"
    # If get method and no {} in the path, it should be called list
    if "GET" in route.methods and "{" not in route.path_format:
        operation_id = operation_id + "list"
    else:
        operation_id = (
            operation_id + list(route.methods)[0].lower()
        )  # add first (and only) method to operation_id
    return operation_id
