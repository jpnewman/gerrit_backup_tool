
"""Remote Screen Module."""

import re

import log

from time import sleep


SCREEN_KEYS = {
    'cursor_up': 'stuff \\033[A',
    'cursor_down': 'stuff \\033[B',
    'cursor_right': 'stuff \\033[C',
    'cursor_left': 'stuff \\033[D',
    'function_key_0': 'stuff \\033[10~',
    'function_key_1': 'stuff \\033OP',
    'function_key_2': 'stuff \\033OQ',
    'function_key_3': 'stuff \\033OR',
    'function_key_4': 'stuff \\033OS',
    'function_key_5': 'stuff \\033[15~',
    'function_key_6': 'stuff \\033[17~',
    'function_key_7': 'stuff \\033[18~',
    'function_key_8': 'stuff \\033[19~',
    'function_key_9': 'stuff \\033[20~',
    'function_key_10': 'stuff \\033[21~',
    'function_key_11': 'stuff \\033[23~',
    'function_key_12': 'stuff \\033[24~',
    'home': 'stuff \\033[1~',
    'end': 'stuff \\033[4~',
    'insert': 'stuff \\033[2~',
    'delete': 'stuff \\033[3~',
    'page_up': 'stuff \\033[5~',
    'page_down': 'stuff \\033[6~',
    'keypad_0': 'stuff 0',
    'keypad_1': 'stuff 1',
    'keypad_2': 'stuff 2',
    'keypad_3': 'stuff 3',
    'keypad_4': 'stuff 4',
    'keypad_5': 'stuff 5',
    'keypad_6': 'stuff 6',
    'keypad_7': 'stuff 7',
    'keypad_8': 'stuff 8',
    'keypad_9': 'stuff 9',
    'keypad_plus': 'stuff +',
    'keypad_minus': 'stuff -',
    'keypad_asterisk': 'stuff *',
    'keypad_slash': 'stuff /',
    'keypad_equals': 'stuff =',
    'keypad_dot': 'stuff .',
    'keypad_comma': 'stuff ,',
    'keypad_enter': 'stuff \\015'
}


class SSHScreen(object):
    """Remote SSH Screen."""

    def __init__(self, ssh, screen_name='remote_screen'):
        """Init Function. Take ssh class object."""
        super(SSHScreen, self).__init__()
        self.ssh = ssh
        self.name = screen_name
        self._id = ''
        self._screens = {}
        self._log_filename = ''
        self._pause_between_commands = 0.05

        self.verbose = False

    def _run_remote_command_clean_stderr(self, cmd):
        """Run remote command."""
        stdout, stderr = self.ssh.run_command(cmd)

        if not stdout:
            return False

        return True

    def install(self):
        """Test if screen is installed on the remote host."""
        if self.installed():
            log.info("screen already installed.")
            return True

        return self._run_remote_command_clean_stderr('sudo apt-get install screen')

    def installed(self):
        """Test if screen is installed on the remote host."""
        return self._run_remote_command_clean_stderr('sudo dpkg --get-selections | grep "^screen[[:space:]]*install$"')

    def create(self):
        """Create remote screen."""
        screen1 = self.get_screens()

        self.ssh.run_command('screen -dmU ' + self.name)

        screen2 = self.get_screens()

        for screen in screen1:
            if screen in screen2:
                del screen2[screen]

        if len(screen2) == 1:
            self._id = screen2.keys()[0]
        else:
            log.info("Unable to determine ")

        self._screens.update(screen2)

        return screen2

    def attach(self):
        """Attach to screen."""
        # return self.ssh.run_command("screen -rU " + self._id)
        pass  # TODO: Implement interactive ssh

    def detach(self):
        """Attach to screen."""
        self.ssh.run_command("screen -d " + self._id)

    def _screen_command(self, cmd):
        """Run screen command."""
        self.ssh.run_command('screen -x ' + self._id + ' -X ' + cmd)

    # https://www.gnu.org/software/screen/manual/screen.html#Input-Translation
    def _screen_key(self, key='keypad_enter', pause=None):
        """Send key to screen."""
        if not pause:
            pause = self._pause_between_commands

        key = key.lower()
        if key not in SCREEN_KEYS:
            log.error("Key not defined.")
            return

        self.ssh.run_command('screen -x ' + self._id + ' -X eval "' + SCREEN_KEYS[key] + '"')
        sleep(pause)

    def command(self, cmd, stuff=True, press_enter=True, pause=None):
        """Stuff screen command."""
        if not pause:
            pause = self._pause_between_commands

        stuff_cmd = ''

        if stuff:
            stuff_cmd = 'stuff '

        self.ssh.run_command('screen -x ' + self._id + ' -X ' + stuff_cmd + cmd)
        sleep(pause)

        if press_enter:
            self._screen_key()

    def screen_command(self, cmd, stuff=True, press_enter=True):
        """Run screen command."""
        self.command(cmd, stuff=False, press_enter=False)

    def set_prompt(self, prompt="PS1=\\'\\u@\\h(${STY}:${WINDOW}):\w$ \\'"):
        """Set bash prompt."""
        self.command(prompt)

    def exists(self):
        """Check if screen exists on remote."""
        if not self._id:
            log.warn("Screen not created.")
            return False

        screens = self.get_screens()

        if self._id in screens.keys():
            return True

        return False

    def _parse_screen_ls_output(self, output):
        """Parse screen ls output."""
        screens = {}
        for line in output.split('\n'):
            if re.search('^\t', line) is None:
                continue

            screen = line.strip().split('\t')
            screens[screen[0]] = {
                'time': screen[1].strip('()'),
                'state': screen[2].strip('()')
            }
        return screens

    def get_screens(self):
        """Get all screens."""
        stdout, stderr = self.ssh.run_command('screen -ls')

        return self._parse_screen_ls_output(stdout)

    def list_screens(self):
        """List all screens."""
        self.ssh.run_command('screen -ls')

    def log_enable(self, log_filename=None, turn_on=True):
        """Enable log."""
        if not log_filename:
            log_filename = self._id + '.log'

        self._log_filename = log_filename
        self.screen_command("logfile " + self._log_filename)

        if turn_on:
            self.log_on()

    def log_on(self):
        """Turn on log."""
        self.screen_command("log on", False)

    def log_flush(self, delay=10):
        """Flush log."""
        self.screen_command("logfile flush %d" % delay)

    def log_timestamp(self, after=10):
        """Timestamp log."""
        self.screen_command("logtstamp on")
        self.screen_command("logtstamp after %d" % after)

    def log_disable(self, delete_log=False):
        """Disable log."""
        self.screen_command("log off")

        if delete_log:
            self.ssh.run_command("rm " + self._log_filename)

        self._log_filename = ''

    def tail_log(self):
        """Tail log."""
        if not self._log_filename:
            log.warn("Log not enabled.")
            return False

        self.ssh.run_command("tail " + self._log_filename)

    def kill(self):
        """Kill screens."""
        self.screen_command('quit')

    def kill_all_screens(self):
        """Kill all screens."""
        self.ssh.run_command('killall screen')
        self._id = ''
        self._screens = {}
