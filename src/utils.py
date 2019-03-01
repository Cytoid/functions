def handle_request(request):
    content_type = request.headers.get('content-type')
    if content_type == 'application/json':
        request_json = request.get_json(silent=True)
        if not request_json:
            raise ValueError("Payload JSON is invalid")
        return request_json
    else:
        raise ValueError("Unknown content type")
