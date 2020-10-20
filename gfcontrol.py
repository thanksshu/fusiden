'''
control girlsfrontline
'''
import queue
import re
import shlex
import subprocess
import threading
from random import SystemRandom

random = SystemRandom()


class AndroidControl():
    '''
    class for controling GirlsFrontline
    '''

    adbpath = 'adb'

    @classmethod
    def list_device(cls):
        '''
        list attached devices
        '''
        cmd = f'{cls.adbpath} devices'
        proc = subprocess.run(shlex.split(cmd),
                              capture_output=True, check=True)
        result = proc.stdout.splitlines()[1:-1]
        device = list()
        for id_device in result:
            device.append(id_device.decode('utf-8').rsplit())
        return device

    def __init__(self, device_index=0, device_id=None):
        '''
        specify a device
        '''
        if device_id:
            self.device_id = device_id
        else:
            self.device_id = self.list_device()[device_index][0]

    @property
    def is_alive(self):
        '''
        check adb connection, return False when dead
        '''
        proc = self.shell(':')
        proc.communicate()
        if proc.returncode != 0:
            return False
        return True

    def shell(self, command, **kwarg):
        '''
        send shell command
        '''
        args = shlex.split(
            f'{self.adbpath} -s {self.device_id} shell {command}')
        print(args)
        popen = subprocess.Popen(args,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, **kwarg)
        return popen

    def get_time(self):
        '''
        get current phone time
        '''
        sub_cmd = shlex.quote('$(date +\'%Y-%m-%d %H:%M:%S.000\')')
        cmd = f'{self.adbpath} -s {self.device_id} shell echo {sub_cmd}'
        result = subprocess.run(shlex.split(
            cmd), capture_output=True, check=True)
        return result.stdout.rstrip().decode('utf-8')

    def get_pid(self, package_name):
        '''
        return pid of a application
        '''
        cmd = f'{self.adbpath} -s {self.device_id} shell pidof -s {package_name}'
        result = subprocess.run(shlex.split(
            cmd), capture_output=True, check=True)
        return result.stdout.rstrip().decode('utf-8')

    def tap(self, pos_x, pos_y, radius=5, duration=50, delta=20):
        '''
        tap somewhere
        '''
        pos_x = pos_x + random.randint(-radius, radius)
        pos_y = pos_y + random.randint(-radius, radius)
        proc = self.swipe(pos_x, pos_y, pos_x, pos_y, radius=0,
                          duration=duration, delta=delta)
        return proc

    def swipe(self, pos_x_start, pos_y_start,  pos_x_end, pos_y_end,
              radius=5, duration=200, delta=100):
        '''
        swipe
        '''
        pos_x_start = pos_x_start + random.randint(-radius, radius)
        pos_x_end = pos_x_end + random.randint(-radius, radius)
        pos_y_start = pos_y_start + random.randint(-radius, radius)
        pos_y_end = pos_y_end + random.randint(-radius, radius)
        duration = duration + random.randint(-delta, delta)

        cmd = (f'{self.adbpath} -s {self.device_id} shell input swipe '
               f'{pos_x_start} {pos_y_start} {pos_x_end} {pos_y_end} {duration}')
        proc = subprocess.run(shlex.split(
            cmd), capture_output=True, check=True)
        return proc

    def tap_in(self, left_up_x, left_up_y, right_bottom_x, right_bottom_y,
               duration=80, delta=15):
        '''
        tap somewhere in a square
        '''
        pos_x = random.randint(left_up_x, right_bottom_x)
        pos_y = random.randint(left_up_y, right_bottom_y)

        proc = self.tap(pos_x, pos_y, radius=0,
                        duration=duration, delta=delta)
        return proc


