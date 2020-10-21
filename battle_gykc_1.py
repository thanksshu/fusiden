'''
诡疫狂潮-1-打捞
'''
from functools import partial
from random import SystemRandom

import action
from gfcontrol import GFControl

random = SystemRandom()
GFControl.adbpath = '/home/thanksshu/Android/sdk/platform-tools/adb'
gf = GFControl(device_id='39V4C19114019806')


@action.log_func
def init_map(*, arg=None):
    """
    令地图满足固定座标
    """
    for _ in range(random.randint(2, 3)):
        gf.swipe(random.randint(540, 1370), random.randint(100, 200),
                 random.randint(540, 1370), random.randint(500, 600))  # 上拉


@action.log_func
def tap_1(*, arg=None):
    """
    点击第一关
    """
    action.sleep(2)
    gf.tap_in(550, 160, 860, 300)


@action.log_func
def tap_hq(*, arg=None):
    """
    点击HQ
    """
    gf.tap(560, 400)


@action.log_func
def tap_wp_1(*, arg=None):
    """
    路径点1
    """
    gf.tap(662, 550)


@action.log_func
def tap_wp_2(*, arg=None):
    """
    路径点2
    """
    gf.tap(926, 390)


@action.log_func
def tap_airport(*, arg=None):
    """
    点击机场
    """
    gf.tap(1062, 616)


task_gykc_1 = list()
task_deassembly = list()

task_deassembly.extend(
    [
        # 点击拆解tab
        [
            {
                'type': 'break_case',
                'match': r'预加载结束',
                'target': partial(action.tap_deassembly_tab, gf),
                'next': 'next'
            }
        ],
        # 点击选择人形
        [
            {
                'type': 'default',
                'target': partial(action.tap_choose_doll_tab, gf),
                'next': 'next'
            }
        ],
        # 点击智能选择
        [
            {
                'type': 'case',
                'target': 'pass',
                'match': r'.*实例化数目0'
            },
            {
                'type': 'break_case',
                'match': r'加载Resource预制物',
                'target': partial(action.tap_smart_choose_doll_btn, gf),
                'next': 'next'
            }
        ],
        # 点击确定
        [
            {
                'type': 'break_case',
                'match': r'.*实例化数目0销毁数目0',
                'target': partial(action.tap_smart_choose_doll_btn, gf),
                'next': 'next'
            }
        ],
        # 点击拆解
        [
            {
                'type': 'default',
                'target': partial(action.tap_deassemble_btn, gf),
                'next': 'next'
            }
        ],
        # 拆解结束，打开快捷菜单
        [
            {
                'type': 'break_case',
                'match': r'.*retireGun',
                'target': partial(action.tap_shortcut_menu, gf),
                'next': 'next'
            }
        ],
        # 菜单弹出，点击战斗
        [
            {
                'type': 'break_case',
                'match': r'.*RefreshRewardMail',
                'target': partial(action.tap_battle_btn, gf),
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break_case',
                'match': r'.*TeamSelectionCharacterLabel',
                'target': partial(action.tap_left, gf, 0),
                'next': (task_gykc_1, 0)
            }
        ]
    ]
)

task_gykc_1.extend(
    [
        # 选择作战
        [
            {
                'type': 'break_case',
                'match': r'.*选择章节-34',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break_case',
                'match': r'.*选择章节-34',
                'target': tap_1,
                'next': 'next'
            }
        ],
        # 作战设置
        [
            {
                'type': 'break_case',
                'match': r'.*Function：Mission/combinationInfo',
                'target': 'pass',
                'next': 'next'
            }
        ],
        [
            {
                'type': 'break_case',
                'match': r'.*Decode',
                'target': partial(action.tap_normal_battle, gf),
                'next': 'next'
            }
        ],
        # 强化或初始化地图
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
        # 点击路径点1
        [
            {
                'type': 'break_case',
                'match': r'.*DeploymentFriendlyTeamController',
                'target': tap_wp_1,
                'next': 'next'
            }
        ],
        # 点击路径点2
        [
            {
                'type': 'break_case',
                'match': r'.*DeploymentPlanModeController\+TeamData',
                'target': tap_wp_2,
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
        # 结算关卡
        [
            {
                'type': 'break_case',
                'match': r'.*清除missionaction',
                'target': partial(action.tap_somewhere, gf, 6),
                'next': 'next'
            }
        ],
        # 确认人形
        [
            {
                'type': 'break_case',
                'match': r'.*播放掉落',
                'target': partial(action.tap_somewhere, gf, 4),
                'next': 'next'
            }
        ],
        # 领取奖励
        [
            {
                'type': 'break_case',
                'match': r'.*MessageboxMessageBox',
                'target': partial(gf.tap_in, *(1300, 70, 1430, 560)),
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
        ]
    ]
)

task_deassembly[-1][0]['next'] = (task_gykc_1, 0)
gf.run_task((task_gykc_1, 2), block_timeout=8)
