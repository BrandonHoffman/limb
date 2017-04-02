import limb

def test_between():
    validator = limb.validation.Between(1, 100)
    assert validator(10) == None
    assert validator(0).code == 200
    assert validator(101).code == 200
