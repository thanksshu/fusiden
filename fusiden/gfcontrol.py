'''
android controling classes
'''
import atexit
import queue
import re
import shlex
import socket
import subprocess
import threading
from random import SystemRandom

from . import utils

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
        if device_id is not None:
            self.device_id = device_id
        else:
            self.device_id = self.list_device()[device_index][0]

        self.monkey_port = None
        self.monkey_socket = None

    def start_monkey(self, monkey_port=5556, timeout=0.2):
        '''
        start monkey
        '''
        # kill existing monkey
        self.stop_monkey()
        self.monkey_port = monkey_port

        # forward port
        cmd = (f'{self.adbpath} -s {self.device_id} '
               f'forward tcp:{self.monkey_port} tcp:{self.monkey_port}')
        subprocess.run(shlex.split(
            cmd), capture_output=True, check=True)

        # start monkey subproc
        popen = self.adb(f'shell monkey --port {self.monkey_port}')
        while True:
            line = popen.stderr.readline()
            if b'data=' in line:
                break
        popen.kill()

        # start monkey tcp connection
        while True:
            self.monkey_socket = socket.create_connection(
                ('localhost', self.monkey_port), timeout)
            if self.monkey('sleep 0') != '':
                break
            self.monkey_socket.close()

        # make sure all monkey related is stopped
        atexit.register(self.stop_monkey)

    def stop_monkey(self):
        '''
        stop monkey
        '''
        if self.monkey_socket is not None:
            # stop monkey
            self.monkey('quit')

            # close socket
            self.monkey_socket.close()
            self.monkey_socket = None

        # kill monkey
        monkey_pid = self.get_pid('com.android.commands.monkey')
        if monkey_pid is not None:
            kill_cmd = (f'{self.adbpath} -s {self.device_id} '
                        f'shell kill {monkey_pid}')
            try:
                subprocess.run(shlex.split(
                    kill_cmd), capture_output=True, check=True)
            except subprocess.CalledProcessError:
                # already killed
                pass

        # remove forward port
        cmd = (f'{self.adbpath} -s {self.device_id} '
               f'forward --remove tcp:{self.monkey_port}')
        try:
            subprocess.run(shlex.split(cmd), capture_output=True, check=True)
        except subprocess.CalledProcessError:
            # no port forward
            pass

    def monkey(self, cmd):
        """
        send cmd to monkey
        """
        self.monkey_socket.sendall(bytes(cmd, 'utf-8') + b'\n')
        return self.monkey_socket.recv(32).rstrip().decode('utf-8')

    @property
    def is_alive(self):
        '''
        check adb connection, return False when dead
        '''
        proc = self.adb('shell :')
        proc.communicate()
        if proc.returncode != 0:
            return False
        return True

    def adb(self, command, **kwarg):
        '''
        send shell command
        '''
        args = shlex.split(
            f'{self.adbpath} -s {self.device_id} {command}')
        popen = subprocess.Popen(args,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, **kwarg)
        # make sure logcat is killed
        atexit.register(utils.kill_subproc, popen)
        return popen

    def get_time(self):
        '''
        get current phone time
        '''
        sub_cmd = shlex.quote('$(date +\'%Y-%m-%d %H:%M:%S.000\')')
        cmd = f'{self.adbpath} -s {self.device_id} shell echo {sub_cmd}'
        result = subprocess.run(shlex.split(cmd),
                                capture_output=True, check=True)
        return result.stdout.rstrip().decode('utf-8')

    def get_pid(self, package_name):
        '''
        return pid of a application
        '''
        cmd = f'{self.adbpath} -s {self.device_id} shell pidof -s {package_name}'
        try:
            result = subprocess.run(shlex.split(cmd),
                                    capture_output=True, check=True)
        except subprocess.CalledProcessError:
            pid = None
        else:
            pid = int(result.stdout.rstrip().decode('utf-8'))
        return pid

    def swipe(self, pos_start, pos_end,
              radius=5, step_duration=5, duration=200, delta=100, *, task_info=None):
        '''
        swipe with monkey
        '''
        pos_start = [pos_start[0] + random.randint(-radius, radius),
                     pos_start[1] + random.randint(-radius, radius)]
        pos_end = [pos_end[0] + random.randint(-radius, radius),
                   pos_end[1] + random.randint(-radius, radius)]
        total_length = [pos_end[0] - pos_start[0], pos_end[1] - pos_start[1]]
        duration = duration + random.randint(-delta, delta)
        step_count = duration / step_duration

        # swipe with move speed linear slow down to zero
        pre_speed = [2 * total_length[0] / duration,
                     2 * total_length[1] / duration]
        delta_speed = [pre_speed[0] / step_count, pre_speed[1] / step_count]
        curr_speed = [pre_speed[0] - delta_speed[0],
                      pre_speed[1] - delta_speed[1]]
        next_pos = [pos_start[0], pos_start[1]]
        self.monkey(f'touch down {pos_start[0]} {pos_start[1]}')
        for _ in range(round(step_count)):
            # lenth of this step
            step_length = [(pre_speed[0] + curr_speed[0]) * step_duration / 2,
                           (pre_speed[1] + curr_speed[1]) * step_duration / 2]
            pre_speed = curr_speed
            # slow down
            curr_speed = [pre_speed[0] - delta_speed[0],
                          pre_speed[1] - delta_speed[1]]
            next_pos = [next_pos[0] + step_length[0],
                        next_pos[1] + step_length[1]]
            self.monkey(f'sleep {step_duration}')
            # use int() to make the value closer to zero
            self.monkey(
                f'touch move {int(next_pos[0])} {int(next_pos[1])}')

        # try to prevent slide
        for _ in range(round(1000 / step_count)):
            self.monkey(f'sleep {step_duration}')
            self.monkey(f'touch move {pos_end[0]} {pos_end[1]}')
        self.monkey(f'touch up {pos_end[0]} {pos_end[1]}')

    def tap(self, pos, radius=5, duration=50, delta=20, *, task_info=None):
        '''
        tap somewhere
        '''
        pos = [pos[0] + random.randint(-radius, radius),
               pos[1] + random.randint(-radius, radius)]
        duration = duration + random.randint(-delta, delta)
        self.monkey(f'touch down {pos[0]} {pos[1]}')
        self.monkey(f'sleep {duration}')
        self.monkey(f'touch up {pos[0]} {pos[1]}')

    def tap_in(self, left_up, right_bottom, duration=80, delta=15, *, task_info=None):
        '''
        tap somewhere in a square
        '''
        pos = [random.randint(left_up[0], right_bottom[0]),
               random.randint(left_up[1], right_bottom[1])]

        self.tap(pos, radius=0,
                 duration=duration, delta=delta)


