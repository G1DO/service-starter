# docs

Canonical homes live in the repo per Template; Notion links here, never pastes.

- `docs/architecture/` holds the diagram sources (sole source plus pointers).
- `docs/contracts/`, `docs/adr/`, `docs/runbook/`, `docs/postmortem/` are N/A absent:
  no trigger has fired (no external consumers, no consequential choices,
  no production operation, no incidents). When a trigger fires, add the
  directory with its files in the same pull request that introduces the need.
- `migrations/` holds current execution only (see its README for expand-contract).
