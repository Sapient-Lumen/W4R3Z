# DeriveBSD rev0529 session audit — launch evidence split and runner-environment resume binding

## Focus

This revision closed the last listed p0 post-detach schema split and corrected a resumable-ledger trust gap that was still risky for cloudtainer work. The cube target was `removable.media.local.post_detach.launch.evidence` because launch evidence is close to the fd-bound worker proof surface and should not keep exact historical literals in the runtime contract.

## Substantive changes

- Split `spec/removable.media.local.post_detach.launch.evidence.schema.json` into a generic runtime contract plus `spec/removable.media.local.post_detach.launch.evidence.fixture.schema.json` for exact canonical fixture literals.
- Updated `tools/check_removable_media_local_post_detach_launch_evidence.py` so canonical launch evidence validates against both schemas while the runtime schema stays generic and const-free.
- Updated docs/760 and ADR-0349 so launch evidence readers know which schema is runtime-facing and which is exact regression fixture evidence.
- Extended `tools/hygiene.py` resumable-ledger semantics with `runner_environment_sha256` and `runner_environment_scope`, binding passed rows to the Python/jsonschema validation engine as well as checker bytes and cube input bytes.
- Extended `spec/cube.hygiene.run.ledger.schema.json` and `tools/check_cube_hygiene_run_ledger.py` so stale runner-environment rows are rejected during resume.
- Refreshed generated/current cube surfaces for r561 and kept the front-door line budget within the hard ceiling.

## Why this matters

The post-detach p0 split queue is now closed: runtime receipt schemas no longer need to carry exact historical literals for the targeted lifecycle proofs. Exact canonical objects are still preserved, but they live in fixture schemas where they belong.

The runner-environment binding closes a subtler completion-risk hole. Previous revs made resume safe across source/docs/spec/tool changes, but a partial ledger could still be replayed under a different interpreter or jsonschema version. That can hide validation-engine drift. Rev0529 makes the validation engine part of the evidence surface.

## Validation evidence

- `release-critical`: 35/35 passed.
- `post-detach`: 39/39 passed via explicit small chunks and input/runner-fingerprinted resume.
- `schema-cube-audit`: 3/3 passed.
- `generated-surface`: 2/2 passed.
- `tools/check_removable_media_local_post_detach_launch_evidence.py` passed.
- `tools/check_cube_hygiene_run_ledger.py` passed.
- `tools/lint_spec_schemas.py` passed.
- `tools/validate_spec_examples.py` passed for 467 examples.

## Current cube audit movement

- Schemas: 455.
- Examples: 467.
- Runtime-contract-shaped schemas: 40.
- Exact fixture schemas: 17.
- Backlog items: 25 total, 17 completed, 8 open.
- Audit next targets: 0.

## Next recommended cut

With the p0 post-detach split queue closed, the next risk-first move is not another registry pass. Either harden the remaining legacy p1/p2 exact-literal surfaces that are actually runtime-critical, starting with `spec/net.publish.session.schema.json` if it is still a live runtime contract, or shift effort to real FreeBSD host proof for the removable-media worker path.
