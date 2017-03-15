
"""Database Class."""

import re

import log
import shell


class Database(object):
    """Database."""

    def __init__(self, host, username, password):
        """Init."""
        super(Database, self).__init__()
        self.host = host
        self.username = username
        self.password = password

        self.verbose = False
        self.dry_run = False

    def run_sql_cmd(self, sqlCmd):
        """Run SQL CMD."""
        cmd = "mysql" \
              + " --host=%s" % self.host \
              + " --user=%s" % self.username \
              + " --password=%s" % self.password \
              + " -e '%s'" % sqlCmd

        if self.verbose:
            log_cmd = re.sub(r" --password=.*? ", " --password=******** ", cmd)
            log.verbose("%s" % log_cmd)

        if not self.dry_run:
            exit_code = shell.run_shell_cmd(cmd, '.', False)

            return exit_code

        return 0

    def run_file_cmd(self, sql_file):
        """Run File CMD."""
        cmd = "mysql" \
              + " --host=%s" % self.host \
              + " --user=%s" % self.username \
              + " --password=%s" % self.password \
              + " < %s" % sql_file

        if self.verbose:
            log_cmd = re.sub(r" --password=.*? ", " --password=******** ", cmd)
            log.verbose("%s" % log_cmd)

        if not self.dry_run:
            exit_code = shell.run_shell_cmd(cmd, '.', False)

            return exit_code

        return 0

    def dump(self, databases_names, database_dump_file):
        """Dump Database."""
        cmd = "mysqldump" \
              + " --host=%s" % self.host \
              + " --user=%s" % self.username \
              + " --password=%s" % self.password \
              + " --opt" \
              + " --quote-names" \
              + " --single-transaction" \
              + " --quick" \
              + " --databases %s" % ' '.join(databases_names) \
              + " > %s" % database_dump_file

        if self.verbose:
            log_cmd = re.sub(r" --password=.*? ", " --password=******** ", cmd)
            log.verbose("%s" % log_cmd)

        if not self.dry_run:
            path = '.'

            exit_code = shell.run_shell_cmd(cmd, path, self.verbose)

            return exit_code

        return 0
