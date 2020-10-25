'''
android controling classes
'''
import atexit
import queue
import re
import shlex
import subprocess
import threading
from random import SystemRandom

from .utils import kill_subproc

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
        # make sure logcat is killed
        atexit.register(kill_subproc, popen)
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

    def tap(self, pos_x, pos_y, *args, radius=5, duration=50, delta=20, **kwargs):
        '''
        tap somewhere
        '''
        pos_x = pos_x + random.randint(-radius, radius)
        pos_y = pos_y + random.randint(-radius, radius)
        proc = self.swipe(pos_x, pos_y, pos_x, pos_y, radius=0,
                          duration=duration, delta=delta)
        return proc

    def swipe(self, pos_x_start, pos_y_start,  pos_x_end, pos_y_end, *args,
              radius=5, duration=200, delta=100, **kwargs):
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

    def tap_in(self, left_up_x, left_up_y, right_bottom_x, right_bottom_y, *args,
               duration=80, delta=15, **kwargs):
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

    def start_logcat(self, stop_event=threading.Event()):
        '''
        start logcat then put needed logcat in queue
        '''
        # get time and pid
        now = self.get_time()
        pid = self.get_pid('com.sunborn.girlsfrontline.cn')
        # clear and adjust log buffer
        cmd = f'{self.adbpath} -s {self.device_id} logcat -c'
        subprocess.run(shlex.split(cmd),
                       capture_output=True, check=True)
        cmd = f'{self.adbpath} -s {self.device_id} logcat -G 16m'
        subprocess.run(shlex.split(cmd),
                       capture_output=True, check=True)
        # start log subproc
        cmd = (f'{self.adbpath} -s {self.device_id}'
               f' logcat -v raw -s Unity -T {shlex.quote(now)} --pid={pid}')
        logcat_proc = subprocess.Popen(shlex.split(cmd),
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
        # make sure logcat will be killed
        atexit.register(kill_subproc, logcat_proc)
        # read log
        pre_line = logcat_proc.stdout.readline()
        while not stop_event.is_set():
            current_line = logcat_proc.stdout.readline()
            # check if needed
            if pre_line and b'DebugLogHandler' in current_line:
                current_log = pre_line.rstrip().decode('utf-8')
                # put log in queue
                self.logcat_queue.put(current_log)
            pre_line = current_line
        # kill subproc
        kill_subproc(logcat_proc)

    def run_task(self, task,
                 block_timeout=15, stop_event=threading.Event(),
                 *, arg=None):
        '''
        run a serials of task
        '''

        def exec_cond(cond_index):
            '''
            match log with a condition and do target
            '''
            nonlocal chain, task_index, task, re_result, timeout_target, stop_event

            # get condition
            cond = task[cond_index]

            # execute target
            if cond['target'] == 'pass':
                target = lambda *args, **kwargs: None
            else:
                target = cond['target']
            # pass in task(chain) info to perform chain, task, condition change
            target_result = target(
                arg={'chain': chain, 'task_index': task_index, 'task': task,
                     'condition_index': cond_index, 'match_result': re_result}
            )
            # change timeout target
            timeout_target = target_result if target_result else target

            # load next task
            # case
            if cond['type'] == 'case':
                exec_cond(cond_index+1)
                return
            # break_case or default
            if cond['type'] == 'default' or cond['type'] == 'break_case':
                # stop task
                if cond['next'] is None:
                    stop_event.set()
                    return

                # shorthand of ['absol', int] chain not changed
                if isinstance(cond['next'], int):
                    cond['next'] = ['absol', cond['next']]
                # shorthand of ['relev', 1|-1|0] chain not changed
                if isinstance(cond['next'], str):
                    if cond['next'] == 'next':
                        cond['next'] = ['relev', 1]
                    elif cond['next'] == 'pre':
                        cond['next'] = ['relev', -1]
                    elif cond['next'] == 'self':
                        cond['next'] = ['relev', 0]
                    else:
                        raise ValueError(
                            '\'next\' value must be \'next\', \'pre\' or \'self\'')

                # task and chain changement
                if isinstance(cond['next'], list):
                    # independent task, no chain and task_index
                    if isinstance(cond['next'][0], dict):
                        task = cond['next']
                        chain = None
                        task_index = None
                    # chained task, must be in chain
                    else:
                        # task index change only
                        if isinstance(cond['next'][0], str):
                            if cond['next'][0] == 'relev':
                                task_index += cond['next'][1]
                            elif cond['next'][0] == 'absol':
                                task_index = cond['next'][1]
                            else:
                                raise ValueError(
                                    'in chain change reference must be \'relev\' or \'absol\'')
                        # chain changement
                        elif isinstance(cond['next'][0], list):
                            chain = cond['next'][0]
                            task_index = cond['next'][1]
                        else:
                            raise TypeError('type must be list or str')

                        # set current task
                        task = chain[task_index]
                    return
                raise TypeError('type of\'next\' must be str, int or list')
            # throw value error
            raise ValueError(
                '\'type\'value must be \'case\', \'break_case\' or \'default\'')

        # declare event to stop logcat
        logcat_stop_event = threading.Event()
        # launch the thread
        store_log_thread = threading.Thread(
            target=self.start_logcat, args=(logcat_stop_event,),
            name='logcat', daemon=True)
        store_log_thread.start()

        # init chain, task
        if isinstance(task[0], list):
            # passed in a task chain
            chain = task[0]
            task_index = task[1]
            task = chain[task_index]
        elif isinstance(task[0], dict):
            # passed in a task
            chain = list()
            task_index = int()

        # start task
        timeout_target = lambda *args, **kwargs: None
        re_result = None
        while not stop_event.is_set():
            # reset log
            log = ''
            # match each condition
            for (cond_index, cond) in enumerate(task):
                # default
                if cond['type'] == 'default':
                    exec_cond(cond_index)
                    break
                # case or break case
                try:
                    if not log:
                        log = self.logcat_queue.get(
                            block=True, timeout=block_timeout)
                except queue.Empty:
                    timeout_target()
                    break
                else:
                    # match log
                    re_result = re.match(cond['match'], log)
                    if re_result:
                        exec_cond(cond_index)
                        break

        # stop logcat thread
        logcat_stop_event.set()
        return chain, task_index, task