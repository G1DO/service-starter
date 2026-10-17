# Migrations

No migrations yet. When the service owns relational data, use expand-contract: expand (additive), migrate/backfill, contract. Forward-only; omit down migrations unless upgrade→downgrade→upgrade is exercised in CI.
