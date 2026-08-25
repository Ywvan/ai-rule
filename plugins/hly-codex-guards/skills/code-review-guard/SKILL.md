---
name: code-review-guard
description: Review the requested diff or user-specified review scope for real code-correctness risks. Review is read-only. This Skill owns review scope, P0-P3 severity semantics, Finding shape, and review-result conventions.
---

# Code Review Guard

## 使用声明

使用本 Skill 时，简短说明正在进行 `$code-review-guard` 只读 Review。

## Review Scope

- Review 只读，不修改代码，不自动修复。
- Finding 只针对当前 diff 或用户指定 Review Scope。
- 为判断当前 Finding 可以读取 Scope 外相关代码、SQL、配置和调用方，但不把与本次变更无关的历史问题纳入本次 Finding。
- 不要从 Checklist 反向寻找问题；不为了凑数量输出 Finding。
- 没有明确问题时允许直接给出无风险结论。

## 风险等级

### P0

会造成严重生产事故、重大数据破坏、安全事故或系统不可用，且触发条件现实明确。

### P1

高概率造成核心业务错误、金额 / 结算 / 权限 / 状态严重错误、接口不可用或大范围回归。

### P2

会造成明确功能错误、边界场景错误、兼容问题或具有现实影响的性能 / 可维护性风险，但影响范围有限。

### P3

与当前 diff 直接相关、有明确现实影响的低风险问题，例如必要可观测性缺失、具体误导性命名或明显不必要复杂度。

纯个人风格偏好不是 P3。

## Finding 格式

每个 Finding 至少说明：

- 严重级别；
- 问题；
- 触发条件；
- 证据；
- 影响；
- 最小修复方向（能够可靠判断时）。

Review Finding 是待后续复核的问题判断，不成为新的需求事实。

## SQL Finding

SQL 相关 Finding 需要说明实际语义或风险来源，例如：

- 目标数据粒度被 JOIN / 聚合 / 去重改变；
- `LEFT JOIN` 与 `WHERE` 组合改变目标范围；
- 租户、权限或有效状态条件发生错误；
- 分页结果不稳定；
- 存在有现实影响的性能问题；
- 不必要复杂结构直接造成维护或正确性风险。

CTE、`DISTINCT`、窗口函数、子查询或 `COALESCE` 本身不直接形成 Finding。

## 输出

优先输出真实 Findings，再给整体结论。

如果没有明确风险，直接写：

`未发现明确 P0/P1/P2/P3 风险。`
