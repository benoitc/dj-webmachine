from webmachine import Resource
from webmachine.auth.oauth import Oauth

class Protected(Resource):

    def to_html(self, req, resp):
        return "<html><p>I'm protected you know.</p></html>"

    def is_authorized(self, req, resp):
        return Oauth().authorized(req, resp)
