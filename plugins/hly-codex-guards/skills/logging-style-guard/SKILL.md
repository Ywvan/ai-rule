---
name: logging-style-guard
description: Use when Codex generates, modifies, or reviews Java/Spring Boot business code involving external calls, MQ, jobs, callbacks, async flows, compensation or retries, state transitions, payment or settlement results, business rejection, skips, fallbacks, or exception paths that can change business outcomes, as well as related logging. Enforce minimal valuable INFO/ERROR logging within the current diff, prohibit DEBUG/TRACE/WARN, require business keys and full exception stack traces, prevent sensitive data leaks, and avoid duplicate logs, high-frequency logs, meaningless logs, loop logs, getter/setter logs, DTO/VO conversion logs, DAO CRUD logs, and tool-method logs.
---

# Codex 日志打印规范

## 使用声明

- 执行本 Skill 的任何实质性操作前，必须先在用户可见消息中明确声明：`正在使用 $<Skill 名称>：<使用原因>`。
- 同时使用多个 Skill 时，必须一次列出全部 Skill 及使用顺序。
- 不得只在最终答复中事后补充声明；如果当前环境没有独立的进度消息通道，应在首条可见回复中声明。

## 核心原则

- 日志用于快速定位问题、还原业务过程、支撑线上排查，并控制日志量。
- 日志不是越多越好；无法帮助定位问题的日志视为无效日志。
- 默认只允许使用 `INFO` 和 `ERROR`。
- 禁止使用 `DEBUG`、`TRACE`、`WARN`。
- `WARN` 场景统一使用 `INFO`，并在日志文案中增加 `[WARNING]` 标识。

## 执行边界

执行策略由 Codex Native Harness 决定。本 Skill 只定义当前授权 diff 内的日志质量和可观测性约束，不规定任务拆分、执行顺序或 Agent 使用方式。

- 日志 Review 始终保持只读。
- 日志修改不得扩大用户授权范围。
- 并行修改不改变日志去重、敏感信息和最终一致性要求。

## 当前日志边界

- 日志 Review 任务始终保持只读；
- 日志检查和修改义务仅限当前任务授权的 diff，不得因委派或并行执行扩大范围。

## 日志最小化

默认不修改当前任务范围之外的日志。

当前 diff 新增或改变关键业务行为时，必须检查当前修改范围内是否具备必要日志。

除非任务明确要求日志改造，或当前 diff 的关键链路确实缺失必要日志，否则禁止：

- 新增日志
- 修改日志
- 删除日志
- 调整日志级别
- 修改日志文案或结构

日志变更必须能够说明原因、排查价值和对应业务链路。无法说明价值的日志不要新增。

## 必须打印日志的场景

只检查当前 diff 中新增或修改的以下关键业务行为是否具备必要日志：

- 外部接口调用；
- MQ 生产或消费；
- Job 和批量任务；
- 第三方回调；
- 异步、补偿或重试；
- 状态流转；
- 支付、金额或结算结果；
- 业务拒绝、跳过、回退或提前返回；
- 改变业务结果的异常捕获；
- 权限或数据范围拒绝。

关键异常必须记录 `ERROR` 日志并打印完整异常堆栈。批量任务应记录批次、执行结果和汇总数量，不在循环中逐条打印正常日志。

## 禁止打印日志的场景

禁止在以下位置新增日志：

- Getter / Setter
- DTO / VO 转换
- Bean 复制
- MapStruct 转换
- Repository 调用
- Mapper 调用
- DAO 层普通 CRUD
- 工具类
- 日期转换
- 字符串处理
- 判空逻辑

## 入口出口日志

禁止无意义的入口、出口日志，例如：

- `enter method`
- `leave method`
- `method start`
- `method finish`

只有 Controller、MQ、Job 或第三方回调入口需要定位业务入口时，才允许保留必要入口日志。

## 循环日志

- 禁止在循环内部逐条打印日志。
- 需要观察批量处理结果时，汇总后统一打印数量、失败原因分布、关键业务主键样例等信息。

## 日志内容规范

### 业务主键

日志应优先包含能定位业务数据的主键，例如：

- `orderNo`
- `supplierOrderNo`
- `tenantId`
- `employeeOid`
- `companyOid`
- `journeyNo`
- `approvalNo`
- `batchNo`

