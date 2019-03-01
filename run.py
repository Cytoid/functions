from flask import Flask, request
from src import resolve_level_files

app = Flask(__name__)

def register(name, func, methods):
	def wrapper():
		return func(request)
	app.add_url_rule('/' + name, name, wrapper, methods=methods)

register('resolve-level-files', resolve_level_files, methods=['POST'])

if __name__ == '__main__':
    app.run()
