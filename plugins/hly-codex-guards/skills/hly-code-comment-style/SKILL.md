---
name: hly-code-comment-style
description: Use when Codex writes, modifies, or reviews Java, Spring Boot, MyBatis XML, SQL, or Liquibase code. This Skill owns HLY-specific Chinese comment conventions and comment placement details.
---

# HLY Code Comment Style

## 注释内容

中文注释补充代码不能直接表达的业务原因、来源、取值约束、默认行为、历史兼容或外部协议限制；不能编造业务含义，也不翻译语法。

“兜底、降级、收敛、兼容、特殊处理、防御性处理、历史逻辑、回刷、脏数据、幂等处理”不能单独作为说明，须交代触发条件、原因或影响。名称已表达做什么时，补充为什么或业务约束，否则不新增；避免 `// 查询数据`、`@param userId 用户ID`、`@return 查询结果`。

## 放置规则

- 新增业务类：说明业务职责；需求或接口契约限定职责边界时一并说明，不虚构“不负责”的范围。
- 新增/修改对外接口、Java interface 业务方法、决定业务结果或调用外部系统的方法，以及返回布尔/状态/金额等影响后续判断的方法：保留业务契约，说明用途及影响结果的参数、返回值、默认值、特殊行为；参数名已表达的用途不机械补 `@param`。
- 当前 diff 新增/修改 Entity、DTO、VO、Query、Result 业务字段，枚举/状态/开关、金额/比例、时间/有效期、外部请求/响应、存储、历史兼容或计算字段：说明该字段涉及的来源、值域、单位/金额口径、时间语义、默认/空值/历史数据行为和协议含义；已有准确说明不重复，不能确认的含义不编造。Logger、注入对象、无业务含义的临时字段、统一技术审计字段不重复注释。
- 行内注释放在业务块上方；一个方法包含多条业务规则时，分别说明代码未表达的原因或约束，不逐行说明、不设固定条数。

## SQL 与数据库

SQL / MyBatis XML 涉及多表关联、聚合/去重、分页/导出或性能约束时，说明代码未表达的业务目的、目标粒度、扫描范围、已确认的索引/过滤依赖或 JOIN/条件原因；不逐字段、逐 JOIN、逐条件注释。

Liquibase 的 changeSet id、表名、字段名已表达意图时不加装饰性 XML 注释；涉及历史兼容、回滚限制、数据回填、默认值或可空策略时，补充代码与已有说明未表达的迁移原因和约束。

新增数据库业务字段的 MySQL `COMMENT`、Liquibase `remarks` 与 Java 说明保持一致；业务语义变化时核对当前 diff 两侧说明，不顺带补齐历史字段。

## Review

仅报告当前 diff 的业务契约缺失、注释失真或编造、字段来源/值域/金额/时间口径错误、数据库与 Java 语义冲突、大量机械注释等实际问题；无问题写“当前 diff 未发现明确注释风险”，不输出检查表。
