import json

from webmachine import Resource

class Hello(Resource):


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


