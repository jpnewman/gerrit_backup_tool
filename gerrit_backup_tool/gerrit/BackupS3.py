
"""Gerrit Backup S3."""

import os

import log


class BackupS3(object):
    """Gerrit Backup S3."""

    def __init__(self, config, s3):
        """Init."""
        super(BackupS3, self).__init__()
        self.config = config
        self.s3 = s3

        self.verbose = False
        self.dry_run = False

    def description(self):
        """Get Backup Description."""
        return "S3 Backup"

    def get_backup_database_path(self):
        """Get Database backup path."""
        database_folder = self.config.get('backup_structure', 'database_folder')
        backup_path = '/'.join([self.config.get('backup', 'ssh_hostname'),
                                database_folder.strip('/'),
                                self.config.get('database', 'database_dump_file')])

        backup_path += '.tar.gz'
        return backup_path

    def get_backup_repo_path(self, repo):
        """Get Repo backup path."""
        repos_folder = self.config.get('backup_structure', 'repos_folder')
        backup_path = '/'.join([self.config.get('backup', 'ssh_hostname'),
                                repos_folder.strip('/'),
                                repo])
        backup_path += '.git.tar.gz'
        return backup_path

    def get_backup_repo_list_path(self):
        """Get Repo List backup path."""
        repos_list_folder = self.config.get('backup_structure', 'repos_list_folder')
        repo_list_filename = self.config.get('script', 'repo_list_filename')

        return '/'.join([self.config.get('backup', 'ssh_hostname'),
                         repos_list_folder.strip('/'),
                         os.path.basename(repo_list_filename)])

    def get_all_versions(self, full_path):
        """Get version."""
        log.info(full_path)
        bucket_versions = self.s3.get_key_versions(full_path)
        return bucket_versions

    def upload_file(self, full_path, filename):
        """Upload file to S3."""
        log.print_log("Uploading file to S3")
        self.s3.upload_file(full_path, filename)

    def download_file(self, full_path, filename):
        """Download file from S3."""
        log.print_log("Downloading file from S3")
        self.s3.download_file(full_path, filename)
