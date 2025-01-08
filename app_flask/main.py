import copy

from flask import Flask, request

from NGD_API_Wrappers import *

app = Flask(__name__)

from marshmallow import Schema, INCLUDE
from marshmallow.fields import Integer, String, Boolean

class ItemsAuthSchema(Schema):
    class Meta:
        unknown = INCLUDE  # Allows additional fields to pass through to query_params

class ItemsAuthLimitSchema(ItemsAuthSchema):
    limit = Integer(data_key='limit', required=False)
    request_limit = Integer(data_key='request-limit', required=False)
    verbose = Boolean(data_key='verbose', required=False)

class ItemsAuthGeomSchema(ItemsAuthSchema):
    wkt = String(required=False)

class ItemsAuthLimitGeomSchema(ItemsAuthLimitSchema, ItemsAuthGeomSchema):
    """Combining the two super classes"""

@app.route("/")
def hello_world():
    args = request.args
    return args

def create_item_route(schema_class: Schema, handler_function, route_suffix: str):
    """Factory function to create route handlers for item endpoints"""
    route = f"/catalyst/features/ngd/ofa/v1/collections/<collection>/items/{route_suffix}"
    
    @app.route(route)
    def handler(collection: str):
        schema = schema_class()
        parsed_params = schema.load(request.args)
        
        custom_params = {
            k: parsed_params.pop(k)
            for k in schema.fields.keys()
            if k in parsed_params
        }
        
        return handler_function(
            collection=collection,
            query_params=parsed_params,
            **custom_params
        )
    
    # Set a unique name for the view function
    handler.__name__ = f"handle_{route_suffix.replace('-', '_')}"
    return handler

items_auth_handler = create_item_route(
    ItemsAuthSchema,
    items_auth,
    "items-auth"
)

items_auth_limit_handler = create_item_route(
    ItemsAuthLimitSchema,
    items_auth_limit,
    "items-auth-limit"
)

items_auth_geom_handler = create_item_route(
    ItemsAuthGeomSchema,
    items_auth_geom,
    "items-auth-geom"
)

items_auth_limit_geom_handler = create_item_route(
    ItemsAuthLimitGeomSchema,
    items_auth_limit_geom,
    "items-auth-limit-geom"
)

if __name__ == "__main__":
    app.run(debug=True)