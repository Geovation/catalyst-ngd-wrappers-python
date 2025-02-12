import azure.functions as func
from azure.functions import HttpRequest, HttpResponse
import logging
from NGD_API_Wrappers import *
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

from marshmallow import Schema, INCLUDE
from marshmallow.fields import Integer, String, Boolean, List

class LatestCollectionsSchema(Schema):
    flag_recent_updates = Boolean(required=False, data_key='flag-recent-updates')
    recent_update_days = Integer(required=False, data_key='recent_update_days')

class BaseSchema(Schema):
    filter_wkt = String(required=False, data_key='filter-wkt')
    use_latest_collection = Boolean(required=False, data_key='use-latest-collection')

    class Meta:
        unknown = INCLUDE  # Allows additional fields to pass through to query_params

class LimitSchema(BaseSchema):
    limit = Integer(data_key='limit', required=False)
    request_limit = Integer(data_key='request-limit', required=False)

class GeomSchema(BaseSchema):
    hierarchical_output = Boolean(required=False, data_key='hierarchical-output')

class ColSchema(GeomSchema):
    collections = List(String(), required=True, data_key='collection')

class LimitGeomSchema(LimitSchema, GeomSchema):
    """Combining Limit and Geom schemas"""

class LimitColSchema(LimitSchema, ColSchema):
    """Combining Limit and Col schemas"""

class GeomColSchema(ColSchema):
    """Combining Geom and Col schemas"""

class LimitGeomColSchema(LimitSchema, ColSchema):
    """Combining Limit, Geom, and Col schemas"""

@app.route(route="http_trigger")
def http_trigger(req: HttpRequest) -> HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    
@app.route("catalyst/features/latest-collections")
def http_latest_collections(req: HttpRequest) -> HttpResponse:
    schema = LatestCollectionsSchema()

    params = {**req.params}
    parsed_params = schema.load(params)

    return get_latest_collection_versions(**parsed_params)

@app.route("catalyst/features/latest-collections/{collection}")
def http_latest_single_col(req: HttpRequest) -> HttpResponse:
    schema = LatestCollectionsSchema()
    collection = req.route_params.get('collection')

    params = {**req.params}
    parsed_params = schema.load(params)

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

def construct_response(req, schema_class, func: callable):
    try:
        schema = schema_class()
        collection = req.route_params.get('collection')

        params = {**req.params}
        if not(collection):
            params['collection'] = params['collection'].split(',')
        parsed_params = schema.load(params)

        custom_params = {
            k: parsed_params.pop(k)
            for k in schema.fields.keys()
            if k in parsed_params
        }
        if collection:
            custom_params['collection'] = collection
        
        data = func(
            query_params=parsed_params,
            **custom_params
        )
        json_data = json.dumps(data)

        return HttpResponse(
            body=json_data,
            mimetype="application/json"
        )
    except Exception as e:
        error_response = {
            "error": str(e),
            "status": 500  # You might want to make this dynamic based on the error type
        }
        return HttpResponse(
            body=json.dumps(error_response),
            mimetype="application/json",
            status_code=500
        )

@app.route("catalyst/features/{collection}/items")
def one(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        BaseSchema,
        items
    )
    return response

@app.route("catalyst/features/{collection}/items/auth")
def two(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        BaseSchema,
        items_auth
    )
    return response

@app.route("catalyst/features/{collection}/items/limit")
def three(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitSchema,
        items_limit
    )
    return response

@app.route("catalyst/features/{collection}/items/geom")
def four(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        GeomSchema,
        items_geom
    )
    return response

@app.route("catalyst/features/multi-collections/items/col")
def five(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        ColSchema,
        items_col
    )
    return response

@app.route("catalyst/features/{collection}/items/limit-geom")
def six(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitGeomSchema,
        items_limit_geom
    )
    return response

@app.route("catalyst/features/multi-collections/items/limit-col")
def seven(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitColSchema,
        items_limit_col
    )
    return response

@app.route("catalyst/features/multi-collections/items/geom-col")
def eight(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        GeomColSchema,
        items_geom_col
    )
    return response

@app.route("catalyst/features/multi-collections/items/limit-geom-col")
def nine(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitGeomColSchema,
        items_limit_geom_col
    )
    return response

@app.route("catalyst/features/{collection}/items/auth-limit")
def ten(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitSchema,
        items_auth_limit
    )
    return response

@app.route("catalyst/features/{collection}/items/auth-geom")
def eleven(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        GeomSchema,
        items_auth_geom
    )
    return response

@app.route("catalyst/features/multi-collections/items/auth-col")
def twelve(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        ColSchema,
        items_auth_col
    )
    return response

@app.route("catalyst/features/{collection}/items/auth-limit-geom")
def thirteen(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitGeomSchema,
        items_auth_limit_geom
    )
    return response

@app.route("catalyst/features/multi-collections/items/auth-limit-col")
def fourteen(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitColSchema,
        items_auth_limit_col
    )
    return response

@app.route("catalyst/features/multi-collections/items/auth-geom-col")
def fifteen(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        GeomColSchema,
        items_auth_geom_col
    )
    return response

@app.route("catalyst/features/multi-collections/items/auth-limit-geom-col")
def sixteen(req: HttpRequest) -> HttpResponse:
    response = construct_response(
        req,
        LimitGeomColSchema,
        items_auth_limit_geom_col
    )
    return response