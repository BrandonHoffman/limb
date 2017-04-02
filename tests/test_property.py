from limb import property
from limb import model
from limb.validation import ValidationError, Between
from functools import partial

class MainObject(model.Model):
    number = property.Integer()
    double = property.Double(validators=[Between(1,100)])
    boolean = property.Boolean()
    string = property.String()

    class MainObject2(model.Model):
        pass

    @property.compound
    def test(self):
        return self.string + str(self.number)

class Fake():
    pass

test = Fake()
    
class TestProperty(object):
    property_name = "number"
    val = 1
    def test_make_error(self):
        prop = getattr(MainObject, self.property_name)
        error = ValidationError(1, "Test Error")
        error_dict = prop._make_error(error)
        assert error_dict["code"] == 1
        assert error_dict["message"] == "Test Error"
        assert error_dict["field"] == self.property_name

    def test_check_type(self):
        prop = getattr(MainObject, self.property_name)
        assert prop.check_type(None) != None
        assert prop.check_type(self.val) == None

    def test_validate(self):
        prop = getattr(MainObject, self.property_name)
        errors = prop.validate(None)
        assert len(errors) == 1
        assert errors[0]["code"] == 100
        assert errors[0]["message"] == "Required Field"

        errors = prop.validate(test)
        assert len(errors) == 1
        assert errors[0]["code"] == 101
        assert "expected" in errors[0]["message"]

    def test_get_set_delete(self):
        obj = MainObject(create=True) 
        assert getattr(obj, self.property_name) == None
        setattr(obj, self.property_name, self.val)
        assert getattr(obj, self.property_name) == self.val
        delattr(obj, self.property_name)
        assert getattr(obj, self.property_name) == None
        

class TestDouble(TestProperty):
    property_name = "double"
    val = 1.1
    def test_validate(self):
        prop = getattr(MainObject, self.property_name)
        super(TestDouble, self).test_validate() 
        errors = prop.validate(0.1)
        assert len(errors) == 1
        errors = prop.validate(120.1)
        assert len(errors) == 1

class TestBoolean(TestProperty):
    property_name = "boolean"
    val = True

class TestString(TestProperty):
    property_name = "string"
    val = "test"

class TestObject(TestProperty):
    property_name = "mainobject2"
    val = MainObject.MainObject2()

    def test_validate(self):
        prop = getattr(MainObject, self.property_name)
        errors = prop.validate(None)
        assert errors == None

    def test_for_json(self):
        prop = getattr(MainObject, self.property_name)
        url = prop.for_json()
        assert False #this should return an absoult resoved url eventually
        
    def test_get_set_delete(self):
        obj = MainObject(create=True) 
        assert getattr(obj, self.property_name).__class__ == partial
        setattr(obj, self.property_name, self.val)
        assert getattr(obj, self.property_name).__class__ == partial
        delattr(obj, self.property_name)
        assert getattr(obj, self.property_name).__class__ == partial

class TestFunction(TestProperty):
    property_name = "test"
    def test_check_type(self):
        prop = getattr(MainObject, self.property_name)
        assert prop.check_type(None) == None
        assert prop.check_type(self.val) == None

    def test_validate(self):
        prop = getattr(MainObject, self.property_name)
        errors = prop.validate(None)
        assert errors == None

    def test_get_set_delete(self):
        obj = MainObject(create=True) 
        obj.string = "name"
        obj.number = 1
        assert getattr(obj, self.property_name) == obj.string + str(obj.number)
        setattr(obj, self.property_name, self.val)
        assert getattr(obj, self.property_name) == obj.string + str(obj.number)
        delattr(obj, self.property_name)
        assert getattr(obj, self.property_name) == obj.string + str(obj.number)
