import azure.functions as func
from azure.functions import HttpResponse
import logging
from NGD_API_Wrappers import *
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
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
    
@app.route(route="catalyst/features/{collection}")
def http_latest_single_col(req):
    collection = req.route_params.get('collection')
    params = {**req.params}
    data = get_specific_latest_collections([collection], **params)
    json_data = json.dumps(data)
    return HttpResponse(
        body=json_data,
        mimetype="application/json"
    )