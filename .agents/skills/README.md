# Project marketing skills

These skills are vendored from
[`alirezarezvani/claude-skills`](https://github.com/alirezarezvani/claude-skills)
at commit `aa8d778811a557a2c28ccadda4cf3d0bd028a4cc` and adapted for Big
Sky AI.

The upstream MIT license is preserved in `UPSTREAM-LICENSE`. Adaptations are
intentionally project-local: every skill must read `docs/marketing-context.md`
before making recommendations or changing public copy.

Installed skills:

- `marketing-context`
- `seo-audit`
- `schema-markup`
- `copy-editing`
- `content-strategy`
- `social-content`

The Herrington-only `social-pipeline-ops` skill is not included. It depends on
that project's manifests, commands, Metricool configuration, and social ledger;
Big Sky AI has no equivalent publishing pipeline.

Do not update these folders by running the upstream bulk installer. Review and
vendor upstream changes selectively so the Big Sky AI guardrails are not
overwritten.
