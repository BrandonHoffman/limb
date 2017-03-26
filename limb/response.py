"""
Copyright 2017 Brandon Hoffman <brandon.michael.hoffman@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from webob import Response

class OK(Response):
    def __init__(self, *args, **kwargs):
        super(OK, self).__init__(*args, **kwargs)
        self.status = 200

class Created(Response):
    def __init__(self, *args, **kwargs):
        super(Created, self).__init__(*args, **kwargs)
        self.status = 201

class NoContent(Response):
    def __init__(self, *args, **kwargs):
        super(NoContent, self).__init__(*args, **kwargs)
        self.status = 204

class BadRequest(Response):
    def __init__(self, *args, **kwargs):
        super(BadRequest, self).__init__(*args, **kwargs)
        self.status = 400

class NotFound(Response):
    def __init__(self, *args, **kwargs):
        super(NotFound, self).__init__(*args, **kwargs)
        self.status = 404

class ValidationError(Response):
    def __init__(self, *args, **kwargs):
        super(ValidationError, self).__init__(*args, **kwargs)
        self.status = 422
