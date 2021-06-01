# 少女前线自动化

-   chain 任务链为数组，内有多个 task
-   task 任务为数组，内有多个 condition
-   condition 为字典，包含多对键值:
    -   `type`:
        -   `break`: 匹配 match 后执行 target 并进行 next 任务
        -   `case`: 执行后会接着匹配下一 condition，无 next
        -   `direct`: 跳过匹配直接执行并进行下一任务，无 match
    -   `match`: 等待匹配的正则表达式
    -   `target`: 匹配后执行的函数，回调时传入任务链信息`info`的引用
        -   `info` 任务链信息:
            -   `'chain'`: 本 target 所在任务链
            -   `'task_index'`: int 对象，本 target 所在 task 在其 chain 中的索引
            -   `'task'`: 本 target 所在 task
            -   `'condition_index'`: int 对象，本 target 所在 condition 在其 task 中的索引
            -   `'condition'`: dict 对象，本 target 所在 condition
            -   `'match_result'`:
            -   `'block_timeout'`: int 对象，当超过此时间游戏仍无抛出新 log 则执行 timeout_target
            -   `'timeout_target'`: Callable 对象，在超时时执行，默认为上一次执行的 target
            -   `'stop_event'`: Event 对象，决定是否停止任务链
    -   `next`: 下一任务，有以下几种:
        -   `'next'`: 等效 `['relev', 1]`
        -   `'pre'`: 等效 `['relev', -1]`
        -   `'self'`: 等效 `['relev', 0]`
        -   `['relev', int]`: 任务链中，本 condition 所在任务的后第 int 任务
        -   `['absol', int]`: 任务链中的第 int 任务
