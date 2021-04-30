'''
雪夜杀礼异想曲 HK21 打捞
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

target.update(
    {
        'hq.tp': [[557, 369]],
        'wp_1.tp': [[673, 372]],
        'wp_2.tp': [[469, 483]],
        'entrance.tpi': [[1040, 230], [1290, 370]]
    }
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


chain_main = list()
chain_entrance = list()
chain_end_factory = list()
chain_deassembly = action.generate_chain_doll_deassembly(gf, [chain_end_factory, 0])
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
                'next': 'next'
            }
        ],
        # 普通作战
        [
            {
                'type': 'break',
                'match': r'.*Function：Mission/combinationInfo',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['combat.setting.normal.tpi'], delay=0.2),
                'next': [chain_main, 0]
            }
        ],
    ]
)
chain_entrance.extend(
    [
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': [chain_main, 1]
            }
        ]
    ]
)
chain_main.extend(
    [
        # 部署主力
        [
            {
                'type': 'break',
                'match': r'.*销毁时间',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*设置canvas至MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.team.confirm.tpi'], delay=0.2),
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
        # 强化 或 补给
        [
            # 强化
            {
                'type': 'break',
                'match': r'.*MessageboxConstructionConfirmBox',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['combat.setting.enhance.tpi'],
                                       delay=0.2),
                'next': [chain_deassembly, 0]
            },
            # 补给
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
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*设置canvas至MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.team.supply.tpi'], delay=0.2),
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
        # 移动主力
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap, args=target['wp_1.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'移动己方梯队From83726To83728',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 部署狗粮
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(action.noise, args=(gf, 1, 3)),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap, args=target['hq.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*设置canvas至MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.team.confirm.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        # 结束回合
        [
            {
                'type': 'break',
                'match': r'刷新UI0',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.start.tpi']),
                'next': 'next'
            }
        ],
        # 等待交战结束
        [
            {
                'type': 'break',
                'match': r'获胜队伍',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=3),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'加载Resource预制物GetNewGun',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=3),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*设置canvas至MessageboxMessageBox',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.reward.somewhere.tpi'],
                                       delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.finish.somewhere.tpi'], delay=1),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'播放回合动画',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 计划模式
        [
            {
                'type': 'break',
                'match': r'视野统计',
                'target': fusiden.pack(gf.tap_in, args=target['battle.plan_mode.tpi']),
                'next': 'next'
            }
        ],
        # 主力计划
        [
            {
                'type': 'break',
                'match': r'.*LUA: StartPlanfalse',
                'target': fusiden.pack(gf.tap,
                                       args=target['wp_1.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*DeploymentFriendlyTeamController',
                'target': fusiden.pack(gf.tap,
                                       args=target['wp_2.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*更新快捷点信息83730',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in, args=([395, 358], [500, 390]), delay=0.4),
                'next': 'next'
            }
        ],
        # 执行计划
        [
            {
                'type': 'break',
                'match': r'更新快捷点信息83726',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.start.tpi']),
                'next': 'next'
            }
        ],
        # 撤离主力
        [
            {
                'type': 'break',
                'match': r'LUA: _CancelPlanfalse',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.team.retreat.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*设置canvas至MessageboxConfirmBoxBasic',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.popup.confirm.tpi']),
                'next': 'next'
            }
        ],
        # 重新作战
        [
            {
                'type': 'break',
                'match': r'关闭BUildUI面板',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.terminate.tpi']),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break',
                'match': r'.*设置canvas至MessageboxAbortMission',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.terminate.retry.tpi'], delay=0.2),
                'next': 0
            }
        ],
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
