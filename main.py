from src import *

from flask import jsonify, current_app as app

from src.exceptions import HTTPException

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
