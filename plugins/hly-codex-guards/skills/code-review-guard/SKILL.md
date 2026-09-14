---
name: code-review-guard
description: Review the requested diff or user-specified review scope for real code-correctness risks. Review is read-only. This Skill owns review scope, search strategy, P0-P3 severity semantics, Finding shape, and review-result conventions.
---

# Code Review Guard

## Review Scope

- Review 只读，不修改代码，不自动修复。
- Finding 只针对当前 diff 或用户指定 Review Scope。
- Analysis Scope 可以扩展到验证当前变更所必需的调用方、被调用方、SQL、配置、数据流、契约和验证证据；分析范围扩大不等于 Finding Scope 或修改范围扩大。
- 不把与本次变更无关的历史问题纳入本次 Finding。
- 不要从 Checklist 反向寻找问题；不为了凑数量输出 Finding。
- 满足下方 Review Completion Gate，且没有明确 Finding 和 Verification Gap 时，才允许给出无风险结论。

## Review Search Strategy

先从当前 diff / Review Scope 提取实际发生变化的可观察行为，例如返回结果、状态、持久化结果、金额、权限、接口可见行为、外部交互、消息、异步结果或失败行为；再沿真实调用链闭环到这些结果。不要把“读过 diff”当成“理解了变更语义”。

只对本次变更实际触及的风险面建立证据。常见风险面包括：

- 逻辑、空值、边界和失败路径；
- 状态、事务、一致性、幂等和并发；
- 数据范围、SQL 粒度、聚合、分页及历史数据兼容；
- API / DTO / 枚举 / 序列化 / 配置等契约兼容；
- 权限、多租户、金额、结算、统计等业务口径；
- 外部接口、MQ、Job、异步、重试、补偿、缓存及发布/回滚交互。

以上不是固定 Checklist。与当前变更无关的类别不展开；相关类别不能仅因 diff 中没有直接出现对应代码就跳过。

对每个可能改变最终业务结果的 Changed Behavior，至少主动寻找一个现实可触发、能够推翻“当前实现正确”判断的主要反例；反例被当前代码或验证证据排除即可停止，不为低相关假设无限扩散。

## 独立行为复核

- Review 结论基于当前 Review Baseline 重建，不继承先前方案、实现说明、代码注释或历史结论。
- 以用户要求或确认、修改前行为和最终 diff 为依据，检查要求的行为是否实现，以及最终 diff 是否引入用户未要求的业务结果、外部交互、持久化结果、权限、状态、金额或接口可见行为变化。
- 最终 diff 引入上述额外行为变化，且没有用户明确要求或确认、当前有效需求/契约或已确认缺陷作为依据时：能够从当前代码、配置、数据流或调用链确认变化已经发生，形成 Finding；无法确认变化是否发生时，记录 Verification Gap。
- 只有缺少证据导致无法判断以下任一事项时，记录 Verification Gap：用户要求的行为是否实现；最终 diff 是否引入上述额外行为变化；与当前 diff 直接相关、现实可触发且一旦成立足以推翻无风险结论的关键行为路径或相关风险面是否已被排除或证实。其他与这些判断无关的未知项不形成 Verification Gap。
- 仅改变内部实现且上述结果均不变时，不视为额外行为变化。
- Verification Gap 不虚构成 Finding，也不得把对应行为表述为已验证正确或兼容。

## Review Completion Gate

- 无风险结论必须建立在与当前 diff 直接相关的 Changed Behavior、关键行为路径和相关风险面已经闭环到结果之上，不能仅因当前尚未发现 Finding 或 Verification Gap 就结束 Review。
- 对相关风险面，Review 内部应能够判断为：已有证据确认、与当前变更不适用，或存在 Verification Gap；无需把该状态机械输出成检查表。
- 若某条与当前 diff 直接相关、现实可触发且一旦成立足以推翻无风险结论的关键行为路径或主要反例尚未取得证据，继续调查；受环境或证据限制无法判断时，记录 Verification Gap。
- 当用户要求行为、额外行为变化、相关风险面及主要反例路径均已有足够证据，且没有现实证据支持其他能够推翻当前结论的主要路径时，才允许结束 Review 并给出无风险结论。

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

- 每个 Finding 使用稳定编号 `RISK-001`、`RISK-002`……，按本次 Review 输出顺序递增。
- 后续复核、讨论或修复同一 Finding 时沿用原编号，不因风险等级或结论变化重新编号。

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

优先输出真实 Findings，再列 Verification Gaps，最后给整体结论。

如果没有明确风险且不存在 Verification Gap，直接写：

`未发现明确 P0/P1/P2/P3 风险。`

存在 Verification Gap 时，说明缺失证据以及无法判定的具体问题；不得给出无条件无风险或可交付结论。
