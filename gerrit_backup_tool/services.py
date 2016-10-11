
"""Services Module."""

import shell


def run_service_command(serviceName, command='status'):
    """Run Service Command."""
    command = "sudo service %s %s" % (serviceName, command)
    shell.run_shell_cmd(command)


def stop_service(serviceName):
    """Stop Service."""
    run_service_command(serviceName, 'stop')


def start_service(serviceName):
    """Start Service."""
    run_service_command(serviceName, 'start')
