.. _recipe:

Recipes
-------

Some quick recipe to show the dj-webmachine usage.

Get path named arguments
++++++++++++++++++++++++

if you have some named arguments in your url pattern, you can get them
using the ``url_kwargs`` member of the req object::

    kwargs = req.url_kwargs

Simplest working resource
+++++++++++++++++++++++++

This simple resource only return HTML

.. code-block:: python

    class MyResource(Resource):
        
        def to_html(self, req, resp):
            return "<html><h1>Hello World!</h1></html>"

Return different content types on GET
+++++++++++++++++++++++++++++++++++++

Suppose you want to serve plaintexts and html clients on valid GET
requests:

.. code-block:: python

    class MyResource(Resource):
        
        def content_types_provided(self, req, resp):
            return [
                ("text/html", self.to_html),
                ("text/plain", self.to_text)
            ]

        def to_html(self, req, resp):
            return "<html><h1>Hello World!</h1></html>"

        def to_text(self, req, resp):
            return "Hello World!"

Handle POST using the resource
++++++++++++++++++++++++++++++

.. code-block:: python

    class MyResource(Resource):

        def allowed_methods(self, req, resp):
            return ['POST']
        
        def accepted_content_types(self, req, resp):
            return [('application/json', self.to_json)]

        def to_json(self, req, resp):
            body = json.loads(req.raw_post_data)
            resp.content = json.dumps(json.dumps(body))

        def post_is_create(self, req, resp):
            return True

Handle GET using the decorator
++++++++++++++++++++++++++++++

.. code-block:: python

    @wm.route(r"taroute$", 
              methods=['GET', 'HEAD'],
              provided=[('text/html', 'text/plain')])
    def fetched(req, resp):
        if resp.content_type == "text/html":
            return "<html><h1>Hello World!</h1></html>"
        return "Hello World!"
        
Handle POST using the decorator
+++++++++++++++++++++++++++++++

Same code for other methods. You can check the method using
``req.method``

.. code-block:: python

    # with teh decorator
    @wm.route(r"taroute$", 
              methods="POST",
              accepted=[('application/json', json.loads)],
              provided=[('application/json', json.dumps)])
    def posted(req, resp):
        # my body has been deserialized
        body = req.raw_post_data
        
        # my body will be serialized
        return body
