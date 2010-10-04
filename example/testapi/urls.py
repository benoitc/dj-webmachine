from django.conf.urls.defaults import *

import webmachine



# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
webmachine.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^testapi/', include('testapi.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^api/', include(apipoint.api_site.urls)),
)

