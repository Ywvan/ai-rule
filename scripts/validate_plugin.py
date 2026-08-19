#!/usr/bin/env python3
"""Validate the hly-codex-guards source tree and an optional userdir ZIP."""

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
    "hly-code-comment-style",
    "logging-style-guard",
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


def read_skill(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        fail(f"Skill front matter 缺失或格式错误：{path}")
    front_matter = match.group(1)
    name_match = re.search(r"(?m)^name:\s*(.+?)\s*$", front_matter)
    description_match = re.search(r"(?m)^description:\s*(.+?)\s*$", front_matter)
    if not name_match or not description_match:
        fail(f"Skill name/description 缺失：{path}")
    return name_match.group(1).strip(), text


def require(text: str, items: tuple[str, ...], name: str) -> None:
    missing = [item for item in items if item not in text]
    if missing:
        fail(f"{name} 缺少规则：{missing}")


def runtime_files(root: Path) -> dict[str, Path]:
    plugin_root = root / "plugins" / PLUGIN_NAME
    files = {
        ".agents/plugins/marketplace.json": root / ".agents" / "plugins" / "marketplace.json",
        f"plugins/{PLUGIN_NAME}/.codex-plugin/plugin.json": plugin_root / ".codex-plugin" / "plugin.json",
    }
    for path in (plugin_root / "skills").rglob("*"):
        if path.is_file():
            files[path.relative_to(root).as_posix()] = path
    return files


def validate_source(root: Path) -> tuple[dict, dict[str, Path]]:
    plugin_root = root / "plugins" / PLUGIN_NAME
    manifest = load_json(plugin_root / ".codex-plugin" / "plugin.json")
    marketplace = load_json(root / ".agents" / "plugins" / "marketplace.json")

    if manifest.get("name") != PLUGIN_NAME:
        fail("plugin.json name 不正确")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        fail(f"plugin.json version 不符合 SemVer：{version!r}")

    entries = marketplace.get("plugins")
    if not isinstance(entries, list):
        fail("marketplace.json 缺少 plugins 数组")
    entry = next((item for item in entries if item.get("name") == PLUGIN_NAME), None)
    if entry is None or entry.get("source", {}).get("path") != f"./plugins/{PLUGIN_NAME}":
        fail("marketplace.json 的插件入口不正确")

    skills_root = plugin_root / "skills"
    dirs = {path.name for path in skills_root.iterdir() if path.is_dir()}
    if dirs != EXPECTED_SKILLS:
        fail(f"Skill 目录不符合预期：{sorted(dirs)}")

    texts: dict[str, str] = {}
    names: set[str] = set()
    for directory in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        name, text = read_skill(directory / "SKILL.md")
        names.add(name)
        texts[directory.name] = text
    if names != EXPECTED_SKILLS:
        fail(f"Skill name 不符合预期：{sorted(names)}")

    review = texts["code-review-guard"]
    require(review, ("Review 只读", "### P0", "### P1", "### P2", "### P3", "不要从 Checklist 反向寻找问题", "Review Finding 是待后续复核的问题判断"), "code-review-guard")
    for forbidden in ("先找全影响点", "必须检查：", "CTE 层级超过 3 层"):
        if forbidden in review:
            fail(f"code-review-guard 仍包含过度流程规则：{forbidden}")

    fix = texts["single-risk-fix"]
    require(fix, ("不预设它一定成立", "重新读取相关当前代码", "Finding 不成立", "不修改代码"), "single-risk-fix")
    if "Fix one confirmed risk" in fix or "已确认风险" in fix:
        fail("single-risk-fix 仍把 Review Finding 预设为 confirmed risk")

    delegation = texts["subagent-delegation-assessment"]
    require(delegation, ("Task Decomposition 不自动触发 Subagent", "保持单 Agent", "权限继承"), "subagent-delegation-assessment")

    manifest_text = json.dumps(manifest, ensure_ascii=False)
    if "confirmed risk" in manifest_text.lower():
        fail("plugin defaultPrompt 不应把风险预设为 confirmed")

    return manifest, runtime_files(root)


def validate_zip(zip_path: Path, source_files: dict[str, Path]) -> None:
    with zipfile.ZipFile(zip_path) as archive:
        actual = {item.filename.replace("\\", "/"): item for item in archive.infolist() if not item.is_dir()}
        expected = set(source_files)
        if set(actual) != expected:
            fail(f"安装 ZIP 文件清单不一致；缺失={sorted(expected - set(actual))}，多余={sorted(set(actual) - expected)}")
        for relative, source in source_files.items():
            source_text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
            zip_text = archive.read(actual[relative]).decode("utf-8").replace("\r\n", "\n")
            if source_text != zip_text:
                fail(f"安装 ZIP 内容与源码不一致：{relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", type=Path, help="可选：校验 userdir 安装 ZIP")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        manifest, files = validate_source(root)
        if args.zip:
            validate_zip(args.zip.resolve(), files)
    except (ValueError, OSError, zipfile.BadZipFile) as error:
        print(f"校验失败：{error}", file=sys.stderr)
        return 1
    print(f"Validation passed: {PLUGIN_NAME} {manifest['version']}; runtime files={len(files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
