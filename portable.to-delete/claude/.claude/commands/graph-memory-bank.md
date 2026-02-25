# Graph Memory Bank (portable)

Цель: создать или поддерживать графовую память проекта (Obsidian-стиль) в `docs/graph/`, чтобы ИИ-агенты могли быстро и экономно собирать точный контекст.

Параметры из запроса пользователя: `$ARGUMENTS`

## Правила

- Узлы атомарные и маленькие.
- У каждого узла YAML frontmatter: `id/type/title/description/status/tags`.
- Максимум ссылок, включая backlinks.
- Никаких секретов в docs.
- Generated не редактировать руками.

## Структура

- `docs/graph/tasks/`: релизы/задачи/коммиты.
- `docs/graph/project/`: семантика системы (архитектура, контракты, API, DB, интеграции).
- `docs/graph/processes/`: правила ведения графа и качество.

## Процесс

1. Если каркаса нет: создай `docs/graph/index.md` и индексы слоев.
2. Release-driven: возьми ближайший релиз/тэг/ноту, выпиши сущности, создай/обнови `dev_task` узлы и связи на `project/*`.
3. Entity-driven: выбери категории сущностей, релевантные проекту (UI/API/Jobs/Events, operations, data/contracts, integrations, config, security, ops) и добей каталоги/узлы.
4. Обновляй индексы и обратные ссылки.

