# Cube audit rev0025 — foundation coherence pass

Revision: rev0028.

This revision deliberately does not advance a new runtime feature. It pauses to audit whether future sessions can resume the office without accidentally flattening BrowserRT into vague ambition, stale artifacts, or overclaims.

## What was audited

The pass checked these surfaces:

- current revision metadata: `CUBE-META.json`, `REVISION-RECEIPT.json`, `REENTRY-CONTRACT.json`, `SURFACE-STATUS.json`, `VALIDATION-INDEX.json`, `package.json`, and `src/browserrt.mjs`;
- future-session handoff: `START_HERE.md`, `CONTEXT-PACK.md`, `docs/00-meta/future-session-office-manual.md`, and `docs/00-meta/non-claims-and-goals-charter.md`;
- test facility: `test/manifest.json`, `test/impact-map.json`, `test/surface-inventory.json`, `test/quarantine.json`, `tools/run_tests.mjs`, and `src/test-facility.mjs`;
- artifact hygiene: current-prefix artifacts, broad release browser-light posture, and retention pressure;
- release economics: per-task estimated time, timeout budgets, and browser/CDP containment.

## Important finding

The audit found a real affected-selection bug in `tools/run_tests.mjs`.

In rev0021, this command could plan an empty run:

```bash
node tools/run_tests.mjs --tier release --changed tools/run_tests.mjs --only-affected --dry-run
```

The cause was subtle: impacted task ids were copied into `--id`, but the original changed-file input filter was still active. Some impacted tasks do not list `tools/run_tests.mjs` in their own inputs, so the runner could select the intended ids and then filter them out.

Rev0022 fixes this by preserving the impacted id set in the selector and adds `facility:affected-runner-dry-run` so the bug cannot silently return.

## Testing architecture verdict

The current test facility is directionally right for the long run:

- tests are manifest-addressable;
- expensive browser/CDP tests are outside broad release by default;
- each task has estimated time, timeout, lane, size, risk, capabilities, and output artifacts;
- timing reports and analysis are generated;
- affected selection and impact maps exist;
- browser processes are one-shot fixtures, not cross-turn daemons.

The facility still needs future hardening:

- more automatic revision/artifact path generation;
- stronger changed-file matrix tests;
- budget-aware release slicing when semantic proofs grow;
- historical artifact retention enforcement;
- maybe a generated manifest helper so future sessions add tests correctly instead of hand-editing many surfaces.

## Artifact retention decision

Current package artifacts should be current-prefix by default. Historical changes belong in `CHANGELOG.md` and docs, not in copied stale generated artifacts unless a previous artifact is intentionally archived and named as historical evidence.

This keeps future sessions from reading stale proof JSON as current truth.

## Non-claim reinforcement

This audit does not prove BrowserRT semantics. It proves the cube foundation is coherent enough to keep working:

```txt
handoff docs + test manifest + impact selection + artifact hygiene + non-claims + browser-light release posture
```

No performance, durability, browser conformance, WebGPU, mesh, or production scheduler claim is promoted by this revision.

## Next slice reminder

The deferred feature slice remains:

```txt
Persisted-spill recovery model.
```

That slice should be fake-provider/model-first before any OPFS/browser spending.
