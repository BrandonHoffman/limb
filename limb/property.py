"""
Copyright 2017 Brandon Hoffman <brandon.michael.hoffman@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from functools import partial
from limb.validation import ValidationError


def compound(func):
    return Function(func)

class Property(object):
    "Emulate PyProperty_Type() in Objects/descrobject.c"

    def __init__(self, cls=None, default=None, validators=[], doc=""):
        self.__doc__ = doc
        self.cls = cls
        self.default = default
        self.validators = validators
        self.store_as = None #this is set later by Schema metaclass
        self.name = None #this is set later by Schema metaclass

    def check_type(self, obj):
        if self.cls and self.cls != obj.__class__:
            return "Object type does not match expected"

    def _make_error(self, error):
        return {
            "code": error.code,
            "message": error.message,
            "field": self.name
        }

    def validate(self, obj):
        errors = []
        type_error = self.check_type(obj)
        if obj == None:
            error = ValidationError(100, "Required Field")
            return [self._make_error(error)]
        if type_error:
            msg = "expected {type1} but got {type2}".format(type1=str(self.cls.__name__), type2=str(obj.__class__.__name__))
            error = ValidationError(101, msg)
            return [self._make_error(error)]
        for validator in self.validators:
            error = validator(obj)
            if error:
                errors.append(self._make_error(error))
        if len(errors) > 0:
            return errors

    def get(self, obj):
        return obj._entity.get(self.store_as, self.default)

    def set(self, obj, value):
        obj._entity[self.store_as] = value

    def delete(self, obj):
        del obj._entity[self.store_as]

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.get(obj)

    def __set__(self, obj, value):
        self.set(obj, value)

    def __delete__(self, obj):
        self.delete(obj)

class Integer(Property):
    def __init__(self, *args, **kwargs):
        super(Integer, self).__init__(*args, **kwargs)
        self.cls = int

class Double(Property):
    def __init__(self, *args, **kwargs):
        super(Double, self).__init__(*args, **kwargs)
        self.cls = float

class Boolean(Property):
    def __init__(self, *args, **kwargs):
        super(Boolean, self).__init__(*args, **kwargs)
        self.cls = bool

class String(Property):
    def __init__(self, *args, **kwargs):
        super(String, self).__init__(*args, **kwargs)
        self.cls = str

class ClassProperty(Property):
    def __init__(self, name, cls, doc=""):
        super(ClassProperty, self).__init__(doc=doc)
        self.cls = cls
        self.name = name

    def get(self, obj):
        #TODO check to ensure obj is saved
        part = partial(self.cls, parent=obj)
        part.for_json = partial(self.for_json, parent=obj)
        return part

    def validate(self, obj):
        pass

    def for_json(self, parent=None):
        return {"url": ""}

    def set(self, obj, value):
        pass

    def delete(self, obj):
        pass

class Function(Property):
    def __init__(self, func, doc=""):
        super(Function, self).__init__(doc=doc)
        self.func = func

    def validate(self, obj):
        pass

    def get(self, obj):
        return self.func(obj)

    def set(self, obj, value):
        pass

    def delete(self, obj):
        pass