class GFControl(AndroidControl):
    '''
    class for controling girlsfrontline
    '''

    def __init__(self, device_index=0, device_id=None):
        super().__init__(device_index=device_index, device_id=device_id)
        self.logcat_queue = queue.Queue()

    def run_task(self, task, block_timeout=15):
        '''
        run a serials of task
        '''

        def start_logcat_thread():
            '''
            start logcat thread
            '''
            nonlocal self, stop_logcat_event

            def _start_logcat():
                '''
                put needed logcat in queue
                '''
                nonlocal self, stop_logcat_event
                # get time and pid
                now = self.get_time()
                pid = self.get_pid('com.sunborn.girlsfrontline.cn')
                # adjust log buffer
                cmd = f'{self.adbpath} -s {self.device_id} logcat -G 2m'
                _ = subprocess.run(shlex.split(
                    cmd), capture_output=True, check=True)
                # start log subproc
                cmd = (f'{self.adbpath} -s {self.device_id}'
                       f' logcat -v raw -s Unity -T {shlex.quote(now)} --pid={pid}')
                logcat_proc = subprocess.Popen(shlex.split(cmd),
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               stdin=subprocess.PIPE)
                # read log
                pre_line = logcat_proc.stdout.readline()
                while not stop_logcat_event.is_set():
                    current_line = logcat_proc.stdout.readline()
                    # check if needed
                    if pre_line and b'DebugLogHandler' in current_line:
                        current_log = pre_line.rstrip().decode('utf-8')
                        # put log in queue
                        self.logcat_queue.put(current_log)
                    pre_line = current_line
                # terminate subproc
                logcat_proc.terminate()
                return

            # launch the thread
            store_log_thread = threading.Thread(
                target=_start_logcat, name='store_logcat', daemon=True)
            store_log_thread.start()

            return

        def exec_cond(cond_index):
            '''
            match log with a condition and do target
            '''
            nonlocal chain, task_index, task, log, re_result, pre_target
            cond = task[cond_index]

            # execute target
            if cond['target'] == 'pass':
                target = lambda *arg: None
            else:
                target = cond['target']
            target((chain, task_index, task, log, re_result, pre_target))
            pre_target = target

            # load next task
            # case or break_case
            if cond['type'] == 'case':
                exec_cond(cond_index+1)
                return
            elif cond['type'] == 'default' or cond['type'] == 'break_case':
                # independent task
                if isinstance(cond['next'], list):
                    task = cond['next']
                    return
                # task in chain
                # int: absolut task index
                if isinstance(cond['next'], int):
                    task_index = cond['next']
                # str: next pre or self
                elif isinstance(cond['next'], str):
                    if cond['next'] == 'next':
                        task_index += 1
                    elif cond['next'] == 'pre':
                        task_index -= 1
                    elif cond['next'] == 'self':
                        pass  # index not changed
                    else:
                        raise ValueError(
                            'value must be \'next\', \'pre\' or \'self\'')
                # change chain or relevent task index
                elif isinstance(cond['next'], tuple):
                    # chain changement
                    if isinstance(cond['next'][0], list):
                        chain = cond['next'][0]
                        task_index = cond['next'][1]
                    # relevent task index
                    elif isinstance(cond['next'][0], str):
                        if cond['next'] == 'next':
                            task_index += cond['next'][1]
                        elif cond['next'] == 'pre':
                            task_index -= cond['next'][1]
                        else:
                            raise ValueError(
                                'value must be \'next\', \'pre\' or \'self\'')
                    else:
                        raise TypeError('type must be list or str')
                task = chain[task_index]
                return
            raise ValueError(
                'value must be \'case\', \'break_case\' or \'default\'')

        # start logcat thread
        stop_logcat_event = threading.Event()
        start_logcat_thread()

        # init chain, task
        if isinstance(task, tuple):
            chain = task[0]
            task_index = task[1]
            task = chain[task_index]
        else:
            chain = list()
            task_index = int()

        # start task
        pre_target = lambda *arg: None
        while True:
            log = ''
            # match each condition
            for (cond_index, cond) in enumerate(task):
                # default
                if cond['type'] == 'default':
                    exec_cond(cond_index)
                    break
                # case or break case
                # extern match
                if (callable(cond['match'])
                        and cond['match']((chain, task_index, cond_index, log))):
                    exec_cond(cond_index)
                    break
                # match log
                if isinstance(cond['match'], str):
                    try:
                        if not log:
                            log = self.logcat_queue.get(
                                block=True, timeout=block_timeout)
                    except queue.Empty:
                        pre_target()
                        break
                    else:
                        re_result = re.match(cond['match'], log)
                        if re_result:
                            exec_cond(cond_index)
                            break

        # stop logcat thread
        stop_logcat_event.set()
        return
