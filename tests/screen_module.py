# -*- coding:utf-8 -*-

"""Screen module."""

from screenutils import list_screens, Screen
import time

# kill known open screens
screens = list_screens()
print(screens)
for screen in screens:
    print(screen.name)
    if screen.name in ['session1', 'session2']:
        screen.kill()

# s1
session_Name = 'session1'
s1 = Screen(session_Name, True)

if not s1.exists:
    raise RuntimeError("ERROR: Session not started: %s" % session_Name)

time.sleep(5000)
# funky prompts could reduce log visibility. Use sh or bash for best results
s1.send_commands('bash')
s1.enable_logs()
s1.send_commands("df")
print(next(s1.logs))

s1.disable_logs()

# s1 = None
# s1 = Screen("session1")
# s1.exists

s1.kill()

# s2
s2 = Screen("session2")
s2.exists
s2.initialize()
s2.exists

print(list_screens())

s2.kill()
