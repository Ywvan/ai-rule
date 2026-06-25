---
name: sql-writing-style
description: "Use when Codex writes, modifies, or reviews SQL, MyBatis SQL, report SQL, or database query logic. Enforce simple, correct, readable, and maintainable SQL; prefer straightforward SELECT/JOIN/WHERE/GROUP BY/ORDER BY; avoid unnecessary CTEs, DISTINCT, window functions, defensive COALESCE/NVL/IFNULL/CAST/CONVERT, nested queries, vague aliases, and speculative future-proof logic."
---

# SQL Writing Style

## 核心原则

SQL 的首要目标是：

1. 正确性
2. 可读性
3. 可维护性

在满足以上目标之前，不要优先追求技巧性写法或极限性能优化。

默认采用最简单且正确的实现方案。

## SQL 分析边界

执行 SQL 分析或 SQL 修改前，分析深度优先于修改速度。允许扩大分析范围，不允许扩大修改范围。

禁止只分析当前 SQL 片段。涉及 SQL 修改时，必须确认是否存在关联的列表、分页、COUNT、导出、汇总、排行、权限包装、DATA 权限和多租户条件。

如果列表、导出、COUNT、汇总共用或部分共用逻辑，必须一起分析影响范围。先找全影响点，再做最小 SQL 修改。

不确定的业务口径必须标注“不确定”，禁止猜测。

## SQL 生成规则

### 优先简单写法

优先使用：

- `SELECT`
- `JOIN`
- `WHERE`
- `GROUP BY`
- `ORDER BY`

避免为了展示技巧而增加复杂结构。

### 谨慎使用 CTE

仅在以下情况允许使用 CTE：

- 表达明确的业务步骤。
- 消除重复逻辑。
- 显著提升可读性。

禁止：

- 单次使用却没有提升可读性的 CTE。
- 多层嵌套 CTE。
- 将简单查询拆分成多个 CTE。

### 谨慎使用 DISTINCT

使用 `DISTINCT` 前必须确认：

- 重复数据确实存在。
- 重复来源明确。

禁止将 `DISTINCT` 当作修复 `JOIN` 问题的手段。

如果需要 `DISTINCT`，应说明产生重复的原因。

### 谨慎使用窗口函数

仅在以下场景使用窗口函数：

- 排名。
- TopN。
- 去重。
- 累计计算。
- 分组统计。

如果 `GROUP BY` 可以解决问题，则优先使用 `GROUP BY`。

### 避免无意义的防御性代码

不要无理由添加：

- `COALESCE`
- `NVL`
- `IFNULL`
- `CAST`
- `CONVERT`

只有在业务逻辑明确要求时才使用。

### 减少嵌套查询

优先：

```sql
SELECT ...
FROM user_info u
JOIN order_info o
```

而不是：

```sql
SELECT *
FROM (
    SELECT *
    FROM (
        ...
    )
)
```

除非嵌套能够明显提升可读性。

### 表别名规范

允许使用短别名：

```sql
user_info u
order_info o
```

禁止：

```sql
a
b
c
t1
t2
t3
```

除非查询极其简单。

## SQL 输出要求

生成 SQL 时：

1. 先给出最简单正确版本。
2. 不主动优化为复杂实现。
3. 不主动增加扩展性代码。
4. 不主动增加兼容性代码。
5. 不主动增加未来可能需要的逻辑。

遵循 YAGNI（You Aren't Gonna Need It）。

只实现当前需求。

## SQL Review 规范

审查 SQL 时重点检查：

- 是否存在多余 CTE。
- 是否存在多余子查询。
- 是否存在无意义 `DISTINCT`。
- 是否存在过度使用窗口函数。
- 是否存在重复逻辑。
- `JOIN` 是否可能造成数据膨胀。
- 是否能进一步简化。

如果能简化：

- 保持结果一致。
- 优先降低复杂度。
- 再考虑性能优化。

## 输出风格

默认输出：

- 简洁。
- 直接。
- 易读。

目标是让普通开发人员在 30 秒内理解 SQL 的业务逻辑。
