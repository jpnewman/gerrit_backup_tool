
"""GerritRemote Class."""

import os

import log


class GerritRemote(object):
    """Gerrit SSH."""

    def __init__(self, config, ssh):
        """Init."""
        super(GerritRemote, self).__init__()
        self.config = config
        self.ssh = ssh

        self.config_filename = ''
        self.repo_list_filename = ''

        self.file_copied_to_remote = False

        self.verbose = False
        self.dry_run = False

    def _copy_script_files_to_remote(self):
        """Copy Script Files to Remote."""
        if self.file_copied_to_remote:
            return

        remote_path = '~/gerrit_backup_tool/'

        self.ssh.run_command("rm -rf %s" % remote_path)

        script_path = os.path.dirname(os.path.realpath(__file__))
        self.ssh.copy_to_remote(script_path,
                                remote_path,
                                ['*.pyc', '.DS_Store'],
                                ['.cache', '__pycahce__'])

        requirements_remotes = os.path.join(script_path, 'requirements_remote.txt')
        gerrit_backup_repo = os.path.join(script_path, self.repo_list_filename)

        self.ssh.copy_files_to_remote(
            [self.config_filename, requirements_remotes, gerrit_backup_repo], remote_path)

        self.file_copied_to_remote = True

    def run_backup_cmd(self, command):
        """Run remote gerrit_backup command."""
        options = ""
        if self.dry_run:
            options += " --dry-run"

        if self.verbose:
            options += " --verbose"

        if self.config.has_option('cmd_arguments', 'repo_list'):
            options += " --repo-list %s" % self.config.get('cmd_arguments', 'repo_list')

        elif self.repo_list_filename:
            options += " --repo-list %s" % self.repo_list_filename

        self.ssh.run_command("sudo pip install -r ./gerrit_backup_tool/requirements_remote.txt")

        cmd = "sudo python ./gerrit_backup_tool/%s %s %s%s" % (self.config.get('script', 'script_python_filename'),
                                                               os.path.basename(
                                                                   self.config_filename),
                                                               command, options)

        self.ssh.run_command(cmd)

    def diskusage(self, repos):
        """Disk Usage Remote."""
        log.print_log("Disk Usage of remote repos on host: %s" %
                      self.config.get('backup', 'ssh_hostname'))
        self._copy_script_files_to_remote()

        self.run_backup_cmd("--diskusage")

    def get_versions(self, repos):
        """Get Versions Remote."""
        log.print_log("Getting Versions of remote repos on host: %s" %
                      self.config.get('backup', 'ssh_hostname'))
        self._copy_script_files_to_remote()

        self.run_backup_cmd("--get-versions")

    def backup_data(self, repos):
        """TAR remote repos."""
        log.print_log("Backing up remote repos on host: %s" %
                      self.config.get('backup', 'ssh_hostname'))
        self._copy_script_files_to_remote()

        self.run_backup_cmd("--backup")

    def restore_data(self, repos):
        """Restore Gerrit."""
        log.print_log("Restoring remote repos on host: %s" %
                      self.config.get('backup', 'ssh_hostname'))
        self._copy_script_files_to_remote()

        self.run_backup_cmd("--restore")
