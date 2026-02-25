# Graph Memory Bank (Agent Skill)

Universal skill for building and maintaining an Obsidian-style graph memory bank inside a repository (usually `docs/graph/`).
Optimized for AI-agent context retrieval: atomic Markdown nodes with YAML frontmatter, dense cross-links, explicit backlinks, and incremental maintenance.

## Install (skills.sh)

Example:

```bash
npx skills add <owner>/<repo> --skill graph-memory-bank
```

Then invoke the skill per your tool's conventions (Codex/Claude Code/OpenCode).

## What’s inside

- `skills/graph-memory-bank/SKILL.md` – the canonical, tool-agnostic instructions.
- `skills/graph-memory-bank/references/` – templates and quality bar.
- `skills/graph-memory-bank/scripts/` – lightweight linter.
- `skills/graph-memory-bank/portable/` – adapters/examples for other tools.

## License

MIT
