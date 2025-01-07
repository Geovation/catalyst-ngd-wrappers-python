from flask import Flask, request

from NGD_API_Wrappers import *

app = Flask(__name__)

@app.route("/test")
def hello_world():
    args = request.args
    return args

@app.route("/catalyst/features/ngd/ofa/v1/collections/<collection>/items/items-auth-limit")
def read_item(collection: str):
    params = request.args
    print(*params)
    result = items_auth(collection=collection, *params)
    return result

if __name__ == "__main__":
    app.run(debug=True)