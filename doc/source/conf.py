# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

import sys, os
import webmachine

sys.path.insert(0, os.path.abspath('.'))
os.environ['DJANGO_SETTINGS_MODULE'] = ""

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest',
'sphinx.ext.viewcode', 'sphinxtogithub']


templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'dj-webmachine'
copyright = u'2010, Benoît Chesnea <benoitc@e-engura.org>u'

version = webmachine.__version__
release = version

exclude_trees = ['_build']

pygments_style = 'sphinx'
html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'dj-webmachinedoc'

latex_documents = [
  ('index', 'dj-webmachine.tex', u'dj-webmachine Documentation',
   u'Benoît Chesneau', 'manual'),
]

man_pages = [
    ('index', 'dj-webmachine', u'dj-webmachine Documentation',
     [u'Benoît Chesneau'], 1)
]

epub_title = u'dj-webmachine'
epub_author = u'Benoît Chesneau'
epub_publisher = u'Benoît Chesneau'
epub_copyright = u'2010, Benoît Chesneau'


