'''
android controling classes
'''
import queue
import re
import shlex
import socket
import subprocess
import threading
from random import SystemRandom

from . import utils

random = SystemRandom()


class AndroidControlConnectionError(Exception):
    '''
    AndroidControl connection error
    '''


class AndroidControl():
    '''
    class for controling GirlsFrontline

    one instance represents a device
    '''

    def __init__(self):
        self.adb_path = 'adb'
        self._device_id = None
        self._monkey_port = None
        self._monkey_socket = None

        self._subproc = list()

    def open_adb(self, command, with_id=True, **kwargs):
        '''
        open a adb subprocess
        '''
        # connect check
        if not self._device_id and with_id:
            raise AndroidControlConnectionError('not connected to any device')

        option_s = f'-s {self._device_id} ' if with_id else ''
        args = shlex.split(f'{self.adb_path} {option_s}{command}')
        kwargs.update({'args': args})
        if 'stdout' not in kwargs:
            kwargs.update({'stdout': subprocess.DEVNULL})
        if 'stdin' not in kwargs:
            kwargs.update({'stdin': subprocess.DEVNULL})
        if 'stderr' not in kwargs:
            kwargs.update({'stderr': subprocess.DEVNULL})
        popen = subprocess.Popen(**kwargs)

        # put in list
        self._subproc.append(popen)

        return popen

    def adb(self, command, with_id=True, timeout=2, **kwargs):
        """
        run a adb command and quit
        """
        # connect check
        if not self._device_id and with_id:
            raise AndroidControlConnectionError('not connected to any device')

        option_s = f'-s {self._device_id} ' if with_id else ''
        args = shlex.split(f'{self.adb_path} {option_s}{command}')
        kwargs.update({'args': args})
        kwargs.update({'timeout': timeout})
        if 'capture_output' not in kwargs:
            kwargs.update({'capture_output': True})
        if 'check' not in kwargs:
            check = True
        else:
            check = kwargs['check']
            kwargs.pop('check', None)
        return subprocess.run(**kwargs, check=check)

    def list_device(self):
        '''
        list attached devices
        '''
        # no connect check needed
        proc = self.adb('devices', with_id=False)
        result = proc.stdout.splitlines()[1:-1]
        device = list()
        for id_device in result:
            device.append(id_device.decode('utf-8').rsplit())
        return device

    def connect(self, device_id, monkey_port=5556, timeout=0.2):
        '''
        specify a device to comunicate with
        '''
        # not closed
        if self._device_id is not None:
            raise AndroidControlConnectionError('not connected to any device')

        self._device_id = device_id
        self._monkey_port = monkey_port

        # forward port
        self.adb(
            f'forward tcp:{self._monkey_port} tcp:{self._monkey_port}', with_id=False)

        # start monkey subproc
        popen = self.open_adb(
            f'shell monkey --port {self._monkey_port}', stderr=subprocess.PIPE)
        while True:
            line = popen.stderr.readline()
            if b'data=' in line:
                break
        popen.kill()

        # start monkey tcp connection
        while True:
            self._monkey_socket = socket.create_connection(
                ('localhost', self._monkey_port), timeout)
            if self.monkey('sleep 0') != '':
                break
            self._monkey_socket.close()

    def close(self):
        '''
        stop monkey
        '''
        # stop all subproc
        for subproc in self._subproc:
            utils.kill_subproc(subproc)
        self._subproc.clear()

        # close socket
        if self._monkey_socket is not None:
            self._monkey_socket.close()

        # kill monkey
        if self._device_id:
            monkey_pid = self.get_pid('com.android.commands.monkey')
            if monkey_pid is not None:
                try:
                    self.adb(f'shell kill {monkey_pid}')
                except subprocess.CalledProcessError:
                    # already killed
                    pass
            # remove forward port
            if self._monkey_port:
                try:
                    self.adb(
                        f'forward --remove tcp:{self._monkey_port}', with_id=False)
                except subprocess.CalledProcessError:
                    # no port forward
                    pass

        self._device_id = None
        self._monkey_port = None
        self._monkey_socket = None

    def monkey(self, cmd):
        """
        send cmd to monkey
        """
        self._monkey_socket.sendall(bytes(cmd, 'utf-8') + b'\n')
        return self._monkey_socket.recv(32).rstrip().decode('utf-8')

    def is_alive(self):
        '''
        check adb connection, return False when dead
        '''
        if not self._device_id:
            raise AndroidControlConnectionError('not connected to any device')

        proc = self.open_adb('shell :')
        proc.communicate()
        if proc.returncode != 0:
            return False
        return True

    def get_time(self):
        '''
        get current phone time
        '''
        if not self._device_id:
            raise AndroidControlConnectionError('not connected to any device')

        sub_cmd = shlex.quote('$(date +\'%Y-%m-%d %H:%M:%S.000\')')
        result = self.adb(f'shell echo {sub_cmd}')
        return result.stdout.rstrip().decode('utf-8')

    def get_pid(self, package_name):
        '''
        return pid of a application
        '''
        if not self._device_id:
            raise AndroidControlConnectionError('not connected to any device')

        try:
            result = self.adb(f'shell pidof -s {package_name}')
        except subprocess.CalledProcessError:
            pid = None
        else:
            pid = int(result.stdout.rstrip().decode('utf-8'))
        return pid

    def swipe(self, pos_start, pos_end,
              radius=5, step_duration=5, duration=200, delta=100,
              *, task_info=None):
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

    def __init__(self):
        super().__init__()
        self._logcat_queue = queue.Queue()
        self._logcat_proc = None

        self.store_log_thread = threading.Thread(
            target=self._store_log,
            name='store_log')

    def _store_log(self):
        """
        store log in queue
        """
        # read log
        pre_line = ''
        while True:
            try:
                current_line = self._logcat_proc.stdout.readline()
            except AttributeError:
                # logcat subproc killed, end loop
                break
            # check if needed
            if pre_line and b'DebugLogHandler' in current_line:
                current_log = pre_line.rstrip().decode('utf-8')
                # put log in queue
                self._logcat_queue.put(current_log)
            pre_line = current_line

    def clear_log(self, *, task_info=None):
        '''
        clear log buffer
        '''
        return self.adb('logcat -c')

    def connect(self, device_id, monkey_port=5556, timeout=0.2):
        '''
        specify a device to communicate with and start logcat subproc
        '''
        super().connect(device_id, monkey_port=monkey_port, timeout=timeout)
        # get time and pid
        time = self.get_time()
        pid = self.get_pid('com.sunborn.girlsfrontline.cn')
        # clear and adjust log buffer
        self.clear_log()
        self.adb('logcat -G 16m')
        # start logcat subproc
        self._logcat_proc = self.open_adb(
            f' logcat -v raw -s Unity -T {shlex.quote(time)} --pid={pid}',
            stdout=subprocess.PIPE)
        # start logcat thread
        self.store_log_thread.start()

    def close(self):
        '''
        stop communicate with the device
        '''

        if self._logcat_proc is not None:
            utils.kill_subproc(self._logcat_proc)
            self._logcat_proc = None

        super().close()

    @staticmethod
    def exec_cond(info, fallback_timeout, *, task_info=None):
        '''
        execute condition
        '''
        # set condition
        info['condition'] = info['task'][info['condition_index']]

        GFControl._call_target(info, fallback_timeout)
        # case, execute next condition
        if info['condition']['type'] == 'case':
            info['condition_index'] += 1
            GFControl.exec_cond(info, fallback_timeout)
        # break or direct, change task
        else:
            GFControl._change_task(info)

    @staticmethod
    def _call_target(info, fallback_timeout):
        '''
        call target
        '''
        temp_timeout_target = info['timeout_target']
        temp_block_timeout = info['block_timeout']
        if info['condition']['target'] == 'pass':
            target = lambda *args, **kwargs: None
        else:
            target = info['condition']['target']
        # pass in task information to target
        # allowing target to change info
        target(task_info=info)
        # test timeout_target changement
        if temp_timeout_target == info['timeout_target']:
            info['timeout_target'] = target
        # test block_timeout changement
        if temp_block_timeout == info['block_timeout']:
            info['block_timeout'] = fallback_timeout

    @staticmethod
    def _change_task(info):
        '''
        change task in info
        '''
        # None type, stop task
        if info['condition']['next'] is None:
            info['stop_event'].set()
            return

        # preprocess shorthands
        # int type, shorthand of ['absol', int]
        if isinstance(info['condition']['next'], int):
            info['condition']['next'] = ['absol', info['condition']['next']]
        # 'next', shorthand of ['relev', 1]
        if info['condition']['next'] == 'next':
            info['condition']['next'] = ['relev', 1]
        # 'pre', shorthand of ['relev', -1]
        if info['condition']['next'] == 'pre':
            info['condition']['next'] = ['relev', -1]
        # 'self', shorthand of ['relev', 0]
        if info['condition']['next'] == 'self':
            info['condition']['next'] = ['relev', 0]

        # list type, task and chain changement
        if isinstance(info['condition']['next'], list):
            # independent task, no chain and task_index
            if isinstance(info['condition']['next'][0], dict):
                info['chain'] = None
                info['task_index'] = None
                info['task'] = info['condition']['next']
                return
            # chained task, must be in chain
            # task index change only
            if info['condition']['next'][0] == 'relev':
                info['task_index'] += info['condition']['next'][1]
                info['task'] = info['chain'][info['task_index']]
                return
            if info['condition']['next'][0] == 'absol':
                info['task_index'] = info['condition']['next'][1]
                info['task'] = info['chain'][info['task_index']]
                return
            # chain changement
            if isinstance(info['condition']['next'][0], list):
                info['chain'] = info['condition']['next'][0]
                info['task_index'] = info['condition']['next'][1]
                info['task'] = info['chain'][info['task_index']]
                return
        value = info['condition']['next']
        raise ValueError(f'\'next\' don\'t support {value}')

    def run_task(self, task, fallback_timeout=8, interval=0.1,
                 stop_event=threading.Event(), *, task_info=None):
        '''
        run a serials of task

        interval -- slow down code (default 0.1 second)
        '''
        # init info
        if isinstance(task[0], list):
            # passed in a task chain
            info = {'chain': task[0],
                    'task_index': task[1],
                    'task': task[0][task[1]]}
        elif isinstance(task[0], dict):
            # passed in a task
            info = {'chain': list(),
                    'task_index': int(),
                    'task': task}
        info.update({'condition_index': int(),
                     'condition': dict(),
                     'match_result': None,
                     'block_timeout': fallback_timeout,
                     'timeout_target': lambda *args, **kwargs: None,
                     'stop_event': stop_event})

        # run task
        timer = utils.Timer()
        while not info['stop_event'].is_set():
            # when task finish or no condition matches
            # declare that a new log is needed
            log = True
            # match each condition
            for (info['condition_index'], info['condition']) in enumerate(info['task']):
                # directly execute 'direct' condition
                if info['condition']['type'] == 'direct':
                    timer.reset()
                    self.exec_cond(info, fallback_timeout)
                    break
                # no log for this iteration, jump condition type that need log
                # make sure a log always start the match with the first condition,
                # or no log will be match
                if log is False:
                    continue
                # 'case' or 'break'
                if (info['condition']['type'] == 'case'
                        or info['condition']['type'] == 'break'):
                    try:
                        # if a new log is needed for the task this iteration
                        if log is True:
                            # use interval to prevent iteration goes too fast
                            log = self._logcat_queue.get(
                                block=True, timeout=interval)
                            # get a log, log is now str type
                            timer.reset()
                            self._logcat_queue.task_done()
                        # if not, continue with the existing log
                    except queue.Empty:
                        # get log failed
                        # use non-block timeout timer to make iteration faster
                        timer.start()
                        # call timeout_target after timeout
                        if timer.check() >= info['block_timeout'] - interval:
                            timer.reset()
                            if self.get_pid('com.sunborn.girlsfrontline.cn'):
                                info['timeout_target']()
                            # connection lost
                            else:
                                raise AndroidControlConnectionError(
                                    'connection lost') from Exception()
                            # restart iteration
                            break
                        # try next condition, but no log for this iteration
                        log = False
                        continue
                    else:
                        # match log
                        info['match_result'] = re.match(
                            info['condition']['match'], log)
                        # if matched, call the target and change task
                        if info['match_result']:
                            timer.reset()
                            self.exec_cond(info, fallback_timeout)
                            break
                        # if not matched, continue in order to match next condition
                        continue
                # unknown type
                raise ValueError(
                    '\'type\' value must be \'case\', \'break\' or \'direct\'')
