from .exceptions import BadRequest
def handle_request(request):
    content_type = request.headers.get('content-type')
    if content_type == 'application/json':
        request_json = request.get_json(silent=True)
        if not request_json:
            raise BadRequest("Payload JSON is invalid")
        return request_json
    else:
        raise BadRequest("Unknown content type")
