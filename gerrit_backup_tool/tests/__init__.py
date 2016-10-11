# flake8: noqa
__author__ = 'John Paul Newman'

import os
import sys

script_path = os.path.dirname(os.path.realpath(__file__))
gerrit_backup_tool_path = os.path.join(script_path, '..')
sys.path.append(os.path.realpath(gerrit_backup_tool_path))
