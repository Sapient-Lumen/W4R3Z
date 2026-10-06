# ADR-0194: Publish-session current contract stack stays canonical and pointer-backed

- Status: Accepted
- Date: 2026-03-20

## Context

The recent publish-session tightening cluster from `docs/593-*` through `docs/603-*` now carries a dense sequence of small laws.
That density is good for precision, but it also creates a new archive-local failure mode: nearby entry docs and numbered publish-session docs can start acting like stale partial companion lists.

Several neighboring datacubes converged on the same maintenance lesson: once a contract cluster gets dense enough, keep one explicit current head/register/map and make local entrypoints point back to it rather than letting each nearby page improvise its own summary of the current stack.

DeriveBSD already prefers one exact law plus one exact checker over ambient folk memory.
The same discipline should apply to the archive's own current-stack navigation for the recent publish-session cluster.

## Decision

We define `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` as the canonical current-stack map for the recent publish-session tightening cluster spanning `docs/593-*` through `docs/603-*`.

Main entry surfaces and nearby publish-session docs must point back to that canonical current-stack map instead of acting as free-form partial companion lists.

This is an archive-control decision only.
It does **not** widen the schema or change `net.publish.session` semantics.
`session_version` therefore stays `0.33`.

## Consequences

- Maintainers get one compact canonical map for the recent publish-session contract stack.
- Nearby docs stay locally useful without silently becoming stale partial registries.
- Archive hygiene can verify that the main entry surfaces and recent numbered publish-session docs still point back to the current-stack map.
- This strengthens archive self-coherence without widening the product architecture.
