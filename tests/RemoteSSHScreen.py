
"""SSH Class Test."""

import log

from SSHScreen import SSHScreen
from SSH import SSH

ssh = SSH('127.0.0.1', 'vagrant')
ssh.port = 2222
ssh.key_file_path = '~/.vagrant.d/insecure_private_key'

# stdout, stderr = ssh.run_command('hostname', False)
# print(stdout
#
# ssh.run_command('ls -lha')

remoteScreen = SSHScreen(ssh)

log.header('install')
print(remoteScreen.install())

log.header('installed')
print(remoteScreen.installed())

remoteScreen.kill_all_screens()

log.header('create')
print(remoteScreen.exists())
print(remoteScreen.create())
print(remoteScreen._id)
print(remoteScreen._screens)

print(remoteScreen.exists())
remoteScreen.log_enable(turn_on=False)
remoteScreen.log_flush(1)
remoteScreen.log_timestamp()
remoteScreen.log_on()
# remoteScreen.command('bash')
# remoteScreen.set_prompt()
remoteScreen.command('echo "TEST"')
remoteScreen.command('ls -lha')

remoteScreen.command('htop', 10)
remoteScreen._screen_key('function_key_5')
# remoteScreen._screen_key('function_key_10')
# remoteScreen.command('clear')

# remoteScreen.attach()

# remoteScreen.tail_log() # NOTE: Can broke the console as it's a binary
# file with escaped chars, etc.

# remoteScreen.log_disable(True)
remoteScreen.log_disable()

# remoteScreen.kill()

log.header('get_screens')
print(remoteScreen.get_screens())

log.header('list_screens')
remoteScreen.list_screens()

# log.header('kill_all_screens')
# remoteScreen.kill_all_screens()

# log.header('list_screens')
# remoteScreen.list_screens()
