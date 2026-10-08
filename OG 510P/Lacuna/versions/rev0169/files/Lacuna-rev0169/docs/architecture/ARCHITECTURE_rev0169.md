# Architecture — rev0169

## Purpose

Revision 0169 is a send-ready test-harness, license, and scenario-template polish pass. It does not change the database schema, event schema, story ledger semantics, checkpoint authority, scenario condition topology, bundle state machine, or provider boundary. Its purpose is to remove the last acceptance-surface ambiguity found in rev0168: tests should complete or fail explicitly inside bounded recipient windows, and generated experiment templates should not accidentally run with placeholder text.

## Changes under audit

```text
src/lacuna/store.py              non-blocking passive WAL cleanup at close
src/lacuna/scenarios.py          fail-closed generated capsule placeholders
tools/run_acceptance.py          per-module bounded acceptance runner
LICENSE                          MIT license
README / START_HERE / docs       current rev0169 acceptance instructions
REVISION.json / ACCEPTANCE_rev0169.json / MANIFEST.sha256
```

## Retained architecture

Rev0169 retains managed ordinary turn runs, source-bound checkpoint runs, fresh post-checkpoint narrator dispatches, partial versus complete public-history custody, four-condition scenario runs, replicated bundles, whole-retained-tree canary scans, post-primary-rating method-identifiability artifacts, bundle block seals, parent-opened bundle child unblind gates, and read-only extracted-artifact checks.

## Teardown principle

Story durability is provided by SQLite WAL recovery and already-committed events, not by a blocking truncating checkpoint during Python fixture teardown. Close-time cleanup now attempts a short passive checkpoint and then closes, allowing later opens to continue normal WAL recovery.

## Authority boundary

This revision adds no new story-authoring or worker power. The acceptance runner, license, template validation, release records, and tests are package custody. They do not mutate story state, attest providers, prove fresh memory, or evaluate narrative quality.
