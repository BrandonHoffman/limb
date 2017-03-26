from framework import framework
from framework import model
from webob import Request, Response

def start_resp(*args, **kwargs):
    pass

class ModelTest(model.Model):
    pass

class TestRouter(object):
    def test_router(self):
        router = framework.Router()
        router2 = framework.Router()
        def handler(request):
            resp = Response("hello world")
            return resp
        router.add_method("POST", handler)
        router2.add_method("GET", handler)
        assert (router.methods["POST"] == handler)
        assert (router2.methods["GET"] == handler)
        assert ("GET" not in router.methods)
        router.add_router("test", router2)
        assert (router.routers["test"] == router2)
        try:
            router.add_router("test", router2)
            assert (False)
        except:
            pass

        router.add_model(ModelTest)
        assert ("modeltest" in router.routers)
        assert (router.routers["modeltest"] == ModelTest._app)

        req = Request.blank("/test")
        resp = router(req.environ, start_resp)
        assert (router.get("GET", ['test'], req) == handler)
        assert (resp[0] == b"hello world")

        req = Request.blank("/not")
        resp = router(req.environ, start_resp)
        assert (router.get("GET", ['not'], req) == framework.not_found)
        assert (resp[0] == b"404 Not found")

        req = Request.blank("/modeltest")
        req.objects = {}
        resp = router(req.environ, start_resp)
        #assert (resp[0] == b"[]")
        assert (router.get("GET", ["modeltest", "1"], req) == ModelTest._get_instance_handler)
        assert (router.get("GET", ["modeltest"], req) == ModelTest._get_handler)
        # TODO: test add_model method
        # TODO: test __call__

    def test_class_router(self):
        #TODO test __call__ for ClassRouter
        #TODO test __call__ for InstanceRouter
        pass
