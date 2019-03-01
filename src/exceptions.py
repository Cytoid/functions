class HTTPException(Exception):
	status_code = 500
	def __init__(self, message, status=None, payload=None):
		super().__init__(self)
		self.message = message
		if status:
			self.status_code = status
		self.payload = payload

	def to_dict(self):
		rv = dict(self.payload or ())
		rv['message'] = self.message
		return rv


class BadRequest(HTTPException):
	status_code = 400

class NotFound(HTTPException):
	status_code = 404
