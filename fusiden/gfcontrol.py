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

    def __init__(self, device_index=0, device_id=None, monkey_port=5556):
        '''
        specify a device
        '''
        if device_id is not None:
            self.device_id = device_id
        else:
            self.device_id = self.list_device()[device_index][0]

        self.monkey_port = monkey_port
        self.monkey = None

    def start_monkey(self):
        '''
        start monkey
        '''
        # kill existing monkey
        self.stop_monkey()

        # forward port
        cmd = (f'{self.adbpath} -s {self.device_id} '
               f'forward tcp:{self.monkey_port} tcp:{self.monkey_port}')
        subprocess.run(shlex.split(
            cmd), capture_output=True, check=True)

        # start monkey subproc
        popen = self.adb(f'shell monkey --port {self.monkey_port}')
        while True:
            line = popen.stderr.readline()
            if line == b'data="5556"\n':
                break
        popen.kill()

        # start monkey tcp connection
        self.monkey = socket.create_connection(
            ('localhost', self.monkey_port), 100)
        while self.send_monkey('sleep 0') == '':
            self.monkey.close()
            self.monkey = socket.create_connection(
                ('localhost', self.monkey_port))

        # make sure all monkey related is stopped
        atexit.register(self.stop_monkey)

    def stop_monkey(self):
        '''
        stop monkey
        '''
        if self.monkey is not None:
            # stop monkey
            self.send_monkey('quit')

            # close socket
            self.monkey.close()
            self.monkey = None

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

    def send_monkey(self, cmd):
        """
        send cmd to monkey
        """
        self.monkey.sendall(bytes(cmd, 'utf-8') + b'\n')
        return self.monkey.recv(32).decode('utf-8')

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

    def adb_swipe(self, pos_x_start, pos_y_start,  pos_x_end, pos_y_end,
                  radius=5, duration=200, delta=100, *, arg=None):
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
        subprocess.run(shlex.split(cmd),
                       capture_output=True, check=True)

    def adb_tap(self, pos_x, pos_y, radius=5, duration=50, delta=20, *, arg=None):
        '''
        tap somewhere
        '''
        pos_x = pos_x + random.randint(-radius, radius)
        pos_y = pos_y + random.randint(-radius, radius)
        self.adb_swipe(pos_x, pos_y, pos_x, pos_y, radius=0,
                       duration=duration, delta=delta)

    def adb_tap_in(self, left_up_x, left_up_y, right_bottom_x, right_bottom_y,
                   duration=80, delta=15, *, arg=None):
        '''
        tap somewhere in a square
        '''
        pos_x = random.randint(left_up_x, right_bottom_x)
        pos_y = random.randint(left_up_y, right_bottom_y)

        self.adb_tap(pos_x, pos_y, radius=0,
                     duration=duration, delta=delta)

    def monkey_swipe(self, pos_start, pos_end,
                     radius=5, step_duration=5, duration=200, delta=100, *, arg=None):
        '''
        swipe with monkey
        '''
        # prevent swipe too fast
        self.send_monkey('sleep 200')

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
        self.send_monkey(f'touch down {pos_start[0]} {pos_start[1]}')
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
            self.send_monkey(f'sleep {step_duration}')
            # use int() to make the value closer to zero
            self.send_monkey(
                f'touch move {int(next_pos[0])} {int(next_pos[1])}')

        # try to prevent slide
        for _ in range(round(1000 / step_count)):
            self.send_monkey(f'sleep {step_duration}')
            self.send_monkey(f'touch move {pos_end[0]} {pos_end[1]}')
        self.send_monkey(f'touch up {pos_end[0]} {pos_end[1]}')

    def monkey_tap(self, pos, radius=5, duration=50, delta=20, *, arg=None):
        '''
        tap somewhere
        '''
        # prevent from tap too fast
        self.send_monkey('sleep 100')

        pos = [pos[0] + random.randint(-radius, radius),
               pos[1] + random.randint(-radius, radius)]
        duration = duration + random.randint(-delta, delta)
        self.send_monkey(f'touch down {pos[0]} {pos[1]}')
        self.send_monkey(f'sleep {duration}')
        self.send_monkey(f'touch up {pos[0]} {pos[1]}')

    def monkey_tap_in(self, left_up, right_bottom, duration=80, delta=15, *, arg=None):
        '''
        tap somewhere in a square
        '''
        pos = [random.randint(left_up[0], right_bottom[0]),
               random.randint(left_up[1], right_bottom[1])]

        self.monkey_tap(pos, radius=0,
                        duration=duration, delta=delta)


class GFControl(AndroidControl):
    '''
    class for controling girlsfrontline
    '''

    def __init__(self, device_index=0, device_id=None, monkey_port=5556):
        super().__init__(device_index=device_index,
                         device_id=device_id,
                         monkey_port=monkey_port)
        self.logcat_queue = queue.Queue()
        self.logcat_proc = None

    def _start_logcat(self, *, arg=None):
        '''
        start logcat then put needed logcat in queue
        '''
        # stop current running subproc
        self._stop_logcat()
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

    def _stop_logcat(self, *, arg=None):
        '''
        start logcat then put needed logcat in queue
        '''
        if self.logcat_proc is not None:
            utils.kill_subproc(self.logcat_proc)
            self.logcat_proc = None

    def _store_log(self, stop_event=threading.Event(), *, arg=None):
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

    def run_task(self, task, block_timeout=15, stop_event=threading.Event(),
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
                raise TypeError('type of \'next\' must be str, int or list')
            # throw value error
            raise ValueError(
                '\'type\'value must be \'case\', \'break_case\' or \'default\'')

        self._start_logcat()
        # declare event to stop logcat
        store_thread_stop_event = threading.Event()
        # launch the thread
        store_thread = threading.Thread(
            target=self._store_log,
            args=(store_thread_stop_event,),
            name='_store_log',
            daemon=True)
        store_thread.start()

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

        # run task
        timeout_target = lambda *args, **kwargs: None
        re_result = None
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
                            block=True, timeout=0.2)
                        timer.reset()
                        self.logcat_queue.task_done()
                except queue.Empty:
                    # get failed, do something after timeout
                    timer.start()
                    if timer.check() >= block_timeout - 0.2:
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

        # kill logcat subproc
        self._stop_logcat()
        # stop store log thread
        store_thread_stop_event.set()
        store_thread.join()
