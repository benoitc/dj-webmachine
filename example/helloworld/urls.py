from django.conf.urls.defaults import *
from helloworld.hello.resource import Hello

import webmachine
urlpatterns = patterns('',
    (r'^wm/', include(webmachine.wm.urls)),
    (r'^$', Hello()),

)

