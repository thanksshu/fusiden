'''
control girlsfrontline
'''
import queue
import re
import shlex
import subprocess
import threading
from random import SystemRandom

import cv2
import numpy as np

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

    def cap_screen(self):
        '''
        get screenshot
        '''
        cmd = f'{self.adbpath} -s {self.device_id} exec-out screencap -p'
        result = subprocess.run(shlex.split(cmd),
                                capture_output=True, check=True)
        # bytes to opencv image
        image = cv2.imdecode(np.fromstring(
            result.stdout, np.uint8), cv2.IMREAD_COLOR)
        return image

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

    def match_img(self, img_matrix):
        '''
        匹配图片
        '''
        screenshot = self.cap_screen()
        template_gray = cv2.cvtColor(img_matrix, cv2.COLOR_BGR2GRAY)
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

        height, width = template_gray.shape
        res = cv2.matchTemplate(
            screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        max_val, max_loc = cv2.minMaxLoc(res)[1::2]
        top_left = max_loc
        bottom_right = (top_left[0] + width, top_left[1] + height)
        return *top_left, *bottom_right, max_val


class GFControl(AndroidControl):
    '''
    class for controling girlsfrontline
    '''

    def __init__(self, device_index=0, device_id=None):
        super().__init__(device_index=device_index, device_id=device_id)
        self.logcat_queue = queue.Queue()

    @staticmethod
    def generate_task_chain(task_chain):
        '''
        generate a task chain
        '''
        chain = [[] for _ in task_chain]
        for (index, chained_task) in enumerate(chain):
            for condition in task_chain[index]:
                # check cond type
                if condition['type'] not in ['case', 'break_case', 'default']:
                    raise ValueError(
                        'value must be \'case\', \'break_case\' or \'default\'')

                # check match
                if 'match' in condition:
                    match = re.compile(condition['match'])
                elif condition['type'] == 'default':
                    match = None

                # check target
                if condition['target'] == 'pass':
                    target = lambda *arg: None
                else:
                    target = condition['target']

                # check next
                if 'next' in condition:
                    if isinstance(condition['next'], int):
                        next_task = chain[condition['next']]
                    elif isinstance(condition['next'], list):
                        next_task = condition['next']
                    elif isinstance(condition['next'], str):
                        if condition['next'] == 'next':
                            next_task = chain[index + 1]
                        elif condition['next'] == 'self':
                            next_task = chained_task
                        else:
                            raise ValueError(
                                'value must be \'self\' or \'next\'')
                elif condition['type'] == 'case':
                    next_task = None

                # init the cond
                cond = {
                    'type': condition['type'],
                    'match': match,
                    'target': target,
                    'next': next_task
                }
                # append the cond
                chained_task.append(cond)
        return chain

    def run_task(self, entrance, block_timeout=15):
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
                required = b'DebugLogHandler'
                while not stop_logcat_event.is_set():
                    current_line = logcat_proc.stdout.readline()
                    # check if needed
                    if required in current_line:
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

        def exec_cond(index):
            '''
            match log with a condition and do target
            '''
            nonlocal pre_target, task
            cond = task[index]
            cond['target']()
            pre_target = cond['target']
            # case or break_case
            if cond['type'] == 'case':
                exec_cond(index+1)
                return
            if cond['type'] == 'default' or cond['type'] == 'break_case':
                task = cond['next']
                return
            raise ValueError(
                'value must be \'case\', \'break_case\' or \'default\'')

        stop_logcat_event = threading.Event()
        start_logcat_thread()
        task = entrance
        pre_target = lambda *arg: None
        while True:
            # read log
            if task[0]['type'] == 'default':
                exec_cond(0)
                continue
            try:
                log = self.logcat_queue.get(
                    block=True, timeout=block_timeout)
            except queue.Empty:
                pre_target()
            else:
                # match conditions
                for (index, condition) in enumerate(task):
                    if (condition['type'] == 'default' or
                            condition['match'].match(log)):
                        exec_cond(index)
                        break
        # stop logcat thread
        stop_logcat_event.set()
        return
