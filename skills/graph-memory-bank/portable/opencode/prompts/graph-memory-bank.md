Build and maintain an Obsidian-style graph memory bank inside this repository, optimized for AI-agent context retrieval.

Hard requirements:
- Prefer Russian unless the user requests English.
- Atomic nodes: one Markdown file per concept/entity/contract.
- Small nodes: split if it grows.
- YAML frontmatter in every node: id/type/title/description/status/tags.
- Use many cross-links and explicit backlinks.
- Never put secrets/credentials in docs (only locations/var names).
- Do not edit generated sections by hand.

Default structure (create if missing):
- docs/graph/tasks/ (releases, tickets, commits, what changed)
- docs/graph/project/ (system semantics: architecture, API, DB, integrations, where to look)
- docs/graph/processes/ (how to maintain the graph, quality rules, generators)

Workflow:
1) Bootstrap the skeleton and indexes (annotate links in indexes).
2) Release-driven pass: for each release/tag/changelog range, list changed entities, create/upgrade ticket nodes, and link into project semantics.
3) Entity-driven pass: pick 5-12 entity categories relevant to the project:
   - entrypoints: UI pages/routes, API endpoints, jobs, events/topics
   - operations: use-cases, commands, workflows
   - data/contracts: DB models, migrations, OpenAPI/AsyncAPI, schemas
   - integrations: external systems, protocols, retries/timeouts/idempotency
   - config/feature flags
   - security (authn/authz, roles, audit)
   - ops (logs/metrics/tracing, alerting, recovery)
   Build catalogs (indexes/hubs) for each category and connect entities across categories.
4) Keep it incremental: every new change updates only affected nodes + indexes/backlinks.

