# Contributing

Branching: short-lived branches, PR to main, no direct pushes to main including trivial changes.
Commits: short imperative subject, link the issue.
PRs: use the PR shape from the Project template; `Closes` only work that completes acceptance, `Refs` otherwise.
Review: correctness against acceptance, readability and boundaries, errors and failure paths, security and authorization, tests for important cases, data and migration safety, contract compatibility. Block on wrong behavior, missing tests for risky paths, security or data risk, or unverified acceptance; do not block on style the linter can enforce.
Releases: through the delivery job with a version and a delivery record.
Task verbs in `Taskfile.yml` are the only entry points.
