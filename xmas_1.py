'''
雪夜杀礼异想曲 1
'''
import json
import signal
import subprocess
import sys
import threading
from random import SystemRandom

import action
import fusiden

# random
random = SystemRandom()

# init Class
gf = fusiden.GFControl()
gf.adb_path = '/home/thanksshu/Android/sdk/platform-tools/adb'

# load target
with open('target.json') as fp:
    target = json.load(fp)


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
            # drag up
            for _ in range(random.randint(1, 2)):
                random_x_start = random.randint(300, 1200)
                random_y_start = random.randint(200, 600)
                random_x_end = random.randint(300, 1200)
                random_y_end = random_y_start + 4000

                gf.swipe([random_x_start, random_y_start],
                         [random_x_end, random_y_end])
            fusiden.rsleep(0.2)
    return _set_init_map_flag, _init_map


set_init_flag, init_map = generate_init_map()

target.update(
    {
        'ap_left.tp': [[506, 319]],
        'ap_right.tp': [[988, 386]],
        'hq.tp': [[748, 597]],
        'wp_1.tp': [[912, 500]],
        'wp_2.tp': [[730, 318]],
        'wp_3.tp': [[454, 624]],
        'wp_4.tp': [[624, 550]],
        'entrance.tpi': [[590, 170], [850, 300]]
    }
)

chain_main = list()
chain_entrance = list()
chain_end_factory = list()
chain_deassembly = action.generate_chain_deassembly(gf, [chain_end_factory, 0])
chain_end_factory.extend(
    [
        # 打开快捷菜单
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in, args=target['global.shortcut.tpi']),
                'next': 'next'
            }
        ],
        # 点击活动
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in, args=target['shortcut.activity.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        # 点击关卡
        [
            {
                'type': 'break',
                'match': r'.*ItemId100073-60/60',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['entrance.tpi']),
                'next': [chain_main, 0]
            }
        ]
    ]
)
chain_entrance.extend(
    [
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['entrance.tpi']),
                'next': [chain_main, 0]
            }
        ]
    ]
)
chain_main.extend(
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
                'next': [chain_deassembly, 0]
            },
            # 初始化地图
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
                'match': r'.*销毁',
                'target': init_map,
                'next': 'next'
            }
        ],
        # 部署左机场
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap,
                                       args=target['ap_left.tp'], delay=0.2),
                'next': 'next'
            }
        ],
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
        # 部署右机场
        [
            {
                'type': 'break',
                'match': r'刷新UI0',
                'target': fusiden.pack(gf.tap,
                                       args=target['ap_right.tp'], delay=0.2),
                'next': 'next'
            }
        ],
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
        # 部署指挥部
        [
            {
                'type': 'break',
                'match': r'刷新UI0',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp'], delay=0.2),
                'next': 'next'
            }
        ],
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
        # 开始作战
        [
            {
                'type': 'break',
                'match': r'刷新UI0',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            }
        ],
        # 补给左机场
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap,
                                       args=target['ap_left.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'选择我方',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'关闭BUildUI面板',
                'target': fusiden.pack(gf.tap,
                                       args=target['ap_left.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in, args=target['battle.team.supply.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'请求补给!!',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 补给右机场
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap,
                                       args=target['ap_right.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'选择我方',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'关闭BUildUI面板',
                'target': fusiden.pack(gf.tap,
                                       args=target['ap_right.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in, args=target['battle.team.supply.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'请求补给!!',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 补给指挥部
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'选择我方',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'关闭BUildUI面板',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in, args=target['battle.team.supply.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'请求补给!!',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 计划模式
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap_in, args=target['battle.plan_mode.tpi']),
                'next': 'next'
            }
        ],
        # 指挥部
        [
            {
                'type': 'break',
                'match': r'LUA: StartPlanfalse',
                'target': fusiden.pack(gf.tap, args=target['wp_1.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息83711',
                'target': fusiden.pack(action.noise, args=(gf, 1, 3)),
                'next': 'next'
            }
        ],
        # 右机场
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap, args=target['ap_right.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*DeploymentFriendlyTeamController',
                'target': fusiden.pack(gf.tap, args=target['wp_2.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息83715',
                'target': fusiden.pack(action.noise, args=(gf, 1, 3)),
                'next': 'next'
            }
        ],
        # 左机场
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap, args=target['ap_left.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*DeploymentFriendlyTeamController',
                'target': fusiden.pack(gf.tap, args=target['wp_3.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息83719',
                'target': fusiden.pack(gf.tap, args=target['wp_4.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息83716',
                'target': fusiden.pack(action.noise, args=(gf, 1, 3)),
                'next': 'next'
            }
        ],
        # 执行计划
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            }
        ],
        # 关卡胜利
        [
            {
                'type': 'break',
                'match': r'调用胜利剧情',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*清除missionaction',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=4.5),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*GetNewGun',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=4),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*MessageboxMessageBox',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.reward.somewhere.tpi'],
                                       delay=0.2),
                'next': 'next'
            },
        ],
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'direct',
                'target': fusiden.pack(set_init_flag, args=(False,)),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi']),
                'next': None
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
        gf.close()

    signal.signal(signal.SIGINT, stop_main)

    print('running...')
    main_stop_event = threading.Event()
    try:
        gf.connect(device_id='39V4C19114019806')
        gf.run_task([chain_entrance, 0],
                    stop_event=main_stop_event, fallback_timeout=15)
        stop_main()
        sys.exit(0)
    except (fusiden.AndroidControlConnectionError,
            TypeError,
            ValueError,
            subprocess.SubprocessError,
            OSError) as exception:
        stop_main()
        raise exception
    sys.exit(0)
