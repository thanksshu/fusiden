'''
log gf
'''
import atexit
import shlex
import subprocess

ID = '39V4C19114019806'
ADB = '/home/thanksshu/Android/sdk/platform-tools/adb'


def kill_subproc(popen):
    """
    kill a subproc
    """
    while popen.poll() is None:
        popen.kill()
        popen.wait()


# get time and pid
DATE = shlex.quote('$(date +\'%Y-%m-%d %H:%M:%S.000\')')
args = shlex.split(f'{ADB} -s {ID} shell echo {DATE}')
time = subprocess.run(args, capture_output=True,
                      check=True).stdout.rstrip().decode('utf-8')

args = shlex.split(
    f'{ADB} -s {ID} shell pidof -s com.sunborn.girlsfrontline.cn')
pid = subprocess.run(args, capture_output=True,
                     check=True).stdout.rstrip().decode('utf-8')


# clear and adjust log buffer
subprocess.run(shlex.split(f'{ADB} -s {ID} logcat -c'), capture_output=True,
               check=True)
subprocess.run(shlex.split(f'{ADB} -s {ID} logcat -G 16m'), capture_output=True,
               check=True)
# start logcat subproc
args = shlex.split(
    f'{ADB} -s {ID} logcat -v raw -s Unity -T {shlex.quote(time)} --pid={pid}')
logcat_proc = subprocess.Popen(args, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
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
