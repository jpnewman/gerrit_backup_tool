#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

"""
This scrip backup and restores Gerrit.

It does the following: -
- Get a list of Gerrit Projects
- Backups Gerrit Projects to AWS S3 Bucket
"""

import argparse
import sys
import os

from datetime import datetime
from imp import reload

import repoList
import utils
import tasks
import log

from ssh.SSH import SSH
from GerritRemote import GerritRemote
from gerrit.Api import Api

reload(sys)
sys.setdefaultencoding('utf-8')


def process(config, args):
    """Processing."""
    repos = []
    ssh = None

    verify_ssl = True
    if config.has_option('backup_api', 'api_verify_ssl'):
        verify_ssl = config.getboolean('backup_api', 'api_verify_ssl')

    if args.repo_list:
        log.print_log("Getting repo list from file: %s" % args.repo_list)

        repos = repoList.parse_repo_list(args.repo_list)

    elif args.backup or args.get_repo_list:
        gerrit_api = Api(config.get('backup_api', 'api_url'), verify_ssl)
        gerrit_api.verbose = args.verbose
        repos = gerrit_api.get_repos()

    if args.get_repo_list:
        gerrit_api = Api(config.get('backup_api', 'api_url'), verify_ssl)
        gerrit_api.verbose = args.verbose
        script_repo_file = gerrit_api.output_repo_list_to_file(
            repos, config.get('script', 'repo_list_filename'))
        log.print_log("Script Repo File: %s" % script_repo_file)
        return

    try:
        config_key = config.get('cmd_arguments', 'config_key').strip()

        script_path = os.path.dirname(os.path.realpath(__file__))
        repo_list_filename = os.path.join(
            script_path + '/..', config.get('script', 'repo_list_filename'))

        ssh = SSH(config.get(config_key, 'ssh_hostname'),
                  config.get(config_key, 'ssh_username'))

        ssh_key_file = config.get(config_key, 'ssh_key_file')
        if ssh_key_file:
            ssh.key_file_path = ssh_key_file

        ssh.port = config.getint(config_key, 'ssh_port')
        ssh.use_screen = args.use_screen
        ssh.verbose = args.verbose
        ssh.dry_run = args.dry_run
        ssh.set_client()

        gerrit_remote = GerritRemote(config, ssh)
        gerrit_remote.config_filename = config.get('cmd_arguments', 'config_file')
        gerrit_remote.repo_list_filename = repo_list_filename
        gerrit_remote.verbose = args.verbose
        gerrit_remote.dry_run = args.dry_run

        if not args.post_tasks_only:
            tasks.pre_tasks(config, False, args.dry_run, args.verbose)

        if args.pre_tasks_only:
            gerrit_remote.run_backup_cmd("--pre-tasks-only")
            return

        if not args.post_tasks_only:
            if args.diskusage:
                gerrit_remote.diskusage(repos)

            if args.get_versions:
                version = gerrit_remote.get_versions(repos)
                if version:
                    log.print_log(version)

            if args.backup:
                gerrit_remote.backup_data(repos)

            if args.restore:
                gerrit_remote.restore_data(repos)

    finally:
        if not args.pre_tasks_only:
            tasks.post_tasks(config, False, args.dry_run, args.verbose)

        if args.post_tasks_only:
            gerrit_remote.run_backup_cmd("--post-tasks-only")

        if ssh:
            ssh.close_client()


def _parse_args():
    """Parse Command Arguments."""
    desc = 'Backups / Restore Gerrit Repos'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('config_file',
                        nargs='+',
                        help='Config File')
    parser.add_argument('--backup',
                        action='store_true',
                        default=False,
                        help='Backups Gerrit')
    parser.add_argument('--restore',
                        action='store_true',
                        default=False,
                        help='Restores Gerrit')
    parser.add_argument('--get-repo-list',
                        action='store_true',
                        default=False,
                        help='diskusage: Gets list of repos')
    parser.add_argument('--diskusage',
                        action='store_true',
                        default=False,
                        help='diskusage: Gets repo disk usage')
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
    parser.add_argument('--use-screen',
                        action='store_true',
                        default=False,
                        help='Use screen on remote. NOTE: screen needs to be installed on remote.')
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


def _test_args(args):
    """Test Arguments."""
    if args.backup is False \
       and args.restore is False \
       and args.diskusage is False \
       and args.get_repo_list is False \
       and args.get_versions is False \
       and args.pre_tasks_only is False \
       and args.post_tasks_only is False:
        log.print_log("Select one of the following command line actions: -")
        log.print_log("  --backup")
        log.print_log("  --restore")
        log.print_log("  --diskusage")
        log.print_log("  --get-repo-list")
        log.print_log("  --get-versions")
        log.print_log("  --pre-tasks-only")
        log.print_log("  --post-tasks-only")
        log.print_log("  --get-repo-list")
        log.print_log("  --get-versions")
        log.print_log("")
        log.print_log(args)
        return 1

    return 0


def _set_config(args, config, config_file_path):
    """Set config."""
    config.add_section('cmd_arguments')
    config.set('cmd_arguments', 'config_file', config_file_path)

    if args.backup \
       or args.diskusage \
       or args.get_versions \
       or args.pre_tasks_only \
       or args.post_tasks_only:
        config.set('cmd_arguments', 'config_key', 'backup')
    elif args.restore:
        config.set('cmd_arguments', 'config_key', 'restore')

    run_task = ''
    if args.backup:
        run_task = 'backup'
    elif args.restore:
        run_task = 'restore'
    elif args.diskusage:
        run_task = 'diskusage'
    elif args.get_repo_list:
        run_task = 'get-repo-list'
    elif args.pre_tasks_only:
        run_task = 'pre-tasks-only'
    elif args.post_tasks_only:
        run_task = 'post-tasks-only'

    config.set('cmd_arguments', 'run_task', run_task)

    config.set('cmd_arguments', 'use_screen', args.use_screen)

    if args.repo_list:
        config.set('cmd_arguments', 'repo_list', args.repo_list)


def main():
    """Main function."""
    log.print_log("Backing up / Restoring Gerrit Repos")

    start_time = datetime.now().replace(microsecond=0)

    args = _parse_args()
    if _test_args(args) != 0:
        return

    config_file_path = args.config_file[0]
    if not os.path.isabs(args.config_file[0]):
        config_file_path = os.path.join(os.getcwd(), args.config_file[0])

    if not os.path.exists(config_file_path):
        raise RuntimeError("ERROR: File not found: %s" % config_file_path)

    config = utils.load_config(config_file_path)

    _set_config(args, config, config_file_path)
    utils.set_common_args(config, args)

    process(config, args)

    end_time = datetime.now().replace(microsecond=0)
    log.print_log("Processing Time: %s" % str(end_time - start_time))
