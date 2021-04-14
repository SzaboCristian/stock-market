def response_code_successful(code):
    return code in [200, 201, 202]


def response(code, data, message):
    return {"data": data, "message": message}, code


def response_deprecated(code, data, message):
    return response(code, data, f"[ Deprecated ] {message}")


def response_200(data):
    return response(200, data, "OK")


def response_400(message):
    return response(400, None, message)


def response_404(message):
    return response(404, None, message)


def response_500(message):
    return response(500, None, message)
