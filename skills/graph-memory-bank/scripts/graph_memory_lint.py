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


FM_DELIM = "---"


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
        m = re.search(rf"(?m)^{re.escape(key)}:\\s*\"?([^\"\\n]+)\"?\\s*$", fm_text)
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

    for p in sorted(md_files):
        fm, err = _read_frontmatter(p)
        if err:
            errors.append((p, err))
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
                errors.append((p, f"missing_{k}"))

        if fm.id:
            ids.setdefault(fm.id, []).append(p)

    dup_ids = {k: v for k, v in ids.items() if len(v) > 1}

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
