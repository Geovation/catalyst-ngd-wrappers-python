import copy

from flask import Flask, request

from NGD_API_Wrappers import *

app = Flask(__name__)

from marshmallow import Schema, INCLUDE
from marshmallow.fields import Integer, String, Boolean, List

class BaseSchema(Schema):
    class Meta:
        unknown = INCLUDE  # Allows additional fields to pass through to query_params

class LimitSchema(BaseSchema):
    limit = Integer(data_key='limit', required=False)
    request_limit = Integer(data_key='request-limit', required=False)

class GeomSchema(BaseSchema):
    filter_wkt = String(required=False, data_key='filter-wkt')
    format_geojson = Boolean(required=False, data_key='format-geojson')

class ColSchema(BaseSchema):
    collection = List(String(), required=True, data_key='collection')

class LimitGeomSchema(LimitSchema, GeomSchema):
    """Combining Limit and Geom schemas"""

class LimitColSchema(LimitSchema, ColSchema):
    """Combining Limit and Col schemas"""

class GeomColSchema(GeomSchema, ColSchema):
    """Combining Geom and Col schemas"""

class LimitGeomColSchema(LimitSchema, GeomSchema, ColSchema):
    """Combining Limit, Geom, and Col schemas"""

@app.route("/", methods=['GET'])
def hello_world():
    args = request.args
    return args

def delistify(params: dict):
    for k, v in params.items():
        if k != 'collection':
            params[k] = v[0]

def create_item_route(schema_class: Schema, handler_function, route_suffix: str, multi_collections: bool = False):
    """Factory function to create route handlers for item endpoints"""

    collection_path_component = 'multi-collection' if multi_collections else '<collection>'
    route = f"/catalyst/features/ngd/ofa/v1/collections/{collection_path_component}/items/{route_suffix}"

    def handler(collection: str | list = None):
        schema = schema_class()
        args = request.args.to_dict(flat=not(multi_collections))
        if multi_collections:
            delistify(args)
        parsed_params = schema.load(args)
        
        custom_params = {
            k: parsed_params.pop(k)
            for k in schema.fields.keys()
            if k in parsed_params
        }
        if collection:
            custom_params['collection'] = collection

        return handler_function(
            query_params=parsed_params,
            **custom_params
        )
    
    # Set a unique name for the view function
    handler.__name__ = f"handle_{route_suffix.replace('-', '_')}"

    app.add_url_rule(
        route,
        view_func=handler,
        methods=['GET']
    )

    return handler

items_auth_handler = create_item_route(
    BaseSchema,
    items_auth,
    "auth"
)

items_auth_limit_handler = create_item_route(
    LimitSchema,
    items_auth_limit,
    "auth-limit"
)

items_auth_geom_handler = create_item_route(
    GeomSchema,
    items_auth_geom,
    "auth-geom"
)

items_auth_limit_geom_handler = create_item_route(
    LimitGeomSchema,
    items_auth_limit_geom,
    "auth-limit-geom"
)

items_auth_col_handler = create_item_route(
    ColSchema,
    items_auth_col,
    "auth-col",
    True
)

items_auth_limit_col_handler = create_item_route(
    LimitColSchema,
    items_auth_limit_col,
    "auth-limit-col",
    True
)

items_auth_geom_col_handler = create_item_route(
    GeomColSchema,
    items_auth_geom_col,
    "auth-geom-col",
    True
)

items_auth_limit_geom_col_handler = create_item_route(
    LimitGeomColSchema,
    items_auth_limit_geom_col,
    "auth-limit-geom-col",
    True
)

if __name__ == "__main__":
    app.run(debug=True)