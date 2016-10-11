
"""SSH Module."""

import os

import shell


class Tar(object):
    """Tar Class."""

    def __init__(self, dry_run=False, verbose=False):
        """Init."""
        super(Tar, self).__init__()
        self.dry_run = dry_run
        self.verbose = verbose

    def create(self, file_path):
        """Create TAR file."""
        path = os.path.dirname(file_path)

        if path == '':
            path = '.'

        folder_name = os.path.basename(file_path)

        tar_filename = "%s.tar.gz" % folder_name
        tar_filename = os.path.join(path, tar_filename)

        extra_tar_options = ""
        if self.verbose:
            extra_tar_options += "v"

        cmd = "tar -%sczf %s %s" % (extra_tar_options, tar_filename, folder_name)

        if not self.dry_run:
            exit_code = shell.run_shell_cmd(cmd, path, self.verbose)

            if exit_code != 0:
                raise RuntimeError("ERROR: Create TAR returned exit code: %d" % exit_code)

        return tar_filename

    def extract(self, file_path):
        """Extract TAR file."""
        path = os.path.dirname(file_path)

        if path == '':
            path = '.'

        extra_tar_options = ""
        if self.verbose:
            extra_tar_options += "v"

        cmd = "tar -%sxzf %s" % (extra_tar_options, file_path)

        if not self.dry_run:
            exit_code = shell.run_shell_cmd(cmd, path, self.verbose)

            if exit_code != 0:
                raise RuntimeError("ERROR: Extract TAR returned exit code: %d" % exit_code)
