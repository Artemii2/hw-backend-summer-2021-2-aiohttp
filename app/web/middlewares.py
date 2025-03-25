import json
import typing

from aiohttp.web_exceptions import *
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}

ERROR_HANDLERS = {
    HTTPException: lambda e: error_json_response(
        http_status=500,
        status=HTTP_ERROR_CODES[500],
        message=e.reason,
        data=e.text,
    ),
    HTTPBadRequest: lambda e: error_json_response(
        http_status=400,
        status=HTTP_ERROR_CODES[400],
        message=e.reason,
        data=e.text,
    ),
    HTTPForbidden: lambda e: error_json_response(
        http_status=403,
        status=HTTP_ERROR_CODES[403],
        message=e.reason,
        data=e.text,
    ),
    HTTPUnauthorized: lambda e: error_json_response(
        http_status=401,
        status=HTTP_ERROR_CODES[401],
        message=e.reason,
        data=e.text,
    ),
    HTTPConflict: lambda e: error_json_response(
        http_status=409,
        status=HTTP_ERROR_CODES[409],
        message=e.reason,
        data=e.text,
    ),
    HTTPNotFound: lambda e: error_json_response(
        http_status=404,
        status=HTTP_ERROR_CODES[404],
        message=e.reason,
        data=e.text,
    )
}

@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPException as e:
        return ERROR_HANDLERS[type(e)](e)

    return response
    # TODO: обработать все исключения-наследники HTTPException и отдельно Exception, как server error
    #  использовать текст из HTTP_ERROR_CODES

@middleware
async def auth_middleware(request: "Request",handler):
    if request.path!="/admin.login":
        cookie=request.cookies.get("session_key")
        if cookie:
            if cookie!=request.app.config.session.key:
                raise HTTPForbidden
        else:
            raise HTTPUnauthorized
    try:
        resp=await handler(request)
    except Exception as e:
        raise e
    return resp

def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
    app.middlewares.append(auth_middleware)
