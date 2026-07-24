#!/usr/bin/env python3
"""Validate the hly-codex-guards source tree and a userdir installation ZIP."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


PLUGIN_NAME = "hly-codex-guards"
EXPECTED_SKILLS = {
    "code-review-guard",
    "codex-round-execution-plan",
    "hly-code-comment-style",
    "logging-style-guard",
    "production-implementation-plan",
    "requirement-scope-clarification",
    "single-risk-fix",
    "sql-writing-style",
    "subagent-delegation-assessment",
}
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"无法解析 JSON：{path}；{error}")


def read_skill_front_matter(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        fail(f"Skill front matter 缺失或格式错误：{path}")
    front_matter = match.group(1)
    name = re.search(r"(?m)^name:\s*(.+?)\s*$", front_matter)
    description = re.search(r"(?m)^description:\s*(.+?)\s*$", front_matter)
    if not name or not name.group(1).strip():
        fail(f"Skill name 为空：{path}")
    if not description or not description.group(1).strip().strip('\"'):
        fail(f"Skill description 为空：{path}")
    return name.group(1).strip(), text


def normalized_text(content: bytes, location: str) -> bytes:
    try:
        return content.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
    except UnicodeDecodeError as error:
        fail(f"运行文件不是 UTF-8 文本：{location}；{error}")


def runtime_files(root: Path) -> dict[str, Path]:
    plugin_root = root / "plugins" / PLUGIN_NAME
    files = {
        ".agents/plugins/marketplace.json": root / ".agents" / "plugins" / "marketplace.json",
        f"plugins/{PLUGIN_NAME}/.codex-plugin/plugin.json": plugin_root / ".codex-plugin" / "plugin.json",
    }
    skills_root = plugin_root / "skills"
    for path in skills_root.rglob("*"):
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path
    return files


def require_text(text: str, expected: tuple[str, ...], rule_name: str) -> None:
    missing = [item for item in expected if item not in text]
    if missing:
        fail(f"{rule_name} 缺少规则：{missing}")


def validate_behavioral_rules(skill_texts: dict[str, str]) -> None:
    logging = skill_texts["logging-style-guard"]
    require_text(
        logging,
        (
            "外部接口调用",
            "状态流转",
            "业务主键",
            "高频查询、循环、逐条转换和普通 CRUD，默认不新增逐次正常 `INFO` 日志",
            "已有日志能够完整覆盖时，不重复新增",
            "不得重复打印相同业务节点、相同异常和相同业务上下文",
            "禁止打印完整请求、响应、DTO、VO、Entity 或认证材料",
        ),
        "日志灰度场景",
    )

    comments = skill_texts["hly-code-comment-style"]
    require_text(
        comments,
        (
            "DTO、VO、Query、Result 字段",
            "Entity 字段",
            "金额字段",
            "枚举或状态字段",
            "时间或有效期字段",
            "布尔和开关字段",
            "Liquibase column 必须有准确 `remarks`",
            "Logger；",
            "允许分别添加必要注释",
            "不要给每一行代码都写注释",
        ),
        "注释灰度场景",
    )

    review = skill_texts["code-review-guard"]
    require_text(
        review,
        (
            "### P0",
            "### P1",
            "### P2",
            "### P3",
            "SQL 有明确更简单的等价写法",
            "命名容易造成具体误解",
            "未发现明确 P0/P1/P2/P3 风险。",
            "不得为了凑数量强行输出 P3",
            "所有子 Agent 均保持只读",
        ),
        "Review 灰度场景",
    )

    execution = skill_texts["production-implementation-plan"]
    require_text(
        execution,
        (
            "直接连续执行",
            "内部分阶段连续执行",
            "正式分轮执行",
            "暂不进入执行",
            "不根据任务大小、Sol、Terra、Ultra 或其他模型和 Agent 配置决定",
        ),
        "执行方式灰度场景",
    )

    short_compatibility = "本 Skill 兼容用户当前选择的模型、推理档位以及单 Agent、Ultra 和子 Agent 执行方式。"
    if sum(short_compatibility in text for text in skill_texts.values()) != len(EXPECTED_SKILLS):
        fail("Ultra 和子 Agent 灰度场景未覆盖全部 Skill")
    if any("不固定子 Agent 数量" in text for text in skill_texts.values()):
        fail("不应在短版兼容规则中重复固定 Agent 规则")

    delegation = skill_texts["subagent-delegation-assessment"]
    require_text(
        delegation,
        (
            "现在委派",
            "后续阶段委派",
            "保持单 Agent",
            "不得只输出 Agent 使用建议后停止",
            "预期收益",
            "协调成本",
            "调查",
            "可写实现",
            "权限继承",
            "主 Agent",
            "不要求切换 Ultra",
            "不预设具体 Subagent 数量",
        ),
        "Subagent 委派评估规则",
    )
    prohibited_patterns = (
        (r"\b(?:Sol|Terra|Luna)\b", "固定具体模型"),
        (r"(?:低|中|高|xhigh|max)推理(?:档位)?", "固定推理档位"),
        (r"固定.{0,12}(?:Subagent|子 Agent).{0,8}数量", "固定 Subagent 数量"),
        (r"固定.{0,12}并发数量", "固定并发数量"),
        (r"(?<!不)要求修改\s*config\.toml", "要求修改 config.toml"),
        (r"协议未稳定.{0,24}(?:允许|可以).{0,24}并行修改", "协议未稳定时并行修改公共协议"),
        (r"Subagent(?:可以|能够|应当).{0,24}(?:获得|拥有).{0,20}更大的权限", "允许 Subagent 扩大原任务权限"),
    )
    for pattern, rule_name in prohibited_patterns:
        if re.search(pattern, delegation, re.IGNORECASE):
            fail(f"Subagent 委派评估规则不应包含：{rule_name}")

def validate_source(root: Path) -> tuple[dict, dict[str, Path]]:
    plugin_json = root / "plugins" / PLUGIN_NAME / ".codex-plugin" / "plugin.json"
    marketplace_json = root / ".agents" / "plugins" / "marketplace.json"
    manifest = load_json(plugin_json)
    marketplace = load_json(marketplace_json)

    if manifest.get("name") != PLUGIN_NAME:
        fail("plugin.json 的 name 与插件目录不一致")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        fail(f"plugin.json 的 version 不符合 SemVer：{version!r}")

    entries = marketplace.get("plugins")
    if not isinstance(entries, list):
        fail("marketplace.json 缺少 plugins 数组")
    entry = next((item for item in entries if item.get("name") == PLUGIN_NAME), None)
    if entry is None:
        fail("marketplace.json 缺少 hly-codex-guards 入口")
    if entry.get("source", {}).get("path") != f"./plugins/{PLUGIN_NAME}":
        fail("marketplace.json 的 source.path 不正确")

    skills_root = root / "plugins" / PLUGIN_NAME / "skills"
    skill_dirs = sorted(path for path in skills_root.iterdir() if path.is_dir())
    actual_dirs = {path.name for path in skill_dirs}
    if actual_dirs != EXPECTED_SKILLS:
        fail(f"Skill 目录不符合预期：{sorted(actual_dirs)}")

    skill_names: list[str] = []
    skill_texts: dict[str, str] = {}
    for directory in skill_dirs:
        skill_name, text = read_skill_front_matter(directory / "SKILL.md")
        skill_names.append(skill_name)
        skill_texts[directory.name] = text
    if len(skill_names) != len(set(skill_names)):
        fail("Skill name 存在重复")
    if set(skill_names) != EXPECTED_SKILLS:
        fail(f"Skill name 不符合预期：{sorted(skill_names)}")

    review = skill_texts["code-review-guard"]
    for level in ("P0", "P1", "P2", "P3"):
        if f"### {level}" not in review:
            fail(f"Review 缺少 {level}")
    required_review_rules = (
        "默认检查和输出 P0/P1/P2/P3",
        "未发现明确 P0/P1/P2/P3 风险。",
        "禁止修改代码",
        "禁止自动修复",
    )
    for rule in required_review_rules:
        if rule not in review:
            fail(f"Review 规则缺失：{rule}")

    logging = skill_texts["logging-style-guard"]
    if "非日志任务一律禁止新增日志" in logging:
        fail("日志规则仍包含非日志任务一律禁止新增日志")
    if "当前任务即使不是日志专项改造" not in logging:
        fail("日志规则缺少当前 diff 的必要日志检查")

    comments = skill_texts["hly-code-comment-style"]
    for field_type in ("DTO、VO、Query、Result", "Entity 字段"):
        if field_type not in comments:
            fail(f"字段注释规则缺少：{field_type}")
    for hard_limit in ("复杂方法最多", "通常不超过 3"):
        if hard_limit in comments:
            fail(f"字段注释规则仍包含硬上限：{hard_limit}")

    if any("## GPT-5.6 执行模式兼容" in text for text in skill_texts.values()):
        fail("仍存在重复的 GPT-5.6 长版兼容规则")
    validate_behavioral_rules(skill_texts)

    return manifest, runtime_files(root)


def validate_zip(zip_path: Path, source_files: dict[str, Path]) -> None:
    if not zip_path.is_file():
        fail(f"安装 ZIP 不存在：{zip_path}")
    try:
        with zipfile.ZipFile(zip_path) as archive:
            zip_files = {
                item.filename.replace("\\", "/"): item
                for item in archive.infolist()
                if not item.is_dir()
            }
            expected = set(source_files)
            actual = set(zip_files)
            if actual != expected:
                missing = sorted(expected - actual)
                extra = sorted(actual - expected)
                fail(f"安装 ZIP 文件清单不一致；缺失={missing}，多余={extra}")
            for relative_path, source_path in source_files.items():
                source_content = normalized_text(source_path.read_bytes(), str(source_path))
                zip_content = normalized_text(archive.read(zip_files[relative_path]), f"{zip_path}!{relative_path}")
                if source_content != zip_content:
                    fail(f"安装 ZIP 内容与源码不一致：{relative_path}")
    except zipfile.BadZipFile as error:
        fail(f"安装 ZIP 无法读取：{zip_path}；{error}")


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 hly-codex-guards 源码和 userdir 安装包")
    parser.add_argument("--zip", required=True, type=Path, help="待校验的 userdir 安装 ZIP")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        manifest, source_files = validate_source(root)
        validate_zip(args.zip.resolve(), source_files)
    except ValueError as error:
        print(f"校验失败：{error}", file=sys.stderr)
        return 1
    print(f"Validation passed: {PLUGIN_NAME} {manifest['version']}; runtime files={len(source_files)}; archive={args.zip.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
