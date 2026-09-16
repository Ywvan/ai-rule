---
name: code-review-guard
description: Review the requested diff or user-specified review scope for real code-correctness risks. Review is read-only. This Skill owns review scope, P0-P3 severity semantics, Finding shape, and review-result conventions.
---

# Code Review Guard

## Review Scope

- Review 只读，不修改代码，不自动修复。
- Finding 只针对当前 diff 或用户指定 Review Scope。
- Analysis Scope 可以扩展到理解当前变更所需的调用方、被调用方、SQL、配置、数据流、契约和验证证据；分析范围扩大不等于 Finding Scope 或修改范围扩大。
- 不把与本次变更无关的历史问题纳入 Finding，不为了凑数量制造问题。

## Review Method

从当前 diff / Review Scope 识别实际改变的可观察行为，例如返回结果、状态、持久化结果、金额、权限、接口行为、外部交互、消息、异步结果或失败行为，再读取足以判断这些变化是否正确的相关代码与证据。

重点关注与当前变更直接相关、可能造成真实业务错误的路径，包括逻辑与边界、状态与一致性、数据范围、接口与序列化契约、权限 / 多租户 / 金额口径，以及外部接口、MQ、Job、重试和补偿等。只调查实际相关的风险面，不机械跑固定 Checklist。

当前 diff、调用链、配置、契约或验证结果已经暴露，且不同取值会改变 Finding 或“无风险”结论的事实，必须验证或记录 Verification Gap；未由当前证据暴露的纯理论可能性不主动枚举。已处理上述事实且不存在未解释的冲突证据时结束分析，不为完整性扩展到与当前变更无关的路径。

## Review Completion Gate

只有同时满足以下条件，才给出无风险结论：当前 diff 的可观察行为变化已定位到实际影响路径；上述会改变结论的已暴露事实均已验证；不存在未解释的冲突证据；不存在阻塞判断的 Verification Gap。Review 不因“暂时没发现问题”自动通过，也不要求为完整性穷尽与当前变更无关的路径。

## 风险等级

### P0

会造成严重生产事故、重大数据破坏、安全事故或系统不可用，且触发条件现实明确。

### P1

高概率造成核心业务错误、金额 / 结算 / 权限 / 状态严重错误、接口不可用或大范围回归。

### P2

会造成明确功能错误、边界场景错误、兼容问题或具有现实影响的性能 / 可维护性风险，但影响范围有限。

### P3

与当前 diff 直接相关、有明确现实影响的低风险问题，例如必要可观测性缺失、具体误导性命名或明显不必要复杂度。纯个人风格偏好不是 P3。

## Finding 格式

每个 Finding 至少说明：

- 严重级别；
- 问题；
- 触发条件；
- 证据；
- 影响；
- 最小修复方向（能够可靠判断时）。

每个 Finding 使用稳定编号 `RISK-001`、`RISK-002`……，按本次 Review 输出顺序递增；后续复核、讨论或修复同一 Finding 时沿用原编号。

Review Finding 是待后续复核的问题判断，不成为新的需求事实。

## SQL Finding

SQL 相关 Finding 需要说明实际语义或风险来源，例如数据粒度、JOIN / 聚合结果、过滤范围、租户 / 权限 / 有效状态、分页稳定性或现实性能影响。CTE、`DISTINCT`、窗口函数、子查询或 `COALESCE` 本身不直接形成 Finding。

## 输出

优先输出真实 Findings，再列 Verification Gaps，最后给整体结论。

如果没有明确风险且不存在 Verification Gap，直接写：

`未发现明确 P0/P1/P2/P3 风险。`

存在 Verification Gap 时，说明缺失证据以及无法判定的具体问题；不得给出无条件无风险或可交付结论。
