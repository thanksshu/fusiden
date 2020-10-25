'''
log gf
'''
import atexit
import shlex
import subprocess

import fusiden

fusiden.GFControl.adbpath = "/home/thanksshu/Android/sdk/platform-tools/adb"
gf = fusiden.GFControl(device_id="39V4C19114019806")


def kill_subproc(subproc):
    """
    terminate a subproc
    """
    while subproc.poll() is None:
        subproc.kill()
        subproc.wait()
    return


# get time and pid
now = gf.get_time()
pid = gf.get_pid('com.sunborn.girlsfrontline.cn')
# adjust log buffer
cmd = f'{gf.adbpath} -s {gf.device_id} logcat -G 2m'
_ = subprocess.run(shlex.split(
    cmd), capture_output=True, check=True)
# start log subproc
cmd = (f'{gf.adbpath} -s {gf.device_id}'
       f' logcat -v raw -s Unity -T {shlex.quote(now)} --pid={pid}')
logcat_proc = subprocess.Popen(shlex.split(cmd),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE)
atexit.register(kill_subproc, logcat_proc)
# read log
pre_line = logcat_proc.stdout.readline()
while True:
    current_line = logcat_proc.stdout.readline()
    # check if needed
    if pre_line and b'DebugLogHandler' in current_line:
        current_log = pre_line.rstrip().decode('utf-8')
        # put log in queue
        print(current_log)
    pre_line = current_line
# terminate subproc
logcat_proc.kill()
