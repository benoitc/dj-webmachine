# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

METHODS_CRUD = { 
    "POST": "create",
    "GET": "read",
    "PUT": "update",
    "HEAD": "read"
}

class Handler(object):

    def __init__(self, resource):

        self.resource = resource

    def decode(self, data):
        return None 

    def encode(self, data):
        return ""
    
    def handle_request(self, req, resp):
        if req.method in ("POST", "PUT"):
            req.decoded_data = self.decode(req, resp)

    def handle_response(self, req, resp):
        if req.method in METHODS_CRUD:
            meth = getattr(self.resource, METHODS_CRUD[req.method])
            body  = meth(req, resp)
            return self.encode(body)
        elif req.method == "DELETE":
            return self.encode(resp._container)
        return False

