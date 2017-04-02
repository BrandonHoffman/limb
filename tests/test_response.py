from limb import response

def test_ok():
    resp = response.OK()
    assert(resp.status_int == 200)

def test_created():
    resp = response.Created()
    assert(resp.status_int == 201)

def test_no_content():
    resp = response.NoContent()
    assert(resp.status_int == 204)

def test_bad():
    resp = response.BadRequest()
    assert(resp.status_int == 400)

def test_not_found():
    resp = response.NotFound()
    assert(resp.status_int == 404)

def test_validation():
    resp = response.ValidationError()
    assert(resp.status_int == 422)
