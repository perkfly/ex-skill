#!/usr/bin/env python3
"""
Skill 文件写入器

负责将生成的 memories.md、persona.md 写入到正确的目录结构，
并生成 meta.json 和完整的 SKILL.md。

用法：
    python3 skill_writer.py --action create --slug xiaomei --meta meta.json \
        --memories memories_content.md --persona persona_content.md \
        --base-dir ./exes

    python3 skill_writer.py --action update --slug xiaomei \
        --memories-patch memories_patch.md --persona-patch persona_patch.md \
        --base-dir ./exes

    python3 skill_writer.py --action list --base-dir ./exes
"""

from __future__ import annotations

import json
import shutil
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


SKILL_MD_TEMPLATE = """\
---
name: ex_{slug}
description: {name}，{identity}
user-invocable: true
---

# {name}

{identity}

---

## PART A：共同记忆

{memories_content}

---

## PART B：人物性格

{persona_content}

---

## 运行规则

接收到任何消息时：

1. **先由 PART B 判断**：你会不会回这条消息？用什么心情和态度回？
2. **再由 PART A 提供记忆**：相关的共同记忆、日常细节、重要时刻
3. **输出时保持 PART B 的表达风格**：你说话的方式、用词习惯、emoji 偏好

**PART B 的 Layer 0 规则永远优先，任何情况下不得违背。**
"""


def slugify(name: str) -> str:
    """
    将姓名转为 slug。
    优先尝试 pypinyin（如已安装），否则 fallback 到简单处理。
    """
    try:
        from pypinyin import lazy_pinyin
        parts = lazy_pinyin(name)
        slug = "_".join(parts)
    except ImportError:
        import unicodedata
        result = []
        for char in name.lower():
            if char.isascii() and (char.isalnum() or char in ("-", "_")):
                result.append(char)
            elif char == " ":
                result.append("_")
        slug = "".join(result)

    import re
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug if slug else "ex"


def build_identity_string(meta: dict) -> str:
    """从 meta 构建身份描述字符串"""
    profile = meta.get("profile", {})
    parts = []

    duration = profile.get("duration", "")
    how_met = profile.get("how_met", "")
    time_since = profile.get("time_since_breakup", "")
    occupation = profile.get("occupation", "")

    if duration:
        parts.append(f"在一起 {duration}")
    if how_met:
        parts.append(how_met)
    if time_since:
        parts.append(f"分手 {time_since}")

    identity = "，".join(parts) if parts else "前任"

    if occupation:
        identity += f"，{occupation}"

    mbti = profile.get("mbti", "")
    if mbti:
        identity += f"，MBTI {mbti}"

    return identity


