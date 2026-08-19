---
name: code-review-guard
description: Review the requested diff or review scope for real code-correctness risks. Use when the user asks for code review, current diff review, SQL review, logging review, or explicitly invokes $code-review-guard. Review is read-only and evidence-based.
---

# Code Review Guard

## 使用声明

执行本 Skill 的实质性操作前，简短说明正在使用 `$code-review-guard` 进行只读代码 Review。不要用长篇流程说明打断 Review。

## Goal

只检查当前 diff 或用户指定范围内的真实代码风险。

- Review 只读，不修改代码，不自动修复。
- 允许读取必要上下游代码验证风险，但不扩展到无关历史问题。
- Finding 必须有代码、SQL、配置、调用链或验证证据支持。
- 不确定的判断标记“不确定”，不要为了凑数量输出问题。

## Review 原则

先理解变更实际语义，再判断风险。不要从 Checklist 反向寻找问题。

根据本次变更实际涉及内容按需检查：

- 业务和代码逻辑错误；
- 空值、边界条件和异常路径；
- 事务、一致性、幂等和并发；
- 状态流转与兼容性；
- API / DTO / 枚举 / 序列化兼容；
- 权限、多租户和数据范围；
- 金额、结算、统计和报表口径；
- SQL 正确性、数据粒度、JOIN / 聚合 / 去重、分页稳定性与明确性能风险；
- 外部调用、MQ、Job、异步、缓存等边界；
- 与本次 diff 直接相关的必要日志和注释。

只有相关时才检查对应类别。不要机械遍历所有风险类型。

## SQL Review

SQL Review 优先检查：

1. 业务口径和数据范围是否正确；
2. JOIN、过滤、聚合、去重是否改变目标粒度；
3. LEFT JOIN / WHERE、租户条件、有效状态等是否改变语义；
4. 是否存在明确的性能或分页稳定性问题；
5. 写法是否存在明显不必要复杂度。

`DISTINCT`、CTE、子查询、窗口函数、`COALESCE` 等本身不是问题。只有当它们掩盖数据膨胀、改变业务口径、显著增加复杂度或引入真实性能风险时才形成 Finding。

## 风险等级

### P0

会造成严重生产事故、重大数据破坏、安全事故或系统不可用，且触发条件现实明确。

### P1

高概率造成核心业务错误、金额 / 结算 / 权限 / 状态严重错误、接口不可用或大范围回归。

### P2

会造成明确功能错误、边界场景错误、兼容问题或具有现实影响的性能 / 可维护性风险，但影响范围有限。

### P3

与当前 diff 直接相关、有明确证据的低风险问题，例如容易造成具体误解的命名、明显缺失的必要日志、SQL 有明确更简单的等价写法等。

禁止把纯个人风格偏好列为 P3。

## Finding 要求

每个 Finding 说明：

- 严重级别；
- 问题；
- 触发条件；
- 证据；
- 影响；
- 最小修复方向（仅当能够可靠判断）。

Review Finding 是待后续复核的问题判断，不是新的需求事实。后续修复仍应重新读取当前代码确认它是否成立。

如果没有明确风险，直接写：`未发现明确 P0/P1/P2/P3 风险。`

## 输出风格

使用直接、易读的中文工程语言。优先描述具体代码行为和影响，不输出大段 Review 方法论、流程承诺或模板化复盘。
