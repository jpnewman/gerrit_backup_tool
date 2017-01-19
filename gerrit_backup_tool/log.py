
"""Log Module."""

import socket
import sys

from datetime import datetime

# http://blog.mathieu-leplatre.info/colored-output-in-console-with-python.html
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def __has_colors(stream, allow_piping=False):
    """Check if Console Has Color."""
    if not hasattr(stream, "isatty"):
        return False
    if not stream.isatty():   # not being piped or redirected
        return allow_piping  # auto color only on TTYs
    try:
        import curses
        curses.setupterm()
        return curses.tigetnum("colors") > 2
    except:
        # guess false in case of error
        return False


# Has Color Init
has_colors = __has_colors(sys.stdout, True)


def printout(text, color=WHITE):
    """Print Color Text."""
    sys.stdout.write(colorText(text, color))


def colorText(text, color=WHITE):
    """Color Text."""
    if has_colors:
        return "\x1b[1;%dm" % (30 + color) + str(text) + "\x1b[0m"

    return text


def print_log(msg, print_date=True, print_hostname=True):
    """Print message with time and host."""
    if print_date:
        printout("[%s] " % datetime.now().replace(microsecond=0), WHITE)

    if print_hostname:
        printout("(%s) " % socket.getfqdn(), BLUE)

    print(msg)
    sys.stdout.flush()


def header(msg, max_width=80, print_date=False, print_hostname=False):
    """Print Header."""
    print_log('=' * max_width, print_date, print_hostname)
    print_log(msg, print_date, print_hostname)
    print_log('=' * max_width, print_date, print_hostname)


def print_color(msg, color=WHITE, print_date=True, print_hostname=True):
    """Print message with color prefix."""
    print_log(colorText(msg, color), print_date, print_hostname)


def print_color_prefix(prefix, color, msg, print_date=True, print_hostname=True):
    """Print message with color prefix."""
    print_log(colorText(prefix, color) + msg, print_date, print_hostname)


def info(msg, print_date=True, print_hostname=True):
    """Print Info Level."""
    print_color_prefix("INFO: ", YELLOW, msg, print_date, print_hostname)


def warn(msg, print_date=True, print_hostname=True):
    """Print Warning Level."""
    print_color_prefix("WARN: ", YELLOW, msg, print_date, print_hostname)


def error(msg, print_date=True, print_hostname=True):
    """Print Error Level."""
    print_color_prefix("ERROR: ", RED, msg, print_date, print_hostname)


def failed(msg, print_date=True, print_hostname=True):
    """Print Failed Level."""
    print_color_prefix("FAILED: ", RED, msg, print_date, print_hostname)


def verbose(msg, print_date=True, print_hostname=True):
    """Print Verbose Level."""
    print_color_prefix("VERBOSE: ", YELLOW, msg, print_date, print_hostname)


def debug(debug_object, print_date=True, print_hostname=True, print_data_type=True):
    """Print Debug Level."""
    if type(debug_object).__name__ == 'str':
        print_color_prefix("DEBUG: ", MAGENTA, debug_object, print_date, print_hostname)
    else:
        print_color_prefix("DEBUG: -", MAGENTA, '', print_date, print_hostname)
        if print_data_type:
            print_color(type(debug_object).__name__)
        print(debug_object)


def todo(msg, print_date=True, print_hostname=True):
    """Print TODO Level."""
    print_color_prefix("TODO: ", RED, msg, print_date, print_hostname)


def task(msg, print_date=True, print_hostname=True):
    """Print Task Level."""
    print_color_prefix("TASK: ", BLUE, msg, print_date, print_hostname)


def skipping(msg, print_date=True, print_hostname=True):
    """Print skipping Level."""
    print_color_prefix("SKIPPING: ", CYAN, msg, print_date, print_hostname)


def running(msg, print_date=True, print_hostname=True):
    """Print running Level."""
    print_color_prefix("RUNNING: ", GREEN, msg, print_date, print_hostname)
