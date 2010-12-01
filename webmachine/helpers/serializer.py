# -*- coding: utf-8 -
#
# This file is part of dj-webmachine released under the MIT license. 
# See the NOTICE for more information.

from calendar import timegm
import decimal
import datetime
import re
import time

from django.core import serializers
from django.db import models
from django.db.models import Model
from django.db.models.query import QuerySet
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import smart_unicode
try:
    from webob.util import status_reasons
except ImportError:
    from webob.statusreasons import status_reasons

try:
    from lxml import etree
except ImportError:
    try:
        from xml.etree.ElementTree import Element
    except ImportError:
        try:
            from elementtree.ElementTree import Element
        except ImportError:
            raise ImportError("You need lxml or elementtree installed.")

re_date = re.compile('^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])$')
re_time = re.compile('^([01]\d|2[0-3])\D?([0-5]\d)\D?([0-5]\d)?\D?(\d{3})?$')
re_datetime = re.compile('^(\d{4})\D?(0[1-9]|1[0-2])\D?([12]\d|0[1-9]|3[01])(\D?([01]\d|2[0-3])\D?([0-5]\d)\D?([0-5]\d)?\D?(\d{3})?([zZ]|([\+-])([01]\d|2[0-3])\D?([0-5]\d)?)?)?$')
re_decimal = re.compile('^(\d+)\.(\d+)$')


__all__ = ['Serializer', 'XMLSerializer', 'JSONSerializer',
'value_to_emittable', 'value_to_python']

try:
    import json
except ImportError:
    import django.utils.simplejson as json

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


