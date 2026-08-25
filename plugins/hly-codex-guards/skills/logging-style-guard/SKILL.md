---
name: logging-style-guard
description: Use when Codex writes, modifies, or reviews Java/Spring business code whose current change needs production observability. This Skill owns logging placement, business-key selection, deduplication, loop aggregation, and sensitive-field details.
---

# Logging Style Guard

## 使用声明

使用本 Skill 时，简短说明正在应用 `$logging-style-guard`。

## 适用范围

只检查当前任务实际新增或改变的业务链路是否具备足够的生产定位信息；不为了统一风格改造历史日志。

日志 Review 保持只读。

## 日志节点选择

当前变更涉及以下节点时，优先判断是否需要留下可定位的业务结果：

- 外部接口请求结果；
- MQ 生产 / 消费；
- Job、批量任务；
- 第三方回调；
- 异步、重试、补偿；
- 关键状态变化；
- 支付、金额、结算结果；
- 业务拒绝、跳过、回退；
- 改变业务结果的异常捕获；
- 权限或数据范围拒绝。

已有上下层日志能够完整定位同一业务节点时，不在相邻层重复记录相同信息。

## 业务定位键

日志优先包含能够定位业务数据的稳定键，例如：

- `orderNo`
- `supplierOrderNo`
- `tenantId`
- `companyOid`
- `employeeOid`
- `journeyNo`
- `approvalNo`
- `batchNo`

不要为了“信息完整”打印整个 DTO、VO、Entity、Request 或 Response。

## 日志内容

- 使用参数化占位符，不用字符串拼接构造日志正文；
- 异常日志保留完整异常对象 / 堆栈，不只打印 `getMessage()`；
- 文案描述业务节点和实际结果，不使用 `enter method`、`leave method`、`method start` 等无业务信息文本；
- 同一个异常由明确业务边界记录后，下层不重复打印同一堆栈，除非下层拥有上层无法获得的关键定位信息。

## 敏感信息

不得直接记录：

- password / secret；
- token / accessToken / refreshToken；
- sign / Cookie / 认证材料；
- 完整身份证号、银行卡号；
- 完整手机号、完整邮箱；
- 完整请求体、响应体或大段 JSON。

确需定位时只记录经过脱敏且与问题定位直接相关的字段。

## 高频与循环

- 不在循环中逐条打印正常成功日志；
- 批量任务优先记录批次、总量、成功 / 失败数量和必要失败样例；
- 高频查询、普通 CRUD、DTO 转换和工具方法不新增逐次正常日志；
- 多层调用只保留能够形成清晰业务定位链路的节点，避免每层重复同一上下文。

## 变更同步

当前业务修改导致已有日志语义失真时，同步修正该日志；已有日志仍准确且足以定位时，不为了本 Skill 产生额外日志 diff。

## Review 输出

日志专项 Review 只报告与当前 diff 直接相关的实际问题，例如：

- 关键失败路径完全不可定位；
- 缺少业务定位键；
- 异常堆栈丢失；
- 重复 / 循环 / 高频日志；
- 敏感信息泄露；
- 因当前改动导致日志语义已经失真。

最终只需说明发现的问题或“当前 diff 未发现明确日志风险”，不输出完整检查表。
