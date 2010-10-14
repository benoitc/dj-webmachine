# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from webmachine import resource
from webmachine import handlers

METHODS_CRUD = { 
    "POST": "create",
    "GET": "read",
    "PUT": "update",
    "DELETE": "delete"
}

class CrudResource(resource.Resource):
    """ simple resource to manage crud action, it take care of
    deserialization, serialization to xml or json by default """


    accept = ['application/json', 'application/xml']
    provides = ['application/json', 'application/xml']

    def create(self, req, resp):
        """ do something on POST """
        return None

    def read(self, req, resp):
        """ do something ong GET or head 
        """
        return None

    def update(self, req, resp):
        """ do something on PUT """

    def delete(self, req, resp):
        """ do something on DELETE """
        return True

    def allowed_methods(self, req, resp):
        return ['DELETE', 'GET', 'HEAD', 'POST', 'PUT']

    # private methods

    def format_suffix_accepted(self, req, resp):
        accepted = []
        for ctype in self.provides:
            accepted.append((ctype, handlers.get_suffix(ctype)))
        return accepted

    def content_types_accepted(self, req, resp):
        accepted = []
        for ctype in self.accept:
            hdl = handlers.get_handler(ctype, self)
            accepted.append((ctype, hdl.handle_request))
        return accepted 

    def content_types_provided(self, req, resp):
        provided = []
        for ctype in self.provides:
            hdl = handlers.get_handler(ctype, self)
            provided.append((ctype, hdl.handle_response))
        return provided

    def delete_resource(self, req, resp):
        return self.delete(req, resp)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        
        urlpatterns = patterns('',
            # update or delete, format suffix given
            url(r'^(?P<id>\w+)\.(?P<%s>\w*)$' % self.format_sufx_param, self, 
                name="%s_action_edit_fmt"  % self.__class__.__name__),

            # update or delete 
            url(r'^(?P<id>\w+)$', self, name="%s_action_edit"  %
                self.__class__.__name__),

            # post or get, suffix given 
            url(r'^\.(?P<%s>\w*)$' % self.format_sufx_param, self, 
                name="%s_index_fmt" % self.__class__.__name__),

            # base url / on the resource.
            url(r'^', self, name="%s_index" % self.__class__.__name__),
        )

        return urlpatterns
