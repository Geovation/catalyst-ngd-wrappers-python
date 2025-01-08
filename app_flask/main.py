import copy

from flask import Flask, request

from NGD_API_Wrappers import *

app = Flask(__name__)

@app.route("/")
def hello_world():
    args = request.args
    return args

@app.route("/catalyst/features/ngd/ofa/v1/collections/<collection>/items/items-auth-limit")
def read_item(collection: str):
    params = request.args.to_dict()
    custom_params = dict()
    for cp in ['limit','request-limit']:
        if cp in params:
            custom_params[cp.replace('-','_')] = int(params.pop(cp))
    result = items_auth_limit(collection=collection, query_params=params, **custom_params)
    return result

@app.route("/catalyst/features/ngd/ofa/v1/collections/<collection>/items/items-auth-limit-geom")
def read_item2(collection: str):
    params = request.args.to_dict()
    custom_params = dict()
    for cp in ['limit','request-limit']:
        if cp in params:
            custom_params[cp.replace('-','_')] = int(params.pop(cp))
    for cp in ['wkt']:
        if cp in params:
            custom_params[cp.replace('-','_')] = params.pop(cp)
    result = items_auth_limit_geom(collection=collection, query_params=params, **custom_params)
    return result

if __name__ == "__main__":
    app.run(debug=True)