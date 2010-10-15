# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from django.core import serializers

from webmachine import resource
from webmachine.resources.crud import CrudResource


__all__ = ['ModelResource']

class ModelResourceMeta(resource.ResourceMeta):
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelResourceMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, ModelResourceMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        model = attrs.get('model', False)
        if not model:
            raise AttributeError("model attribute isn't set")

        attrs['form'] = attrs.get('form')
        
        new_class = super_new(cls, name, bases, attrs)
        return new_class

        
class ModelResource(CrudResource):
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

    
    def create(self, req, resp):
        instance = self.model(**req.decoded_data)
        instance.save()
        return instance

    def read(self, req, resp):
        return req.obj

    def update(self, req, resp):
        instance = req.obj
        for k, v in req.decoded_data.items():
            setattr(instance, k, v)
        return {"ok", True, "id": req.id}


    def delete(self, req, resp):
        req.obj.delete()
        return {"ok": True, "id": req.obj_id}

    def allowed_methods(self, req, resp):
        if "id" in req.url_kwargs:
            return ['DELETE', 'GET', 'HEAD', 'POST', 'PUT']
        return ['GET', 'HEAD', 'POST']

    def resource_exists(self, req, resp):
        resource_id = req.url_kwargs.get("id")
        if not resource_id:
            return True

        obj = self.find(resource_id)
        if not obj:
            return False
        req.obj_id = resource_id
        req.obj = obj
        return True
