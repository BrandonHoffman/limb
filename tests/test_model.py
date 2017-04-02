from limb.router import Router
from limb.model import Model, compound
from limb.property import *
from limb.validation import Between
import limb.serialize as json 
from webob import Request
import simplejson

class Sample(Model):
    index = Integer(validators=[Between(1, 100)])
    money = Double()
    boolean = Boolean(default=True)
    name = String()

    class Sample2(Model):
        index = Integer()
        money = Double()
        boolean = Boolean()

class Sample3(Model):
    name = String()
    
class TestModel(object):
    def test_init(self):
        assert {} ==  Sample._app.routers 
        assert 2 == len(Sample._app.methods)
        assert "GET" in Sample._app.methods
        assert "POST" in Sample._app.methods
        assert 1 == len(Sample._app.instance_router.routers)
        assert "sample2" in Sample._app.instance_router.routers 
        assert Sample.Sample2._app == Sample._app.instance_router.routers["sample2"]
        assert 4 == len(Sample._app.instance_router.methods)
        assert "GET" in Sample._app.instance_router.methods
        assert "PUT" in Sample._app.instance_router.methods
        assert "PATCH" in Sample._app.instance_router.methods
        assert "DELETE" in Sample._app.instance_router.methods
        assert "index" in Sample._properties
        assert "money" in Sample._properties
        assert "boolean" in Sample._properties
        assert "name" in Sample._properties
        assert "sample2" in Sample._properties
        assert Sample.Sample2.parent() == Sample

    def test_entity(self):
        obj = Sample(create=True)
        obj.name = "test_name"
        obj.save()
        obj2 = Sample(ident=obj.id)
        assert obj2.name == "test_name"

        obj3 = Sample(entity=obj2._entity)
        assert obj2.name == "test_name"
        assert obj3.id == obj.id

        obj3_samp = Sample.Sample2(parent=obj3, create=True)
        assert obj3.key == obj3_samp.key.parent 
        obj3.delete()

        obj4 = Sample(ident=obj.id)
        assert obj4.name != "test_name"


    def test_for_json(self):
        obj = Sample(create=True)
        obj.name = "test_name"
        json_obj = obj.for_json()
        assert "index" in json_obj
        assert "money" in json_obj
        assert "boolean" in json_obj
        assert "name" in json_obj
        assert "sample2" in json_obj
        
    def test_list(self):
        obj = Sample(create=True)
        obj.save()
        obj_samp = Sample.Sample2(parent=obj, create=True)
        obj_samp.save()

        obj2 = Sample(create=True)
        obj2.save()
        obj2_samp = Sample.Sample2(parent=obj2, create=True)
        obj2_samp.save()

        obj3 = Sample()

        assert obj.id in [temp.id for temp in Sample.list()]
        res = [temp.id for temp in Sample.Sample2.list()]
        assert obj_samp.id in res
        assert obj2_samp.id in res
        res = [temp.id for temp in Sample.Sample2.list(parent=obj)]
        assert obj_samp.id in res
        assert obj2_samp.id not in res
        assert None == Sample.Sample2.list(parent=obj3)

    def test_delete(self):
        obj = Sample(create=True)
        obj.save()
        req = Request.blank("") 
        setattr(req, "objects", {"sample": obj})

        obj2 = Sample(ident=100000)
        req2 = Request.blank("") 
        setattr(req2, "objects", {"sample": obj2})
        assert obj.id in [temp.id for temp in Sample.list()]
        resp = Sample._delete_instance_handler(req)
        assert(resp.status_code == 204)
        resp2 = Sample._delete_instance_handler(req2)
        assert(resp2.status_code == 404)
        assert obj.id not in [temp.id for temp in Sample.list()]
        
    def test_get(self):
        obj = Sample(create=True)
        obj.save()
        req = Request.blank("") 
        setattr(req, "objects", {"sample": obj})
        resp = Sample.Sample2._get_handler(req)
        res = simplejson.loads(resp.body.decode("utf-8"))
        assert(resp.status_code == 200)
        assert len(res) == 0
        obj2 = Sample.Sample2(parent=obj, create=True)
        obj2.save()
        res = simplejson.loads(resp.body.decode("utf-8"))
        assert(resp.status_code == 200)
        assert len(res) == 0

    def test_post(self):
        req = Request.blank("", POST="{}")

        resp = Sample._post_handler(req)
        assert(resp.status_code == 422)
        errors = simplejson.loads(resp.body)
        assert len(errors) == 3

        req2 = Request.blank("", POST='{"index":1,"money":1.0,"name":"brandon"}')
        resp2 = Sample._post_handler(req2)
        assert(resp2.status_code == 201)

        res = simplejson.loads(resp2.body.decode("utf-8"))
        assert res['index'] == 1
        assert res['money'] == 1.0
        assert res['name'] == 'brandon'

        obj = Sample(create=True)
        obj.save()
        req3 = Request.blank("", POST='{"index":1,"money":1.0,"boolean":true}')
        setattr(req3, "objects", {"sample": obj})
        resp3 = Sample.Sample2._post_handler(req3)
        res = simplejson.loads(resp3.body.decode("utf-8"))
        print(res)
        assert res['index'] == 1
        assert res['money'] == 1.0
        assert res['boolean'] == True

    def test_get_instance(self):
        temp = Sample(create=True)
        temp.save()
        obj = Sample(ident=temp.id)
        req = Request.blank("")
        setattr(req, "objects", {"sample": obj})
        resp = Sample._get_instance_handler(req)
        assert (resp.status_code == 200)
        res = resp.body.decode("utf-8")
        assert res == json.dumps(obj)

        req2 = Request.blank("")
        obj2 = Sample(ident=10000000000000)
        setattr(req2, "objects", {"sample": obj2})
        resp2 = Sample._get_instance_handler(req2)
        assert(resp2.status_code == 404)

    def test_put_instance(self):
        obj = Sample(create=True)
        obj.save()
        obj2 = Sample(ident=100000)
        req = Request.blank("", POST="{}") 
        setattr(req, "objects", {"sample": obj})

        resp = Sample._put_instance_handler(req)
        assert(resp.status_code == 422)
        errors = simplejson.loads(resp.body)
        assert len(errors) == 3

        req2 = Request.blank("", POST='{"index":1,"money":1.0,"name":"brandon"}') 
        setattr(req2, "objects", {"sample": obj})
        resp2 = Sample._put_instance_handler(req2)
        assert(resp2.status_code == 200)

        expected = json.dumps(obj)
        assert(resp2.body.decode("utf-8") == expected)

        req3 = Request.blank("", POST='{}') 
        setattr(req3, "objects", {"sample": obj2})
        resp3 = Sample._put_instance_handler(req3)
        assert(resp3.status_code == 404)

    def test_patch_instance(self):
        obj = Sample(create=True)
        obj.save()
        obj2 = Sample(ident=100000)

        req = Request.blank("", POST="{}") 
        setattr(req, "objects", {"sample": obj})
        resp = Sample._patch_instance_handler(req)
        assert(resp.status_code == 200)

        req2 = Request.blank("", POST='{"index":1,"name":"brandon"}') 
        setattr(req2, "objects", {"sample": obj})
        resp2 = Sample._patch_instance_handler(req2)
        assert(resp2.status_code == 200)
        assert(obj.name == "brandon")
        expected = json.dumps(obj)
        assert(resp2.body.decode("utf-8") == expected)

        req3 = Request.blank("", POST='{}') 
        setattr(req3, "objects", {"sample": obj2})
        resp3 = Sample._patch_instance_handler(req3)
        assert(resp3.status_code == 404)

        req4 = Request.blank("", POST='{"test":1}') 
        setattr(req4, "objects", {"sample": obj})
        resp4 = Sample._patch_instance_handler(req4)
        assert(resp4.status_code == 200)

        req5 = Request.blank("", POST='{"money":0}') 
        setattr(req5, "objects", {"sample": obj})
        resp5 = Sample._patch_instance_handler(req5)
        assert(resp5.status_code == 422)
        errors = simplejson.loads(resp5.body.decode("utf-8"))
        assert len(errors) == 1
