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
    def __init__(self, field_name, status_code=400):
        APIInvalidUsage.__init__(self, "'%s' field was missing or blank." % field_name, payload={
            "error": "missing-field",
            "field": field_name
        }, status_code=status_code)


class RequiresLogin(Exception):
    status_code = 401
    status = "failed"
    message = "This method requires login."

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["status"] = self.status
        rv['message'] = self.message
        return rv


class RequiresHTTPS(Exception):
    status_code = 401
    status = "failed"
    message = "This method requires a secure protocol."

    def __init__(self, payload=None):
        Exception.__init__(self)
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["status"] = self.status
        rv['message'] = self.message
        return rv


class AuthTokenInvalid(APIInvalidUsage):
    def __init__(self, status_code=400):
        APIInvalidUsage.__init__(self, "your auth code was not valid", payload={
            "error": "auth_token-invalid"
        }, status_code=status_code)


class AuthTokenExpired(APIInvalidUsage):
    def __init__(self, status_code=400):
        APIInvalidUsage.__init__(self, "your auth code has expired", payload={
            "error": "auth_token-expired"
        }, status_code=status_code)


class APIInvalidField(APIInvalidUsage):
    def __init__(self, field_name, status_code=400):
        APIInvalidUsage.__init__(self, "'%s' field was invalid." % field_name, payload={
            "error": "invalid-field",
            "field": field_name
        }, status_code=status_code)


class UserNotFound(APIInvalidUsage):
    def __init__(self, status_code=400):
        APIInvalidUsage.__init__(self, "User could not be found", payload={
            "error": "user-not-found"
        }, status_code=status_code)


class EstabNotFound(APIInvalidUsage):
    def __init__(self, status_code=400):
        APIInvalidUsage.__init__(self, "User could not be found", payload={
            "error": "user-not-found"
        }, status_code=status_code)
