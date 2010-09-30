# -*- coding: utf-8 -
#
# This file is part of dj-apipoint released under the Apache 2 license. 
# See the NOTICE for more information.

from django.http import HttpResponse
from django.utils.datastructures import SortedDict

class ApiSite(object):

    def __init__(self, name=None, app_name='apipoint'):
        self._registry = []
        self.name = name or 'admin'
        self.app_name = app_name

    def register(self, *ress):
        ress = ress or []
        for res in ress:
            self._registry.append(res) 
            
    def unregister(self, res):
        if res not in self._registry:
            raise ValueError('The resource %s is not registered' % res.__name__)
        del self._registry[res]


    def get_urls(self):
        from django.conf.urls.defaults import patterns, url, include
        urlpatterns = patterns('', 
            url(r'^$', self.index, name="index"),
        )

        for res in self._registry:
            instance = res()
            urlpatterns += patterns('',
                url(r'^%s/' % res._meta.app_label,
                    include(instance.get_urls()))
            )
        return urlpatterns

    def urls(self):
        return self.get_urls(), self.app_name, self.name
    urls = property(urls)


    def index(self, request):
        return HttpResponse("api index")

# This global object represent main api site
api_site = ApiSite()
