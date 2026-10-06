# Unprivileged + distributed bulk builds (pkgsrc pbulk lessons)

Pkgsrc’s bulk build tooling (`pbulk`) supports:
- unprivileged bulk builds
- distributed worker builds (via chroots or remote SSH nodes)

References:
- NetBSD pkgsrc bulk build guide (pbulk, unprivileged + distributed). https://www.netbsd.org/docs/pkgsrc/bulk.html

## DeriveBSD direction

Treat “builder pools” as a first-class resource:
- builders run unprivileged by default
- distributed workers are normal (not an afterthought)
- action cache keys are derived from Plan + environment normalization

This complements:
- `docs/104-builder-tiers.md`
- witness rebuilders (`docs/116-witness-rebuilders-diffoscope.md`)
- optional REAPI-aligned builder pools (`docs/136-remote-execution-api-builder-pools.md`)

## v1 minimalism

- allow multiple builder nodes but require:
  - identical builder base digest
  - identical toolchain digests
  - deny-network by default (fetchers separated)

See RFC-0086.
