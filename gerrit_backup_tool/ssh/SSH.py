
"""SSH Module."""

import os
import scp

import log

import paramiko
import fnmatch


class SSH(object):
    """SSH Connection."""

    def __init__(self, hostname, username):
        """Init."""
        super(SSH, self).__init__()
        self.port = 22
        self._key_file_path = None

        self.hostname = hostname
        self.username = username

        self.timeout = 30

        self.use_screen = False

        self.verbose = False
        self.dry_run = False

        self.ssh_client = None

    @property
    def key_file_path(self):
        """key_file_path property."""
        return self._x

    @key_file_path.setter
    def key_file_path(self, value):
        """Set Key file path."""
        if value.startswith('~'):
            self._key_file_path = os.path.expanduser(value)
        else:
            self._key_file_path = os.path.abspath(value)

    def set_client(self):
        """Set SSH Client."""
        self.ssh_client = self.get_client()

    def get_client(self):
        """Get SSH Client."""
        if self.ssh_client is not None:
            return self.ssh_client

        key = None
        if self._key_file_path:
            key = paramiko.RSAKey.from_private_key_file(self._key_file_path)

        client = paramiko.SSHClient()

        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.verbose:
            key_file_path = ''
            if self._key_file_path:
                key_file_path = " -i %s" % (self._key_file_path)

            log.verbose("ssh%s -p %d %s@%s" % (key_file_path,
                                               self.port,
                                               self.username,
                                               self.hostname))

        try:
            client.connect(hostname=self.hostname,
                           username=self.username,
                           port=self.port,
                           pkey=key,
                           timeout=self.timeout)
        except paramiko.AuthenticationException:
            raise RuntimeError("ERROR: SSH Authentication Error!")

        return client

    def close_client(self):
        """Close SSH Client."""
        if self.ssh_client is not None:
            self.ssh_client.close()

    def run_command(self, cmd, log_output=True):
        """SSH Command."""
        if self.verbose:
            log.verbose("Running remote command: %s" % cmd)

        ssh_client = self.get_client()

        _, stdout, stderr = ssh_client.exec_command(cmd)

        if log_output:
            for output in [stdout, stderr]:
                if output is not None:
                    for line in output:
                        log.print_log(line.strip('\n'), False, False)

        ret_stdout = stdout.read()
        ret_stderr = stderr.read()

        if self.ssh_client is None:
            ssh_client.close()

        return ret_stdout, ret_stderr

    def scp_copy_file(self, local_file_path, remote_file_path):
        """Copy file to remote via SCP."""
        ssh_client = self.get_client()

        if self.verbose:
            log.verbose("Copy file to remote: -")
            log.verbose("  %s" % local_file_path)
            log.verbose("  %s" % remote_file_path)

        with scp.SCPClient(ssh_client.get_transport()) as scp_client:
            scp_client.put(local_file_path, remote_file_path)

        if self.ssh_client is None:
            ssh_client.close()

    def copy_to_remote(self, local_path, remote_path, exclude_files=[], exclude_folders=[]):
        """Copy Folders to Remote."""
        log.print_log("Copy path to remote: %s" % self.hostname)

        created_remote_directories = []
        for root, dirnames, filenames in os.walk(local_path, topdown=True):
            dirnames[:] = [d for d in dirnames if d not in exclude_folders]

            for filename in filenames:
                skip = False
                for exclude_file in exclude_files:
                    if fnmatch.fnmatch(filename, exclude_file):
                        skip = True

                if skip:
                    continue

                remote_file_path = os.path.join(root, filename)
                remote_file_path = str.replace(remote_file_path, local_path, '')
                remote_file_path = remote_path.rstrip('/') + '/' + remote_file_path.lstrip('/')

                remote_file_dir = os.path.dirname(remote_file_path)
                if remote_file_dir not in created_remote_directories:

                    if self.verbose:
                        log.verbose("Creating remote path: %s" % remote_file_dir)

                    self.run_command("mkdir -p %s" % remote_file_dir)
                    created_remote_directories.append(remote_file_dir)

                local_filename = os.path.join(root, filename)
                self.scp_copy_file(local_filename, remote_file_path)

    def copy_files_to_remote(self, files, remote_path):
        """Copy Files to Remote."""
        log.print_log("Copy files to remote: %s" % self.hostname)

        self.run_command("mkdir -p %s" % remote_path)

        for local_file_path in files:
            remote_file_path = os.path.join(remote_path, os.path.basename(local_file_path))

            if not os.path.exists(local_file_path):
                raise RuntimeError("ERROR: File not found: %s" % local_file_path)

            self.scp_copy_file(local_file_path, remote_file_path)
