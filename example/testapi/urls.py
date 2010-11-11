from django.conf.urls.defaults import *
from testapi.hello.resource import Hello

urlpatterns = patterns('',
    (r'^$', Hello()),
)

