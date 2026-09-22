# Changelog

## 0.3.1-rc.9 - 2026-09-22

### Changed

- `code-review-guard` 增加现实可达性与现有保护门禁：代码风险形态本身不直接形成 Finding；会改变结论的触发链、guard、状态约束、事务 / 锁、幂等及上下游保护需要核验，证据不足时进入 Verification Gap。
- 当 `gitnexus-review` 当前可用且 Review 涉及可观察行为、共享契约、跨模块 / 跨服务调用、影响范围或合并风险时，将其作为 Structural Evidence Specialist 主动参与；`code-review-guard` 继续拥有 Finding Scope、P0-P3、证据 / 完成门禁与最终输出。
- GitNexus 的 caller、dependent、affected process 等图谱关系只作为调查线索，具体实现事实仍回到当前源码核验；逐 symbol 全量 impact、全量 direct dependent、expert lens / swarm / critic、PDG / taint 仅在证据需要或用户明确要求深度结构 / 安全 Review 时执行，不自动触发 Subagent。
- 更新 `validate_plugin.py` 的 Review 不变量校验，移除已失效的旧版固定文本要求，改为校验当前 evidence gate、reachability、Structural Evidence 和 Subagent 边界。

### Compatibility

- Review 仍保持只读，不扩大 Finding Scope，不自动修复。
- 不恢复固定 Checklist 或无差别全量图谱遍历；SQL、日志、注释、single-risk 与 Subagent Specialist 的既有职责不变。
- `gitnexus-review` 不可用时，继续按 `code-review-guard` 与当前可用代码导航工具完成 Review。

## 0.3.1-rc.6 - 2026-09-14

### Changed

- `code-review-guard` 明确区分 Finding Scope 与 Analysis Scope：Finding 仍只归属于当前 diff / Review Scope，但允许读取验证 Changed Behavior 所需的调用方、被调用方、SQL、配置、数据流、契约和验证证据。
- 新增轻量 Review Search Strategy：先识别实际 Changed Behavior，再按当前变更相关的风险面调查，不恢复固定 Checklist。
- 对会改变最终业务结果的 Changed Behavior 增加主要反例检查，防止仅因模型没有主动想到替代路径就过早闭环。
- Review Completion Gate 增加相关风险面覆盖要求；相关风险面内部应能判断为已有证据、与当前变更不适用或 Verification Gap，但不要求机械输出检查表。
- 修正 `code-review-guard` 默认提示词中 `only current diff` 容易造成的 Diff Anchoring，明确“Finding 限定范围，分析按必要上下文扩展”。
- `sql-writing-style` 先确认实际消费者，仅在公共逻辑、部分共用或消费者不明确时扩大调查，避免局部 SQL 为完整性无差别搜索无关调用方。
- 校验脚本增加 Search Strategy、Analysis Scope、Changed Behavior 与主要反例规则检查。

### Compatibility

- Review 仍保持只读，不扩大 Finding Scope，不自动修复。
- 不恢复固定 Must Check Checklist，不要求无差别遍历全部风险类型或上下游。
- P0-P3、Finding 编号、Verification Gap 与 SQL Finding 语义保持兼容。

## 0.3.1-rc.5 - 2026-09-11

### Changed

- `code-review-guard` 增加 Review Completion Gate：无风险结论必须基于与当前 diff 直接相关的关键行为路径已经闭环到结果，不能仅因尚未发现 Finding 或 Verification Gap 就提前结束 Review。
- Verification Gap 仅新增一种会阻塞无风险结论的情况：与当前 diff 直接相关、现实可触发且一旦成立足以推翻无风险结论的关键行为路径缺少证据；其他未知项仍不扩张为 Verification Gap。
- 保留“不从 Checklist 反向寻找问题”和“不为低相关假设无限扩散”，避免通过提高误报和保守程度换取覆盖率。
- 校验脚本新增 Completion Gate 关键约束检查。

## 0.3.0-rc.1 - 2026-07-24

### Added

- 新增 `subagent-delegation-assessment` Skill。
- 多服务、多仓库、多模块及存在独立工作流的任务可以独立评估 Subagent 使用。
- 支持“现在委派”“后续阶段委派”“保持单 Agent”三种明确结论。
- 对有明确净收益的只读调查、测试和独立工作流支持有界委派。

### Compatibility

- 现有 8 个 Skill 内容保持不变。
- 不修改 Codex 配置文件。
- 不新增自定义 Agent 配置。
- 不固定模型、推理档位、Subagent 数量或并发数量。
- 不要求用户切换 Ultra。
- 不将多服务任务机械等同于必须使用 Subagent。
- Review、单风险修复、正式分轮、SQL、日志和注释规则保持不变。

## 0.2.1-rc.1 - 2026-07-14

### Changed

- 日志规则要求当前 diff 的关键业务行为检查必要日志，同时限制在当前任务范围内。
- 新增或修改的业务结构字段默认要求准确中文注释，并保留技术字段例外和证据约束。
- Review 默认检查 P0/P1/P2/P3，明确 P2/P3 边界和 P3 证据要求。
- 8 个 Skill 的通用执行模式和 Agent 规则压缩为模型中立短版。
- 生产实现方案增加直接连续、内部分阶段连续、正式分轮和暂不进入执行的推荐方式。

### Added

- 新增源码与 userdir 安装包一致性校验脚本。
- 新增仅打包运行时文件的 userdir 安装脚本。

### Compatibility

- 此版本为灰度候选版本，不覆盖 `hly-codex-guards-userdir-v0.2.0.zip`。
- Review 仍然只读；单风险修复、正式分轮停止条件和高风险业务语义保护保持不变。
