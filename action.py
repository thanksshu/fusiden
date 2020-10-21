"""
常用函数
"""
import time
from functools import partial
from random import SystemRandom

from gfcontrol import GFControl

random = SystemRandom()


# 其他操作
def log_func(func):
    """
    log 装饰器
    """
    def wrapper(*args, **kwargs):
        print(func.__name__)
        return func(*args, **kwargs)
    return wrapper


def sleep(sec, ratio=0.2, *, arg=None):
    """
    random sleep time
    """
    time.sleep(sec + random.uniform(0, sec * ratio))
    return


@log_func
def noise(gfcontrol: GFControl, min_times=0, max_times=3, *, arg=None):
    """
    乱点以产生噪音
    """
    if random.randint(0, 1) == 1 or min_times > 0:
        times = random.randint(min_times, max_times)
        for _ in range(0, times):
            gfcontrol.tap_in(70, 200, 300, 450)
        for _ in range(0, random.randint(0, max_times - times)):
            gfcontrol.tap_in(1170, 150, 1460, 550)


@log_func
def tap_somewhere(gfcontrol: GFControl, time_before_tap=0, *, arg=None):
    """
    结算画面随意点击
    """
    sleep(time_before_tap)
    gfcontrol.tap_in(700, 130, 1400, 700)


# 战斗
# 左侧
@log_func
def tap_left(gfcontrol: GFControl, number, *, arg=None):
    '''
    选择第n个战斗类型
    '''
    y_top = 108 + number * 90
    y_bott = 187 + number * 90
    gfcontrol.tap_in(120, y_top, 280, y_bott)


# 右侧
@log_func
def swipe_right_down(gfcontrol: GFControl, *, arg=None):
    """
    下拉到战役底
    """
    sleep(2)
    for _ in range(random.randint(2, 4)):
        gfcontrol.swipe(random.randint(540, 1370), random.randint(
            500, 600), random.randint(540, 1370), random.randint(0, 300))


@log_func
def tap_right(gfcontrol: GFControl, number, *, arg=None):
    """
    点击第n个战役
    """
    y_top = 250 + number * 119
    y_bott = 330 + number * 119
    gfcontrol.tap_in(590, y_top, 1370, y_bott)


@log_func
def tap_right_second(gfcontrol: GFControl, *, arg=None):
    """
    点击第二个战役
    """
    gfcontrol.tap_in(590, 370, 1300, 460)


# 中间
@log_func
def swpie_middle_up(gfcontrol: GFControl, *, arg=None):
    """
    滑动章节至顶
    """
    gfcontrol.swipe(360, 160, 360, 650)


@log_func
def tap_middle(gfcontrol: GFControl, number, *, arg=None):
    """
    点击第n个章节
    """
    y_top = 103 + number * 101
    y_bott = 192 + number * 101
    gfcontrol.tap_in(300, y_top, 420, y_bott)


# 上方难度
@log_func
def tap_difficuty(gfcontrol: GFControl, number, *, arg=None):
    """
    点击第n个章节
    """
    x_left = 1047 + number * 115
    x_right = 1151 + number * 115
    gfcontrol.tap_in(x_left, 160, x_right, 220)


# 作战设置/普通作战
@log_func
def tap_normal_battle(gfcontrol: GFControl, *, arg=None):
    """
    点击普通作战
    """
    gfcontrol.tap_in(1100, 570, 1200, 630)


# 作战设置/*作战/人形强化
@log_func
def tap_go_for_enhance(gfcontrol: GFControl, *, arg=None):
    """
    人形已满，去拆解
    """
    gfcontrol.tap_in(830, 470, 1000, 520)


# 战役中
# 选择梯队
@log_func
def tap_confirm(gfcontrol: GFControl, *, arg=None):
    """
    点击确定部署梯队
    """
    gfcontrol.tap_in(1200, 610, 1350, 660)  # 确定部署梯队


@log_func
def tap_formation(gfcontrol, *, arg=None):
    """
    点击队伍编成
    """
    gfcontrol.tap_in(280, 610, 440, 640)


