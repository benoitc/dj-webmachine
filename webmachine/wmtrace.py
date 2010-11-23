# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from __future__ import with_statement

from datetime import datetime
import inspect
import os
import json
import traceback

def update_trace(state, req, resp, trace):
    infos = {
            "request": {
                "headers": req.headers.items(),
                "get": [(k, req.GET.getlist(k)) for k in req.GET],
                "post": [(k, req.POST.getlist(k)) for k in req.POST],
                "cookies": [(k, req.COOKIES.get(k)) for k in req.COOKIES],
                "url_args": req.url_args,
                "url_kwarg": req.url_kwargs
            },
            "response": {
                "code": resp.status_code,
                "headers": resp.headerlist
            }

    }

    if hasattr(req, 'session'):
        infos['request'].update({
            'session': [(k, req.session.get(k)) for k in \
                    req.session.keys()]
        })

    if isinstance(state, int):
        name = str(state)
    else:
        name = state.__name__

    trace.append((name, infos))

def update_ex_trace(trace, e):
    trace.append(("error", traceback.format_exc()))

def write_trace(res, trace):
    if not res.trace:
        return

    if not res.trace_path:
        trace_path = "/tmp"

    now = datetime.now().replace(microsecond=0).isoformat() + 'Z'
    fname = os.path.join(os.path.abspath(trace_path),
            "wmtrace-%s-%s.trace" % (res.__class__.__name__, now))

    with open(fname, "w+b") as f:
        f.write(json.dumps(trace))


