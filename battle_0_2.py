'''
0-2 自动拖尸 维修 拆低星人形
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
parser.add_argument('hitman', type=str, help='hitman in the team now')
parser.add_argument('-f', action='store_true', default=False,
                    help='directly fix m16')
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
    {'airport.tp': [[530, 523]],
     'hq.tp': [[764, 523]],
     'wp.tp': [[687, 142]],
     'ehq.tp': [[954, 164]]}
)


def generate_change_hitman(hitman):
    """
    生成更换打手函数
    """
    hitman = hitman if hitman else hitman

    hitman_list = ['g11', [0, 4], 'an94', [0, 5]]

    @fusiden.utils.log_func
    def _set_hitman(*, task_info=None):
        """
        更换打手
        """
        nonlocal hitman, hitman_list
        if hitman == hitman_list[0]:
            hitman = hitman_list[2]
        elif hitman == hitman_list[2]:
            hitman = hitman_list[0]
        print(hitman)

    @fusiden.utils.log_func
    def _change_hitman(*, task_info=None):
        """
        更换打手
        """
        nonlocal hitman, hitman_list
        if hitman == hitman_list[0]:
            action.tap_doll_in_warehouse(gf, *hitman_list[3])
        elif hitman == hitman_list[2]:
            action.tap_doll_in_warehouse(gf, *hitman_list[1])

    return _change_hitman, _set_hitman


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
            random_y_end = random_y_start + 500
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


def generate_repair_m16(direct_fix=False):
    """
    生成 flag 控制
    """
    repair_flag = direct_fix

    @fusiden.utils.log_func
    def _set_repair_flag(value, *, task_info=None):
        """
        改变 repair flag
        """
        nonlocal repair_flag
        repair_flag = value

    @fusiden.utils.log_func
    def _check_m16(*, task_info=None):
        """
        检测M16性命状态
        """
        nonlocal repair_flag

        task_info['condition']['next'] = 'next' if repair_flag else ['relev', 4]

    return _set_repair_flag, _check_m16


output = generate_output()
set_repair_flag, check_m16 = generate_repair_m16(args.f)
change_hitman, set_hitman = generate_change_hitman(args.hitman)
set_init_flag, init_map = generate_init_map(args.i)

# tasks
chain_0_2 = list()
chain_end = list()
chain_entrance = list()
chain_deassembly = action.generate_chain_deassembly(
    gf, [chain_end, 0])
chain_enheance = action.generate_chain_enhance(
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
                'target': fusiden.pack(set_repair_flag, args=(False,)),
                'next': 'next'
            }
        ],
        # 换人，点击队伍编成
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['battle.team.formation.tpi']),
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
        # 点击排序方式
        [
            {
                'type': 'break',
                'match': r'.*CharacterDisabled',
                'target': fusiden.pack(gf.tap_in, args=target['warehouse.sort.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap_in,
                                       args=target['warehouse.sort.favor.tpi'],
                                       delay=0.2),
                'next': 'next'
            }
        ],
        # 点击所需人形
        [
            {
                'type': 'break',
                'match': r'.*实例化数目',
                'target': fusiden.pack(change_hitman, delay=1),
                'next': 'next'
            }
        ],
        # 改变打手标记
        [
            {
                'type': 'break',
                'match': r'.*RequestChangeTeam success',
                'target': set_hitman,
                'next': 'next'
            }
        ],
        # 点击返回
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gf.tap, args=target['global.back.tp']),
                'next': 'next'
            }
        ],
        # 初始化地图
        [
            {
                'type': 'break',
                'match': r'.*预加载物体TeamSelectionCharacterLabel',
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
                'match': r'.*LUA: StartPlanfalse',
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
                'target': fusiden.pack(set_repair_flag, args=(True,)),
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
