"""
Copyright 2017 Brandon Hoffman <brandon.michael.hoffman@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from webob import Request, Response
from webob.exc import HTTPNotFound
from limb.response import NotFound

# todo: look into unqlite-python and vedis for mocking a memcache/ndb option for testing
def not_found(request):
    return NotFound("404 Not found")

class Router(object):
    def __init__(self, base_url=""):
        self.methods = {}
        self.routers = {}
        self.parent = None
        self.base_url = base_url

    def add_method(self, method, function):
        # TODO: possibly check for method already existing
        self.methods[method] = function

    def add_router(self, route, router):
        if route in self.routers:
            raise Exception("duplicate definition for route")
        #TODO: make sure router does not already exist as another child
        router.parent = self
        self.routers[route] = router

    def add_model(self, model):
        self.add_router(model.get_entity_name(), model._app)

    def get_default(self, method, uri, request):
        return not_found

    def get(self, method, uri, request):
        if len(uri) == 0:
            return self.methods.get(method, not_found)
        else:
            next_uri = uri[0]
            next_router = self.routers.get(next_uri, None)
            if next_router:
                return next_router.get(method, uri[1:], request)
            else:
                return self.get_default(method, uri, request)

    def url(self, ids=[], parts=None):
        if parts == None:
            parts = []
        parts.append(self.base_url)
        parts.reverse()
        return '/'.join(parts)
        
    def __call__(self, environ, start_response):
        request = Request(environ)
        request.objects = {}
        path = request.path[1:] # strip the leading /
        if path == "":
            uri = []
        else:
            uri = path.split("/")
        respCls = self.get(request.method, uri, request)
        response = respCls(request)
        return response(environ, start_response)

class InstanceRouter(Router):
    def __init__(self, model):
        super(InstanceRouter, self).__init__()
        self.model = model
        self.name = model.get_entity_name()
        self.type = int

    def url(self, ids, parts=None):
        if parts == None:
            parts = []
        parts.append(ids[0])
        return self.parent.url(ids[1:], parts) 

    def get(self, method, uri, request):
        id = self.type(uri[0])
        parent = None
        if self.model._parent_model:
            parent_name = self.model._parent_model.get_entity_name()
            parent = request.objects[parent_name]
        obj = self.model(ident=id, parent=parent)
        request.objects[self.name] = obj
        obj._get()
        if obj._entity_cached == None:
            return not_found

        return super(InstanceRouter, self).get(method, uri[1:], request)

class ClassRouter(Router):
    def __init__(self, model):
        super(ClassRouter, self).__init__()
        self.instance_router = InstanceRouter(model)
        self.instance_router.parent = self
        self.name = model.get_entity_name()

    def url(self, ids=[], parts=None):
        if parts == None:
            parts = []
        parts.append(self.name)
        if self.parent:
            return self.parent.url(ids, parts) 
        else:
            return super(ClassRouter, self).url(ids, parts)

    def get_default(self, method, uri, request):
        return self.instance_router.get(method, uri, request)

