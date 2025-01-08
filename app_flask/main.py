import copy

from flask import Flask, request

from NGD_API_Wrappers import *

app = Flask(__name__)

from marshmallow import Schema, INCLUDE
from marshmallow.fields import Integer, String, Boolean

class ItemsAuthLimitSchema(Schema):
    limit = Integer(data_key='limit', required=False)
    request_limit = Integer(data_key='request-limit', required=False)
    verbose = Boolean(data_key='verbose', required=False)

    class Meta:
        unknown = INCLUDE  # Allows additional fields to pass through to query_params

class ItemsAuthLimitGeomSchema(ItemsAuthLimitSchema):
    wkt = String(required=False)

@app.route("/")
def hello_world():
    args = request.args
    return args

@app.route("/catalyst/features/ngd/ofa/v1/collections/<collection>/items/items-auth-limit")
def read_item(collection: str):
    # Parse and validate parameters
    schema = ItemsAuthLimitSchema()
    parsed_params = schema.load(request.args)
    
    custom_param_names = schema.fields.keys()
    
    # Separate custom parameters from query parameters
    custom_params = {
        k: parsed_params.pop(k)
        for k in custom_param_names
        if k in parsed_params
    }
    # Pass remaining parameters as query_params
    result = items_auth_limit(
        collection=collection,
        query_params=parsed_params,
        **custom_params
    )
    return result

@app.route("/catalyst/features/ngd/ofa/v1/collections/<collection>/items/items-auth-limit-geom")
def read_item2(collection: str):
    # Parse and validate parameters
    schema = ItemsAuthLimitGeomSchema()
    parsed_params = schema.load(request.args)

    custom_param_names = schema.fields.keys()
    
    # Separate custom parameters from query parameters
    custom_params = {
        k: parsed_params.pop(k)
        for k in custom_param_names
        if k in parsed_params
    }
    
    # Pass remaining parameters as query_params
    result = items_auth_limit_geom(
        collection=collection,
        query_params=parsed_params,
        **custom_params
    )
    return result

if __name__ == "__main__":
    app.run(debug=True)