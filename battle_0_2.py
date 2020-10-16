'''
0-2自动全薪练级
'''
from functools import partial
from random import SystemRandom

import action
from gfcontrol import GFControl

random = SystemRandom()
GFControl.adbpath = '/home/thanksshu/Android/sdk/platform-tools/adb'
gf = GFControl(device_id='39V4C19114019806')


@action.log_func
def init_map():
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
def tap_airport():
    """
    点击机场
    """
    gf.tap(500, 490)


@action.log_func
def tap_hq():
    """
    点击指挥部
    """
    gf.tap(772, 492)


@action.log_func
def tap_waypoint():
    """
    点击左上路径点
    """
    gf.tap(691, 138, radius=3)


@action.log_func
def tap_ehq():
    """
    点击敌指挥部
    """
    gf.tap(966, 164)


task_0_2 = list()

task_deassembly = action.task_deassembly(gf, (task_0_2, 0))

task_0_2.extend(
    [
        [
            {
                'type': 'break_case',
                'match': r'.*TeamSelectionCharacterLabel',
                'target': partial(action.tap_right_second, gf),
                'next': 'next'
            }
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
                'target': partial(action.noise, gf, 3),
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
                'type': 'default',
                'target': partial(action.noise, gf, 3),
                'next': 'next'
            }
        ],

        # 选择机场
        [
            {
                'type': 'break_case',
                'match': r'刷新UI0',
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
                'type': 'default',
                'target': partial(action.noise, gf, 3),
                'next': 'next'
            }
        ],

        # 点击指挥部
        [
            {
                'type': 'break_case',
                'match': r'.*StartPlanfalse',
                'target': tap_hq,
                'next': 'next'
            }
        ],

        # 点击路径点
        [
            {
                'type': 'break_case',
                'match': r'关闭BUildUI面板',
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
        # 等待
        [
            {
                'type': 'break_case',
                'match': r'.*变更计划模式状态normal',
                'target': 'pass',
                'next': 'next'
            }
        ],

        # 噪音
        [
            {
                'type': 'default',
                'target': partial(action.noise, gf, 4),
                'next': 'next'
            }
        ],
        # 等待
        [
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
                'match': r'.*销毁时间',
                'target': partial(action.tap_start, gf),
                'next': 'next'
            }
        ],
        # 结算关卡
        [
            {
                'type': 'break_case',
                'match': r'.*missionaction',
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
        ]
    ]
)

gf.run_task((task_0_2, 0))
