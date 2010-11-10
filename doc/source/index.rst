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

A dj-webmachine application is a set of Resources objects, each of which
is a set of methods over the state of the resource.

These methodes give you a place to define the representations and other 
Web-relevant properties of your application's resources. 

For most of dj-webmachine applications, most of the Resources instance 
are small and isolated. The web behavior introduced :ref:`by directly mapping the HTTP <diagram>` 
make your application easy to debug and read.



Contents:

.. toctree::
   :maxdepth: 1

   introduction
   docs

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

