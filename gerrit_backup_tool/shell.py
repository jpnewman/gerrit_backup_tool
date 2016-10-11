
"""Shell Module."""

import subprocess as sp

import log


def run_shell_cmd(cmd, path='.', verbose=False):
    """Run Shell Command."""
    if verbose:
        log.verbose(cmd)

    process = sp.Popen(cmd, shell=True, cwd=path)
    stdout, stderr = process.communicate()
    exit_code = process.wait()

    for output in [stdout, stderr]:
        if output is not None:
            for line in output:
                log.print_log(line.strip('\n'))

    return exit_code
