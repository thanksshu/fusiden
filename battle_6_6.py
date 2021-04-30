'''
6-6 自动打捞 维修 处理多余低星人形

M4A1 MOD3 打捞队 放至首个梯队 狗粮队第二
地图预先缩放
'''
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
from random import Random, SystemRandom
from typing import Match

import action
import fusiden

parser = argparse.ArgumentParser(description='auto run 6-6')
parser.add_argument('-i', action='store_true', default=False,
                    help='init map')
parser.add_argument('-e', action='store_true', default=False,
                    help='enhance when full')
args = parser.parse_args()

random = SystemRandom()

gf = fusiden.GFControl()
gf.adb_path = '/home/thanksshu/Android/sdk/platform-tools/adb'

with open('target.json') as fp:
    target = json.load(fp)

target.update(
    {'hq.tp': [[470, 319]],
     'airport.tp': [[1045, 300]],
     'wp.tp': [[786, 328]],
     'ehq.tp': [[831, 431]]}
)


def generate_init_map(first_init=False):
    """
    生成地图初始化
    """
    flag = first_init

    def _set_init_map_flag(value, *, task_info=None):
        """
        改变是否初始化地图
        """
        nonlocal flag
        flag = value

    @fusiden.utils.log_func
    def _init_map(*, task_info=None):
        nonlocal flag
        if flag is True:
            # 下拉地图
            for _ in range(random.randint(1, 2)):
                random_x_start = random.randint(300, 1200)
                random_y_start = random.randint(200, 600)
                random_x_end = random.randint(300, 1200)
                random_y_end = random_y_start - 4000

                gf.swipe([random_x_start, random_y_start],
                         [random_x_end, random_y_end])
            fusiden.rsleep(0.2)
            # 上拉地图
            random_x_start = random.randint(600, 1200)
            random_x_end = random.randint(600, 1200)
            random_y_start = random.randint(50, 340)
            random_y_end = random_y_start + 400
            gf.swipe([random_x_start, random_y_start],
                     [random_x_end, random_y_end],
                     duration=1200, radius=0, delta=0)
    return _set_init_map_flag, _init_map


def generate_output():
    """
    生成 output 函数
    """
    count = 0

    @fusiden.utils.log_func
    def _output(*, task_info=None):
        """
        输出
        """
        nonlocal count
        fusiden.rsleep(1)
        count += 1
        os.write(1, b"\x1b[2J\x1b[H")
        print(f'count: {count}')
    return _output


output = generate_output()
set_init_flag, init_map = generate_init_map(args.i)

# tasks
chain_6_6 = list()
chain_end = list()
chain_entrance = list()
chain_deassembly = action.generate_chain_doll_deassembly(
    gf, [chain_end, 0])
chain_enheance = action.generate_chain_doll_enhance(
    gf, [chain_end, 0])
chain_end.extend(
    [
        # 打开快捷菜单
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in, args=target['global.shortcut.tpi']),
                'next': 'next'
            }
        ],
        # 点击战斗
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap, args=target['shortcut.combat.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        # 等一下
        [
            {
                'type': 'break',
                'match': r'.*Mission/drawEvent|.*TeamSelectionCharacterLabel',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 等一下
        [
            {
                'type': 'break',
                'match': r'.*TeamSelectionCharacterLabel|.*Decode',
                'target': fusiden.pack(fusiden.utils.rsleep, args=(0.5,)),
                'next': [chain_entrance, 0]
            }
        ]
    ]
)
chain_6_6.extend(
    [
        # 普通作战
        [
            {
                'type': 'break',
                'match': r'.*Function：Mission/combinationInfo',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['combat.setting.normal.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        # 进入地图 或 人形已满
        [
            # 人形已满，去强化
            {
                'type': 'break',
                'match': r'.*RevertcanvasMissionInfo',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['combat.setting.enhance.tpi'],
                                       delay=0.2),
                'next': [chain_deassembly, 0] if not args.e else [chain_enheance, 0]
            },
            # 准备初始化地图
            {
                'type': 'break',
                'match': r'预加载物体DeploymentExplain',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # # 等一下
        # [
        #     {
        #         'type': 'break',
        #         'match': r'.*Decode|.*销毁时间',
        #         'target': 'pass',
        #         'next': 'next'
        #     }
        # ],
        # 初始化地图
        [
            {
                'type': 'break',
                'match': r'.*销毁时间',
                'target': init_map,
                'next': 'next'
            }
        ],
        # 噪音
        [
            {
                'type': 'direct',
                'target': fusiden.pack(action.noise, args=(gf,)),
                'next': 'next'
            }
        ],
        # 点击HQ
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        # 点击确认部署
        [
            {
                'type': 'break',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.team.confirm.tpi'],
                                       delay=0.2),
                'next': 'next'
            }
        ],
        # 噪音
        [
            {
                'type': 'break',
                'match': r'刷新UI0',
                'target': fusiden.pack(action.noise, args=(gf,)),
                'next': 'next'
            }
        ],
        # 开始作战
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            }
        ],
        # 点击HQ
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        # 等待
        [
            {
                'type': 'break',
                'match': r'选择我方',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 再点
        [
            {
                'type': 'break',
                'match': r'关闭BUildUI面板',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        # 点击补给
        [
            {
                'type': 'break',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in, args=target['battle.team.supply.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        # 等待
        [
            {
                'type': 'break',
                'match': r'请求补给!!',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 进入计划模式
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap_in, args=target['battle.plan_mode.tpi']),
                'next': 'next'
            }
        ],
        # 点击敌指挥部
        [
            {
                'type': 'break',
                'match': r'变更计划模式状态fastPlan',
                'target': fusiden.pack(gf.tap,
                                       args=target['wp.tp']),
                'next': 'next'
            }
        ],
        # 点击路径点右方机场
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息1622',
                'target': fusiden.pack(gf.tap,
                                       args=target['ehq.tp']),
                'next': 'next'
            }
        ],
        # 执行计划
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息1633',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            }
        ],
        # 等待 * 2
        *[
            [
                # 防计划中断
                {
                    'type': 'break',
                    'match': r'.*变更计划模式状态pause',
                    'target': fusiden.pack(gf.tap_in,
                                           args=target['battle.popup.cancel.tpi'],
                                           delay=0.4),
                    'next': 'self'
                },
                {
                    'type': 'break',
                    'match': r'.*变更计划模式状态normal',
                    'target': 'pass',
                    'next': 'next'
                }
            ] for _ in range(2)
        ],
        # 结束回合
        [
            {
                'type': 'break',
                'match': r'.*销毁时间',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi'], delay=0.4),
                'next': 'next'
            }
        ],
        # 结算成果
        [
            {
                'type': 'break',
                'match': r'.*清除missionaction',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=4.5),
                'next': 'next'
            }
        ],
        # 确认人形
        [
            {
                'type': 'break',
                'match': r'.*GetNewGun',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=4),
                'next': 'next'
            }
        ],
        # 再点一下
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        # 取消地图初始化
        [
            {
                'type': 'direct',
                'target': fusiden.pack(set_init_flag, args=(False,)),
                'next': 'next'
            }
        ],
        # 回到任务选择界面
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi']),
                # 'next': None
                'next': [chain_end, 2]
            }
        ]
    ]
)
chain_entrance.extend(
    [
        # 清屏计数
        [
            {
                'type': 'direct',
                'target': output,
                'next': 'next'
            }
        ],
        [
            {
                'type': 'direct',
                'target': gf.clear_log,
                'next': 'next'
            }
        ],
        # 下拉到底
        *[
            [
                {
                    'type': 'direct',
                    'target': fusiden.pack(gf.swipe, args=([1000, 600], [1000, 200]), kwargs={'radius': 30}, delay=0.2),
                    'next': 'next'
                }
            ] for _ in range(random.randint(2, 3))
        ],
        # 点击 6-6
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in, args=([570, 560], [1350, 620]), delay=0.2),
                'next': [chain_6_6, 0]
            }
        ]
    ]
)

if __name__ == "__main__":
    sigint = signal.getsignal(signal.SIGINT)

    def stop_main(*args):
        '''
        stop main
        '''
        signal.signal(signal.SIGINT, sigint)
        main_stop_event.set()
        print('quitting...')

    signal.signal(signal.SIGINT, stop_main)

    print('running...')
    main_stop_event = threading.Event()
    try:
        gf.connect(device_id='39V4C19114019806')
        gf.run_task([chain_entrance, 0],
                    stop_event=main_stop_event, fallback_timeout=15)
    except (fusiden.AndroidControlConnectionError,
            TypeError,
            ValueError,
            subprocess.SubprocessError,
            OSError) as exception:
        print(exception)
        stop_main()
    gf.close()
    sys.exit(0)
