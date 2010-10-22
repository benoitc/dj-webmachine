
from webmachine.exc import HTTPClientError

class Auth(object):

    def authorized(self, request):
        return True

class BasicAuth(Auth):

    def __init__(self, func=authenticate, realm="API"):
        self.func = func
        self.realm = realm

    def authorized(self, request):
        auth_str = request.META.get("HTTP_AUTHORIZATION")
        if not auth_str:
            return False

        try:
            (meth, auth) = auth_str.split(" ", 1)
            if meth.lower() != "basic":
                # bad method
                return False
            auth = auth.strip().decode('base64')
            (user, pwd) = auth.split(":", 1)
        except (ValueError, binascii.Error):
            raise HTTPClientError()

        request.user = self.func(username=username, password=pwd)
        if not request.user:
            request.user = AnonymousUser()
            return False

        return True

