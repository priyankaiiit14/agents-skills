---
name: security-review
description: Security-focused review of changed code on the current branch. Checks for OWASP top 10 and common vulnerabilities.
user-invocable: true
---

Run `git diff main...HEAD` to get changed files. Review for:

1. **Injection** — SQL, shell, XSS, template injection via unsanitized input
2. **Auth** — missing auth checks, privilege escalation, insecure defaults
3. **Secrets** — hardcoded keys, tokens, passwords, or paths in code/logs
4. **Data exposure** — PII in logs, overly broad API responses, unmasked errors
5. **Deps** — newly added packages with known CVEs (`pip audit` / `npm audit` if applicable)
6. **Crypto** — weak algorithms, hardcoded salts, client-side-only validation

Output: one finding per line — file:line, issue, severity (critical/high/medium). Skip clean areas entirely.
