# Create your views here.

from webmachine.resource import Resource
from webmachine.sites import api_site

import json

class HelloRes(Resource):

    def content_types_provided(self, req, resp):
        return ( 
            ("", self.to_html),
            ("application/json", self.to_json)
        )

    def to_html(self, req, resp):
        return "<html><body>Hello world!</body></html>"

    def to_json(self, req, resp):
        return json.dumps({"message": "hello world!", "ok": True})


api_site.register(HelloRes)
