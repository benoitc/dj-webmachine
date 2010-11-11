from django.conf.urls.defaults import *
from webmachine.auth import oauth_res

from testoauth.protected.resource import Protected

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^oauth/', include('oauth.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),

    (r'auth', oauth_res.OauthResource().get_urls()),
    (r'$^', Protected()),
)
