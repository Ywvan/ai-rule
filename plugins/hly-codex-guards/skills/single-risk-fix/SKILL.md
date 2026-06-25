---
name: single-risk-fix
description: "Fix only one confirmed risk. Use when the user provides a risk number, risk description, and affected files, and asks Codex to make the smallest possible code change for that single risk. If information is missing, business meaning is uncertain, or the minimal change boundary is unclear, ask the user for clarification and wait for confirmation before editing. Do not refactor, change unrelated code, modify database structure, alter API contracts, change response structures, change enum definitions, or alter existing business semantics or historical data handling."
---

# Single Risk Fix

## Goal

只修复一个风险点。

禁止顺手优化。

禁止顺手重构。

禁止修改无关代码。

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
