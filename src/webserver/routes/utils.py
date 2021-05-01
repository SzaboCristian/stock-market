##############
# API params #
##############

def api_param(_in, required=True, description=None, **kwargs) -> dict:
    param = {
        "in": _in,
        "required": required,
        "description": description
    }
    param.update(dict(**kwargs))
    return param


def api_param_path(required=True, description=None, **kwargs) -> dict:
    return api_param("path", required, description, **kwargs)


def api_param_query(required=True, description=None, **kwargs) -> dict:
    return api_param("query", required, description, **kwargs)


def api_param_form(required=True, description=None, **kwargs) -> dict:
    return api_param("formData", required, description, **kwargs)


def api_param_body(required=True, description=None, **kwargs) -> dict:
    return api_param("body", required, description, **kwargs)


# TODO
def get_optional_parameter(name, expected_type):
    pass


def get_required_parameter(name, expected_type):
    pass
