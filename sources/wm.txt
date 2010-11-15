.. _wm:

Minimal API building
++++++++++++++++++++

Combinating the power of Django and the :ref:`resources <resources>` it's relatively easy to buid an api. The process is also eased using the WM object. dj-webmachine offer a way to create automatically resources by using the ``route`` decorator.

Using this decorator, our helloworld example can be rewritten like that:

.. code-block:: python


    from webmachine.api import wm

    import json
    @wm.route(r"^$")
    def hello(req, resp):
        return "<html><p>hello world!</p></html>"


    @wm.route(r"^$", provided=[("application/json", json.dumps)])
    def hello_json(req, resp):
        return {"ok": True, "message": "hellow world"}

and the urls.py:

.. code-block:: python

    from django.conf.urls.defaults import *

    import webmachine

    webmachine.autodiscover()

    urlpatterns = patterns('',
        (r'^', include(webmachine.wm.urls))
    )

The autodiscover will detect all resources modules and add then to the
url dispatching. The route decorator works a little like the one in
bottle_ or for that matter flask_ (though bottle was the first). 

This decorator works differently though. It create full
:class:`webmachine.resource.Resource` instancse registered in the wm
object. So we are abble to provide all the features available in a
resource:

 - settings which content is accepted, provided
 - assiciate serializers to the content types
 - throttling
 - authorization 

The helloworld could be written in one function:


.. code-block:: python

    def resource_exists(req, resp):
        return True

    @wm.route(r"^hello$", 
            provided=["text/html", ("application/json", json.dumps)],
            resource_exists=resource_exists
            
            )
    def all_in_one(req, resp):
        if resp.content_type == "application/json":
            return {"ok": True, "message": "hellow world! All in one"}
        else:
            return "<html><p>hello world! All in one</p></html>"


You can see that we set in the decorator the provided contents, we call
a function ``resources_exists`` to check if this resource exists. Then
in the function we return the content dependiong on the response content
type depending on the HTTP requests. The response is then automatically
serialized using the ``json.dumps`` function associated to the json
content-type. Easy isn't it ? You can pass any :ref:`resource methods <resources>`
to the decorator.


.. _bottle: http://bottle.paws.de/
.. _flask: http://flask.pocoo.org
