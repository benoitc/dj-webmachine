# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from django.http import HttpResponse

class Site(object):

    def __init__(self, name=None, app_name='webmachine'):
        self._registry = []
        self.name = name or 'api'
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
            if not res._meta.resource_prefix:
                pattern = r'^%s' % res._meta.app_label
            else:
                pattern = r'^%s/%s' % (res._meta.app_label,
                    res._meta.resource_prefix)
            

            urlpatterns += patterns('',
                url(pattern, include(instance.get_urls())),
            )
        return urlpatterns

    def urls(self):
        return self.get_urls(), self.app_name, self.name
    urls = property(urls)


    def index(self, request):
        return HttpResponse("api index")

# This global object represent the main api site
site = Site() 
