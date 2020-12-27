"""
常用函数
"""
import json
from random import SystemRandom

import fusiden

with open('target.json') as fp:
    target = json.load(fp)

random = SystemRandom()


# 其他操作
def noise(gfcontrol: fusiden.GFControl, min_times=0, max_times=3, *, task_info=None):
    """
    乱点以产生噪音
    """
    if random.randint(0, 1) == 1 or min_times > 0:
        times = random.randint(min_times, max_times)
        for _ in range(0, times):
            gfcontrol.tap_in([70, 200], [300, 450])
        for _ in range(0, random.randint(0, max_times - times)):
            gfcontrol.tap_in([1250, 150], [1300, 550])


# combat factory research
def tap_left(gfcontrol: fusiden.GFControl, number, *, task_info=None):
    '''
    combat 左侧 选择
    '''
    y_top = 108 + number * 90
    y_bott = 187 + number * 90
    gfcontrol.tap_in([120, y_top], [280, y_bott])


# combat
def tap_right(gfcontrol: fusiden.GFControl, number, *, task_info=None):
    """
    combat 右侧 选择
    """
    y_top = 260 + number * 119
    y_bott = 330 + number * 119
    gfcontrol.tap_in([590, y_top], [1370, y_bott])


# combat
def tap_middle(gfcontrol: fusiden.GFControl, number, *, task_info=None):
    """
    combat 中间 选择
    """
    y_top = 103 + number * 101
    y_bott = 192 + number * 101
    gfcontrol.tap_in([300, y_top], [420, y_bott])


# combat
def tap_difficuty(gfcontrol: fusiden.GFControl, number, *, task_info=None):
    """
    combat 右上 选择
    """
    x_left = 1047 + number * 115
    x_right = 1151 + number * 115
    gfcontrol.tap_in([x_left, 160], [x_right, 220])


# battle team
def tap_fast_repair(gfcontrol, number, *, task_info=None):
    """
    battle 点击梯队内人形
    """
    x_left = 323 + number * 180
    x_right = 436 + number * 180
    gfcontrol.tap_in([x_left, 160], [x_right, 580])


# formation
def tap_doll_in_team(gfcontrol, number, *, task_info=None):
    """
    formation 编队选择人形
    """
    x_left = 340 + number * 183
    x_right = 400 + number * 183
    gfcontrol.tap_in([x_left, 170], [x_right, 490])


# warehouse
def tap_doll_in_warehouse(gfcontrol, line, row, *, task_info=None):
    """
    warehouse 选择人形
    """
    x_left = 210 + row * 174
    x_right = 260 + row * 174
    y_top = 170 + line * 301
    y_bott = 330 + line * 301
    gfcontrol.tap_in([x_left, y_top], [x_right, y_bott])


# 生成拆解任务
def generate_chain_deassembly(gfcontrol: fusiden.GFControl, next_task):
    '''
    return task deassembly
    '''
    task = [
        # 点击拆解
        [
            {
                'type': 'break',
                'match': r'.*预加载结束',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['factory.deassembly.tpi']),
                'next': 'next'
            }
        ],
        # 点击选择人形
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['factory.deassembly.doll.tpi'], delay=0.5),
                'next': 'next'
            }
        ],
        # 点击智能选择
        [
            {
                'type': 'break',
                'match': r'.*CharacterListLabel',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['warehouse.confirm.tpi']),
                'next': 'next'
            }
        ],
        # 点击确定
        [
            {
                'type': 'break',
                'match': r'.*实例化数目0销毁数目0',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['warehouse.confirm.tpi']),
                'next': 'next'
            }
        ],
        # 拆解
        [
            {
                'type': 'break',
                'match': r'.*SmallGunItem',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['factory.deassembly.deassembly.tpi']),
                'next': 'next'
            },
            # 再无低星人形
            {
                'type': 'break',
                'match': r'.*实例化数目0销毁数目0',
                'target': 'pass',
                'next': None
            }
        ],
        # 结束
        [
            {
                'type': 'break',
                'match': r'.*Gun/retireGun',
                'target': 'pass',
                'next': next_task
            }
        ],
    ]
    return task


# 生成强化任务
def generate_chain_enhance(gfcontrol: fusiden.GFControl, next_task):
    '''
    return task enhance
    '''
    task = [
        # 点击强化
        [
            {
                'type': 'break',
                'match': r'.*预加载结束',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['factory.enhance.tpi']),
                'next': 'next'
            }
        ],
        # 点击“选择人形”
        [
            {
                'type': 'direct',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['factory.enhance.choose_main.tpi'], delay=0.2),
                'next': 'next'
            }
        ],
        # 选择人形
        [
            {
                'type': 'break',
                'match': r'.*UGUIPrefabs/CharacterList/CharacterListLabel',
                'target': fusiden.pack(tap_doll_in_warehouse, args=(gfcontrol, 0, 0), delay=0.5),
                'next': 'next'
            },
        ],
        # 不可编辑 点击选择素材
        # TODO: 结束失败
        [
            # 含有不可编辑人形
            {
                'type': 'break',
                'match': r'.*CharacterDisabled',
                'target': 'pass',
                'next': 'self'
            },
            # 不可编辑
            {
                'type': 'break',
                'match': r'.*LiteMessageTips',
                'target': 'pass',
                'next': None
            },
            # 点击选择素材
            {
                'type': 'direct',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['factory.enhance.choose_sub.tpi'],
                                       delay=0.2),
                'next': 'next'
            }
        ],
        # 点击智能选择
        [
            {
                'type': 'break',
                'match': r'.*实例化数目',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['warehouse.confirm.tpi']),
                'next': 'next'
            }
        ],
        # 点击确定
        [
            {
                'type': 'break',
                'match': r'.*实例化数目0销毁数目0',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['warehouse.confirm.tpi']),
                'next': 'next'
            }
        ],
        # 强化 再无低星人形
        [
            # 强化
            {
                'type': 'break',
                'match': r'.*SmallGunItem',
                'target': fusiden.pack(gfcontrol.tap_in,
                                       args=target['factory.enhance.enhance.tpi']),
                'next': 'next'
            },
            # 再无低星人形
            {
                'type': 'break',
                'match': r'.*实例化数目0销毁数目0',
                'target': 'pass',
                'next': None
            },
        ],
        # 结束
        [
            {
                'type': 'break',
                'match': r'.*eatGun',
                'target': 'pass',
                'next': next_task
            }
        ],
    ]
    return task
