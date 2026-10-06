# Cube audit — rev0031

This audit pass did two things:

1. Added a new resilience proof and contract audit.
2. Refactored stale currentness surfaces, especially `Makefile`, after finding rev0029 artifact paths in a rev0030 package.

## Finding: stale Makefile artifact paths

The extracted rev0030 cube had `package.json` and runtime constants aligned to rev0030, but `Makefile` still contained rev0029 artifact paths in several convenience targets. Manifest-driven release tests were not broken because the manifest used explicit current paths, but future sessions running `make lint`, `make test-release`, or older convenience targets could have written confusing stale artifacts.

## Fix

Rev0031 rewrites `Makefile` to derive current revision/prefix through Node once:

```make
REV := $(shell node -e "import('./src/browserrt.mjs').then(m=>process.stdout.write(m.REVISION))")
PFX := $(shell node -e "import('./src/browserrt.mjs').then(m=>process.stdout.write('REV'+m.REVISION.slice(3)))")
```

Future session rule: do not hardcode previous revision artifact prefixes in convenience commands.

## Current posture

- Broad release remains browser-light.
- New slice is release-tier and fake-provider.
- Non-claims are legible in `REVISION-RECEIPT.json`, `CONTEXT-PACK.md`, and `docs/00-meta/non-claims-and-goals-charter.md`.