def create_skill(
    base_dir: Path,
    slug: str,
    meta: dict,
    memories_content: str,
    persona_content: str,
) -> Path:
    """创建新的前任 Skill 目录结构"""

    skill_dir = base_dir / slug
    skill_dir.mkdir(parents=True, exist_ok=True)

    # 创建子目录
    (skill_dir / "versions").mkdir(exist_ok=True)
    (skill_dir / "knowledge" / "chats").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "photos").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "social").mkdir(parents=True, exist_ok=True)

    # 写入 memories.md
    (skill_dir / "memories.md").write_text(memories_content, encoding="utf-8")

    # 写入 persona.md
    (skill_dir / "persona.md").write_text(persona_content, encoding="utf-8")

    # 生成并写入 SKILL.md
    name = meta.get("name", slug)
    identity = build_identity_string(meta)

    skill_md = SKILL_MD_TEMPLATE.format(
        slug=slug,
        name=name,
        identity=identity,
        memories_content=memories_content,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # 写入 memories-only skill
    memories_only = (
        f"---\nname: ex_{slug}_memories\n"
        f"description: {name} 的共同记忆（仅 Memories，无 Persona）\n"
        f"user-invocable: true\n---\n\n{memories_content}\n"
    )
    (skill_dir / "memories_skill.md").write_text(memories_only, encoding="utf-8")

    # 写入 persona-only skill
    persona_only = (
        f"---\nname: ex_{slug}_persona\n"
        f"description: {name} 的人物性格（仅 Persona，无共同记忆）\n"
        f"user-invocable: true\n---\n\n{persona_content}\n"
    )
    (skill_dir / "persona_skill.md").write_text(persona_only, encoding="utf-8")

    # 写入 meta.json
    now = datetime.now(timezone.utc).isoformat()
    meta["slug"] = slug
    meta.setdefault("created_at", now)
    meta["updated_at"] = now
    meta["version"] = "v1"
    meta.setdefault("corrections_count", 0)

    (skill_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return skill_dir


def update_skill(
    skill_dir: Path,
    memories_patch: Optional[str] = None,
    persona_patch: Optional[str] = None,
    correction: Optional[dict] = None,
) -> str:
    """更新现有 Skill，先存档当前版本，再写入更新"""

    meta_path = skill_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    current_version = meta.get("version", "v1")
    try:
        version_num = int(current_version.lstrip("v").split("_")[0]) + 1
    except ValueError:
        version_num = 2
    new_version = f"v{version_num}"

    # 存档当前版本
    version_dir = skill_dir / "versions" / current_version
    version_dir.mkdir(parents=True, exist_ok=True)
    for fname in ("SKILL.md", "memories.md", "persona.md"):
        src = skill_dir / fname
        if src.exists():
            shutil.copy2(src, version_dir / fname)

    # 应用 memories patch
    if memories_patch:
        current_memories = (skill_dir / "memories.md").read_text(encoding="utf-8")
        new_memories = current_memories + "\n\n" + memories_patch
        (skill_dir / "memories.md").write_text(new_memories, encoding="utf-8")

    # 应用 persona patch 或 correction
    if persona_patch or correction:
        current_persona = (skill_dir / "persona.md").read_text(encoding="utf-8")

        if correction:
            correction_line = (
                f"\n- [{correction.get('scene', '通用')}] "
                f"不应该 {correction['wrong']}，应该 {correction['correct']}"
            )
            target = "## Correction 记录"
            if target in current_persona:
                insert_pos = current_persona.index(target) + len(target)
                rest = current_persona[insert_pos:]
                skip = "\n\n（暂无记录）"
                if rest.startswith(skip):
                    rest = rest[len(skip):]
                new_persona = current_persona[:insert_pos] + correction_line + rest
            else:
                new_persona = (
                    current_persona
                    + f"\n\n## Correction 记录\n{correction_line}\n"
                )
            meta["corrections_count"] = meta.get("corrections_count", 0) + 1
        else:
            new_persona = current_persona + "\n\n" + persona_patch

        (skill_dir / "persona.md").write_text(new_persona, encoding="utf-8")

    # 重新生成 SKILL.md
    memories_content = (skill_dir / "memories.md").read_text(encoding="utf-8")
    persona_content = (skill_dir / "persona.md").read_text(encoding="utf-8")
    name = meta.get("name", skill_dir.name)
    identity = build_identity_string(meta)

    skill_md = SKILL_MD_TEMPLATE.format(
        slug=skill_dir.name,
        name=name,
        identity=identity,
        memories_content=memories_content,
        persona_content=persona_content,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # 更新 meta
    meta["version"] = new_version
    meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return new_version


def list_exes(base_dir: Path) -> list:
    """列出所有已创建的前任 Skill"""
    exes = []

    if not base_dir.exists():
        return exes

    for skill_dir in sorted(base_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        meta_path = skill_dir / "meta.json"
        if not meta_path.exists():
            continue

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        exes.append({
            "slug": meta.get("slug", skill_dir.name),
            "name": meta.get("name", skill_dir.name),
            "identity": build_identity_string(meta),
            "version": meta.get("version", "v1"),
            "updated_at": meta.get("updated_at", ""),
            "corrections_count": meta.get("corrections_count", 0),
        })

    return exes


def main() -> None:
    parser = argparse.ArgumentParser(description="Skill 文件写入器")
    parser.add_argument("--action", required=True, choices=["create", "update", "list"])
    parser.add_argument("--slug", help="前任 slug（用于目录名）")
    parser.add_argument("--name", help="前任昵称")
    parser.add_argument("--meta", help="meta.json 文件路径")
    parser.add_argument("--memories", help="memories.md 内容文件路径")
    parser.add_argument("--persona", help="persona.md 内容文件路径")
    parser.add_argument("--memories-patch", help="memories.md 增量更新内容文件路径")
    parser.add_argument("--persona-patch", help="persona.md 增量更新内容文件路径")
    parser.add_argument(
        "--base-dir",
        default="./exes",
        help="前任 Skill 根目录（默认：./exes）",
    )

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser()

    if args.action == "list":
        exes = list_exes(base_dir)
        if not exes:
            print("暂无已创建的前任 Skill")
        else:
            print(f"已创建 {len(exes)} 个前任 Skill：\n")
            for e in exes:
                updated = e["updated_at"][:10] if e["updated_at"] else "未知"
                print(f"  [{e['slug']}]  {e['name']} — {e['identity']}")
                print(f"    版本: {e['version']}  纠正次数: {e['corrections_count']}  更新: {updated}")
                print()

    elif args.action == "create":
        if not args.slug and not args.name:
            print("错误：create 操作需要 --slug 或 --name", file=sys.stderr)
            sys.exit(1)

        meta: dict = {}
        if args.meta:
            meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
        if args.name:
            meta["name"] = args.name

        slug = args.slug or slugify(meta.get("name", "ex"))

        memories_content = ""
        if args.memories:
            memories_content = Path(args.memories).read_text(encoding="utf-8")

        persona_content = ""
        if args.persona:
            persona_content = Path(args.persona).read_text(encoding="utf-8")

        skill_dir = create_skill(base_dir, slug, meta, memories_content, persona_content)
        print(f"✅ Skill 已创建：{skill_dir}")
        print(f"   触发词：/{slug}")

    elif args.action == "update":
        if not args.slug:
            print("错误：update 操作需要 --slug", file=sys.stderr)
            sys.exit(1)

        skill_dir = base_dir / args.slug
        if not skill_dir.exists():
            print(f"错误：找不到 Skill 目录 {skill_dir}", file=sys.stderr)
            sys.exit(1)

        memories_patch = Path(args.memories_patch).read_text(encoding="utf-8") if args.memories_patch else None
        persona_patch = Path(args.persona_patch).read_text(encoding="utf-8") if args.persona_patch else None

        new_version = update_skill(skill_dir, memories_patch, persona_patch)
        print(f"✅ Skill 已更新到 {new_version}：{skill_dir}")


if __name__ == "__main__":
    main()
