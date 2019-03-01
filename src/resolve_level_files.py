import os
import tempfile
import json
import zipfile
import string
import random
from flask import Response
from google.cloud import storage

from .utils import handle_request
from . import exceptions

bucket = storage.Client().bucket('assets.staging.cytoid.io')


def run (request):
	payload = handle_request(request)
	if 'url' not in payload:
		raise exceptions.BadRequest('url of the target file not specified')
	filepath = payload['url']
	parseLevelFile(filepath)
	return ''

def assetPaths(metadata):
	yield metadata['music_preview']['path']
	yield metadata['music']['path']
	yield metadata['background']['path']

def parseLevelFile(filepath):
	fileblob = bucket.get_blob(filepath)
	if not fileblob:
		raise exceptions.NotFound('file not found')
		return

	# Temp File to download level file into
	filedata = {}
	try:
		with tempfile.TemporaryDirectory() as temp_dir,\
			tempfile.TemporaryFile() as temp_file:
			fileblob.download_to_file(temp_file)
			with zipfile.ZipFile(temp_file, 'r') as zipFile,\
				zipFile.open('level.json') as meta_file:
				metadata = json.load(meta_file)
				print(metadata)
				filedata['metadata'] = metadata
				
				level_dir_path = os.path.join('levels', randomStr(30))
				for path in assetPaths(filedata['metadata']):
					zipFile.extract(path, path=temp_dir)
					upload_file(temp_dir, level_dir_path, path)
					os.remove(os.path.join(temp_dir, path))
				print(level_dir_path)

	except FileNotFoundError as error:
		raise exceptions.NotFound("file specified in metadata not found")
	except zipfile.BadZipFile as error:
		raise exceptions.BadRequest("Zip Package Invalid")
	except zipfile.LargeZipFile as error:
		raise exceptions.HTTPException("Zip Package too big", status=501)
	return ''

def upload_file(source_path, destination_path, filename):
	bucket.blob(
		os.path.join(destination_path, filename)
	).upload_from_filename(
		os.path.join(source_path, filename)
	)

def checkFileExistance(directory, data):
	if not data:
		return False
	path = data.get('path')
	if not path:
		return False
	path = os.path.join(directory, path)
	if not os.path.isfile(path):
		return False
	return True

def randomStr(size, chars=None):
	if not chars:
		chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
	return ''.join(random.choice(chars) for x in range(size))
