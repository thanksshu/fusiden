'''
0-2 自动拖尸 维修 拆低星人形
'''
import argparse
import os
from functools import partial
from random import SystemRandom

import action
from gfcontrol import GFControl


parser = argparse.ArgumentParser(description='auto run 0-2')
parser.add_argument('hitman', type=str, help='hitman in the team now')
parser.add_argument('-e', type=int, default=3, nargs='?',
                    help='entrance number for the chain')
parser.add_argument('-f', type=bool, default=False, nargs='?',
                    help='directly fix m16')
args = parser.parse_args()
print(args)

random = SystemRandom()
GFControl.adbpath = '/home/thanksshu/Android/sdk/platform-tools/adb'
gf = GFControl(device_id='39V4C19114019806')


# targets

@action.log_func
def init_map(*, arg=None):
    """
    令地图满足固定座标
    """
    for _ in range(random.randint(2, 3)):
        gf.swipe(random.randint(540, 1370), random.randint(
            500, 600), random.randint(540, 1370), random.randint(0, 100))  # 下拉以找到 5-6
    action.sleep(0.5)

    random_x_start = random.randint(600, 1200)
    random_x_end = random.randint(600, 1200)
    random_y_start = random.randint(50, 340)
    random_y_end = random_y_start + 500
    gf.swipe(random_x_start, random_y_start,
             random_x_end, random_y_end,
             duration=1200, radius=0, delta=50)  # 令地图满足固定座标


@action.log_func
def tap_airport(*, arg=None):
    """
    点击机场
    """
    gf.tap(510, 490)


@action.log_func
def tap_hq(*, arg=None):
    """
    点击指挥部
    """
    gf.tap(772, 492)


@action.log_func
def tap_waypoint(*, arg=None):
    """
    点击左上路径点
    """
    gf.tap(691, 138, radius=3)


@action.log_func
def tap_ehq(*, arg=None):
    """
    点击敌指挥部
    """
    gf.tap(966, 164)


def generate_output():
    """
    生成 output 函数
    """
    count = 1

    @action.log_func
    def _o(*, arg=None):
        """
        输出
        """
        nonlocal count
        count += 1
        os.write(1, b"\x1b[2J\x1b[H")
        print(f'count: {count}')
    return _o


def generate_repair_m16(direct_fix=False):
    """
    生成 flag 控制
    """
    repair_flag = direct_fix

    @action.log_func
    def _set_repair_flag(value, *, arg=None):
        """
        改变 repair flag
        """
        nonlocal repair_flag
        repair_flag = value

    @action.log_func
    def _check_m16(*, arg=None):
        """
        检测M16性命状态
        """
        nonlocal repair_flag
        chain = arg[0]
        task_index = arg[1]
        cond_index = arg[2]
        if repair_flag is False:
            chain[task_index][cond_index]['next'] = ('next', 4)
        else:
            chain[task_index][cond_index]['next'] = 'next'
    return _set_repair_flag, _check_m16


def generate_change_hitman(hitman):
    """
    生成更换打手函数
    """
    hitman = hitman if hitman else hitman

    @action.log_func
    def _change_hitman(*, arg=None):
        """
        更换打手
        """
        nonlocal hitman
        if hitman == 'g11':
            # gf.tap_in(850, 120, 990, 480)
            action.tap_doll_in_warehouse(gf, 0, 4)
            hitman = 'an94'
        else:
            # gf.tap_in(494, 120, 646, 480)
            action.tap_doll_in_warehouse(gf, 0, 2)
            hitman = 'g11'
    return _change_hitman


output = generate_output()
set_repair_flag, check_m16 = generate_repair_m16(args.f)
change_hitman = generate_change_hitman(args.hitman)

