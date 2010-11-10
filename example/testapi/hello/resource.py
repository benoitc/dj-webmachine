# Create your views here.

from webmachine import Resource
from webmachine.resources import ModelResource, CrudResource
from webmachine.sites import site

from testapi.hello.models import Entry

import json

class Hello(Resource):


    class Meta:
        resource_prefix = ''

    def format_suffix_accepted(self, req, resp):
        return [("json", "application/json")]

    def content_types_provided(self, req, resp):
        return ( 
            ("", self.to_html),
            ("application/json", self.to_json)
        )

    def to_html(self, req, resp):
        return "<html><body>Hello world!</body></html>\n"
    
    def to_json(self, req, resp):
        return "%s\n" % json.dumps({"message": "hello world!", "ok": True})


