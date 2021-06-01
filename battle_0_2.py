'''
0-2 自动拖尸 维修 处理多余低星人形
16鸽在队尾 打手倒2
'''
import argparse
import json
import os
import signal
import subprocess
import sys
import threading
from random import SystemRandom

import action
import fusiden

parser = argparse.ArgumentParser(description='auto run 0-2')
parser.add_argument('-f', action='store_true', default=False,
                    help='directly fix m16')
parser.add_argument('-i', action='store_true', default=False,
                    help='init map')
parser.add_argument('-e', action='store_true', default=False,
                    help='enhance when full default destroy')
args = parser.parse_args()

random = SystemRandom()

gf = fusiden.GFControl()
gf.adb_path = '/home/thanksshu/Android/sdk/platform-tools/adb'

with open('target.json') as fp:
    target = json.load(fp)

hitman_dict = {
    'm4 sopmod iimod': (0, 5),
    'ar15mod': (0, 5)
}

namespace = argparse.Namespace(
    hitman=list(hitman_dict)[0],
    count=0,
    map_flag=args.i,
    repair_flag=args.f
)


target.update(
    {'airport.tp': [[530, 523]],
     'hq.tp': [[764, 523]],
     'wp.tp': [[687, 142]],
     'ehq.tp': [[954, 164]]}
)


@fusiden.utils.log_func
def init_map(*, task_info=None):
    if namespace.map_flag is True:
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
        random_y_end = random_y_start + 500
        gf.swipe([random_x_start, random_y_start],
                 [random_x_end, random_y_end],
                 duration=1200, radius=0, delta=0)


@fusiden.utils.log_func
def output(*, task_info=None):
    """
    输出
    """
    fusiden.rsleep(1)
    namespace.count += 1
    os.write(1, b"\x1b[2J\x1b[H")
    print(f'count: {namespace.count}')


@fusiden.utils.log_func
def check_m16(*, task_info=None):
    """
    检测M16性命状态
    """
    task_info['condition']['next'] = 'next' if namespace.repair_flag else [
        'relev', 4]


