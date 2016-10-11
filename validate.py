# https://gist.github.com/mwaterfall/5084540
#
#
# Recursively validates all python files with pyflakes that were modified
# since the last validation, and provides basic stats. Ignores hidden
# directories.
#
# NOTE:
# You should set your favourite version control system to ignore
# the validate.db file that is used to track when which files
# have changed since last validation.
#
# Usage: $ python validate.py [--help] [--all] [--stats]
#

try:
    import pyflakes
    pyflakes  # avoid unused warning when validating self!
except ImportError:
    print('Validate requires pyflakes. Please install '
          'with: pip install pyflakes')
    exit()

import argparse
import os
import pickle
from subprocess import call
import re

# Matches:       .dir/foo   /foo/.git/bar
# Doesn't match: ./dir/foo  ./foo/./bar
path_in_hidden_folders = re.compile(r'^(.*/)?\.[^/]+/.+$')

# Options
parser = argparse.ArgumentParser(description="""
Recursively validates all
python files with pyflakes that were modified since the last
validation,and provides basic stats. Ignores hidden directories.
""")
parser.add_argument('--all', dest='all', action='store_true', default=False,
                    help='check all files, regardless of last modification '
                         'and validation dates')
parser.add_argument('--stats', dest='stats', action='store_true',
                    default=False, help='return statistics on Python '
                                        'files (line count, etc)')
args = parser.parse_args()

# Setup
skip_paths = []

# Stats
file_count = 0
validated_count = 0
validated_issue_count = 0
line_count = 0

# Validate db
try:
    db_file = open('./validate.db', 'r+b')
    validate_db = pickle.load(db_file)
except (EOFError, IOError):
    db_file = open('./validate.db', 'w+b')
    validate_db = {'modifieds': {}}

# Validate recursivly - traverse all files and folders
if args.all or not validate_db['modifieds']:
    print('\n---- Validating all files ----')
else:
    print('\n---- Validating files modified since last validation ----')
for dirname, dirnames, filenames in os.walk('.'):
    for filename in filenames:
        if filename.endswith('.py'):

            # File details
            path = os.path.join(dirname, filename)

            # Skip
            if path in skip_paths:
                continue
            if path_in_hidden_folders.match(path):
                continue

            # Validate
            file_count += 1
            mtime = int(os.stat(path).st_mtime)
            if args.all or validate_db['modifieds'].get(path, 0) < mtime:
                if call(['pyflakes', path]):
                    validated_issue_count += 1
                validated_count += 1
            if not args.all:
                validate_db['modifieds'][path] = mtime

            # Stats
            if args.stats:
                line_count += sum(1 for line in open(path))
if validated_issue_count == 0:
    print('ALL OKAY')
print('\n---- Validation summary ----')
print('Files with validation issues: %i' % validated_issue_count)
print('Validated files: %i' % validated_count)
print('Total python files: %i' % file_count)

# Print stats
if args.stats:
    print('\n---- Stats ----')
    print('Total python line count: %i' % line_count)

# Save db
db_file.seek(0)
pickle.dump(validate_db, db_file, pickle.HIGHEST_PROTOCOL)
db_file.close()

# Finish
print('')
