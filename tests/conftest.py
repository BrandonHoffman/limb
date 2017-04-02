import pytest
import tempfile
from limb import emulators

conf = {}

def pytest_configure(config):
    tempfs = tempfile.mkdtemp()
    process = emulators.setup_datastore(db=tempfs)
    conf["process"] = process

def pytest_unconfigure(config):
    conf["process"].kill()
    print("removing test dir")
    print("destroy emulators")