class GFControl(AndroidControl):
    '''
    class for controling girlsfrontline
    '''

    def __init__(self, device_index=0, device_id=None):
        super().__init__(device_index=device_index,
                         device_id=device_id)
        self.logcat_queue = queue.Queue()
        self.logcat_proc = None
        # TODO: use thread pool
        self.store_log_thread = threading.Thread(
            target=self.store_log,
            name='store_log',
            daemon=True)

    def start_logcat(self, *, task_info=None):
        '''
        start logcat then put needed logcat in queue
        '''
        # stop current running subproc
        self.stop_logcat()
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
        # start logcat subproc
        self.logcat_proc = self.adb(
            f' logcat -v raw -s Unity -T {shlex.quote(now)} --pid={pid}')
        # make sure logcat will be killed

    def stop_logcat(self, *, task_info=None):
        '''
        start logcat then put needed logcat in queue
        '''
        if self.logcat_proc is not None:
            utils.kill_subproc(self.logcat_proc)
            self.logcat_proc = None

    def store_log(self, stop_event=threading.Event(), *, task_info=None):
        """
        store log in queue
        """
        # read log
        pre_line = self.logcat_proc.stdout.readline()
        while not stop_event.is_set():
            try:
                current_line = self.logcat_proc.stdout.readline()
            except AttributeError:
                # logcat subproc killed
                stop_event.set()
            # check if needed
            if pre_line and b'DebugLogHandler' in current_line:
                current_log = pre_line.rstrip().decode('utf-8')
                # put log in queue
                self.logcat_queue.put(current_log)
            pre_line = current_line

    def run_task(self, task, block_timeout=8, queue_get_time=0.2, stop_event=threading.Event(),
                 *, task_info=None):
        '''
        run a serials of task
        '''

        def exec_cond(cond_index):
            '''
            match log with a condition and do target
            '''
            nonlocal chain, task_index, task, re_result, stop_event
            nonlocal timeout_target, next_block_timeout, block_timeout

            # get condition
            cond = task[cond_index]

            # execute target
            if cond['target'] == 'pass':
                target = lambda *args, **kwargs: None
            else:
                target = cond['target']
            # pass in task(chain) info to perform chain, task, condition change
            target_result = target(
                task_info={'chain': chain, 'task_index': task_index, 'task': task,
                           'condition_index': cond_index, 'match_result': re_result}
            )
            # change timeout target
            timeout_target = target_result[0] if target_result and target_result[0] else target
            if target_result and target_result[1]:
                next_block_timeout = target_result[1]
            else:
                next_block_timeout = block_timeout

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
                raise TypeError('type of \'next\' must be str, int or list')
            # throw value error
            raise ValueError(
                '\'type\'value must be \'case\', \'break_case\' or \'default\'')

        # start log thread
        self.start_logcat()
        self.store_log_thread.start()

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

        timeout_target = lambda *args, **kwargs: None
        re_result = None
        next_block_timeout = block_timeout
        # run task
        timer = utils.Timer()
        while not stop_event.is_set():
            # reset log
            log = ''
            # match each condition
            for (cond_index, cond) in enumerate(task):
                # default
                if cond['type'] == 'default':
                    timer.reset()
                    exec_cond(cond_index)
                    break
                # case or break case
                try:
                    # pick a log for this task
                    if not log:
                        log = self.logcat_queue.get(
                            block=True, timeout=queue_get_time)
                        timer.reset()
                        self.logcat_queue.task_done()
                except queue.Empty:
                    # get failed, do something after timeout
                    timer.start()
                    if timer.check() >= next_block_timeout - queue_get_time:
                        timer.reset()
                        timeout_target()
                    break
                else:
                    # match log
                    re_result = re.match(cond['match'], log)
                    if re_result:
                        timer.reset()
                        exec_cond(cond_index)
                        break

        # stop logcat proc and store log thread
        self.stop_logcat()
        self.store_log_thread.join()
