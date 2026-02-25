#!/usr/bin/env python3
"""
Lightweight linter for graph memory banks.

Goal: catch the most damaging issues for AI-agent retrieval:
  - missing YAML frontmatter
  - missing id/type/title/status
  - duplicate ids

Keep it dependency-free (no PyYAML).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from urllib.parse import unquote


FM_DELIM = "---"
FENCE = "```"


@dataclass(frozen=True)
class Frontmatter:
    id: str | None
    type: str | None
    title: str | None
    status: str | None


def _read_frontmatter(path: Path) -> tuple[Frontmatter | None, str | None]:
    """
    Return (frontmatter, error). If file has no parseable frontmatter, return (None, error).
    This is deliberately strict: YAML must be the first thing in the file.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return None, f"read_error: {e}"

    if not text.startswith(FM_DELIM + "\n"):
        return None, "missing_frontmatter"

    end = text.find("\n" + FM_DELIM + "\n", len(FM_DELIM) + 1)
    if end == -1:
        # allow EOF delimiter too
        end = text.find("\n" + FM_DELIM, len(FM_DELIM) + 1)
        if end == -1:
            return None, "unterminated_frontmatter"

    fm_text = text[len(FM_DELIM) + 1 : end]

    # Minimal YAML-ish extraction. Good enough for the recommended schema.
    def pick(key: str) -> str | None:
        # NOTE: Use real whitespace/newline tokens. Avoid over-escaping '\s'/'\n',
        # otherwise we end up matching a literal backslash and never extracting keys.
        m = re.search(rf"(?m)^{re.escape(key)}:\s*\"?([^\"\n]+)\"?\s*$", fm_text)
        if not m:
            return None
        return m.group(1).strip()

    return (
        Frontmatter(
            id=pick("id"),
            type=pick("type"),
            title=pick("title"),
            status=pick("status"),
        ),
        None,
    )


def _strip_fenced_code_blocks(text: str) -> str:
    """
    Remove fenced code blocks (``` ... ```) to reduce false positives when parsing links.
    This is intentionally simple and line-based.
    """
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith(FENCE):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def _extract_markdown_link_targets(text: str) -> list[str]:
    """
    Extract raw link targets from markdown links/images: [text](target), ![alt](target).
    Intentionally lightweight (no full markdown parser).
    """
    stripped = _strip_fenced_code_blocks(text)
    targets: list[str] = []
    # Match both links and images: [text](target) / ![alt](target)
    for m in re.finditer(r"!?\[[^\]]*\]\(([^)]+)\)", stripped):
        t = (m.group(1) or "").strip()
        if not t:
            continue
        targets.append(t)
    return targets


def _normalize_link_target(raw: str) -> str:
    t = raw.strip()
    if t.startswith("<") and t.endswith(">"):
        t = t[1:-1].strip()
    # drop query/fragment
    for sep in ("#", "?"):
        if sep in t:
            t = t.split(sep, 1)[0].strip()
    # markdown escapes / URL encoding
    t = t.replace("\\)", ")").replace("\\(", "(")
    t = unquote(t)
    return t


def _is_external_link(target: str) -> bool:
    t = target.lower()
    if t.startswith("#"):
        return True
    if "://" in t:
        return True
    if t.startswith("mailto:") or t.startswith("tel:"):
        return True
    return False


def _resolve_link_path(from_file: Path, target: str) -> Path:
    # Resolve relative to the file folder. Treat absolute paths as absolute.
    if os.path.isabs(target):
        return Path(target).resolve()
    return (from_file.parent / target).resolve()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root",
        default="docs/graph",
        help="Root folder of the graph memory bank (default: docs/graph)",
    )
    ap.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Glob to exclude (repeatable), matched against path relative to --root. Example: '**/_generated/**'",
    )
    ap.add_argument(
        "--required",
        default="id,type,title,status",
        help="Comma-separated required keys (default: id,type,title,status)",
    )
    ap.add_argument(
        "--check-links",
        dest="check_links",
        action="store_true",
        default=True,
        help="Check that local markdown links to *.md files exist (default: true).",
    )
    ap.add_argument(
        "--no-check-links",
        dest="check_links",
        action="store_false",
        help="Disable broken-link checks.",
    )
    ap.add_argument(
        "--check-orphans",
        dest="check_orphans",
        action="store_true",
        default=True,
        help="Check for orphan nodes (no inbound links within --root). Default: true.",
    )
    ap.add_argument(
        "--no-check-orphans",
        dest="check_orphans",
        action="store_false",
        help="Disable orphan-node checks.",
    )
    ap.add_argument(
        "--root-index",
        default="index.md",
        help="File name treated as the root entrypoint for orphan checks (relative to --root). Default: index.md",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    required = [s.strip() for s in args.required.split(",") if s.strip()]
    # Support a common "globstar" habit: treat "**" same as "*"
    exclude_globs = [g.strip().replace("**", "*") for g in args.exclude if g.strip()]

    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2

    md_files: list[Path] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(".md"):
                p = Path(dirpath) / fn
                rel = str(p.relative_to(root))
                if any(fnmatch(rel, g) for g in exclude_globs):
                    continue
                md_files.append(p)

    errors: list[tuple[Path, str]] = []
    ids: dict[str, list[Path]] = {}
    inbound: dict[Path, int] = {p.resolve(): 0 for p in md_files}

    def record_error(p: Path, code: str) -> None:
        errors.append((p, code))

    for p in sorted(md_files):
        fm, err = _read_frontmatter(p)
        if err:
            record_error(p, err)
            continue

        assert fm is not None
        kv = {
            "id": fm.id,
            "type": fm.type,
            "title": fm.title,
            "status": fm.status,
        }
        for k in required:
            if not kv.get(k):
                record_error(p, f"missing_{k}")

        if fm.id:
            ids.setdefault(fm.id, []).append(p)

        if args.check_links or args.check_orphans:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                record_error(p, f"read_error: {e}")
                continue

            for raw_target in _extract_markdown_link_targets(text):
                if _is_external_link(raw_target):
                    continue
                target = _normalize_link_target(raw_target)
                if not target:
                    continue
                if not target.lower().endswith(".md"):
                    continue

                resolved = _resolve_link_path(p, target)

                if args.check_links and not resolved.exists():
                    record_error(p, f"broken_link:{target}")

                if args.check_orphans:
                    resolved_norm = resolved.resolve()
                    if resolved_norm in inbound and resolved_norm != p.resolve():
                        inbound[resolved_norm] += 1

    dup_ids = {k: v for k, v in ids.items() if len(v) > 1}

    if args.check_orphans:
        root_index = (root / str(args.root_index)).resolve()
        for p in sorted(md_files):
            pp = p.resolve()
            if pp == root_index:
                continue
            if inbound.get(pp, 0) == 0:
                record_error(p, "orphan_node")

    def safe_print(s: str = "") -> None:
        try:
            print(s)
        except BrokenPipeError:
            # piping into head(1) etc
            raise SystemExit(1)

    if errors:
        safe_print("Frontmatter issues:")
        for p, e in errors:
            rel = p.relative_to(root.parent) if root.parent in p.parents else p
            safe_print(f"- {rel}: {e}")

    if dup_ids:
        safe_print("\nDuplicate ids:")
        for _id, paths in sorted(dup_ids.items()):
            safe_print(f"- id: {_id}")
            for p in paths:
                rel = p.relative_to(root.parent) if root.parent in p.parents else p
                safe_print(f"  - {rel}")

    if errors or dup_ids:
        return 1

    safe_print(f"OK: {len(md_files)} markdown files under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
