# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import time

from django.core.cache import cache

class Limiter(object):

    def __init__(self, res, **options):
        self.res = res
        self.options = options

    def allowed(self, request):
        if self.whitelisted(request):
            return True
        elif self.blacklisted(request):
            return False
        return True

    def whitelisted(self, request):
        return False

    def blacklisted(self, request):
        return False

    def client_identifier(self, request):
        if request.user.is_authenticated:
            ident = request.user.username
        else:
            ident = request.META.get("REMOTE_ADDR", None)
        if not ident:
            return ''

        ident = "%s,%s" % (self.res.__class__.__name__, ident)
        return ident

    def cache_get(self, key, default=None):
        return cache.get(key, default)

    def cache_set(self, key, value, expires):
        return cache.set(key, value, expires)

    def cache_key(self, request):
        if not "key_prefix" in self.options:
            return self.client_identifier()
        key = "%s:%s" % (self.options.get("key_prefix"), 
                self.client_identifier())
        return key


class Interval(Limiter):
    """
    This rate limiter strategy throttles the application by enforcing a
    minimum interval (by default, 1 second) between subsequent allowed HTTP
    requests.

    ex::
        from webmachine import Resource
        from webmachine.throttle import Interval
        
        class MyResource(Resource):
            ...

            def forbidden(self, req, resp):
                return Interval(self).allowed(req)
    """

    def allowed(self, request):
        t1 = time.time()
        key = self.cache_key(request)
        t0 = self.cache_get(key)
        allowed = not t0 or (t1 - t0) >= self.min_interval()
        try:
            self.cache_set(key, t1) 
        except:
            return True
        return allowed

    def min_interval(self):
        return "min" in self.options and self.options.get("min") or 1

class TimeWindow(Limiter):
    """
    Return ```true``` if fewer than maximum number of requests
    permitted for the current window of time have been made.
    """

    def allowed(self, request):
        t1 = time.time()
        key = self.cache_key(request)
        count = int(self.cache_get(key) or 0)
        allowed = count <= self.max_per_window()
        try:
            self.cache_set(key, t1) 
        except:
            return True
        return allowed

    def max_per_window(self):
        raise NotImplementedError


class Daily(TimeWindow):
    """ 
    This rate limiter strategy throttles the application by defining a
    maximum number of allowed HTTP requests per day (by default, 86,400
    requests per 24 hours, which works out to an average of 1 request per
    second).

    Note that this strategy doesn't use a sliding time window, but rather
    tracks requests per calendar day. This means that the throttling counter
    is reset at midnight (according to the server's local timezone) every
    night.

    ex::
        from webmachine import Resource
        from webmachine.throttle import Daily
        
        class MyResource(Resource):
            ...

            def forbidden(self, req, resp):
                return Daily(self).allowed(req)    
    """

    def max_per_window(self):
        return "max" in self.options and self.options.get(max) or 86400

    def cache_key(self, request):
        return "%s:%s" % (super(Daily, self).cache_key(request),
                time.strftime('%Y-%m-%d'))

class Hourly(TimeWindow):
    """
    This rate limiter strategy throttles the application by defining a
    maximum number of allowed HTTP requests per hour (by default, 3,600
    requests per 60 minutes, which works out to an average of 1 request per
    second).

    Note that this strategy doesn't use a sliding time window, but rather
    tracks requests per distinct hour. This means that the throttling
    counter is reset every hour on the hour (according to the server's local
    timezone).

    ex::
        from webmachine import Resource
        from webmachine.throttle import Hourly
        
        class MyResource(Resource):
            ...

            def forbidden(self, req, resp):
                return Hourly(self).allowed(req)    
    """

    def max_per_window(self):
        return "max" in self.options and self.options.get(max) or 3600

    def cache_key(self, request):
        return "%s:%s" % (super(Daily, self).cache_key(request),
                time.strftime('%Y-%m-%dT%H'))

