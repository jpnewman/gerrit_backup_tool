
"""Tasks Module."""

import services
import shell
import time

import log

from mysql.Database import Database
from jenkins.Jenkins import Jenkins


def skip_task(config, section, is_remote):
    """Skip Task."""
    runForCommands = []
    if config.has_option(section, 'run_for_commands'):
        runForCommands = config.get(section, 'run_for_commands').split(',')

    pre_tasks_only = config.get('cmd_arguments', 'run_task').lower() == 'pre-tasks-only'
    post_tasks_only = config.get('cmd_arguments', 'run_task').lower() == 'post-tasks-only'

    runForAnyCommand = False
    if pre_tasks_only or post_tasks_only:
        runForAnyCommand = True

    if len(runForCommands) > 0 and not runForAnyCommand:
        if config.get('cmd_arguments', 'run_task') not in runForCommands:
            log.skipping("Task '%s' as 'run_for_commands' does not match" % section)
            return True

    runRemotely = False
    if config.has_option(section, 'run_remotely'):
        runRemotely = config.getboolean(section, 'run_remotely')

    if runRemotely != is_remote:
        log.skipping("Task '%s' as 'run_remotely' does not match" % section)
        return True

    log.running("Task '%s'" % section)
    return False


def _sleep(config, section):
    """Sleep."""
    if config.has_option(section, 'sleep'):
        sleepTime = config.getint(section, 'sleep')
        log.info("Sleeping for %d seconds" % sleepTime)
        time.sleep(sleepTime)


def run_tasks(config, is_remote, taskPrefix, dry_run=False, verbose=False):
    """Run tasks."""
    for section in config.sections():
        if not section.startswith("%s:" % taskPrefix):
            continue

        taskParts = section.split(':')

        if len(taskParts) < 2:
            raise RuntimeError("ERROR: Task not defined correctly")

        if skip_task(config, section, is_remote):
            continue

        taskName = taskParts[1].lower()
        if taskName == 'stop_jenkins_job':
            jenkinsUrl = config.get(section, 'jenkins_url')
            jobName = taskParts[2]

            if not dry_run:
                _sleep(config, section)
                jenkins = Jenkins(jenkinsUrl)
                jenkins_job_status = jenkins.disable_job_and_wait(jobName)
                if jenkins_job_status != 0:
                    raise RuntimeError("ERROR: Disabling Jenkins Job: %d" % jenkins_job_status)

        if taskName == 'start_jenkins_job':
            jenkinsUrl = config.get(section, 'jenkins_url')
            jobName = taskParts[2]

            if not dry_run:
                _sleep(config, section)
                jenkins = Jenkins(jenkinsUrl)
                jenkins.enable_job(jobName)

        elif taskName == 'stop_services':
            serviceNames = config.get(section, 'services').split(',')

            for serviceName in serviceNames:
                log.info("Stopping service: %s" % serviceName)
                if not dry_run:
                    _sleep(config, section)
                    services.stop_service(serviceName)

        elif taskName == 'start_services':
            serviceNames = config.get(section, 'services').split(',')

            for serviceName in serviceNames:
                log.info("Starting service: %s" % serviceName)
                if not dry_run:
                    _sleep(config, section)
                    services.start_service(serviceName)

        elif taskName == 'command':
            command = config.get(section, 'command')
            pwd = config.get(section, 'pwd')

            if not dry_run:
                _sleep(config, section)
                shell.run_shell_cmd(command, pwd)

        elif taskName == 'database_command':
            if not dry_run:
                _sleep(config, section)
                database = Database(config.get('database', 'database_host'),
                                    config.get('database', 'database_username'),
                                    config.get('database', 'database_password'))
                database.verbose = verbose
                database.dry_run = dry_run
                database.run_sql_cmd(config.get(section, 'command'))


def pre_tasks(config, is_remote, dry_run=False, verbose=False):
    """Pre-backup / restore tasks."""
    run_tasks(config, is_remote, 'pre_tasks', dry_run, verbose)


def post_tasks(config, is_remote, dry_run=False, verbose=False):
    """Post-backup / restore tasks."""
    run_tasks(config, is_remote, 'post_tasks', dry_run, verbose)