### 占位符

- 必须使用日志占位符。
- 禁止用字符串拼接构造日志内容。

### 异常堆栈

- `ERROR` 日志必须打印完整异常堆栈。
- 禁止只打印异常消息。

## 敏感信息

禁止打印以下敏感信息：

- `password`
- `token`
- `accessToken`
- `refreshToken`
- `sign`
- `secret`
- 身份证号
- 银行卡号
- 完整手机号
- 完整邮箱

禁止打印完整请求、响应、DTO、VO、Entity 或认证材料。

无法确认字段是否敏感时，默认不打印。

## 重复和高频日志

- 已有日志能够完整覆盖时，不重复新增。
- 高频查询、循环、逐条转换和普通 CRUD，默认不新增逐次正常 `INFO` 日志。
- 多个调用层或并行修改不得重复打印相同业务节点、相同异常和相同业务上下文。

## 非日志需求

当前任务即使不是日志专项改造，只要当前 diff 新增或改变了关键业务行为，也必须在当前修改范围内检查并补齐必要日志。

允许：

- 补充当前新增关键节点的必要日志；
- 补充当前新增异常、拒绝、跳过、回退和状态流转的必要日志；
- 更新因当前业务改动而失真的日志。

禁止：

- 修改当前任务范围之外的历史日志；
- 全文件、全模块或全链路补日志；
- 统一改写历史日志文案；
- 因补日志改变业务逻辑、接口协议或 SQL 口径。

补充当前 diff 的必要日志不得改变任务阶段或扩大修改范围。

## Code Review 检查项

Review 日志相关代码时重点检查：

- 是否缺少关键业务日志
- 是否缺少异常日志
- 是否打印业务主键
- 是否打印完整异常堆栈
- 是否存在循环日志
- 是否存在无意义日志
- 是否泄露敏感信息
- 是否在非日志需求中顺手改了日志

## Codex 执行要求

1. 默认不修改当前任务范围之外的日志。
2. 当前 diff 新增或改变关键业务行为时，必须检查当前修改范围内是否具备必要日志。
3. 已有日志完整覆盖时，不重复新增。
4. 已有日志因本次改动失真时，同步更新。
5. 日志修改严格限制在当前任务授权的 diff 内。
6. `INFO` 用于业务流程记录。
7. `ERROR` 用于异常记录。
8. 禁止使用 `DEBUG`。
9. 禁止使用 `TRACE`。
10. 禁止使用 `WARN`。
11. `WARN` 场景统一使用 `INFO` 并增加 `[WARNING]` 标识。
12. `ERROR` 日志必须打印完整异常堆栈。
13. 日志必须包含业务主键。
14. 日志不得包含敏感信息。
15. 禁止循环日志。
16. 禁止无意义日志。
17. 新增日志必须说明排查价值。
18. 无法证明价值的日志应删除。

## Final Logging Check

在完成代码修改或 review 前，必须检查当前 diff 是否存在以下日志问题：

- 是否存在静默 return，例如 return false、return Boolean.FALSE、return;
- 是否存在 catch 后吞掉异常、改变业务结果或转为失败返回，但当前层以及明确的上层业务边界均没有可定位的异常日志
- 是否存在外部调用失败、MQ、Job、回调、异步、补偿、状态流转、金额计算、权限拦截、业务跳过但没有关键日志
- 是否新增了 log.warn、log.debug、log.trace
- 是否使用字符串拼接日志
- 是否打印手机号、邮箱、证件号、token、完整请求体、完整响应体、完整响应 JSON
- 是否存在已有日志已完整覆盖却重复新增日志
- 是否存在高频查询、循环、逐条转换或普通 CRUD 的逐次正常 INFO
- 是否有多个调用层或并行修改重复打印相同业务节点、异常或业务上下文
- 是否修改了当前任务范围之外的日志

如果发现问题：

- 只允许在当前修改范围内修复
- 不允许扩大修改范围
- 不允许修改无关文件
- 不允许为了补日志制造无业务价值日志
- 不允许改变原有业务逻辑
- 不允许改变接口协议
- 不允许改变 SQL 口径

最终回复只需简要说明日志检查结果，不需要输出完整检查表。
