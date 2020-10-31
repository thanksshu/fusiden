"""
常用函数
"""
import json
from functools import partial
from random import SystemRandom

from fusiden import GFControl
from fusiden.utils import log_func

with open('/home/thanksshu/Documents/Girlsfront/target.json') as fp:
    target = json.load(fp)

random = SystemRandom()


# 其他操作
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
            gfcontrol.tap_in(1250, 150, 1460, 550)


# combat factory research
@log_func
def tap_left(gfcontrol: GFControl, number, *, arg=None):
    '''
    combat 左侧 选择
    '''
    y_top = 108 + number * 90
    y_bott = 187 + number * 90
    gfcontrol.tap_in(120, y_top, 280, y_bott)


# combat
@log_func
def tap_right(gfcontrol: GFControl, number, *, arg=None):
    """
    combat 右侧 选择
    """
    y_top = 250 + number * 119
    y_bott = 330 + number * 119
    gfcontrol.tap_in(590, y_top, 1370, y_bott)


# combat
@log_func
def tap_middle(gfcontrol: GFControl, number, *, arg=None):
    """
    combat 中间 选择
    """
    y_top = 103 + number * 101
    y_bott = 192 + number * 101
    gfcontrol.tap_in(300, y_top, 420, y_bott)


# combat
@log_func
def tap_difficuty(gfcontrol: GFControl, number, *, arg=None):
    """
    combat 右上 选择
    """
    x_left = 1047 + number * 115
    x_right = 1151 + number * 115
    gfcontrol.tap_in(x_left, 160, x_right, 220)


# battle team
@log_func
def tap_fast_repair(gfcontrol, number, *, arg=None):
    """
    battle 点击梯队内人形
    """
    x_left = 323 + number * 180
    x_right = 436 + number * 180
    gfcontrol.tap_in(x_left, 160, x_right, 580)


# formation
@log_func
def tap_doll_in_team(gfcontrol, number, *, arg=None):
    """
    formation 编队选择人形
    """
    x_left = 320 + number * 183
    x_right = 390 + number * 183
    gfcontrol.tap_in(x_left, 170, x_right, 490)


# warehouse
@log_func
def tap_doll_in_warehouse(gfcontrol, line, row, *, arg=None):
    """
    warehouse 选择人形
    """
    x_left = 180 + row * 174
    x_right = 260 + row * 174
    y_top = 170 + line * 301
    y_bott = 330 + line * 301
    gfcontrol.tap_in(x_left+50, y_top, x_right, y_bott)


# 生成拆解任务
def generate_chain_deassembly(gfcontrol: GFControl, next_task):
    '''
    return task deassembly
    '''
    task = [
        # 点击拆解
        [
            {
                'type': 'break_case',
                'match': r'.*RetireMain',
                'target': partial(gfcontrol.tap_in, *target['factory.deassembly.tpi']),
                'next': 'next'
            }
        ],
        # 点击选择人形
        [
            {
                'type': 'default',
                'target': partial(gfcontrol.tap_in, *target['factory.deassembly.doll.tpi']),
                'next': 'next'
            }
        ],
        # 点击智能选择
        [
            {
                'type': 'break_case',
                'match': r'.*CharacterListLabel',
                'target': partial(gfcontrol.tap_in, *target['warehouse.confirm.tpi']),
                'next': 'next'
            }
        ],
        # 点击确定
        [
            {
                'type': 'break_case',
                'match': r'.*实例化数目0销毁数目0',
                'target': partial(gfcontrol.tap_in, *target['warehouse.confirm.tpi']),
                'next': 'next'
            }
        ],
        # 拆解
        [
            {
                'type': 'break_case',
                'match': r'.*SmallGunItem',
                'target': partial(gfcontrol.tap_in, *target['factory.deassembly.deassembly.tpi']),
                'next': 'next'
            },
            # 再无低星人形
            {
                'type': 'break_case',
                'match': r'.*实例化数目0销毁数目0',
                'target': 'pass',
                'next': None
            },
        ],
        # 打开快捷菜单
        [
            {
                'type': 'break_case',
                'match': r'.*retireGun',
                'target': partial(gfcontrol.tap_in, *target['global.shortcut.tpi']),
                'next': 'next'
            }
        ],
        # 点击战斗
        [
            {
                'type': 'default',
                'target': partial(gfcontrol.tap, *target['shortcut.combat.tp']),
                'next': next_task
            }
        ]
    ]
    return task
