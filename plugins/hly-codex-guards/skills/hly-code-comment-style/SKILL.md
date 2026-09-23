---
name: hly-code-comment-style
description: Use when the current task adds, changes, or reviews business comments, public business methods, business fields/contracts, MyBatis XML comments, or Liquibase schema documentation. This Skill owns HLY-specific Chinese comment conventions and comment placement details.
---

# HLY Code Comment Style

## 注释内容

中文注释用于帮助人工理解业务职责、流程阶段，以及代码不能直接表达的业务原因、来源、取值约束、默认行为、历史兼容或外部协议限制；不能编造业务含义，也不逐行翻译代码。

AI 新增或明显修改的核心业务类、核心业务方法和较长业务流程，即使命名清晰，也应根据人工阅读需要保留简洁的业务契约或阶段说明。

注释必须与紧邻代码存在明确业务对应。“兜底、降级、兼容、特殊处理、防御性处理、历史逻辑、幂等处理、保证正常流程、确保数据正确”等表述不能单独作为说明；须明确具体对象以及触发条件、原因、约束或结果影响。不得把需求、设计、Review 或 Agent 执行过程写入代码。

如果删除一条注释不会影响对业务职责、流程阶段、规则原因或数据语义的理解，则不新增或不保留。

## 放置规则

- 新增业务类：说明核心业务职责；存在已确认的职责边界时一并说明。
- 对外接口、Java interface 业务方法、决定业务结果或调用外部系统的方法，以及涉及状态、金额、权限、配置等关键语义的方法：保留必要业务契约。
- 一个方法包含多个独立业务阶段或较长业务流程时，可使用少量块注释帮助人工快速定位流程阶段；不逐行解释调用。
- 当前 diff 新增或修改的重要业务字段，按实际需要说明来源、值域、金额/时间口径、默认/空值行为或外部协议含义；已有准确说明不重复，不能确认的含义不编造。
- 简单 CRUD、getter/setter、普通转换、显然的局部变量和工具方法不机械增加注释。

## SQL 与数据库

SQL / MyBatis XML 涉及多表关联、聚合/去重、分页/导出或不直观条件时，说明代码未直接表达的业务目的、数据粒度或条件原因；不逐字段、逐 JOIN、逐条件注释。

Liquibase 的 changeSet、表名和字段名已表达意图时不增加装饰性注释；历史兼容、数据回填、默认值、可空策略等存在非显然约束时补充说明。

新增数据库业务字段的 MySQL `COMMENT`、Liquibase `remarks` 与 Java 说明保持业务语义一致；不顺带补齐当前任务之外的历史字段。

## Review

仅报告当前 diff 中实际存在的核心业务代码缺少必要人工阅读说明、注释重复代码、泛化或与具体代码无关的 AI 式说明、需求/设计/Review/Agent 过程进入代码、注释失真或编造、字段/数据库语义错误、大量机械注释等问题；无问题写“当前 diff 未发现明确注释风险”，不输出检查表。
