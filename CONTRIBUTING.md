# Contributing to Kernel Module Manager

We welcome issues and pull requests that improve diagnostic reliability, security controls, evaluation coverage, or documentation accuracy.

## Development Workflow

1. Fork and clone the repository.
2. Ensure you have Go 1.22+ and Python 3.11+ installed.
3. Verify test suites and linters pass:
   ```bash
   make test
   make lint
   ```
4. Run the offline evaluation smoke test:
   ```bash
   make eval
   ```
5. Follow Conventional Commits for commit messages (`feat: ...`, `fix: ...`, `test: ...`, `docs: ...`).

## Architecture & Diagram Changes

If you modify system components or data flows, update the corresponding Archify JSON definitions in `docs/diagrams/` and validate them before submitting your PR:

```bash
node ~/.agents/skills/archify/bin/archify.mjs validate <type> docs/diagrams/<name>.json --quality showcase --repo-root .
node ~/.agents/skills/archify/bin/archify.mjs deliver <type> docs/diagrams/<name>.json docs/diagrams/<name>.html --quality showcase --repo-root .
```

## Security Contributions

Please report any security findings according to the process outlined in [SECURITY.md](SECURITY.md).
