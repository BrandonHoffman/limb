"""
Copyright 2017 Brandon Hoffman <brandon.michael.hoffman@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import subprocess
import time
import re
import os

exports_re = re.compile("(?P<name>[\w]+)=(?P<val>[^ \t\r\f\v]+)")


def setup_datastore(db=None):
    datastore = None

    db_log = open(".datastore.log", "w")

    print("setting up datastore emulator.............")
    emulator_run_command = ["gcloud", "beta", "emulators", "datastore", "start"]
    emulator_env_command = ["gcloud", "beta", "emulators", "datastore", "env-init"]
    if db:
        emulator_run_command.append("--data-dir=" + db)
        emulator_env_command.append("--data-dir=" + db)
    try:
        datastore = subprocess.Popen(emulator_run_command, stdout=db_log, stderr=db_log)
        time.sleep(5)
        result = subprocess.check_output(emulator_env_command)
        result = result.decode("utf-8")
        results = result.split("\n")
        exports = []
        for result in results:
            match = exports_re.search(result)
            if match:
                exports.append(match.groups())

    except subprocess.CalledProcessError as e:
        print ("error starting datastore emulator......")
        raise e
    for (name, value) in exports:
        os.environ[name] = value
    print ("datastore emulator runnning........")
    return datastore

