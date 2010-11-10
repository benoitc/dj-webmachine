.. _resources: 

dj-webmachine Resource object methods
-------------------------------------

all dj-webmachine resources should inherit from the Resource object:

.. code-block:: python

    from webmachine import Resource

    class MyResource(Resource):
        """ my app resource """


All Resource methods are of the signature::

    def f(self, req, resp):
        pass

req is a :class:django.http.HttpRequest instance, and resp a
:class:django.http.HttpResource instance. This instances have been
:ref:`improved to support more HTTP semantics <http>`. At any time you
can manipulate this object to return the response you want or pass
values to other methods.

Tere are over 30 Resource methods you can define, but any of them can 
be omitted as they have reasonable defaults.

Each methods are described below:

.. autoclass:: webmachine.Resource
   :members:
   :inherited-members:
   