# tasks
chain_0_2 = list()
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
                'type': 'case',
                'match': r'.*TeamSelectionCharacterLabel',
                'target': 'pass',
            },
            {
                'type': 'break',
                'match': r'.*Mission/drawEvent',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 等一下
        [
            {
                'type': 'case',
                'match': r'.*Decode',
                'target': 'pass',
            },
            {
                'type': 'break',
                'match': r'.*TeamSelectionCharacterLabel',
                'target': fusiden.pack(fusiden.utils.rsleep, args=(0.5,)),
                'next': [chain_entrance, 0]
            }
        ]
    ]
)
chain_0_2.extend(
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
        # 点击指挥部
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp'], delay=0.2),
                'next': 'next'
            }
        ],
        # 检查16哥是否幸存
        [
            {
                'type': 'break',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': fusiden.pack(check_m16, delay=0.2),
                'next': 'next'
            }
        ],
        # 16哥性命不保，点击以快修
        [
            {
                'type': 'direct',
                'target': fusiden.pack(action.tap_doll_in_team, args=(gf, 4)),
                'next': 'next'
            }
        ],
        # 点击确认
        [
            {
                'type': 'break',
                'match': r'.*MessageboxNormalFixConfirmBox',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['repair.onepress.confirm.tpi'],
                                       delay=0.2),
                'next': 'next'
            }
        ],
        # 修完后标记重置
        [
            {
                'type': 'break',
                'match': r'.*LiteMessageTips',
                'target': fusiden.utils.gen_setattr(args=(namespace, 'repair_flag', False)),
                'next': 'next'
            }
        ],
        # 点击队伍编成
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.team.formation.tpi']),
                'next': 'next'
            }
        ],
        # 判断队中打手
        [
            {
                'type': 'break',
                'match': rf'.*character_{list(hitman_dict)[0]}',
                'target': fusiden.utils.gen_setattr(args=(namespace, 'hitman', list(hitman_dict)[0])),
                'next': 'next'
            },
            {
                'type': 'break',
                'match': rf'.*character_{list(hitman_dict)[1]}',
                'target': fusiden.utils.gen_setattr(args=(namespace, 'hitman', list(hitman_dict)[1])),
                'next': 'next'
            }
        ],
        # 点击右二的打手
        [
            {
                'type': 'break',
                'match': r'预加载物体TileSetting',
                'target': fusiden.pack(action.tap_doll_in_team, args=(gf, 3)),
                'next': 'next'
            }
        ],
        # # 点击排序方式
        # [
        #     {
        #         'type': 'break',
        #         'match': r'.*CharacterDisabled',
        #         'target': fusiden.pack(gf.tap_in, args=target['warehouse.sort.tpi'], delay=0.2),
        #         'next': 'next'
        #     }
        # ],
        # [
        #     {
        #         'type': 'direct',
        #         'target': fusiden.pack(gf.tap_in,
        #                                args=target['warehouse.sort.favor.tpi'],
        #                                delay=0.2),
        #         'next': 'next'
        #     }
        # ],
        # 点击所需人形
        [
            {
                'type': 'break',
                'match': r'.*实例化数目',
                'target': fusiden.pack(action.tap_in_warehouse,
                                       args=(gf, *hitman_dict[namespace.hitman]), delay=0.2),
                'next': 'next'
            }
        ],
        # 点击返回
        [
            {
                'type': 'break',
                'match': r'RequestChangeTeam success',
                'target': fusiden.pack(gf.tap, args=target['global.back.tp']),
                'next': 'next'
            }
        ],
        # 初始化地图
        [
            {
                'type': 'break',
                'match': r'.*DeploymentCircle',
                'target': fusiden.pack(init_map, delay=0.2),
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
        # 选择机场
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap,
                                       args=target['airport.tp']),
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
        # 开始作战
        [
            {
                'type': 'break',
                'match': r'刷新UI0',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            }
        ],
        # 点击机场
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap,
                                       args=target['airport.tp']),
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
        # 再点击机场
        [
            {
                'type': 'break',
                'match': r'关闭BUildUI面板',
                'target': fusiden.pack(gf.tap,
                                       args=target['airport.tp']),
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
        # 点击指挥部
        [
            {
                'type': 'break',
                'match': r'.*Next',
                'target': fusiden.pack(gf.tap,
                                       args=target['hq.tp']),
                'next': 'next'
            }
        ],
        # 进入计划模式
        [
            {
                'type': 'break',
                'match': r'.*关闭BUildUI面板',
                'target': fusiden.pack(gf.tap_in, args=target['battle.plan_mode.tpi']),
                'next': 'next'
            }
        ],
        # 点击路径点
        [
            {
                'type': 'break',
                'match': r'变更计划模式状态fastPlan',
                'target': fusiden.pack(gf.tap,
                                       args=target['wp.tp']),
                'next': 'next'
            }
        ],
        # 点击敌指挥部
        [
            {
                'type': 'break',
                'match': r'.*更新快捷点信息16',
                'target': fusiden.pack(gf.tap,
                                       args=target['ehq.tp']),
                'next': 'next'
            }
        ],
        # 执行计划
        [
            {
                'type': 'break',
                'match': r'.*更新快捷点信息25',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
                'next': 'next'
            }
        ],
        # 回合结束，等待
        [
            # 防计划中断,防弹药口粮不足
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
        ],
        # 等待
        [
            # 16哥，快死了吗？
            {
                'type': 'break',
                'match': r'.*\{"id":188211898,"life":(1?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\}',
                'target': fusiden.utils.gen_setattr(args=(namespace, 'repair_flag', True)),
                'next': 'self'
            },
            # 防计划中断
            {
                'type': 'break',
                'match': '.*变更计划模式状态pause',
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
        ],
        # 结束回合
        [
            # 防中断
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
                'match': r'.*销毁',
                'target': fusiden.pack(gf.tap_in, args=target['battle.start.tpi']),
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
                'target': fusiden.utils.gen_setattr(args=(namespace, 'map_flag', False)),
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
        # 点击 0-2
        [
            {
                'type': 'direct',
                'target': fusiden.pack(action.tap_right, args=(gf, 1)),
                'next': [chain_0_2, 0]
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
                    stop_event=main_stop_event, fallback_timeout=6)
    except (fusiden.AndroidControlConnectionError,
            TypeError,
            ValueError,
            subprocess.SubprocessError,
            OSError) as exception:
        print(exception)
        stop_main()
    gf.close()
    sys.exit(0)
