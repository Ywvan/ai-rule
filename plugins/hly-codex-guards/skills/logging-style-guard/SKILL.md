---
name: logging-style-guard
description: Use when the current change affects external API calls, MQ, Jobs/batches, callbacks, async/retry/compensation, business-state transitions, payment/amount/settlement flows, rejection/fallback paths, or exception handling that requires production observability. This Skill owns logging placement, business-key selection, deduplication, loop aggregation, and sensitive-field details.
---

# Logging Style Guard

仅处理当前变更链路的生产定位信息，不改造历史日志；日志 Review 保持只读。

## 节点与定位

外部接口结果、MQ 生产/消费、Job/批量任务、第三方回调、异步/重试/补偿、关键状态、支付/金额/结算、业务拒绝/跳过/回退、改变业务结果的异常捕获、权限/数据范围拒绝，检查能否用业务键或关联标识从日志还原业务对象、节点和实际结果。已有上下层日志能关联到同一处理过程且覆盖上述信息时，不重复增加；缺失时仅补对应信息。

选择稳定业务键，如 `orderNo`、`supplierOrderNo`、`tenantId`、`companyOid`、`employeeOid`、`journeyNo`、`approvalNo`、`batchNo`；不打印完整 DTO/VO/Entity/Request/Response 来代替定位键。

## 内容与敏感信息

- 使用参数化占位符，不拼接日志正文；文案说明业务节点与实际结果，不写 `enter/leave method` 或 `method start`。
- 异常保留完整异常对象/堆栈，不只记录 `getMessage()`。同一异常在明确业务边界记录后，下层不重复堆栈，除非其持有上层无法取得的关键定位信息。
- 不直接记录 password/secret、token/accessToken/refreshToken、sign/Cookie/认证材料、完整身份证/银行卡/手机号/邮箱、完整请求体/响应体或大段 JSON；确需定位只记录脱敏且直接相关的字段。

## 高频、批量与同步

不在循环打印逐条正常成功日志；批量记录批次、总量、成功/失败数和失败样例。高频查询、普通 CRUD、DTO 转换和工具方法不新增逐次正常日志；多层调用不重复相同上下文。

当前修改使日志语义失真时同步修正；已有日志准确且满足“节点与定位”标准时，不为本 Skill 增加日志 diff。

Review 按以上规则只报告当前 diff 的不可定位失败路径、业务键/堆栈缺失、重复/循环/高频日志、敏感信息泄露或日志失真；无问题写“当前 diff 未发现明确日志风险”，不输出检查表。
