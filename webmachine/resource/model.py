# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from django.core import serializers

from webmachine.resource import base

class ModelResourceMeta(base.ResourceMeta):
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelResourceMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, ModelResourceMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
            
        model = attrs.get('model', False)
        if not model:
            raise AttributeError("model attribute isn't set")
        
        return super_new(cls, name, bases, attrs)

        
class ModelResource(base.Resource):
    __metaclass__ = ModelResourceMeta


    model = None
    form = None

    def __init__(self, model=None, form=None):
        if model is not None:
            self.model = model
        if model is not None:
            self.form = form

        if not self.model:
            raise ValueError("You should specify a form")


    def find(self, key):
        """ this method is used to get the object to read, delete or
        update. Could be ovveridable, should return a model instance."""
        try:
            return self.model.objects.get(id=key)
        except self.model.DoesNotExist:
            return False
        except self.model.MultipleObjectsReturned, e:
            raise HTTPBadRequest(str(e))

    
    def create(self, obj, req, resp):
        pass

    def read(self, req, resp):
        pass


    def update(self, obj, req, resp):
        pass

    def delete(self, obj, req, resp):
        obj.delete()
        return True

    def unkown_method(self, obj, req, resp):
        return
    
    # these methods below shouldn't be edited most of the time. 
    def to_html(self, req, resp):
        return '<html></html>'

    def to_json(self, req, resp):
        return '{}'

    def to_xml(self, req, resp):
        return 'xml'

    def from_json(self, req, resp):
        objs = list(serializers.deserialize("json", req.body))
        
        print type(obj)
        print objs[0]
        self._handle_request_body(obj, req, resp)

    def from_xml(self, req, resp):
        objs = list(serializers.deserialize("xml", req.body))
        self._handle_request_body(obj, req, resp)


    def _handle_request_body(self, obj, req, resp):
        if req.method == "POST":
            self.create(objs[0], req, resp)
        elif req.method == "PUT":
            self.update(objs[0], req, resp)
        else:
            self.unknow_method(objs[0], req, resp)
        
    def allowed_methods(self, req, resp):
        return ['DELETE', 'GET', 'HEAD', 'POST', 'PUT']

    def content_types_accepted(self, req, resp):
        ret = [
            ("application/xml", self.from_xml),
            ("application/json", self.from_json)
        ]

        if self.form is not None:
            # we specified a form 
            ret += [
                ("application/x-www-form-urlencoded ",
                    self.from_form),
                ("multipart/form-data", self.from_form)
            ]
        return ret
    
    def content_types_provided(self, req, resp):
        return ( 
            ("", self.to_html),
            ("text/html", self.to_html),
            ("application/xhtml+xml", self.to_html),
            ("application/json", self.to_json),
            ("application/xml", self.to_xml)
        )

    def resource_exists(self, req, resp):
        resource_id = req.url_kwargs.get("id")
        if not resource_id:
            return True

        obj = self.find(reource_id)
        if not obj:
            return False
        req.obj = obj
        return True


    def delete_resource(self, req, resp):
        return self.delete(req.obj, req, resp)

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url


        urlpatterns = patterns('',
            url(r'^(?P<action>\w+)/(?P<id>\w+)$', self, name="%s_action_edit"  %
                self.__class__.__name__),
            url(r'^(?P<action>\w+)$', self, name="%s_action"  %
                self.__class__.__name__),
            url(r'^$', self, name="%s_index" % self.__class__.__name__),
        )
        return urlpatterns

    
        
    

