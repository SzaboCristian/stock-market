import json

from flask import request


#####################
# Swagger doc utils #
#####################

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


#################
# Request utils #
#################

def validate_param_type(param, expected_type) -> tuple:
    """
    Validate param type.
    @param param: object
    @param expected_type: object
    @return: tuple
    """
    try:
        if isinstance(param, expected_type):
            return param, 'OK'

        if expected_type in [list, dict]:
            parsed = json.loads(param)
            if isinstance(parsed, expected_type):
                return parsed, 'OK'
            return None, 'Param [{}] must be of type {}'.format(param, expected_type.__name__)

        if expected_type is bool:
            return param.strip().lower() in ["true", "1"], 'OK'

        return expected_type(param), 'OK'
    except (ValueError, Exception):
        return None, 'Param [{}] must be of type {}'.format(param, expected_type.__name__)


def get_request_body_parameter(name) -> object:
    """
    Get parameter from request body.
    @param name: string
    @return: object
    """
    try:
        data = request.get_json()
    except ValueError:
        return None

    if not data or name not in data:
        return None

    return data[name]


def get_request_parameter(name, expected_type, required=False):
    """
    Get parameter from request.
    @param name: param name
    @param expected_type: param type
    @param required: boolean
    @return: tuple/object (required/not required)
    """
    param = request.args.get(name, None)
    if not param:
        param = get_request_body_parameter(name)
    if not param:
        param = request.form.get(name, None)
    if not param:
        return (None, 'Param {} is required'.format(param)) if required else None

    param, msg = validate_param_type(param, expected_type)
    return (param, msg) if required else param
