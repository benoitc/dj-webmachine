.. _auth:

Handle authorization
--------------------

webmachine offer mechanism to authenticate via basic authentication or
oauth. All authentication module should inherit from
:class:`webmachine.auth.base.Auth`.

.. code-block:: python

    class Auth(object):

    def authorized(self, request):
        return True

Basic Authentification
++++++++++++++++++++++

To handle basic authentication just do this in your ``Resource``
class:

.. code-block:: python

    from webmachine import Resource
    from webmachine.auth import BasicAuth

    class MyResource(Resource):

        ...

        def is_authorized(self, req, resp):
            return BasicAuth().authorized(req, resp)

OAUTH
+++++

.. warning::

    You need to install restkit_ >= 3.0.2 to have oauth in your application.

.. _restkit: http://benoitc.github.com/restkit

It's easy to handle oauth in your dj-webmachine application. First you
need to add the oauth resource to your ``urls.py`` file:

.. code-block:: python

    from webmachine.auth import oauth_res

    urlpatterns = patterns('',

        ...

        (r'^auth/', include(oauth_res.OauthResource().get_urls())),
    )

Then like with the basic authentication add the class
:class:`webmachine.auth.oauth.Oauth` in your resource:

.. code-block:: python

    from webmachine import Resource
    from webmachine.authoauth import Oauth

    class MyResource(Resource):

        ...

        def is_authorized(self, req, resp):
            return Oauth().authorized(req, resp)

Test it
~~~~~~~

Create a consumer

.. code-block:: python

    >>> from webmachine.models import Consumer
    >>> consumer = Consumer.objects.create_consumer()


Request a token for this consumer. We use the restkit_ client to do that.


.. code-block:: python

    >>> from restkit import request
    >>> from restkit.filters import OAuthFilter
    >>> from restkit.oauth2 import Token
    >>> resp = request("http://127.0.0.1:8000/auth/request_token", 
    filters=[OAuthFilter("*", consumer)])
    >>> resp.status_int
    200

You need now to read the response body, and create a token request on
the client side:

.. code-block:: python

    >>> import urlparse
    >>> qs = urlparse.parse_qs(resp.body_string())
    >>> request_token = Token(qs['oauth_token'][0], qs['oauth_token_secret'][0])

Now we need to authorize our client:

.. code-block:: python

    >>> resp = request("http://127.0.0.1:8000/auth/authorize", 
    filters=[OAuthFilter("*", consumer, request_token)])

We now need to read the body for the second step, since we send a form
here to the client. We are again using restkit to send the result of the
form and get the tokens back.

.. code-block:: python

    >>> form = {'authorize_access': 1, 'oauth_token': '2e8bfdaddb664d97ada4b8cec6827bcf', 
    'csrf_signature': 'iGHjuOEppMeg+gHWyYV/etLRxTQ='}
    >>> resp = request("http://127.0.0.1:8000/auth/authorize", method="POST", 
    body=form, filters=[OAuthFilter("*", consumer, request_token)])

We are now authorized, and we need to ask an access token:

.. code-block:: python

    >>> resp = request("http://127.0.0.1:8000/auth/access_token", 
    filters=[OAuthFilter("*", consumer, request_token)])
    >>> qs = urlparse.parse_qs(resp.body_string())
    >>> access_token = Token(qs['oauth_token'][0], qs['oauth_token_secret'][0])

If you use tthe testoauth application in ``examples`` folder, you can
then test if you are authorized. Without the acces token:

.. code-block:: python

    >>> resp = request("http://127.0.0.1:8000/")
    >>> resp.status_int
    401
    >>> resp.headers
    {'date': 'Thu, 11 Nov 2010 23:16:25 GMT', 'content-type': 'text/html', 
    'www-authenticate': 'OAuth realm="OAuth"', 'server': 'WSGIServer/0.1 Python/2.7'}
    
You can see the **WWW-Authenticate** header.

Using the access token:

.. code-block:: python

    >>> resp = request("http://127.0.0.1:8000/", 
    filters=[OAuthFilter("*", consumer, access_token)])
    >>> resp.status_int
    200
    >>> resp.body_string()
    "<html><p>I'm protected you know.</p></html>"


AUTH classes description
++++++++++++++++++++++++

Basic authentication
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: webmachine.auth.BasicAuth
   :members:
   :undoc-members:

Oauth authentication
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: webmachine.auth.oauth.Oauth
   :members:
   :undoc-members:

Datastore
~~~~~~~~~

Find here the description of the abstract class you need to use if you
want to create your own class. This class mmanage creation and request
of tokens, nonces and consumer. See the
:class:`webmachine.auth.oauth_datastore.DataStore` for a complete
example. To use you own class add it to your settings:

.. code-block:: python

    OAUTH_DATASTORE = 'webmachine.auth.oauth_store.DataStore'

.. autoclass:: webmachine.auth.oauth_store.OAuthDataStore
   :members:
   :undoc-members:

.. autoclass:: webmachine.auth.oauth_store.DataStore
   :members:
   :undoc-members:
