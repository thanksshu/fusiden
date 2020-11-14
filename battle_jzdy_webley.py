'''
茧中蝶影 狂欢夜行 打捞 韦伯利
'''
import json
import signal
import sys
import threading
from random import SystemRandom

import action
import fusiden

random = SystemRandom()

fusiden.GFControl.adbpath = '/home/thanksshu/Android/sdk/platform-tools/adb'
gf = fusiden.GFControl(device_id='39V4C19114019806')

with open('/home/thanksshu/Documents/Girlsfront/target.json') as fp:
    target = json.load(fp)


@fusiden.utils.log_func
def init_map(*, task_info=None):
    """
    令地图满足固定座标
    """
    # 下拉地图
    for _ in range(random.randint(1, 2)):
        random_x_start = random.randint(300, 1200)
        random_y_start = random.randint(200, 600)
        random_x_end = random.randint(300, 1200)
        random_y_end = random_y_start - 2000

        gf.swipe(random_x_start, random_y_start,
                 random_x_end, random_y_end)

    fusiden.rsleep(0.2)

    # 上拉地图
    random_x_start = random.randint(600, 1200)
    random_x_end = random.randint(600, 1200)
    random_y_start = random.randint(50, 340)
    random_y_end = random_y_start + 450

    gf.swipe((random_x_start, random_y_start),
             (random_x_end, random_y_end),
             duration=1200, radius=0, delta=50)


@fusiden.utils.log_func
def tap_hq(*, task_info=None):
    """
    点击指挥部
    """
    gf.tap((752, 395))


@fusiden.utils.log_func
def tap_waypoint(*, task_info=None):
    """
    点击路径点
    """
    gf.tap((610, 538))


@fusiden.utils.log_func
def tap_ehq(*, task_info=None):
    """
    点击目标
    """
    gf.tap((584, 492))


chain_main = list()
task_entrance = [
    {
        'type': 'direct',
        'target': fusiden.pack(gf.tap_in, args=((750, 270), (810, 290))),
        'next': [chain_main, 0]
    }
]
chain_end_factory = [
    # 打开快捷菜单
    [
        {
            'type': 'direct',
            'target': fusiden.pack(gf.tap_in, args=target['global.shortcut.tpi']),
            'next': 'next'
        }
    ],
    # 点击茧中蝶影
    [
        {
            'type': 'direct',
            'target': fusiden.pack(gf.tap_in, args=target['shortcut.activity.tpi']),
            'next': 'next'
        }
    ],
    # 点击关卡
    [
        {
            'type': 'break',
            'match': r'Sprite-Add',
            'target': 'pass',
            'next': task_entrance
        }
    ]
]
# chain_deassembly = action.generate_chain_deassembly(gf, [chain_end_factory, 0])
chain_enhance = action.generate_chain_enhance(gf, [chain_end_factory, 0])
chain_main.extend(
    [
        # 点击确认出击
        [
            {
                'type': 'break',
                'match': r'.*Mission/combinationInfo',
                'target': fusiden.pack(gf.tap_in, args=((1340, 400), (1440, 460))),
                'next': 'next'
            }
        ],
        # 去强化 等一下
        [
            # 去强化
            {
                'type': 'break',
                'match': r'.*MessageboxConstructionConfirmBox',
                'target': fusiden.pack(gf.tap_in, args=target['combat.setting.enhance.tpi']),
                # 'next': [chain_deassembly, 0]
                'next': [chain_enhance, 0]
            },
            # 等一下
            {
                'type': 'break',
                'match': r'.*载入场景耗时',
                'target': 'pass',
                'next': 'next'
            }
        ],
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
        # 点击指挥部
        [
            {
                'type': 'direct',
                'target': tap_hq,
                'next': 'next'
            }
        ],
        # 确认部署
        [
            {
                'type': 'break',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in, args=target['battle.team.confirm.tpi']),
                'next': 'next'
            },
        ],
        # 开始作战
        [
            {
                'type': 'break',
                'match': r'刷新UI0',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            },
        ],
        # 噪音
        [
            {
                'type': 'direct',
                'target': fusiden.pack(action.noise, args=(gf,)),
                'next': 'next'
            }
        ],
        # 检查被检测 等待补给
        [
            # 安全
            {
                'type': 'break',
                'match': r'.*清空数组',
                'target': fusiden.pack(fusiden.tprint, args=('\nsafe\n',)),
                'next': 'self'
            },
            # 被检测到
            {
                'type': 'break',
                'match': r'.*记录相同次数',
                'target': fusiden.pack(fusiden.tprint, args=('\nunsafe\n',)),
                'next': 'self'
            },
            # 等待补给
            {
                'type': 'break',
                'match': r'请求补给!!',
                'target': 'pass',
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
        # 检查被检测 计划模式
        [
            # 安全
            {
                'type': 'break',
                'match': r'.*清空数组',
                'target': fusiden.pack(fusiden.tprint, args=('\nsafe\n',)),
                'next': 'self'
            },
            # 被检测到
            {
                'type': 'break',
                'match': r'.*记录相同次数',
                'target': fusiden.pack(fusiden.tprint, args=('\nunsafe\n')),
                'next': 'self'
            },
            # 计划模式
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap_in, args=target['battle.plan_mode.tpi']),
                'next': 'next'
            },
        ],
        # 检查被检测 点击HQ
        [
            # 安全
            {
                'type': 'break',
                'match': r'.*清空数组',
                'target': fusiden.pack(fusiden.tprint, args=('\nsafe\n')),
                'next': 'self'
            },
            # 被检测到
            {
                'type': 'break',
                'match': r'.*记录相同次数',
                'target': fusiden.pack(fusiden.tprint, args=('\nunsafe\n')),
                'next': 'self'
            },
            # 点击HQ
            {
                'type': 'break',
                'match': r'.*StartPlanfalse',
                'target': tap_hq,
                'next': 'next'
            },
        ],
        # 点击路径点
        [
            {
                'type': 'break',
                'match': r'光标定位',
                'target': tap_waypoint,
                'next': 'next'
            },
        ],
        # 点击最后目标
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息72919',
                'target': tap_ehq,
                'next': 'next'
            },
        ],
        # 执行计划
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息72918',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            },
        ],
        # TODO: Result_New 检测出货
        # 防止意外 等一下
        [
            # 防止意外
            {
                'type': 'break',
                'match': r'.*变更计划模式状态pause',
                'target': fusiden.pack(gf.tap_in, args=target['battle.popup.cancel.tpi']),
                'next': 'self'
            },
            # 等一下
            {
                'type': 'break',
                'match': r'.*变更计划模式状态normal',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # TODO: Result_New 检测出货
        # 防止意外 结束回合
        [
            # 防止意外
            {
                'type': 'break',
                'match': r'.*变更计划模式状态pause',
                'target': fusiden.pack(gf.tap_in, args=target['battle.popup.cancel.tpi']),
                'next': 'self'
            },
            # 结束回合
            {
                'type': 'break',
                'match': r'变更计划模式状态normal',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            },
        ],
        # 点击立绘
        [
            {
                'type': 'break',
                'match': r'.*清除missionaction',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'],
                                       delay=4),
                'next': 'next'
            },
        ],
        # 点击立绘
        [
            {
                'type': 'break',
                'match': r'加载Resource预制物GetNewGun',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'],
                                       delay=3),
                'next': 'next'
            },
        ],
        # 接受奖励
        [
            {
                'type': 'break',
                'match': r'.*MessageboxMessageBox',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.rewrad.somewhere.tpi']),
                'next': 'next'
            },
        ],
        # 点击立绘
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'],
                                       delay=0.5),
                'next': 'next'
            },
        ],
        # 结束
        [
            {
                'type': 'break',
                'match': r'Sprite-Add',
                'target': 'pass',
                'next': task_entrance
            },
        ]
    ]
)

if __name__ == "__main__":
    original_sigint = signal.getsignal(signal.SIGINT)

    def stop_main(*args):
        '''
        stop main
        '''
        signal.signal(signal.SIGINT, original_sigint)
        main_stop_event.set()
        print('quitting...')

    signal.signal(signal.SIGINT, stop_main)

    print('running...')
    main_stop_event = threading.Event()
    gf.run_task(task_entrance, stop_event=main_stop_event)
    sys.exit(0)
