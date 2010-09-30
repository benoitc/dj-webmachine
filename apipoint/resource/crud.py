# -*- coding: utf-8 -
#
# This file is part of dj-apipoint released under the Apache 2 license. 
# See the NOTICE for more information.

from apipoint.resource import base

__all__ = ['CrudResource']


class CrudResource(base.Resource):
    """ Simple crud resource """

    def allowed_methods(self, req, resp):
        return ["DELETE", "GET", "HEAD", "POST", "PUT"]

    def create(self, req, resp):
        return None

    def read(self, req, resp):
        return None

    def update(self, req, resp):
        return None

    def delete(self, req, resp):
        return None


    def post_is_create(self, req, resp):
        if req.method == "POST" or req.url_kwargs.get('action') == "create":
            return self.create(req, resp)
        return False

    def process_post(self, req, resp):
        return self.update(req, post) 

    def delete_resource(self, req, resp):
        return self.delete(req, resp)


    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include

        
        urlpatterns = patterns('',
            url(r'^(?P<action>\w+)/(?P<id>.+)$', self, name="edit"),
            url(r'^(?P<action>\w+)$', self, name="use"),
        )

        return urlpatterns += super(CrudResource, self).get_urls()
