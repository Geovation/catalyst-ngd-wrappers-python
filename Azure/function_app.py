import azure.functions as func
from azure.functions import HttpRequest, HttpResponse
from NGD_API_Wrappers import *
import json

import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)

def callback_function(envelope):
    envelope.data.baseData.message += " - Custom message"

handler = AzureLogHandler(connection_string='InstrumentationKey=b4b97b45-708f-41fd-85cc-e2cb6d02acd6')
handler.add_telemetry_processor(callback_function)
logger.addHandler(handler)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

from marshmallow import Schema, INCLUDE, EXCLUDE
from marshmallow.fields import Integer, String, Boolean, List
from marshmallow.exceptions import ValidationError

class LatestCollectionsSchema(Schema):
    flag_recent_updates = Boolean(data_key='flag-recent-updates', required=False)
    recent_update_days = Integer(data_key='recent-update-days', required=False)

    class Meta:
        unknown = EXCLUDE

class BaseSchema(Schema):
    wkt = String(data_key='wkt', required=False)
    use_latest_collection = Boolean(data_key='use-latest-collection',required=False)

    class Meta:
        unknown = INCLUDE  # Allows additional fields to pass through to query_params

class AbstractHierarchicalSchema(BaseSchema):
    hierarchical_output = Boolean(data_key='hierarchical-output', required=False)

class LimitSchema(BaseSchema):
    limit = Integer(data_key='limit', required=False)
    request_limit = Integer(data_key='request-limit', required=False)

class GeomSchema(AbstractHierarchicalSchema):
    wkt = String(data_key='wkt', required=True)

class ColSchema(AbstractHierarchicalSchema):
    collection = List(String(), data_key='collection', required=True)

class LimitGeomSchema(LimitSchema, GeomSchema):
    wkt = String(data_key='wkt', required=True)

class LimitColSchema(LimitSchema, ColSchema):
    """Combining Limit and Col schemas"""

class GeomColSchema(GeomSchema, ColSchema):
    wkt = String(data_key='wkt', required=True)

class LimitGeomColSchema(LimitSchema, GeomSchema, ColSchema):
    wkt = String(data_key='wkt', required=True)

@app.function_name('http_latest_collections')
@app.route("catalyst/features/latest-collections")
def http_latest_collections(req: HttpRequest) -> HttpResponse:

    if req.method != 'GET':
        code = 405
        error_body = json.dumps({
            "code": code,
            "description": "The HTTP method requested is not supported. This endpoint only supports 'GET' requests.",
            "errorSource": "Catalyst Wrapper"
        })
        return HttpResponse(
            body=error_body,
            mimetype="application/json",
            status_code=code
        )

    schema = LatestCollectionsSchema()

    params = {**req.params}
    try:
        parsed_params = schema.load(params)
    except ValidationError as e:
        code = 400
        error_body = json.dumps({
            "code": code,
            "description": str(e),
            "errorSource": "Catalyst Wrapper"
        })
        return HttpResponse(
            error_body,
            mimetype="application/json",
            status_code=400
        )

    data = get_latest_collection_versions(**parsed_params)
    json_data = json.dumps(data)

    return HttpResponse(
        body=json_data,
        mimetype="application/json"
    )

@app.function_name('http_latest_single_col')
@app.route("catalyst/features/latest-collections/{collection}")
def http_latest_single_col(req: HttpRequest) -> HttpResponse:

    if req.method != 'GET':
        code = 405
        error_body = json.dumps({
            "code": code,
            "description": "The HTTP method requested is not supported. This endpoint only supports 'GET' requests.",
            "errorSource": "Catalyst Wrapper"
        })
        return HttpResponse(
            body=error_body,
            mimetype="application/json",
            status_code=code
        )

    schema = LatestCollectionsSchema()
    collection = req.route_params.get('collection')

    params = {**req.params}
    try:
        parsed_params = schema.load(params)
    except Exception as e:
        code = 400
        error_body = json.dumps({
            "code": code,
            "description": str(e),
            "errorSource": "Catalyst Wrapper"
        })
        return HttpResponse(
            body=error_body,
            mimetype="application/json",
            status_code=code
        )

    data = get_specific_latest_collections([collection], **parsed_params)
    json_data = json.dumps(data)

    return HttpResponse(
        body=json_data,
        mimetype="application/json"
    )

def delistify(params: dict):
    for k, v in params.items():
        if k != 'collection':
            params[k] = v[0]

