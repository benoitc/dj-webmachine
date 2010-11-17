.. _wm:

Simple Routing
+++++++++++++++++++++++++++++++++++++

Combinating the power of Django and the :ref:`resources <resources>` it's relatively easy to buid an api. The process is also eased using the WM object. dj-webmachine offer a way to create automatically resources by using the ``route`` decorator.

Using this decorator, our helloworld example can be rewritten like that:

.. code-block:: python


    from webmachine.ap import wm

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

This decorator works differently though. It creates full
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

Mapping a resource
------------------

You can also map your :ref:`Resources classes<resources>` using the wm
object and the method :func:`webmachine.api.WM.add_resource`

If a pattern is given, the path will be
``/<wmpath>/<app_label>/pattern/resource urls``. if no pattern is given the resource_name will be used.

Ex for urls.py:

.. code-block:: python

    from django.conf.urls.defaults import *

    import webmachine
    webmachine.autodicover()

    urlpatterns = patterns('',
        (r'^wm/', include(webmachine.wm.urls)),

    )

and a resources.py file in one django app named hello

.. code-block:: python

    from webmachine import Resource
    from webmachine import wm

    class Hello(Resource):

        def to_html(self, req, resp):
            return "<html><body>Hello world!</body></html>\n"


    # available at wm/hello
    wm.add_resource(Hello, r"^hello")

    # available at wm/helloworld/hello
    wm.add_resource(Hello)

You can then access to /wm/hello and /wm/hello/hello pathes
automatically.

You can also override the resource path by using the Meta class:

.. code-block:: python

    class Hello(Resource):
        class Meta:
            resource_path = ""

If you set the resource path, the resource url added to the
**WM** instance i
``/<wmpath>/<app_label>/<resource_path>/resource_urls`` .

Custom WM instance
------------------

Sometimes you want to create custom WM instance instead to use the
global one provided. For that you can import the class
:class:`webmachine.api.WM`:

.. autoclass:: webmachine.api.WM
   :members:
   :undoc-members:

.. _bottle: http://bottle.paws.de/
.. _flask: http://flask.pocoo.org
