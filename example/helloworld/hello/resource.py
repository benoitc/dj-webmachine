import json

from webmachine import Resource
from webmachine import wm

class Hello(Resource):

    def content_types_provided(self, req, resp):
        return ( 
            ("", self.to_html),
            ("application/json", self.to_json)
        )

    def to_html(self, req, resp):
        return "<html><body>Hello world!</body></html>\n"
    
    def to_json(self, req, resp):
        return "%s\n" % json.dumps({"message": "hello world!", "ok": True})


# available at wm/hello
wm.add_resource(Hello, r"^hello")


# available at wm/helloworld/hello
wm.add_resource(Hello)