def construct_response(req: HttpRequest, schema_class: type, func: callable) -> HttpResponse:

    try:
        if req.method != 'GET':
            code = 405
            error_body = json.dumps({
                "code": code,
                "description": "The HTTP method requested is not supported. This endpoint only supports 'GET' requests.",
                "errorSource": "Catalyst Wrapper"
            })
            return HttpResponse(
                body=error_body,
                mimetype="application/json",
                status_code=code
            )

        schema = schema_class()
        collection = req.route_params.get('collection')

        params = {**req.params}

        if not(collection):
            col = params.get('collection')
            if col:
                params['collection'] = params.get('collection').split(',')

        try:
            parsed_params = schema.load(params)
        except Exception as e:
            code = 400
            error_body = json.dumps({
                "code": code,
                "description": str(e),
                "errorSource": "Catalyst Wrapper"
            })
            return HttpResponse(
                body=error_body,
                mimetype="application/json",
                status_code=code
            )

        custom_params = {
            k: parsed_params.pop(k)
            for k in schema.fields.keys()
            if k in parsed_params
        }
        if collection:
            custom_params['collection'] = collection

        headers = req.headers.__dict__.get('__http_headers__')
        data = func(
            query_params=parsed_params,
            headers=headers,
            **custom_params
        )
        descr = data.get('description')
        if data.get('errorSource') and type(descr) == str:
            fields = [x.replace('_','-') for x in schema.fields if x != 'limit']
            attributes = ', '.join(fields)
            data['description'] = descr.format(attr=attributes)
        json_data = json.dumps(data)

        return HttpResponse(
            body=json_data,
            mimetype="application/json"
        )
    except Exception as e:
        code = 500
        error_string = str(e)
        error_response = json.dumps({
            "code": code,
            "description": error_string,
            "errorSource": "Catalyst Wrapper"
        })
        return HttpResponse(
            body=error_response,
            mimetype="application/json",
            status_code=code
        )

@app.function_name('http_base')
@app.route("catalyst/features/{collection}/items")
def http_base(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        BaseSchema,
        items
    )
    return response

@app.function_name('http_auth')
@app.route("catalyst/features/{collection}/items/auth")
def http_auth(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        BaseSchema,
        items_auth
    )
    return response

@app.function_name('http_limit')
@app.route("catalyst/features/{collection}/items/limit")
def http_limit(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitSchema,
        items_limit
    )
    return response

@app.function_name('http_geom')
@app.route("catalyst/features/{collection}/items/geom")
def http_geom(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        GeomSchema,
        items_geom
    )
    return response

@app.function_name('http_col')
@app.route("catalyst/features/multi-collection/items/col")
def http_col(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        ColSchema,
        items_col
    )
    return response

@app.function_name('http_limit_geom')
@app.route("catalyst/features/{collection}/items/limit-geom")
def http_limit_geom(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitGeomSchema,
        items_limit_geom
    )
    return response

@app.function_name('http_limit_col')
@app.route("catalyst/features/multi-collection/items/limit-col")
def http_limit_col(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitColSchema,
        items_limit_col
    )
    return response

@app.function_name('http_geom_col')
@app.route("catalyst/features/multi-collection/items/geom-col")
def http_geom_col(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        GeomColSchema,
        items_geom_col
    )
    return response

@app.function_name('http_limit_geom_col')
@app.route("catalyst/features/multi-collection/items/limit-geom-col")
def http_limit_geom_col(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitGeomColSchema,
        items_limit_geom_col
    )
    return response

@app.function_name('http_auth_limit')
@app.route("catalyst/features/{collection}/items/auth-limit")
def http_auth_limit(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitSchema,
        items_auth_limit
    )
    return response

@app.function_name('http_auth_geom')
@app.route("catalyst/features/{collection}/items/auth-geom")
def http_auth_geom(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        GeomSchema,
        items_auth_geom
    )
    return response

@app.function_name('http_auth_col')
@app.route("catalyst/features/multi-collection/items/auth-col")
def http_auth_col(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        ColSchema,
        items_auth_col
    )
    return response

@app.function_name('http_auth_limit_geom')
@app.route("catalyst/features/{collection}/items/auth-limit-geom")
def http_auth_limit_geom(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitGeomSchema,
        items_auth_limit_geom
    )
    return response

@app.function_name('http_auth_limit_col')
@app.route("catalyst/features/multi-collection/items/auth-limit-col")
def http_auth_geom_col(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitColSchema,
        items_auth_limit_col
    )
    return response

@app.function_name('http_auth_geom_col')
@app.route("catalyst/features/multi-collection/items/auth-geom-col")
def http_auth_geom_col(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        GeomColSchema,
        items_auth_geom_col
    )
    return response

@app.function_name('http_auth_limit_geom_col')
@app.route("catalyst/features/multi-collection/items/auth-limit-geom-col")
def http_auth_limit_geom_col(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitGeomColSchema,
        items_auth_limit_geom_col
    )
    return response
