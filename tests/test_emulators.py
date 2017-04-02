import limb
import mock
import subprocess

def test_emulators():
    assert 'localhost' in limb.model.client()._connection.host

@mock.patch('limb.emulators.subprocess.Popen')
def test_emulators_error(subMock):
    original_host = limb.model.client()._connection.host
    subMock.side_effect = subprocess.CalledProcessError("", "")
    try:
        datastore = limb.emulators.setup_datastore(db="test")
        assert False
    except subprocess.CalledProcessError as e:
        assert True
        assert subMock.call_args_list[0][0][0] == ['gcloud', 'beta', 'emulators', 'datastore', 'start', '--data-dir=test']
        assert original_host == limb.model.client()._connection.host
