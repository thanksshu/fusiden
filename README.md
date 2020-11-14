# 少女前线自动化

- condition 为字典，包含多对键值
- task 为数组，内有多个 condition
- chain 为数组，内有多个 task

## condition

- `type`：
    - `break`：匹配后执行
    - `case`：执行后会接着执行下一`condition`，无`next`
    - `direct`：跳过匹配直接执行，无`match`，
