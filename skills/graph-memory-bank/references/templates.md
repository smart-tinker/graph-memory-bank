# Шаблоны узлов (Graph Memory Bank)

Все шаблоны ниже намеренно “тонкие”: заполни минимально, потом наращивай по мере нахождения evidence.

Рекомендация: держи `description` как 1 предложение, которое объясняет “зачем этот узел существует”.

## Узел: индекс (index)

```md
---
id: "graph:<layer>/<name>"
type: "index"
title: "<Заголовок>"
description: "<Коротко: что тут лежит и зачем>"
status: "curated"
tags:
  - "<layer>"
---

# <Заголовок>

## Разделы

- [<Узел 1>](...)
- [<Узел 2>](...)
```

## Узел: ревью релиза (release_review)

```md
---
id: "graph:tasks/reviews/release-<name>-<version>"
type: "release_review"
title: "Ревью: релиз <name> <version>"
description: "Ревью релиза <name> <version>: список затронутых сущностей и покрытие графовой документацией."
status: "curated"
tags:
  - "tasks"
  - "release"
release: "<version>"
---

# Ревью: релиз <name> <version>

## Якоря

- релиз-нота: `<path>`
- git range: `<a..b>`

## Список сущностей

### Задачи

- [DEV-xxxxx](../dev/DEV-xxxxx.md) <кратко>

### Подсистемы/артефакты

- <модули/папки/сервисы>

### Точки входа в граф

- [Проект (индекс)](../../project/index.md)
```

## Узел: DEV задача (dev_task)

```md
---
id: "graph:tasks/dev/DEV-<num>"
type: "dev_task"
title: "DEV-<num>: <краткий заголовок>"
description: "<1 предложение: что изменено>"
status: "stub" # -> curated, когда добавлен evidence и связи
tags:
  - "tasks"
  - "dev"
dev: "DEV-<num>"
releases:
  - "<version>"
source_paths:
  - "<путь-в-репо>"
---

# DEV-<num>: <краткий заголовок>

## Коротко

<2-6 буллетов по сути изменений>

## Evidence (где смотреть)

- коммиты: `<hash>` (опционально)
- якоря в коде/SQL/конфиге: `<paths>`

## Затронутые сущности (семантика)

- [<семантический узел>](../../project/<...>.md)

## Релизы и обратные ссылки

- релиз: [<version>](../releases/release-<...>.md)
- ревью: [<version>](../reviews/release-<...>.md)
```

## Узел: семантическая сущность проекта (project)

```md
---
id: "graph:project/<slug>"
type: "project"
title: "<Сущность/подсистема>"
description: "<Зачем этот узел: что он объясняет агенту>"
status: "curated"
tags:
  - "project"
  - "semantics"
source_paths:
  - "<якоря>"
---

# <Сущность/подсистема>

## Что это

<кратко>

## Точки входа (куда смотреть в коде)

- `<path>`

## Связанные узлы

- [<узел>](...)
```

## Узел: ключ конфигурации / feature flag

```md
---
id: "graph:project/config/<KEY>"
type: "config"
title: "<SYSTEM>: <KEY>"
description: "Ключ/флаг конфигурации <KEY>: влияние и контекст."
status: "curated"
tags:
  - "config"
---

# <KEY>

## Контекст

- добавлен/изменен в: `<path>`
- релиз/задача: [DEV-xxxxx](../../tasks/dev/DEV-xxxxx.md)

## Где используется

- `<path>` (код)
```

