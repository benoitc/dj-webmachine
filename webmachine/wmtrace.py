# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import os
import os.path
from glob import iglob

try:
    import json
except ImportError:
    import django.utils.simplejson as json

from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.views import static
from webmachine import Resource

class WMTraceResource(Resource):

    def __init__(self, path="/tmp"):
        if path.endswith("/"):
            path = path[:-1]
        self.path = os.path.abspath(path)
    
    def trace_list_html(self, req, resp):
        files = [os.path.basename(f).split("wmtrace-")[1] for f in \
                iglob("%s/wmtrace-*.*" % self.path)]
        return render_to_string("wm/wmtrace_list.html", {
            "path": self.path, 
            "files": files
        })

    def trace_html(self, req, resp):
        fname = req.url_kwargs["file"]
        fname = os.path.join(self.path, "wmtrace-%s" % fname)
        with open(fname, "r+b") as f:
            return render_to_string("wm/wmtrace.html", {
                "fname": fname,
                "trace": f.read()
            })

    def to_html(self, req, resp):
        if "file" in req.url_kwargs:
            return self.trace_html(req, resp)
        return self.trace_list_html(req, resp)


    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        media_path = os.path.abspath(os.path.join(__file__, "..",
            "media"))
        print media_path
        urlpatterns = patterns('',
            url(r'wmtrace-(?P<file>.+)$', self, name="wmtrace"),
            url(r'^static/(?P<path>.*)', static.serve, {
                'document_root': media_path,
                'show_indexes': False
            }),
            url(r'$', self, name="wmtrace_list"),
            
        )

        return urlpatterns

