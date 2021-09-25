import datetime
import json
import time
from functools import wraps

from flask import request, Response

from util import config
from util.logger.logger import Logger


def fails_safe_request(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        result = 500, [], "Server error. Please contact administrator."
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            Logger.exception("failsafe exception")
        return result

    return decorated


def webserver_logger(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        logger = Logger.get_logger("webserver_logger", config.DOCKER_WEB_REQUESTS_LOGS_FILEPATH)
        Logger.LOG_DIR = config.DOCKER_LOG_DIR

        client_ip = request.access_route[-1]
        if client_ip in config.NO_LOG_IPS:
            return func(*args, **kwargs)

        def process_body_json(_json):
            processed_json = {}
            for key, value in _json.items():
                if isinstance(value, dict):
                    processed_json[key] = process_body_json(value)
                else:
                    processed_json[key] = str(type(value))
            return processed_json

        # get args
        try:
            args_json = json.dumps(list(request.args.items()), separators=(',', ':'))
        except:
            args_json = json.dumps([])

        try:
            form_json = json.dumps(list(request.form.items()), separators=(',', ':'))
        except:
            form_json = json.dumps([])

        try:
            body_json = process_body_json(request.get_json())
            body_json = json.dumps(body_json, separators=(',', ':'))
        except:
            body_json = json.dumps({})

        args_json = args_json.replace(" ", "-")
        form_json = form_json.replace(" ", "-")
        body_json = body_json.replace(" ", "-")

        now = datetime.datetime.now()
        request_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        milisec = float(now.strftime("%f")) / 1000
        request_timestamp += f",{int(milisec)}"

        request_start = time.time()
        response = func(*args, **kwargs)
        request_end = time.time()

        try:
            if isinstance(response, tuple):
                data, status_code = response
                response_size = len(json.dumps(data))
            else:
                if isinstance(response, Response):
                    status_code = response.status_code
                    response_size = len(json.dumps(response.data))
                elif isinstance(response, str):
                    status_code = 200
                    response_size = len(response)
                else:
                    status_code = -1
                    response_size = -1
        except:
            response_size = -1
            status_code = -1

        message_info = dict(timestamp=request_timestamp, ip=client_ip, method=request.method, url=request.url,
                            args=args_json, form=form_json, body=body_json,
                            request_time=" {0:.3f}".format(request_end - request_start),
                            response_status=status_code, response_size="{0:.2f}KB".format(response_size / 1024))
        logger.info(json.dumps(message_info))
        return response

    return decorated
