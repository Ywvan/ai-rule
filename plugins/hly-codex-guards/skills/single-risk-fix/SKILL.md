---
name: single-risk-fix
description: "Use only when the user explicitly invokes $single-risk-fix. Fix one confirmed risk with the smallest possible code change. Do not activate implicitly from a risk number, risk description, affected files, or a request for a minimal fix. If information is missing, business meaning is uncertain, or the minimal change boundary is unclear, ask the user for clarification and wait for confirmation before editing. Do not refactor, change unrelated code, modify database structure, alter API contracts, change response structures, change enum definitions, or alter existing business semantics or historical data handling."
---

# Single Risk Fix

## 使用声明

- 执行本 Skill 的任何实质性操作前，必须先在用户可见消息中明确声明：`正在使用 $<Skill 名称>：<使用原因>`。
- 同时使用多个 Skill 时，必须一次列出全部 Skill 及使用顺序。
- 不得只在最终答复中事后补充声明；如果当前环境没有独立的进度消息通道，应在首条可见回复中声明。

## Goal

只修复一个风险点。

禁止顺手优化。

禁止顺手重构。

禁止修改无关代码。

## 执行边界

执行策略由 Codex Native Harness 决定。本 Skill 只定义单一已确认风险的修复边界，不规定任务拆分、执行顺序或 Agent 使用方式。

- 所有调查、修改和验证必须围绕同一个风险编号及已确认文件范围。
- 发现其他风险时只报告证据，不得扩展为第二个修复任务。
- 最终修改和验证必须仍是当前风险的最小必要修复。

## 修复分析边界

修复问题时，分析深度优先于修改速度。允许扩大分析范围，不允许扩大修改范围。

禁止边分析边修改。禁止看到疑似问题后立即改代码。

修复前必须确认问题现象、根因、上游调用、下游调用、数据流、影响范围、兼容性风险，以及是否影响接口、数据库和原有业务语义。

允许查看任意调用链，不允许修改未明确确认的文件。分析阶段可以多看文件，实施阶段只能改确认范围内的文件。

先找全影响点，再做最小修改。不确定的业务含义必须标注“不确定”，禁止猜测。

## Input

输入必须包含：

- 风险编号
- 风险描述
- 涉及文件

例如：

`RISK-001`

## Clarification Gate

编码前必须确认输入足以定位一个已确认风险点，并且能够判断最小修改边界。

如果出现以下情况，不要编码，先询问用户并等待确认：

- 缺少风险编号、风险描述或涉及文件。
- 风险是否成立不确定。
- 业务含义、字段含义、状态含义或历史数据处理语义不确定。
- 无法判断最小修改边界。
- 存在多个修复方案，需要用户选择。
- 修复可能需要修改接口协议、数据库结构、返回结构、枚举定义或历史数据处理逻辑。

输出：

```markdown
## 需要补充信息

原因：

需要确认的问题：
```

等待用户确认后再继续。

## Modification Principle

遵守：

1. 最小改动
2. 不允许重构
3. 不允许修改无关文件
4. 不允许修改数据库结构
5. 不允许修改接口协议
6. 不允许修改返回结构
7. 不允许修改枚举定义
8. 不允许改变已有业务语义
9. 不允许改变历史数据处理逻辑
10. 如果当前风险修复点涉及日志或注释，只允许在当前风险范围内按 Logging Style Guard 和 Hly Code Comment Style 补齐，不得扩大到无关代码。
11. 不允许为了补日志或注释修改其他风险点、顺手整理周边日志、顺手补全全文件注释或修改本次风险之外的代码。

## 当前风险日志和注释收口

代码修改完成后，仅检查当前风险的 diff：

- 新增关键业务行为是否缺少必要日志；
- 现有日志是否足以定位新增分支；
- 是否存在静默失败、静默跳过、静默回退、重复日志、高频正常 `INFO` 或敏感信息泄露；
- 是否修改了当前风险范围之外的日志；
- 新增业务字段是否缺少必要注释；
- 新增数据库字段是否缺少 `COMMENT` 或 `remarks`；
- 新增 interface 方法或核心方法是否缺少必要业务说明；
- 已有注释是否因本次修改而失真；
- 是否存在编造语义或废话注释。

发现缺失时，只允许在当前风险原有修改范围内补齐。该检查不新增风险或扩大任务阶段。

存在并行修改时，各修改范围分别检查日志和注释；最终统一检查遗漏、重复日志、业务术语和共享字段说明是否一致，并确保没有超出当前风险范围。

## 长任务与验证失败边界

无论采用何种执行策略，所有调查、修改和验证仍必须围绕同一个风险编号。

验证失败时，只修复与当前风险直接相关的问题。

其他失败只记录证据，不得扩展为第二个风险。

当前风险的验证失败时，不得声明修复完成；必须先判断失败是否由当前风险 diff 引入。属于当前风险范围的问题做最小修复后重新验证，范围外问题只记录证据。环境原因无法验证时，说明原因并提供人工验证步骤。

## Must Stop Conditions

如果发现必须扩大改动范围：

立即停止。

输出：

```markdown
## 无法按最小修改完成

原因：

影响范围：

必须扩大的修改：
```

等待确认。

不要继续编码。

## Output Format

```markdown
## 修复方案

### 风险编号

RISK-XXX

### 修改文件

- xxx.java

### 修改内容

说明具体修改点。

### 影响范围

说明影响范围。

### 兼容性检查

- 接口兼容
- 数据兼容
- 枚举兼容
- 历史数据兼容

### 建议补充测试

列出需要验证的场景。
```

## Forbidden

禁止：

- rename
- move file
- 抽取公共组件
- 架构升级
- 大规模代码整理
- 自动格式化整个文件
- 修改无关 import
