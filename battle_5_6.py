from functools import partial
from random import SystemRandom

import action
from gfcontrol import GFControl

random = SystemRandom()

# 初始化地图
@action.log_func
def init_map(gfcontrol: GFControl):
    """
    令地图满足固定座标
    """
    for _ in range(random.randint(2, 3)):
        gfcontrol.swipe(random.randint(540, 1370), random.randint(
            500, 600), random.randint(540, 1370), random.randint(0, 100))  # 下拉以找到 5-6
    action.sleep(0.5)

    random_x_start = random.randint(600, 1200)
    random_x_end = random.randint(600, 1200)
    random_y_start = random.randint(50, 340)
    random_y_end = random_y_start + 380
    gfcontrol.swipe(random_x_start, random_y_start,
                    random_x_end, random_y_end,
                    duration=1200, radius=0, delta=50)  # 令地图满足固定座标


# 右上机场
@action.log_func
def tap_airport(gfcontrol: GFControl):
    """
    点击机场
    """
    gfcontrol.tap(1000, 160, radius=3)


# 指挥部
@action.log_func
def tap_hq(gfcontrol: GFControl):
    """
    点击指挥部
    """
    gfcontrol.tap(990, 630, radius=3)


# 敌方指挥部
@action.log_func
def tap_ehq(gfcontrol: GFControl):
    """
        点击敌方指挥部
        """
    gfcontrol.tap(533, 180, radius=3)  # 点击敌方指挥部


GFControl.adbpath = '/home/thanksshu/Android/sdk/platform-tools/adb'
gf = GFControl(device_id='39V4C19114019806')

task_deassembly = action.task_deassembly(gf)

task_battle = GFControl.generate_task_chain(
    [
        [
            {
                'type': 'break_case',
                'match': r'.*TeamSelectionCharacterLabel',
                'target': partial(action.swipe_down, gf),
                'next': 'next'
            }
        ],

        # 点击5-6
        [
            {
                'type': 'default',
                'target': partial(action.tap_right_fourth, gf),
                'next': 'next'
            }
        ],

        # 普通作战
        [
            {
                'type': 'break_case',
                'match': r'.*Function：Mission/combinationInfo',
                'target': partial(action.tap_normal_battle, gf),
                'next': 'next'
            },
            # 人形已满，去强化
            {
                'type': 'break_case',
                'match': r'.*RevertcanvasMissionInfo',
                'target': partial(
                    action.tap_go_for_enhance, gf),
                'next': task_deassembly[0]
            }
        ],
        # 初始化地图
        [
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
                'target': partial(init_map, gf),
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

        # 点击机场
        [
            {
                'type': 'default',
                'target': partial(tap_airport, gf),
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

        # 选择指挥部
        [
            {
                'type': 'break_case',
                'match': r'刷新UI0',
                'target': partial(tap_hq, gf),
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
                'match': r'.*Next',
                'target': partial(print, 'pass'),
                'next': 'next'
            },

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

        # 点击机场
        [
            {
                'type': 'break_case',
                'match': r'.*StartPlanfalse',
                'target': partial(tap_airport, gf),
                'next': 'next'
            }
        ],

        # 点击敌指挥部
        [
            {
                'type': 'break_case',
                'match': r'关闭BUildUI面板',
                'target': partial(tap_ehq, gf),
                'next': 'next'
            }
        ],

        # 执行计划
        [
            {
                'type': 'break_case',
                'match': r'.*DeploymentPlanModeController\+TeamData',
                'target': partial(action.tap_start, gf),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break_case',
                'match': r'.*变更计划模式状态normal',
                'target': partial(print, 'pass'),
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

        # 结束回合
        [
            {
                'type': 'break_case',
                'match': r'.*变更计划模式状态normal',
                'target': partial(print, 'pass'),
                'next': 'next'
            }
        ],

        [
            {
                'type': 'break_case',
                'match': r'.*销毁',
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

task_deassembly[-1][0]['next'] = task_battle[0]

gf.run_task(task_battle[0])
