
"""Gerrit Backup Folder."""

import os
import shutil

import log


class BackupFolder(object):
    """Gerrit Backup Folder."""

    def __init__(self, config):
        """Init."""
        super(BackupFolder, self).__init__()
        self.config = config

        self.verbose = False
        self.dry_run = False

    def _get_back_file_path(self, file_path):
        """Get backup file path."""
        backup_file = self.config.get('backup_folder', 'backup_folder')
        return os.path.join(backup_file, file_path)

    def description(self):
        """Get Backup Description."""
        return "Folder Backup"

    # TODO: Versioning
    def get_backup_database_path(self):
        """Get Database backup path."""
        database_folder = self.config.get('backup_structure', 'database_folder')
        backup_path = '/'.join([self.config.get('backup', 'ssh_hostname'),
                                database_folder.strip('/'),
                                self.config.get('database', 'database_dump_file')])

        backup_path += '.tar.gz'
        return backup_path

    # TODO: Versioning
    def get_backup_repo_path(self, repo):
        """Get Repo backup path."""
        repos_folder = self.config.get('backup_structure', 'repos_folder')
        backup_path = '/'.join([self.config.get('backup', 'ssh_hostname'),
                                repos_folder.strip('/'),
                                repo])
        backup_path += '.git.tar.gz'
        return backup_path

    # TODO: Versioning
    def get_backup_repo_list_path(self):
        """Get Repo List backup path."""
        repos_list_folder = self.config.get('backup_structure', 'repos_list_folder')
        repo_list_filename = self.config.get('script', 'repo_list_filename')

        return '/'.join([self.config.get('backup', 'ssh_hostname'),
                         repos_list_folder.strip('/'),
                         os.path.basename(repo_list_filename)])

    # TODO: Versioning
    def get_all_versions(self, full_path):
        """Get version."""
        log.info(full_path)
        log.todo("Implement: %s" % full_path)
        return ['0']

    def upload_file(self, trg_file, src_file):
        """Upload file from folder."""
        backup_file = self._get_back_file_path(trg_file)
        backup_folder = os.path.dirname(backup_file)

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        log.print_log("Uploading file: -")
        log.print_log("  From: %s" % src_file)
        log.print_log("  To: %s" % backup_file)
        shutil.copy(src_file, backup_file)

    def download_file(self, trg_file, src_file):
        """Download file from folder."""
        backup_file = self._get_back_file_path(trg_file)

        log.print_log("Downloading file: -")
        log.print_log("  From: %s" % backup_file)
        log.print_log("  To: %s" % src_file)
        shutil.copy(backup_file, src_file)
