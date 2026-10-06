# Future refactor information design

Revision: rev0028.

Future refactors should be guided by artifacts, not vibes. The cube should make it obvious what changed, what needs testing, and what claims are earned.

## Information future sessions need

For each slice, future sessions need:

- the primitive being tested;
- the provider being used;
- the artifact path;
- the exact manifest id;
- the estimated runtime;
- the failure/non-claim boundary;
- which future slice depends on it;
- whether it is fake-provider, Node, browser, OPFS, SAB, or GPU.

## Current gaps

The current cube still has some manual revision churn. Artifact names and proof command paths are not fully generated from one source of truth. Rev0022 introduces `CUBE-META.json` and a generic `tools/run_current_proof.mjs`, but more generation would help.

## Desired future helper

A future helper could be:

```bash
node tools/add_slice.mjs --id storage:persisted-spill-recovery-proof --lane storage --tier release
```

It would update the manifest, impact map, surface inventory, validation doc stub, receipt stub, and artifact path consistently.

Do not build that helper until hand edits become the bottleneck. For now, the checklist is enough.
