# Audit — rev0157

## Scope

This audit targeted the boundary between `ready-to-commit` and actual kernel mutation in rev0156, then reviewed recovery and concurrency consequences created by strengthening that boundary.

The audit covered:

- proposal normalization and model-generated identifiers;
- changeset execution and rollback behavior;
- turn-run readiness transitions;
- exact event and projection custody;
- direct commit mismatch handling;
- post-commit crash retry;
- historical context authentication;
- same-run concurrency and lock-file substitution;
- schema/document/provider consistency; and
- preservation of database schema 8 and event schema 1.

## Finding A — readiness overstated sidecar validation

**Prior state.** A valid proposal plus required advisory verifier state could make a run ready before the mutation engine had executed every operation.

**Risk.** A less capable coordinator could reasonably read “ready” as kernel-executable. Semantic operation errors would appear only at commit, after the workflow had declared success.

**Repair.** Add `lacuna.turn-preparation.v1`; execute the exact normalized change through the real engine, collect post-state artifacts, roll back, replay again, and publish readiness only after exact comparison.

**Result.** A kernel-invalid proposal remains at the prior stage and no final proposal/preparation manifest transition is published.

## Finding B — separate preview logic would be a future split-brain

**Risk.** A hand-written dry-run implementation would need to duplicate every operation, projection, review-head, and constraint rule.

**Repair.** Refactor `apply_changeset`, `preview_changeset`, and `apply_prepared_changeset` onto `_execute_changeset`.

**Result.** Preview and commit differ only in supplied execution material and transaction outcome.

## Finding C — random generated operation IDs prevented independent replay

**Risk.** A model may omit creator IDs. Re-normalizing the same proposal generated different IDs, making context/event comparison unstable and historical validation impossible.

**Repair.** Seed omitted operation IDs from proposal identity and operation position. Keep event IDs random but freeze them during preparation.

**Result.** Independent invocations derive the same normalized change-set while preserving occurrence-specific event identity.

## Finding D — a commit/sidecar crash had no authenticated success path

**Prior state.** SQLite could commit before `60-turn-receipt.json` and `run.json` were updated. Retrying commit encountered a duplicate change and required manual interpretation.

**Repair.** Detect an existing prepared `proposal_id`; verify the live cube; authenticate the preparation; compare the durable payload, receipt, and full event chain; emit a recovered v3 receipt; never apply again.

**Result.** Retry is idempotent with respect to ledger events when the durable change is exact.

## Finding E — current projection cannot authenticate an old prepared context

**Risk.** Later turns legitimately change audience/planner contexts. Either comparing against current context would falsely refuse, or trusting stored context would allow a forged sidecar with recomputed digests.

**Repair.** Add an in-memory historical snapshot at an exact changeset boundary, delete later ledger material only in the copy, rebuild all projections, verify, then replay the preparation there.

**Result.** Recovery after later head advance succeeds for an exact preparation and rejects an edited/rehashed prepared context.

## Finding F — same-run transitions were only socially serialized

**Risk.** Two local parent processes could audit the same state and interleave artifact/manifest writes.

**Repair.** Add `.run.lock`; require an owner-only regular, single-linked, non-symlink file; take a nonblocking exclusive advisory lock over complete status, accept, and commit calls.

**Result.** Cooperative contention and symlink substitution refuse before transition work.

## Finding G — committed-run audit needed durable equality

**Risk.** A sidecar could claim committed using a receipt structurally bound to a proposal while the database held a divergent same-ID change.

**Repair.** Committed run audit validates receipt v3 and compares the preparation’s canonical payload digest, change receipt, and event chain with `Cube.committed_change`.

**Result.** Sidecar completion cannot conceal a different durable change under the same proposal ID.

## Adversarial tests added

1. `ready-to-commit` contains an exact preparation and leaves the cube head unchanged.
2. A structurally valid but kernel-invalid proposal never becomes ready.
3. Commit retry recovers the exact durable change after a later turn advances the head and does not duplicate events.
4. A prepared context edited and rehashed to preserve local JSON consistency fails historical replay.
5. Same-run lock contention and lock symlink substitution fail closed.

The accepted suite grows from 175 to 180 tests.

## Manual and structural checks

- Python compile: pass.
- Full unittest discovery: pass.
- Draft 2020-12 schema metaschema validation: pass when optional `jsonschema` is available.
- Standard-library runtime/schema field parity: pass.
- TOML parse: pass.
- JSON parse: pass.
- Markdown relative-link audit: pass.
- Database verification and projection rebuild behavior: pass.
- Manifest member integrity in clean extraction: recorded in the acceptance artifact.

## Refusal behavior reviewed

The revised path refuses:

- unsafe or busy `.run.lock`;
- unexpected stage artifacts;
- proposal, packet, return, role, schema, path, or digest mismatch;
- stale direct-commit head;
- kernel-invalid operation semantics;
- duplicate or malformed prepared event IDs;
- discontinuous sequence or hash chain;
- altered event payload, timestamp, receipt, head, or contexts;
- preparation from another cube/request/proposal;
- durable same-ID change with different payload/receipt/events;
- invalid historical boundary or failed historical projection rebuild; and
- edited `NEXT.md` or manifest-derived next action.

## Residual risks

### Cross-store atomicity

SQLite and sidecar files remain separate stores. Rev0157 repairs the most important post-commit crash window but does not make the two stores transactionally atomic. A crash during `begin` can still leave a source-bound request without a complete run directory.

### Lock scope

The lock is advisory, same-host, and per-run. It does not coordinate network hosts or different run directories, and a hostile account can replace both database and sidecar. Expected-head refusal remains the cross-run concurrency boundary.

### Historical snapshot cost and scope

Recovery copies the database and rebuilds projections. This favors correctness over large-cube efficiency. Snapshots require exact changeset boundaries and are not a general historical write interface.

### Artifact confidentiality

Preparation contains event payloads and projected contexts. Run directory mode and operator handling remain important; encryption, retention, redaction, and secure deletion are external.

### Provider and semantic limits

No lock, digest, task card, preparation, verifier, or receipt proves remote model identity, hard context isolation, semantic non-leakage, truth, narrative quality, or fairness.

## Audit conclusion

The audited weak seam was real: workflow readiness and executable readiness were not identical. Rev0157 makes that distinction machine-enforced, gives the exact execution a stable custody object, and closes the common post-commit retry hazard without changing the underlying epistemic ledger model.
