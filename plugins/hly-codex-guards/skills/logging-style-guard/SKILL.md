---
name: logging-style-guard
description: Use when Codex generates, modifies, or reviews Java/Spring Boot/MQ/Job/external-call logging. Enforce minimal valuable INFO/ERROR logging, prohibit DEBUG/TRACE/WARN, require business keys and full exception stack traces, prevent sensitive data leaks, and avoid meaningless logs, loop logs, getter/setter logs, DTO/VO conversion logs, DAO CRUD logs, and incidental log changes during non-log tasks.
---

# Codex 日志打印规范

## 核心原则

- 日志用于快速定位问题、还原业务过程、支撑线上排查，并控制日志量。
- 日志不是越多越好；无法帮助定位问题的日志视为无效日志。
- 默认只允许使用 `INFO` 和 `ERROR`。
- 禁止使用 `DEBUG`、`TRACE`、`WARN`。
- `WARN` 场景统一使用 `INFO`，并在日志文案中增加 `[WARNING]` 标识。

## 日志最小化

除非任务明确要求日志改造，或关键链路确实缺失必要日志，否则禁止：

- 新增日志
- 修改日志
- 删除日志
- 调整日志级别
- 修改日志文案或结构

日志变更视为功能变更，必须说明原因、排查价值和对应业务链路。无法说明价值的日志不要新增。

## 必须打印日志的场景

在以下关键链路中补充必要日志：

- 外部接口调用：HTTP、RPC、Dubbo、OpenFeign、MQ 生产、支付接口、第三方供应商接口。
- MQ 消费：能定位 `messageId`、业务主键和消费结果。
- Job 执行：记录开始、结束、耗时、成功数量和失败数量。
- 业务状态流转：如创建订单、支付成功、支付失败、审批通过、审批驳回、退款成功、同步成功。
- 数据修复任务：能定位批次号、修复条件和修复数量。
- 异常处理：关键异常必须记录 `ERROR` 日志，并打印完整异常堆栈。
- 关键兜底逻辑：默认值兜底、数据缺失兜底、降级逻辑、容错逻辑。

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

## 非日志需求

如果当前任务目标不是日志改造，禁止顺手做以下修改：

- 修改日志级别
- 修改日志文案
- 新增日志
- 删除日志
- 调整日志结构

只有发现关键业务链路缺失必要日志，并且该缺失会影响本次任务验证或线上排查时，才允许提出补充日志；实际修改前说明原因。

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

1. 默认不新增日志。
2. 默认不修改已有日志。
3. 默认不调整日志级别。
4. 默认不修改日志文案。
5. 仅在关键业务链路缺失日志时允许补充。
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
- 是否存在 catch 后未记录 error 日志
- 是否存在外部调用失败、MQ、Job、回调、异步、补偿、状态流转、金额计算、权限拦截、业务跳过但没有关键日志
- 是否新增了 log.warn、log.debug、log.trace
- 是否使用字符串拼接日志
- 是否打印手机号、邮箱、证件号、token、完整请求体、完整响应体、完整响应 JSON

如果发现问题：

- 只允许在当前修改范围内修复
- 不允许扩大修改范围
- 不允许修改无关文件
- 不允许为了补日志制造无业务价值日志
- 不允许改变原有业务逻辑
- 不允许改变接口协议
- 不允许改变 SQL 口径

最终回复只需简要说明日志检查结果，不需要输出完整检查表。