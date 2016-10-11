
"""Utils Module."""

import ConfigParser
import os


def load_config(config_file_path):
    """Load Configuration file."""
    if not os.path.exists(config_file_path):
        raise RuntimeError("ERROR: File not found: %s" % config_file_path)

    config = ConfigParser.RawConfigParser()
    config.read(config_file_path)

    return config


def set_common_args(config, args):
    """Parse Common Arguments."""
    config.set('cmd_arguments', 'dry_run', str(args.dry_run))
    config.set('cmd_arguments', 'verbose', str(args.verbose))
    config.set('cmd_arguments', 'debug', str(args.debug))


def get_remote_user_home(config):
    """Generate Remote User Home path."""
    config_key = config.get('cmd_arguments', 'config_key').strip()
    return "/home/%s" % (config.get(config_key, 'ssh_username'))


def human_size(nbytes):
    """Human Size String."""
    size_suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

    if nbytes == 0:
        return '0 B'

    i = 0
    while nbytes >= 1024 and i < len(size_suffixes) - 1:
        nbytes /= 1024.
        i += 1

    formatted = ('%.2f' % nbytes).rstrip('0').rstrip('.')

    return '%s %s' % (formatted, size_suffixes[i])
