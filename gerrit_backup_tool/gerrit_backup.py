#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""
This scrip backup and restores Gerrit.

This script does the following : -
- Get a list of Gerrit Projects
- Backups Gerrit Projects to AWS S3 Bucket
"""

import argparse
import sys
import os

from imp import reload

import repoList
import utils
import tasks
import log

from aws.S3 import S3

from gerrit.Backup import Backup
from gerrit.BackupS3 import BackupS3
from gerrit.BackupFolder import BackupFolder

reload(sys)
sys.setdefaultencoding('utf-8')


def process(config, args):
    """Processing."""
    backup_classes = []

    if config.has_section('backup_s3cfg'):
        s3 = S3(config.get('backup_s3cfg', 'access_key'),
                config.get('backup_s3cfg', 'secret_key'),
                config.get('backup_s3cfg', 's3_backup_bucket'))

        if config.has_section('gpg'):
            s3.encrypt_files = config.getboolean('gpg', 'encrypt_files')

        s3.content_type = 'application/tar+gzip'

        backup_classes.append(BackupS3(config, s3))

    if config.has_section('backup_folder'):
        backup_classes.append(BackupFolder(config))

    if len(backup_classes) > 0:
        log.info("Backup Classes: -")
        for backup_class in backup_classes:
            log.info("- %s" % backup_class.description())

    gerrit = Backup(config, backup_classes)
    gerrit.verbose = args.verbose
    gerrit.dry_run = args.dry_run

    try:
        if not args.post_tasks_only:
            tasks.pre_tasks(config, True, args.dry_run, args.verbose)

        if args.pre_tasks_only:
            return

        if not args.post_tasks_only:
            if args.backup or args.backup_database:
                log.print_log("Backing up Database")
                gerrit.backup_database()

            if args.restore or args.restore_database:
                log.print_log("Restoring Database")
                # s3.list_bucket_keys(config)
                gerrit.restore_database()

            repo_list_filename = config.get('script', 'repo_list_filename')
            script_path = os.path.dirname(os.path.realpath(__file__))
            repo_list_file = os.path.join(script_path, repo_list_filename)

            if not os.path.exists(repo_list_file):
                raise RuntimeError("ERROR: File not found: %s" % repo_list_file)

            repos = []
            if config.has_option('cmd_arguments', 'repo_list'):
                repos = repoList.parse_repo_list(repo_list_file)
            else:
                for backup_class in backup_classes:
                    backup_path = backup_class.get_backup_repo_list_path()
                    backup_class.download_file(backup_path, repo_list_file)
                    backup_class_repos = repoList.parse_repo_list(repo_list_file)

                    repos += backup_class_repos

                repos = list(set(repos))

            total_repos = len(repos)
            repo_cnt = 0
            for repo in repos:
                repo_cnt += 1
                repo_percentage = (float(repo_cnt) / total_repos) * 100
                progress = " [{0:d}/{1:d}] {2:.2f}%".format(repo_cnt,
                                                            total_repos,
                                                            repo_percentage)

                if args.diskusage:
                    log.print_log("Reporting Repo Disk Usage%s" % progress)
                    gerrit.get_repo_disk_usage(repo)

                if args.get_versions:
                    gerrit.get_versions(repo)

                if args.backup or args.backup_repos:
                    log.info("Backing up Repos%s" % progress)
                    gerrit.backup_repo(repo)

                if args.restore or args.restore_repos:
                    tasks.pre_tasks(config, False, args.dry_run, args.verbose)
                    log.print_log("Restoring Repos%s" % progress)
                    gerrit.restore_repo(repo)

            if args.backup or args.backup_repos:
                gerrit.backup_repo_list()

    finally:
        if not args.pre_tasks_only:
            tasks.post_tasks(config, True, args.dry_run, args.verbose)


def _parse_args():
    """Parse Command Arguments."""
    desc = 'Backups Gerrit Repos'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('config_file',
                        nargs='+',
                        help='Config File')
    parser.add_argument('--diskusage',
                        action='store_true',
                        default=False,
                        help='diskusage: Gets repo disk usage')
    parser.add_argument('--backup',
                        action='store_true',
                        default=False,
                        help='backups database and repos')
    parser.add_argument('--backup-database',
                        action='store_true',
                        default=False,
                        help='backup-database: Dump, TAR, and backups database')
    parser.add_argument('--backup-repos',
                        action='store_true',
                        default=False,
                        help='backup-repos: TAR and backups repos')
    parser.add_argument('--restore',
                        action='store_true',
                        default=False,
                        help='restore database and repos')
    parser.add_argument('--restore-database',
                        action='store_true',
                        default=False,
                        help='restore-database: Download, Extract TAR, and import database')
    parser.add_argument('--restore-repos',
                        action='store_true',
                        default=False,
                        help='restore-repos: Download, Extract TAR and restore repos')
    parser.add_argument('--repo-list',
                        help='File containing a list of repos to backup')
    parser.add_argument('--get-versions',
                        action='store_true',
                        default=False,
                        help='Get backup versions')
    parser.add_argument('--pre-tasks-only',
                        action='store_true',
                        default=False,
                        help='Run pre-tasks only')
    parser.add_argument('--post-tasks-only',
                        action='store_true',
                        default=False,
                        help='Run post-tasks only')
    parser.add_argument('--dry-run',
                        action='store_true',
                        default=False,
                        help='Dry-run. No action taken')
    parser.add_argument('--verbose',
                        action='store_true',
                        default=False,
                        help='Verbose output')
    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Debug output')
    return parser.parse_args()


def _set_config(args, config, config_file_path):
    """Set config."""
    config.add_section('cmd_arguments')

    if args.backup_database or args.backup_repos or args.diskusage:
        config.set('cmd_arguments', 'config_key', 'backup')
    elif args.restore_database or args.restore_repos:
        config.set('cmd_arguments', 'config_key', 'restore')

    run_task = ''
    if args.diskusage:
        run_task = 'diskusage'
    elif args.backup or args.backup_database or args.backup_repos:
        run_task = 'backup'
    elif args.restore or args.restore_database or args.restore_repos:
        run_task = 'restore'
    elif args.pre_tasks_only:
        run_task = 'pre-tasks-only'
    elif args.post_tasks_only:
        run_task = 'post-tasks-only'

    config.set('cmd_arguments', 'run_task', run_task)

    if args.repo_list:
        config.set('cmd_arguments', 'repo_list', args.repo_list)


def main():
    """Main function."""
    log.info("Backing up / Restoring Remote Gerrit Repos")

    args = _parse_args()

    script_path = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(script_path, args.config_file[0])

    if not os.path.exists(config_file_path):
        raise RuntimeError("ERROR: File not found: %s" % config_file_path)

    config = utils.load_config(config_file_path)

    _set_config(args, config, config_file_path)
    utils.set_common_args(config, args)

    process(config, args)

if __name__ == "__main__":
    main()
