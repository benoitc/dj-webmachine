# Create your views here.

from webmachine.resource import Resource, ModelResource
from webmachine.sites import site

from testapi.hello.models import Entry

import json

class Hello(Resource):

    class Meta:
        resource_prefix = ''

    def content_types_provided(self, req, resp):
        return ( 
            ("", self.to_html),
            ("application/json", self.to_json)
        )

    def to_html(self, req, resp):
        return "<html><body>Hello world!</body></html>"

    def to_json(self, req, resp):
        return json.dumps({"message": "hello world!", "ok": True})


class Entry(ModelResource):
    model = Entry

site.register(Hello, Entry)
