"""
Copyright 2017 Brandon Hoffman <brandon.michael.hoffman@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from limb.router import ClassRouter
from limb.response import *
from limb.property import Property, Function, ClassProperty
from webob import Response
from google.cloud import datastore
from enum import Enum
from six import add_metaclass
import limb.serialize as json

client = datastore.Client()

class ValidationRange(Enum):
    NONE = 0,
    ONLY_NEW = 1,
    ALL = 2

def compound(func):
    return Function(func)

class Schema(type):
    def __new__(cls, name, bases, dct):
        obj = super(Schema, cls).__new__(cls, name, bases, dct)
        obj._app = ClassRouter(obj)
        obj._app.add_method("POST", obj._post_handler)
        obj._app.add_method("GET", obj._get_handler)
        obj._app.instance_router.add_method("GET", obj._get_instance_handler)
        obj._app.instance_router.add_method("PUT", obj._put_instance_handler)
        obj._app.instance_router.add_method("PATCH", obj._patch_instance_handler)
        obj._app.instance_router.add_method("DELETE", obj._delete_instance_handler)
        _properties = []
        for attribute in dir(obj):
            attr = getattr(obj, attribute)
            if issubclass(attr.__class__, Property):
                attr_value = "_" + attribute
                attr.store_as = attr_value
                attr.name = attribute
                _properties.append(attribute)
            if issubclass(attr.__class__, Schema):
                obj.add_nested(attr)
                name = attr.get_entity_name()
                setattr(obj, name, ClassProperty(name, attr))
                _properties.append(name)
                attr._parent_model = obj
        obj._properties = _properties
        return obj

#@add_metaclass(Schema)
class Model(object, metaclass=Schema):
    _entity_name = None
    _properties = []
    _parent_model = None

    @property
    def _entity(self):
        #if hasattr(self, "_entity_cached"):
        try:
            return self._entity_cached
        except:
        #else:
            return self._get()

    @classmethod
    def add_nested(cls, model):
        model._parent_model = cls
        cls._app.instance_router.add_model(model)

    def __init__(self, ident=None, parent=None, entity=None, create=False):
        parent_key = None
        self.create=False
        if parent:
            parent_key = parent.key
        name = self.get_entity_name()
        if ident:
            self.key = client.key(name, ident, parent=parent_key)
        else:
            self.key = client.key(name, parent=parent_key)
        if entity:
            self._entity_cached = entity
        elif create:
            self._entity_cached = datastore.Entity(self.key)

    def for_json(self):
        json_obj = {}
        for attribute in self._properties:
            value = getattr(self, attribute)
            json_obj[attribute] = value
        return json_obj

    @classmethod
    def parent(cls):
        return cls._parent_model

    @compound
    def id(self):
        return self.key.id

    def _get_idents(self, request):
        idents = []
        for param in request.url_parameters.values():
            idents += param.params
        return idents

    @compound
    def url(self):
        parts = [str(path) for path in self.key.flat_path]
        return "/".join(parts)

    @classmethod
    def add_action(cls, uri, router):
        cls._app.add_router(uri, router)

    @classmethod
    def add_instance_action(cls, uri, router):
        cls._app.instance_router.add_router(uri, router)

    @classmethod
    def _post_handler(cls, request):
        parent = None
        if(cls._parent_model):
            parent = request.objects.get(cls._parent_model.get_entity_name())
        obj = cls(parent=parent, create=True)
        errors = []
        for (prop_name) in cls._properties:
            prop = getattr(cls, prop_name)
            val = request.json_body.get(prop_name, prop.default)
            var_errors =prop.validate(val)
            if var_errors:
                errors += var_errors
            else:
                setattr(obj, prop_name, val)
        if errors:
            return ValidationError(json.dumps(errors))
        else:
            obj.save()
            return Created(json.dumps(obj))

    @classmethod
    def _get_handler(cls, request):
        parent = None
        if(cls._parent_model):
            parent = request.objects.get(cls._parent_model.get_entity_name())
        results = cls.list(parent=parent)
        if results:
            return OK(json.dumps(list(results)))
        else:
            return NotFound()

    @classmethod
    def _get_instance_handler(cls, request):
        obj = request.objects[cls.get_entity_name()]
        if obj._entity != None:
            return OK(json.dumps(obj))
        else:
            return NotFound()

    @classmethod
    def _put_instance_handler(cls, request):
        obj = request.objects[cls.get_entity_name()]
        if(obj._entity != None):
            errors = []
            for prop_name in cls._properties:
                prop = getattr(cls, prop_name)
                val = request.json_body.get(prop_name, prop.default)
                var_errors =prop.validate(val)
                if var_errors:
                    errors += var_errors
                else:
                    setattr(obj, prop_name, val)
            if errors:
                return ValidationError(json.dumps(errors))
            else:
                obj.save()
                return OK(json.dumps(obj))
        else:
            return NotFound()

    @classmethod
    def _patch_instance_handler(cls, request):
        obj = request.objects[cls.get_entity_name()]
        if(obj._entity != None):
            errors = []
            for (key, val) in request.json.items():
                prop = getattr(cls, key, None)
                if prop == None:
                    continue # extra field skip
                var_errors = prop.validate(val)
                if var_errors:
                    errors += var_errors
                else:
                    setattr(obj, key, val)
            if errors:
                return ValidationError(json.dumps(errors))
            else:
                obj.save()
                return OK(json.dumps(obj))
        else:
            return NotFound()

    @classmethod
    def _delete_instance_handler(cls, request):
        obj = request.objects[cls.get_entity_name()]
        if obj._entity != None:
            obj.delete()
            return NoContent("DONE")
        else:
            response = NotFound()
        return response

    @classmethod
    def get_entity_name(cls):
        return (cls._entity_name or cls.__name__).lower()


    def _get(self):
        self._entity_cached = client.get(self.key)
        return self._entity_cached


    def save(self):
        client.put(self._entity)
        self.key = self._entity.key

    @classmethod
    def list(cls, parent=None):
        name = cls.get_entity_name()
        ancestor = None
        if parent:
            ancestor = parent.key
            if parent._entity == None:
                return None
        query = client.query(kind=name, ancestor=ancestor)
        return cls._iterator(query, parent=parent)

    @classmethod
    def _iterator(cls, query, parent=None):
        for entity in query.fetch():
            yield cls(ident=entity.key.id, parent=parent, entity=entity)

    def delete(self):
        client.delete(self.key)
        #TODO: cascade to properties will need to be in a transaction

