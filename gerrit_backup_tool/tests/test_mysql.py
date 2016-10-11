
"""Test MySQL class."""

import unittest

import sys
from cStringIO import StringIO
from contextlib import contextmanager

from mysql.Database import Database


@contextmanager
def capture(command, *args, **kwargs):
    """Capture stdout."""
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


class DatabaseTests(unittest.TestCase):
    """Test Database Class."""

    def setUp(self):
        """Setup."""
        self.database = Database('localhost',
                                 'root',
                                 'password123')

    def test_run_sql_cmd_password_mask(self):
        """Test run_sql_cmd."""
        self.database.verbose = True
        self.database.dry_run = True
        with capture(self.database.run_sql_cmd, "SHOW DATABASE;") as output:
            self.assertTrue(" --password=******** " in output)

if __name__ == '__main__':
    unittest.main()
