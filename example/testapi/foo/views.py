# Create your views here.


from apipoint.resource import Resource

class HelloRes(Resource):

    def to_html(self, req, resp):
        return "<html><body>Hello world!</body></html>"