class Serializer(object):

    def __init__(self, includes

    def _to_string(self, value):
        return value

    def _to_python(self, value):
        return value

    def serialize(self, value):
        value = value_to_emittable(value)
        return self._to_string(value)

    def unserialize(self, value):
        if isinstance(value, basestring):
            value = StringIO.StringIO(value)

        # make sure we have loaded the models
        models.get_apps()
        return value_to_python(self._to_python(value))


class XMLSerializer(Serializer):

    def __init__(self, root="response", version="1.0"):
        self.root = root
        self.version = version

    def add_element(self, xml, name, value, **attrs):
        if isinstance(value, dict) and "meta" in value:
            meta = value.pop('meta')
            xml.startElement(name, {
                "model": meta.get('model'),
                "pk": smart_unicode(meta.get('pk') or '')
            })
        else:
            xml.startElement(name, attrs)
        self.parse_xml(xml, value)
        xml.endElement(name)

    def parse_list(self, xml, data):
        for item in data:
            if isinstance(item, dict) and 'meta' in item:
                meta = item.pop('meta')
                name = meta['model'].rsplit(".", 1)[1]
                xml.startElement(name, {
                    "model": meta.get('model'),
                    "pk": smart_unicode(meta.get('pk') or '')
                })
            else:
                name = "entity"
                xml.startElement(name, {})
            self.parse_xml(xml, item)
            xml.endElement(name)

    def parse_xml(self, xml, data):
        if isinstance(data, (list, tuple,)):
            self.parse_list(xml, data)
        elif isinstance(data, dict):
            for k, v in data.iteritems():
                self.add_element(xml, k, v)
        else:
            xml.characters(smart_unicode(data))

    def _to_string(self, value):
        stream = StringIO.StringIO()
        xml = SimplerXMLGenerator(stream, "utf-8")
        xml.startDocument()
        xml.startElement(self.root, {"version": self.version})
        self.parse_xml(xml, value)
        xml.endElement(self.root)
        xml.endDocument()
        return stream.getvalue()

    def _to_python(self, value):
        ctx = etree.iterparse(value, events=("start", "end"))
        obj = {}
        for action, elem in ctx:
            obj[elem.tag]  = ctx

            print("%s: %s" % (action, elem.tag))
        return value

class JSONSerializer(Serializer):

    def _to_string(self, value):
        stream = StringIO.StringIO()
        json.dump(value, stream)
        return stream.getvalue()

    def _to_python(self, value):
        return json.load(value)



def dict_to_emittable(value, fields=None, exclude=None):
    """ convert a dict to json """
    return dict([(k, value_to_emittable(v)) for k, v in value.iteritems()])

def list_to_emittable(value, fields=None, exclude=None):
    """ convert a list to json """
    return [value_to_emittable(item) for item in value]

def relm_to_emittable(value):
    return value_to_emittable(value.all())


def fk_to_emittable(value, field):
    return value_to_emittable(getattr(value, field.name))


def m2m_to_emittable(value, field):
    return [model_to_emittable(m) for m in getattr(value, field.name).iterator() ]

def qs_to_emittable(value, fields=None, exclude=None):
    return [value_to_emittable(v, fields=fields, exclude=exclude) for v in value]

def model_to_emittable(instance, fields=None, exclude=None):
    meta = instance._meta
    if not fields and not exclude:
        ret = {}
        for f in meta.fields:
            ret[f.attname] = value_to_emittable(getattr(instance,
                f.attname))

        fields = dir(instance.__class__) + ret.keys()
        extra = [k for k in dir(instance) if k not in fields]

        for k in extra:
            ret[k] = value_to_emittable(getattr(instance, k))
    else:
        fields_list = []
        fields_iter = iter(meta.local_fields + meta.virtual_fields + meta.many_to_many)
        for f in fields_iter:
            value = None
            if fields and not f.name in fields:
                continue
            if exclude and f.name in exclude:
                continue
            
            
            if f in meta.many_to_many:
                if f.serialize:
                    value = m2m_to_emittable(instance, f)
            else:
                if f.serialize:
                    if not f.rel:
                        value = value_to_emittable(getattr(instance,
                            f.attname))
                    else:
                        value = fk_to_emittable(instance, f)

            if value is None:
                continue

            fields_list.append((f.name, value))

        ret = dict(fields_list)
    if ret:
        ret.update({ 
            "meta": {
                "model": smart_unicode(instance._meta),
                "pk":smart_unicode(instance._get_pk_val(), strings_only=True)
            }
        })
    return ret

def value_to_emittable(value, fields=None, exclude=None):
    """ convert a value to json using appropriate regexp.
For Dates we use ISO 8601. Decimal are converted to string.
"""
    if isinstance(value, QuerySet):
        value = qs_to_emittable(value, fields=fields, exclude=exclude)
    elif isinstance(value, datetime.datetime):
        value = value.replace(microsecond=0).isoformat() + 'Z'
    elif isinstance(value, datetime.date):
        value = value.isoformat()
    elif isinstance(value, datetime.time):
        value = value.replace(microsecond=0).isoformat()
    elif isinstance(value, decimal.Decimal):
        value = str(value)
    elif isinstance(value, list):
        value = list_to_emittable(value, fields=fields, exclude=exclude)
    elif isinstance(value, dict):
        value = dict_to_emittable(value, fields=fields,
                exclude=exclude)
    elif isinstance(value, Model):
        value = model_to_emittable(value, fields=fields,
                exclude=exclude)

    elif repr(value).startswith("<django.db.models.fields.related.RelatedManager"):
        # related managers
        value = relm_to_emittable(value)
    else:
        value = smart_unicode(value, strings_only=True)

    return value

def datetime_to_python(value):
    if isinstance(value, basestring):
        try:
            value = value.split('.', 1)[0] # strip out microseconds
            value = value.rstrip('Z') # remove timezone separator
            value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
        except ValueError, e:
            raise ValueError('Invalid ISO date/time %r' % value)
        return value

def date_to_python(value):
    if isinstance(value, basestring):
        try:
            value = datetime.date(*time.strptime(value, '%Y-%m-%d')[:3])
        except ValueError, e:
            raise ValueError('Invalid ISO date %r' % value)
    return value

def time_to_python(value):
    if isinstance(value, basestring):
        try:
            value = value.split('.', 1)[0] # strip out microseconds
            value = datetime.time(*time.strptime(value, '%H:%M:%S')[3:6])
        except ValueError, e:
            raise ValueError('Invalid ISO time %r' % value)
    return value



def value_to_python(value, convert_decimal=True, convert_number=True):
    """ convert a json value to python type using regexp. values converted
    have been put in json via `value_to_emittable` .
    """

    if isinstance(value, basestring):
        if re_date.match(value):
            value = date_to_python(value)
        elif re_time.match(value):
            value = time_to_python(value)
        elif re_datetime.match(value):
            value = datetime_to_python(value)
        elif re_decimal.match(value) and convert_decimal:
            value = decimal.Decimal(value)
        elif value.isdigit() and convert_number:
            value = int(value)
        elif value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False

    elif isinstance(value, list):
        value = list_to_python(value, convert_decimal=convert_decimal,
                convert_number=convert_number)
    elif isinstance(value, dict):
        value = dict_to_python(value, convert_decimal=convert_decimal,
                convert_number=convert_number)
    return value

def list_to_python(value, convert_decimal=True,
        convert_number=True):
    """ convert a list of json values to python list """
    return [value_to_python(item, convert_decimal=convert_decimal, \
        convert_number=convert_number) for item in value]

def dict_to_python(value, convert_decimal=True,
        convert_number=True):
    """ convert a json object values to python dict """
    ret = dict([(k, value_to_python(v,  convert_decimal=convert_decimal, \
        convert_number=convert_number)) for k, v in value.iteritems()])

    # this is a model, try to recreate it
    if "meta" in ret:
        meta = ret.pop('meta')
        models.get_apps()
        try:
            Model = models.get_model(*meta["model"].split("."))
        except TypeError:
            Model = None
        if Model is not None:
            instance = Model()
            if "pk" in meta:
                setattr(instance, Model._meta.pk.attname,
                    Model._meta.pk.to_python(meta["pk"]))
                for (fname, fvalue) in ret.items():    
                    setattr(instance, fname, fvalue)
            return instance
    return ret