# tasks
task_0_2 = list()
task_deassembly = action.generate_task_deassembly(gf, (task_0_2, 1))
task_0_2.extend(
    [
        # 清屏，计数
        [
            {
                'type': 'default',
                'target': output,
                'next': 'next'
            }
        ],
        # 结束战斗,从工厂返回后,点击 0-2
        [
            {
                'type': 'case',
                'match': r'.*TeamSelectionCharacterLabel',
                'target': 'pass',
            },
            {
                'type': 'break_case',
                'match': r'.*Mission/drawEvent',
                'target': 'pass',
                'next': 'next'
            },
        ],
        [
            {
                'type': 'case',
                'match': r'.*Decode',
                'target': 'pass',
                'next': ('next', 2)
            },
            {
                'type': 'break_case',
                'match': r'.*TeamSelectionCharacterLabel',
                'target': partial(action.tap_right, gf, 1),
                'next': 'next'
            },
        ],
        # 作战设置
        [
            {
                'type': 'break_case',
                'match': r'.*Function：Mission/combinationInfo',
                'target': partial(action.tap_normal_battle, gf),
                'next': 'next'
            }
        ],
        # 进入地图 或 人形已满
        [
            # 人形已满，去强化
            {
                'type': 'break_case',
                'match': r'.*RevertcanvasMissionInfo',
                'target': partial(
                        action.tap_go_for_enhance, gf),
                'next': (task_deassembly, 0)
            },
            # 初始化地图
            {
                'type': 'break_case',
                'match': r'.*载入场景耗时',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 初始化地图
        [
            {
                'type': 'break_case',
                'match': r'.*销毁',
                'target': init_map,
                'next': 'next'
            }
        ],
        # 噪音
        [
            {
                'type': 'default',
                'target': partial(action.noise, gf),
                'next': 'next'
            }
        ],
        # 点击指挥部
        [
            {
                'type': 'default',
                'target': tap_hq,
                'next': 'next'
            }
        ],
        # 检查16哥是否幸存
        [
            {
                'type': 'break_case',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': check_m16,
                'next': 'next'
            }
        ],
        # 16哥性命不保，点击以快修
        [
            {
                'type': 'default',
                'target': partial(action.tap_doll_in_team, gf, 4),
                'next': 'next'
            }
        ],
        # 点击确认
        [
            {
                'type': 'break_case',
                'match': r'.*MessageboxNormalFixConfirmBox',
                'target': partial(action.tap_onepress_confirm, gf),
                'next': 'next'
            }
        ],
        # 修完后标记重置
        [
            {
                'type': 'break_case',
                'match': r'.*LiteMessageTips',
                'target': partial(set_repair_flag, False),
                'next': 'next'
            }
        ],
        # 换人，点击队伍编成
        [
            {
                'type': 'default',
                'target': partial(action.tap_formation, gf),
                'next': 'next'
            }
        ],
        # 点击右二的打手
        [
            {
                'type': 'break_case',
                'match': r'预加载物体TileSetting',
                'target': partial(action.tap_doll_in_team, gf, 3),
                'next': 'next'
            }
        ],
        # 点击所需人形
        [
            {
                'type': 'break_case',
                'match': r'.*CharacterDisabled',
                'target': change_hitman,
                'next': 'next'
            }
        ],
        # 点击返回
        [
            {
                'type': 'break_case',
                'match': r'.*RequestChangeTeam success',
                'target': partial(action.tap_goback, gf),
                'next': 'next'
            }
        ],
        # 初始化地图
        [
            {
                'type': 'break_case',
                'match': r'变更计划模式状态normal',
                'target': init_map,
                'next': 'next'
            }
        ],
        # 点击HQ
        [
            {
                'type': 'default',
                'target': tap_hq,
                'next': 'next'
            }
        ],
        # 点击确认部署
        [
            {
                'type': 'break_case',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': partial(action.tap_confirm, gf),
                'next': 'next'
            }
        ],
        # 噪音
        [
            {
                'type': 'break_case',
                'match': r'刷新UI0',
                'target': partial(action.noise, gf),
                'next': 'next'
            }
        ],
        # 选择机场
        [
            {
                'type': 'default',
                'target': tap_airport,
                'next': 'next'
            }
        ],
        # 点击确认部署
        [
            {
                'type': 'break_case',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': partial(action.tap_confirm, gf),
                'next': 'next'
            }
        ],
        # 开始作战
        [
            {
                'type': 'break_case',
                'match': r'刷新UI0',
                'target': partial(action.tap_start, gf),
                'next': 'next'
            }
        ],
        # 点击机场
        [
            {
                'type': 'break_case',
                'match': r'.*Next',
                'target': tap_airport,
                'next': 'next'
            }
        ],
        # 点击第二次
        [
            {
                'type': 'break_case',
                'match': r'选择我方',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break_case',
                'match': r'关闭BUildUI面板',
                'target': tap_airport,
                'next': 'next'
            }
        ],
        # 点击补给
        [
            {
                'type': 'break_case',
                'match': r'.*MessageboxDeploymentTeamInfo',
                'target': partial(gf.tap_in, 1200, 530, 1390, 590),
                'next': 'next'
            }
        ],
        # 计划模式
        [
            {
                'type': 'break_case',
                'match': r'请求补给!!',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break_case',
                'match': r'.*Next',
                'target': partial(action.tap_plan_mode, gf),
                'next': 'next'
            }
        ],
        # 噪音
        [
            {
                'type': 'break_case',
                'match': r'.*StartPlanfalse',
                'target': partial(action.noise, gf, min_times=1),
                'next': 'next'
            }
        ],
        # 点击指挥部
        [
            {
                'type': 'break_case',
                'match': r'.*取消选中梯队',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break_case',
                'match': r'.*关闭BUildUI面板',
                'target': tap_hq,
                'next': 'next'
            }
        ],
        # 点击路径点
        [
            {
                'type': 'break_case',
                'match': r'.*DeploymentFriendlyTeamController',
                'target': tap_waypoint,
                'next': 'next'
            }
        ],
        # 点击敌指挥部
        [
            {
                'type': 'break_case',
                'match': r'.*DeploymentPlanModeController',
                'target': tap_ehq,
                'next': 'next'
            }
        ],
        # 执行计划
        [
            {
                'type': 'break_case',
                'match': r'.*DeploymentPlanModeController',
                'target': partial(action.tap_start, gf),
                'next': 'next'
            }
        ],
        # 回合结束，等待
        [
            # 防计划中断
            {
                'type': 'break_case',
                'match': r'.*变更计划模式状态pause',
                'target': partial(action.tap_cancel, gf),
                'next': 'self'
            },
            {
                'type': 'break_case',
                'match': r'.*变更计划模式状态normal',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 新回合，等待
        [
            # 16哥，快死了吗？
            {
                'type': 'break_case',
                'match': r'.*\{"id":188211898,"life":(1?[0-9]{1,2}|2[0-4][0-9]|25[0-5])\}',
                'target': partial(set_repair_flag, True),
                'next': 'self'
            },
            # 防计划中断
            {
                'type': 'break_case',
                'match': '.*变更计划模式状态pause',
                'target': partial(action.tap_cancel, gf),
                'next': 'self'
            },
            {
                'type': 'break_case',
                'match': r'.*变更计划模式状态normal',
                'target': 'pass',
                'next': 'next'
            }
        ],
        # 结束回合
        [
            {
                'type': 'break_case',
                'match': r'.*变更计划模式状态pause',
                'target': partial(action.tap_cancel, gf),
                'next': 'self'
            },
            {
                'type': 'break_case',
                'match': r'.*销毁时间',
                'target': partial(action.tap_start, gf),
                'next': 'next'
            }
        ],
        # 结算关卡
        [
            {
                'type': 'break_case',
                'match': r'.*清除missionaction',
                'target': partial(action.tap_somewhere, gf, 4),
                'next': 'next'
            }
        ],
        # 确认人形
        [
            {
                'type': 'break_case',
                'match': r'.*GetNewGun',
                'target': partial(action.tap_somewhere, gf, 2),
                'next': 'next'
            }
        ],
        # 再点一下
        [
            {
                'type': 'default',
                'target': partial(action.tap_somewhere, gf, 1),
                'next': 'next'
            }
        ],
        # 回到任务选择界面
        [
            {
                'type': 'default',
                'target': partial(action.tap_somewhere, gf, 1),
                'next': 0
            }
        ],
    ]
)

gf.run_task((task_0_2, args.e))
