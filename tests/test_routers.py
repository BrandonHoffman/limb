from limb import router
from limb import model
from limb import property
from webob import Request, Response

def start_resp(*args, **kwargs):
    pass

class ModelTest(model.Model):
    class ModelTest2(model.Model):
        pass

class TestRouter(object):
    def test_router(self):
        router_test = router.Router()
        router_test_2 = router.Router()

        def handler(request):
            resp = Response("hello world")
            return resp

        def handler2(request):
            resp = Response("goodbye")
            return resp

        router_test.add_method("POST", handler)
        router_test.add_method("GET", handler2)
        router_test_2.add_method("GET", handler)
        assert (router_test.methods["POST"] == handler)
        assert (router_test_2.methods["GET"] == handler)
        assert ("PATCH" not in router_test.methods)
        router_test.add_router("test", router_test_2)
        assert (router_test.routers["test"] == router_test_2)
        try:
            router_test.add_router("test", router_test_2)
            assert (False)
        except:
            pass

        router_test.add_model(ModelTest)
        assert ("modeltest" in router_test.routers)
        assert (router_test.routers["modeltest"] == ModelTest._app)

        assert (ModelTest._app.instance_router != None)
        assert ("modeltest2" in ModelTest._app.instance_router.routers)

        req = Request.blank("/test")
        resp = router_test(req.environ, start_resp)
        assert (router_test.get("GET", ['test'], req) == handler)
        assert (resp[0] == b"hello world")

        req = Request.blank("")
        resp = router_test(req.environ, start_resp)
        assert (router_test.get("GET", [], req) == handler2)
        assert (resp[0] == b"goodbye")

        req = Request.blank("/not")
        resp = router_test(req.environ, start_resp)
        assert (router_test.get("GET", ['not'], req) == router.not_found)
        assert (resp[0] == b"404 Not found")

        req = Request.blank("/modeltest")
        req.objects = {}
        resp = router_test(req.environ, start_resp)
        assert (resp[0] == b"[]")
        assert (router_test.get("GET", ["modeltest"], req) == ModelTest._get_handler)
        assert (router_test.get("POST", ["modeltest"], req) == ModelTest._post_handler)
        assert (router_test.get("GET", ["modeltest", "1"], req) == router.not_found)
        test_obj = ModelTest(create=True)
        test_obj.save()
        ident = str(test_obj.id)
        assert (router_test.get("GET", ["modeltest", ident], req) == ModelTest._get_instance_handler)
        assert (router_test.get("PUT", ["modeltest", ident], req) == ModelTest._put_instance_handler)
        assert (router_test.get("PATCH", ["modeltest", ident], req) == ModelTest._patch_instance_handler)
        assert (router_test.get("DELETE", ["modeltest", ident], req) == ModelTest._delete_instance_handler)
    
        test_obj_2 = test_obj.modeltest2(create=True)
        test_obj_2.save()
        obj_2_ident = str(test_obj_2.id) 
        assert (router_test.get("GET", ["modeltest", ident, "modeltest2"], req) == ModelTest.ModelTest2._get_handler)
        assert (router_test.get("GET", ["modeltest", ident, "modeltest2", obj_2_ident], req) == ModelTest.ModelTest2._get_instance_handler)
        # TODO: test add_model method
        # TODO: test __call__

    def test_class_router(self):
        #TODO test __call__ for ClassRouter
        #TODO test __call__ for InstanceRouter
        pass
