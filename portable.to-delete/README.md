# Portable Graph Memory Bank (cross-tool pack)

Нет одного “универсального” стандарта скиллов, который одинаково понимают Codex, Claude Code и OpenCode.
Практичный вариант: держать один и тот же контент промпта и иметь маленькие “адаптеры” под конкретные инструменты.

Эта папка как раз про это.

## Что является “каноном”

- `portable/prompt.md` — каноничный промпт/инструкция (tool-agnostic).

## Codex

Codex-формат скилла находится в корне папки скилла:
- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`

Для переноса достаточно целиком папки `graph-memory-bank/`.

## Claude Code

Claude Code понимает:
- проектные инструкции в `CLAUDE.md`
- кастомные команды в `.claude/commands/*.md`

Готовые адаптеры:
- `portable/claude/CLAUDE.md` (короткий фрагмент, который можно включить в проект)
- `portable/claude/.claude/commands/graph-memory-bank.md` (slash-команда)

## OpenCode

OpenCode конфигурирует агентов через `opencode.json` и может подтягивать prompt из файла.

Готовые адаптеры:
- `portable/opencode/opencode.json` (пример агента)
- `portable/opencode/prompts/graph-memory-bank.md` (prompt для агента)

