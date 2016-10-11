
"""Gerrit Backup."""

import shutil
import os

import shell
import log

from tar.Tar import Tar
from mysql.Database import Database


class Backup(object):
    """Gerrit Backup."""

    def __init__(self, config, backup_classes=[]):
        """Init."""
        super(Backup, self).__init__()
        self.config = config
        self.backup_classes = backup_classes

        self.verbose = False
        self.dry_run = False

        if len(self.backup_classes) == 0:
            raise RuntimeError('ERROR: No Backup classes!')

    def _get_repo_path(self, repo):
        """Return Repo Path."""
        gerrit_path = self.config.get('gerrit', 'gerrit_path')

        repo_path = os.path.join(gerrit_path, 'git')
        repo_path = os.path.join(repo_path, repo + '.git')

        return repo_path

    def _get_script_path(self):
        """Return Script Path."""
        return os.path.abspath(os.path.expanduser('~/gerrit_backup_tool'))

    def get_repo_disk_usage(self, repo):
        """Get Repos Disk Uages."""
        repo_path = self._get_repo_path(repo)

        cmd = "du -sh %s" % repo_path

        if not self.dry_run:
            return shell.run_shell_cmd(cmd, '.''', self.verbose)

        return 0

    def get_versions(self, repo):
        """Get version."""

        # TODO: Implement in all backup classes

        for backup_class in self.backup_classes:
            backup_path = backup_class.get_backup_repo_path(repo)
            versions = backup_class.get_all_versions(backup_path)
            for version in versions:
                log.print_log("- %s" % version)

        return 0

    def backup_database(self):
        """Backup Database."""
        exit_code = 0

        if not self.dry_run:
            path = '.'

            database = Database(self.config.get('database', 'database_host'),
                                self.config.get('database', 'database_username'),
                                self.config.get('database', 'database_password'))

            sql_dump_file = os.path.join(path, self.config.get('database', 'database_dump_file'))
            sql_dump_file = os.path.abspath(sql_dump_file)

            exit_code = database.dump([self.config.get('database', 'databases_name')], sql_dump_file)

            tar = Tar(self.dry_run, self.verbose)
            tar_file_path = tar.create(sql_dump_file)

            for backup_class in self.backup_classes:
                backup_path = backup_class.get_backup_database_path()
                backup_class.upload_file(backup_path, tar_file_path)

            if os.path.exists(tar_file_path):
                os.remove(os.path.abspath(tar_file_path))

            del database

        return exit_code

    def restore_database(self):
        """Restoring Database."""
        # database_folder = self.config.get('backup_structure', 'database_folder')
        database_dump_file = self.config.get('database', 'database_dump_file')

        tar_file = database_dump_file + '.tar.gz'

        if not self.dry_run:
            path = '.'

            tar = Tar(self.dry_run, self.verbose)

            log.print_log("Getting File...")
            for backup_class in self.backup_classes:
                backup_path = backup_class.get_backup_repo_list_path()
                backup_class.download_file(backup_path, tar_file)

            chown_cmd = "sudo chown %s:%s %s" % (self.config.get('restore', 'ssh_username'),
                                                 self.config.get('restore', 'ssh_username'),
                                                 tar_file)
            shell.run_shell_cmd(chown_cmd, path, self.verbose)

            log.print_log("Extracting TAR File...")
            tar.extract(tar_file)

            chown_cmd = "sudo chown %s:%s %s" % (self.config.get('restore', 'ssh_username'),
                                                 self.config.get('restore', 'ssh_username'),
                                                 database_dump_file)
            shell.run_shell_cmd(chown_cmd, path, self.verbose)

            log.print_log("Restoring Database...")

            database = Database(self.config.get('database', 'database_host'),
                                self.config.get('database', 'database_username'),
                                self.config.get('database', 'database_password'))

            database.run_file_cmd(self.config.get('database', 'database_dump_file'))

            del database

        return 0  # TODO: Error handling

    def backup_repo(self, repo):
        """Backing up Repo."""
        repo_path = self._get_repo_path(repo)

        if not self.dry_run:
            tar = Tar(self.dry_run, self.verbose)
            tar_file_path = tar.create(repo_path)

            # repos_folder = os.path.join(self.config.get('backup_structure', 'repos_folder'), os.path.dirname(repo))

            # backup_path = '/'.join([self.config.get('backup', 'ssh_hostname'),
            #                         repos_folder.strip('/'),
            #                         os.path.basename(tar_file_path)])

            for backup_class in self.backup_classes:
                backup_path = backup_class.get_backup_repo_path(repo)
                backup_class.upload_file(backup_path, tar_file_path)

            if os.path.exists(tar_file_path):
                os.remove(os.path.abspath(tar_file_path))

    def backup_repo_list(self):
        """Backing up Repo List File."""
        log.print_log("Backing up Repo List File")

        repo_list_filename = self.config.get('script', 'repo_list_filename')

        script_path = self._get_script_path()
        repo_list_file = os.path.join(script_path, repo_list_filename)

        if not self.dry_run:
            for backup_class in self.backup_classes:
                backup_path = backup_class.get_backup_repo_list_path()
                backup_class.upload_file(backup_path, repo_list_file)

    def restore_repo(self, repo):
        """Restoring Repo."""
        repo_path = os.path.dirname(self._get_repo_path(repo))

        tar_ext = '.git.tar.gz'
        repo_name = os.path.basename(repo)
        tar_filename = repo_name + tar_ext
        tar_file_path = os.path.join(repo_path, tar_filename)

        tar_extracted_path = os.path.join(repo_path, repo_name) + '.git'

        path = '.'

        if not self.dry_run:
            if os.path.exists(tar_extracted_path):
                shutil.rmtree(tar_extracted_path)

            if not os.path.exists(tar_extracted_path):
                log.print_log("Deleting Pervious Repo: %s" % tar_extracted_path)
                os.makedirs(tar_extracted_path)
                os.rmdir(tar_extracted_path)

            log.print_log("Downloading File...")

            for backup_class in self.backup_classes:
                backup_path = backup_class.get_backup_repo_path(repo)
                backup_class.download_file(backup_path, tar_file_path)

            chown_cmd = "sudo chown %s:%s %s" % (self.config.get('gerrit', 'gerrit_username'),
                                                 self.config.get('gerrit', 'gerrit_group'),
                                                 tar_file_path)
            shell.run_shell_cmd(chown_cmd, path, self.verbose)

            log.print_log("Extracting TAR File...")

            tar = Tar(self.dry_run, self.verbose)
            tar.extract(tar_file_path)

            chown_cmd = "sudo chown -R %s:%s %s" % (self.config.get('gerrit', 'gerrit_username'),
                                                    self.config.get('gerrit', 'gerrit_group'),
                                                    repo_path)
            shell.run_shell_cmd(chown_cmd, path, self.verbose)

            if os.path.exists(tar_file_path):
                os.remove(os.path.abspath(tar_file_path))
