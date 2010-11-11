from django.conf.urls.defaults import *
from helloworld.hello.resource import Hello

urlpatterns = patterns('',
    (r'^$', Hello()),
)

