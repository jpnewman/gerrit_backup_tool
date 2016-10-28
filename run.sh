#!/bin/bash

# Ubuntu
sudo apt-get install -y build-essential libssl-dev libffi-dev python-dev

virtualenv -p /usr/local/bin/python2.7 venv
source venv/bin/activate

./venv/bin/pip install -r requirements.txt
python gerrit_backup_tool gerrit_backup.cfg --backup --verbose
exit_code=$?

deactivate

echo "Exit Code: $exit_code"
exit $exit_code
