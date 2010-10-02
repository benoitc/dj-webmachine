# -*- coding: utf-8 -
#
# This file is part of dj-apipoint released under the MIT license. 
# See the NOTICE for more information.


from apipoint.resource import base


class ModelResource(base.Resource):

    model = None
    form = None

    def __init__(self, model=None, form=None):
        if model is not None:
            self.model = model
        if model is not None:
            self.form = form

        if not self.model:
            raise ValueError("You should specify a form")


    def get_model(self, key):
        """ this method is used to get the object to read, delete or
        update. Could be ovveridable, should return a model instance."""
        try:
            return self.model.objects.get(id=key)
        except self.model.DoesNotExist:
            return False
        except self.model.MultipleObjectsReturned, e:
            raise HTTPBadRequest(str(e))

    # these methods below shouldn't be edited most of the time.

    def allowed_methods(self, req, resp):
        return ['DELETE', 'GET', 'HEAD', 'POST', 'PUT']

    def content_types_accepted(self, req, resp):
        ret = [
            ("application/xml", self.from_xml),
            ("application/json": self.from_json)
        ]

        if self.form is not None:
            # we specified a form 
            ret += [
                ("application/x-www-form-urlencoded ",
                    self.from_form),
                ("multipart/form-data", self.from_form)
            ]
        return ret

    def resource_exists(self, req, resp):
        resource_id = req.url_kwargs.get("id")
        if not resource_id:
            return True

        obj = get_obj(reource_id)
        if not obj:
            return False
        req.obj = obj
        return True


    def delete_resource(self, req, resp):
        if req.obj:
            req.obj.delete()
        return False

    def get_urls(self):
        from django.conf.urls.defaults import patterns, url
        urlpatterns = patterns('',
            url('e

    
        
    

