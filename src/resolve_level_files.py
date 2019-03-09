import os
import tempfile
import json
import zipfile
import string
import random
from flask import Response, jsonify
from google.cloud import storage

from .utils import handle_request
from . import exceptions

bucket = storage.Client().bucket('assets.cytoid.io')


def run (request):
	payload = handle_request(request)
	filepath = payload.get('packagePath')
	bundlepath = payload.get('bundlePath')
	if not filepath or not bundlepath:
		raise exceptions.BadRequest('packagePath or bundlePath not specified')
	return jsonify(parseLevelFile(filepath, bundlepath))

def assetPaths(metadata):
	yield metadata['music_preview']['path']
	yield metadata['music']['path']
	yield metadata['background']['path']

def parseLevelFile(filepath, bundlepath):
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

				for asset_filename in assetPaths(filedata['metadata']):
					zipFile.extract(asset_filename, path=temp_dir)
					bucket.blob(
						os.path.join(bundlepath, asset_filename)
					).upload_from_filename(
						os.path.join(temp_dir, asset_filename)
					)
					os.remove(os.path.join(temp_dir, asset_filename))

	except FileNotFoundError as error:
		raise exceptions.NotFound("file specified in metadata not found")
	except zipfile.BadZipFile as error:
		raise exceptions.BadRequest("Zip Package Invalid")
	except zipfile.LargeZipFile as error:
		raise exceptions.HTTPException("Zip Package too big", status=501)
	return filedata

def randomStr(size, chars=None):
	if not chars:
		chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
	return ''.join(random.choice(chars) for x in range(size))
