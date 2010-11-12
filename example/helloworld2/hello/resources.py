from webmachine.api import wm

import json
@wm.route(r"^$")
def hello(req, resp):
    return "<html><p>hello world!</p></html>"


@wm.route(r"^$", provided=[("application/json", json.dumps)])
def hello_json(req, resp):
    return {"ok": True, "message": "hellow world"}

@wm.route(r"^hello$", provided=["text/html", ("application/json", json.dumps)])
def all_in_one(req, resp):
    if resp.content_type == "application/json":
        return {"ok": True, "message": "hellow world! All in one"}
    else:
        return "<html><p>hello world! All in one</p></html>"


