.. _throttling:

Throttling
++++++++++

Sometimes you may not want people to call a certain action many times in a 
short period of time. dj-webmachine allows you to throttle requests
using different methods.

Interval
--------

This rate limiter strategy throttles the application by enforcing a 
minimal interval (by default, 1 second) betweeb subsequent allowed 
HTTP requests.

In the resource object:

.. code-block:: python

    from webmachine import Resource
    from webmachine.throttle import Interval
    
    class MyResource(Resource):
        ...

        def forbidden(self, req, resp):
            return Interval(self).allowed(req)

You can throttle according to the request method too by simply checking
the request instance:

.. code-block:: python

    def forbidden(self, req, resp):
        if req.method == 'POST':
            return Interval(self).allowed(req)

You can also throttle using the :ref:`route decorator <wm>`:

.. code-block:: python

    def throttle_post(req, resp):
        if req.method == 'POST':
            return Interval(self).allowed(req)


    @wm.route("^$", forbbiden=throttle_post)
    def myres(req, resp):
        ...

TimeWindow
----------

This rate limiter strategy throttles the application by defining a
maximum number of allowed HTTP requests in a time window.


Daily
~~~~~

This rate limiter strategy throttles the application by defining a
maximum number of allowed HTTP requests per day (by default, 86,400
requests per 24 hours, which works out to an average of 1 request per
second).

.. note:: 

    This strategy doesn't use a sliding time window, but rather
    tracks requests per calendar day. This means that the throttling counter
    is reset at midnight (according to the server's local timezone) every
    night.


.. code-block:: python

    from webmachine import Resource
    from webmachine.throttle import Daily
    
    class MyResource(Resource):
        ...

        def forbidden(self, req, resp):
            return Daily(self).allowed(req) 

Hourly
~~~~~~


This rate limiter strategy throttles the application by defining a
maximum number of allowed HTTP requests per hour (by default, 3,600
requests per 60 minutes, which works out to an average of 1 request per
second).

.. note::

    Note that this strategy doesn't use a sliding time window, but rather
    tracks requests per distinct hour. This means that the throttling
    counter is reset every hour on the hour (according to the server's local
    timezone).

.. code-block:: python

    from webmachine import Resource
    from webmachine.throttle import Hourly
    
    class MyResource(Resource):
        ...

        def forbidden(self, req, resp):
            return Hourly(self).allowed(req)    



