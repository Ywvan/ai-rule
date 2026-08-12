---
name: single-risk-fix
description: "Fix only one confirmed risk. Use when the user provides a risk number, risk description, and affected files, and asks Codex to make the smallest possible code change for that single risk. If information is missing, business meaning is uncertain, or the minimal change boundary is unclear, ask the user for clarification and wait for confirmation before editing. Do not refactor, change unrelated code, modify database structure, alter API contracts, change response structures, change enum definitions, or alter existing business semantics or historical data handling."
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

## 执行模式兼容

本 Skill 兼容用户当前选择的模型、推理档位以及单 Agent、Ultra 和子 Agent 执行方式。

执行方式不得改变：

- 当前 Skill 的只读或可写权限；
- 当前任务、轮次、风险或 Review 范围；
- 已确认业务口径；
- 允许和禁止修改范围；
- 验证要求和停止条件。

子 Agent 发现范围外问题时只能报告，不得自行扩大任务。
主 Agent 负责结果去重、冲突处理、最终 diff 检查和验证。

### 当前 Skill 执行边界

- 主 Agent 和所有子 Agent 必须围绕同一个风险编号，并继承当前风险的只读或可写状态和允许修改范围。
- 子 Agent 发现其他风险时只能报告证据，不得将其扩展为第二个修复任务。
- 主 Agent 必须确保最终修改和验证仍只处理当前风险。

### 并行修改规则

当前风险允许并行实现时，所有 Agent 仍只处理同一个风险编号和已确认文件范围。

- 子 Agent 发现其他风险时只能报告，不得修复；
- 并行实现不得扩大当前风险或文件范围；
- 主 Agent 负责检查最终修改是否仍为最小修复并完成验证。

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

发现缺失时，只允许在当前风险原有修改范围内补齐。该检查不新增风险、不增加执行轮次、不要求额外确认。

每个修改代码的子 Agent 负责检查自己修改范围内的日志和注释；主 Agent 最终检查遗漏、重复日志、业务术语和共享字段说明是否一致，并确保没有超出当前风险范围。

## 长任务与验证失败边界

使用子 Agent 或长任务执行时，所有调查、修改和验证仍必须围绕同一个风险编号。

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
