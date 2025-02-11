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
def http_latest_single_col(req: HttpRequest) -> HttpResponse:
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

def construct_response(req, schema_class, collection, func: callable):
    schema = schema_class()
    collection = req.route_params.get('collection')

    params = {**req.params}
    parsed_params = schema.load(params)

    custom_params = {
        k: parsed_params.pop(k)
        for k in schema.fields.keys()
        if k in parsed_params
    }
    if collection:
        custom_params['collection'] = collection

    data = func(
        query_params = parsed_params
        **custom_params
    )
    json_data = json.dumps(data)

    return HttpResponse(
        body=json_data,
        mimetype="application/json"
    )