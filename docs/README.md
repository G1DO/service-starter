# docs

Canonical homes live in the repo per Template; Notion links here, never pastes.

- `docs/architecture/` holds the diagram sources (sole source plus pointers).
- `docs/contracts/`, `docs/adr/`, `docs/runbook/`, `docs/postmortem/` are N/A absent:
  no trigger has fired (no external consumers, no consequential choices,
  no production operation, no incidents). When a trigger fires, add the
  directory with its files in the same pull request that introduces the need.
- `migrations/` holds current execution only (see its README for expand-contract).
- `sbom.cdx.json` and `provenance.json` are N/A absent: no distribution claimed.
  When external distribution fires, `task deliver` generates them and `deliver.yml`
  publishes them to release assets where consumers can find them.
