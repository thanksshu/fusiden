"""
常用函数
"""
import time
from random import SystemRandom
from functools import partial

from gfcontrol import GFControl

random = SystemRandom()


# 其他操作

def log_func(func):
    """
    log 装饰器
    """
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper


@log_func
def swipe_down(gfcontrol: GFControl):
    """
    下拉到底
    """
    sleep(2)
    for _ in range(random.randint(2, 4)):
        gfcontrol.swipe(random.randint(540, 1370), random.randint(
            500, 600), random.randint(540, 1370), random.randint(0, 300))


@log_func
def sleep(sec, ratio=0.2):
    """
    random sleep time
    """
    time.sleep(sec + random.uniform(0, sec * ratio))
    return


@log_func
def noise(gfcontrol: GFControl, max_times):
    """
    乱点以产生噪音
    """
    if random.randint(0, 1) == 1:
        times = random.randint(0, max_times)
        for _ in range(0, times):
            gfcontrol.tap_in(70, 200, 300, 450)
        for _ in range(0, random.randint(0, max_times - times)):
            gfcontrol.tap_in(1170, 150, 1460, 550)


@log_func
def tap_somewhere(gfcontrol: GFControl, time_before_tap=0):
    """
    结算画面随意点击
    """
    sleep(time_before_tap)
    gfcontrol.tap_in(10, 130, 1400, 700)

# 战斗选择


@log_func
def tap_left_first(gfcontrol: GFControl):
    '''
    tap left first one
    '''
    sleep(2)
    gfcontrol.tap_in(120, 110, 280, 180)


@log_func
def tap_right_fourth(gfcontrol: GFControl):
    """
    点击第四个战役
    """
    gfcontrol.tap_in(590, 560, 1370, 640)


def tap_right_second(gfcontrol: GFControl):
    """
    点击第二个战役
    """
    gfcontrol.tap_in(590, 370, 1430, 460)

# 作战设置/普通作战


@log_func
def tap_normal_battle(gfcontrol: GFControl):
    """
    点击普通作战
    """
    gfcontrol.tap_in(1100, 570, 1200, 630)


# 作战设置/*作战/人形强化

@log_func
def tap_go_for_enhance(gfcontrol: GFControl):
    """
    人形已满，去拆解
    """
    gfcontrol.tap_in(830, 470, 1000, 520)


# 战役中

@log_func
def tap_confirm(gfcontrol: GFControl):
    """
    点击确定部署梯队
    """
    gfcontrol.tap_in(1200, 610, 1350, 660)  # 确定部署梯队


@log_func
def tap_plan_mode(gfcontrol: GFControl):
    """
    点击计划模式
    """
    gfcontrol.tap_in(50, 570, 150, 610)  # 计划模式


@log_func
def tap_start(gfcontrol: GFControl):
    """
    点击 开始作战
    """
    gfcontrol.tap_in(1380, 610, 1480, 700)  # 开始作战、执行计划、结束回合


# 工厂
# 工厂/回收拆解
@log_func
def tap_deassembly_tab(gfcontrol: GFControl):
    """
    点击拆解
    """
    sleep(1)
    for _ in range(random.randint(2, 4)):
        gfcontrol.tap_in(130, 380, 290, 450)


# 工厂/回收拆解/选择角色

@log_func
def tap_choose_doll_tab(gfcontrol: GFControl):
    """
    拆解，选择角色
    """
    gfcontrol.tap_in(370, 170, 520, 260)


# 工厂/回收拆解/选择角色/智能选择、确定

@log_func
def tap_smart_choose_doll_btn(gfcontrol: GFControl):
    """
    智能选择、确定
    """
    gfcontrol.tap_in(1210, 590, 1370, 700)


# 工厂/回收拆解/拆解
@log_func
def tap_deassemble_btn(gfcontrol: GFControl):
    """
    点击拆解
    """
    gfcontrol.tap_in(1170, 570, 1330, 630)


# 快捷导航

@log_func
def tap_shortcut_menu(gfcontrol: GFControl):
    """
    开启快速菜单
    """
    gfcontrol.tap_in(300, 20, 360, 80)


# 快捷导航/战斗
@log_func
def tap_battle_btn(gfcontrol: GFControl):
    """
    点击战斗圆钮
    """
    gfcontrol.tap(260, 230)


# 拆解任务
def task_deassembly(gfcontrol: GFControl, next_task):
    '''
    return task deassembly
    '''
    task = [
        # 点击拆解tab
        [
            {
                'type': 'break_case',
                'match': r'预加载结束',
                'target': partial(tap_deassembly_tab, gfcontrol),
                'next': 'next'
            }
        ],
        # 点击选择人形
        [
            {
                'type': 'default',
                'target': partial(tap_choose_doll_tab, gfcontrol),
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
                'target': partial(tap_smart_choose_doll_btn, gfcontrol),
                'next': 'next'
            }
        ],
        # 点击确定
        [
            {
                'type': 'break_case',
                'match': r'.*实例化数目0销毁数目0',
                'target': partial(tap_smart_choose_doll_btn, gfcontrol),
                'next': 'next'
            }
        ],
        # 点击拆解
        [
            {
                'type': 'default',
                'target': partial(tap_deassemble_btn, gfcontrol),
                'next': 'next'
            }
        ],
        # 拆解结束，打开快捷菜单
        [
            {
                'type': 'break_case',
                'match': r'.*retireGun',
                'target': partial(tap_shortcut_menu, gfcontrol),
                'next': 'next'
            }
        ],
        # 菜单弹出，点击战斗
        [
            {
                'type': 'break_case',
                'match': r'.*RefreshRewardMail',
                'target': partial(tap_battle_btn, gfcontrol),
                'next': next_task
            }
        ]
    ]
    return task
