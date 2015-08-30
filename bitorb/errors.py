class APIInvalidUsage(Exception):
    status_code = 400
    status = "failed"

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["status"] = self.status
        rv['message'] = self.message
        return rv


class APIMissingField(APIInvalidUsage):
    def __init__(self, field_name):
        APIInvalidUsage.__init__(self, "'%s' field was missing or blank." % field_name, payload={
            "error": "missing-field",
            "field": field_name
        })


class AuthTokenInvalid(APIInvalidUsage):
    def __init__(self):
        APIInvalidUsage.__init__(self, "your auth code was not valid", payload={
            "error": "auth_token-invalid"
        })


class AuthTokenExpired(APIInvalidUsage):
    def __init__(self):
        APIInvalidUsage.__init__(self, "your auth code has expired", payload={
            "error": "auth_token-expired"
        })


