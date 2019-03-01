from flask import Flask, request, jsonify
from src import resolve_level_files
from src.exceptions import HTTPException

app = Flask(__name__)

def register(name, func, methods):
	def wrapper():
		return func(request)
	app.add_url_rule('/' + name, name, wrapper, methods=methods)

register('resolve-level-files', resolve_level_files, methods=['POST'])

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    app.run()
