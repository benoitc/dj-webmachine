.. dj-webmachine documentation master file, created by
   sphinx-quickstart on Wed Nov 10 16:19:42 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to dj-webmachine's documentation!
=========================================

webmachine provides a REST toolkit based on Django. It's heavily
inspired on `webmachine <http://webmachine.basho.com/>`_ from Basho.


dj-webmachine is an application layer that adds HTTP semantic awareness on 
top of Django and provides a simple and clean way to connect that to
your applications' behavior. dj-webmachine also offers you the
possibility to build simple API based on your model and the tools to
create automatically docs and clients from it (work in progress).

Contents:

.. toctree::
   :maxdepth: 1

   introduction
   docs


Resource oriented
-----------------

A dj-webmachine application is a set of :ref:`Resources objects<resources>`, each of which
is a set of methods over the state of the resource.

.. code-block:: python
    
    from webmachine import Resource
    
    class Hello(Resource):

        def to_html(self, req, resp):
            return "<html><body>Hello world!</body></html>\n"

These methodes give you a place to define the representations and other 
Web-relevant properties of your application's resources. 

For most of dj-webmachine applications, most of the Resources instance 
are small and isolated. The web behavior introduced :ref:`by directly mapping the HTTP <diagram>` 
make your application easy to debug and read.

Simple Routing
--------------

Combinating the power of Django and the resources it’s relatively easy to buid an api. The process is also eased using the WM object. dj-webmachine offer a way to create automatically resources by using :ref:`the route decorator<wm>`.

.. code-block:: python

    from webmachine.ap import wm

    import json
    @wm.route(r"^$")
    def hello(req, resp):
        return "<html><p>hello world!</p></html>"



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

