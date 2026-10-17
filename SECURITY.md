# Security

Report: open a private security advisory or email the repo owner with affected version, reproduction, and impact. Do not open a public issue for vulnerabilities.
Handling: acknowledge within 2 working days, fix privately, disclose after a fix is available.
Secrets: never committed and never pasted into Notion, issues, PRs, comments, or logs; environment-specific config stays out of the repo; enable GitHub secret scanning + push protection, with gitleaks as defense-in-depth in pre-commit and CI (full history).
Dependencies: update monthly, critical within 7 days; Dependabot alerts + version updates on, dependency review blocks new vulns at PR time.
Sensitive paths follow the CODEOWNERS rule.
