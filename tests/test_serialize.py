import limb

def test_serialize():
    expected = '[\n\t1,\n\ttrue,\n\t[],\n\t"abc",\n\t{}\n]'
    test = [1, True, [], "abc", {}]
    actual = limb.serialize.dumps(test)
    assert expected == actual