@log_func
def tap_fast_repair(gfcontrol, number, *, arg=None):
    """
    点击人形以快速修复
    """
    x_left = 273 + number * 180
    x_right = 436 + number * 180
    gfcontrol.tap_in(x_left, 160, x_right, 580)


# 计划模式
@log_func
def tap_plan_mode(gfcontrol: GFControl, *, arg=None):
    """
    点击计划模式
    """
    gfcontrol.tap_in(50, 570, 150, 610)  # 计划模式


@log_func
def tap_start(gfcontrol: GFControl, *, arg=None):
    """
    点击 开始作战
    """
    gfcontrol.tap_in(1380, 610, 1480, 700)  # 开始作战、执行计划、结束回合


@log_func
def tap_cancel(gfcontrol: GFControl, *, arg=None):
    """
    当计划被中断，点击取消
    """
    gfcontrol.tap_in(560, 470, 710, 520)


# 编成
# 点击梯队内人形
@log_func
def tap_doll_in_team(gfcontrol, number, *, arg=None):
    """
    编队选择人形
    """
    x_left = 270 + number * 183
    x_right = 435 + number * 183
    gfcontrol.tap_in(x_left, 170, x_right, 490)


# 选择仓库内替换人形
@log_func
def tap_doll_in_warehouse(gfcontrol, line, row, *, arg=None):
    """
    仓库选择人形
    """
    x_left = 144 + row * 174
    x_right = 296 + row * 174
    y_top = 116 + line * 301
    y_bott = 393 + line * 301
    gfcontrol.tap_in(x_left, y_top, x_right, y_bott)


# 左上角返回
@log_func
def tap_goback(gfcontrol, *, arg=None):
    """
    点击左上角返回
    """
    gfcontrol.tap(212, 52)


# 工厂
# 工厂/回收拆解
@log_func
def tap_deassembly_tab(gfcontrol: GFControl, *, arg=None):
    """
    点击拆解
    """
    for _ in range(random.randint(1, 3)):
        gfcontrol.tap_in(130, 380, 290, 450)


# 工厂/回收拆解/选择角色
@log_func
def tap_choose_doll_tab(gfcontrol: GFControl, *, arg=None):
    """
    拆解，选择角色
    """
    gfcontrol.tap_in(370, 170, 520, 260)


# 工厂/回收拆解/选择角色/智能选择、确定
@log_func
def tap_smart_choose_doll_btn(gfcontrol: GFControl, *, arg=None):
    """
    智能选择、确定
    """
    gfcontrol.tap_in(1210, 590, 1370, 700)


# 工厂/回收拆解/拆解
@log_func
def tap_deassemble_btn(gfcontrol: GFControl, *, arg=None):
    """
    点击拆解
    """
    gfcontrol.tap_in(1170, 570, 1330, 630)


# 快捷导航
@log_func
def tap_shortcut_menu(gfcontrol: GFControl, *, arg=None):
    """
    开启快速菜单
    """
    gfcontrol.tap_in(300, 20, 360, 80)


# 快捷导航/战斗
@log_func
def tap_battle_btn(gfcontrol: GFControl, *, arg=None):
    """
    点击战斗圆钮
    """
    gfcontrol.tap(260, 230)


# 快捷导航/返回基地
@log_func
def tap_base_btn(gfcontrol: GFControl, *, arg=None):
    """
    点击返回基地
    """
    gfcontrol.tap_in(200, 110, 500, 170)


# 主界面
@log_func
def tap_repair(gfcontrol, *, arg=None):
    """
    进入修复
    """
    gfcontrol.tap_in(370, 560, 470, 570)


# 修复界面
# 一键修复
@log_func
def tap_onepress(gfcontrol, *, arg=None):
    """
    一键修复
    """
    gfcontrol.tap_in(1170, 650, 1400, 700)


# 一键修复确认
@log_func
def tap_onepress_confirm(gfcontrol, *, arg=None):
    """
    确认一键修复
    """
    gfcontrol.tap_in(1000, 520, 1160, 570)


# 生成拆解任务
def generate_task_deassembly(gfcontrol: GFControl, next_task):
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
