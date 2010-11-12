from webmachine.api import wm

import json
@wm.route(r"^$")
def hello(req, resp):
    return "<html><p>hello world!</p></html>"


@wm.route(r"^$", provided=[("application/json", json.dumps)])
def hello_json(req, resp):
    print "ici"
    return {"ok": True, "message": "hellow world"}

