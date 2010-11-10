.. _resources: 

dj-webmachine Resource object methods
-------------------------------------

All dj-webmachine resources should inherit from the
:class:`webmachine.Resource` class:

.. code-block:: python

    from webmachine import Resource

    class MyResource(Resource):
        """ my app resource """


**Resource methods** are of the signature:

.. code-block:: python

    def f(self, req, resp):
        return result

``req`` is a :class:`django.http.HttpRequest` instance, and ``resp`` a
:class:`django.http.HttpResource` instance. This instances have been
:ref:`improved to support more HTTP semantics <http>`. At any time you
can manipulate this object to return the response you want or pass
values to other methods.

There are over 30 Resource methods you can define, but any of them can 
be omitted as they have reasonable defaults.

Resource methods description
++++++++++++++++++++++++++++

.. autoclass:: webmachine.Resource
   :members:
   :undoc-members:
   
