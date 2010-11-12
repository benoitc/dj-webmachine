from django.conf.urls.defaults import *

import webmachine

webmachine.autodiscover()
print len(webmachine.wm.routes)

urlpatterns = patterns('',
    (r'^', include(webmachine.wm.urls))
)
