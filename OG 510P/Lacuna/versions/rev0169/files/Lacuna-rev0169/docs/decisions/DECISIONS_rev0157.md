# Decisions — rev0157

## D157-1 — “Ready” requires exact kernel rehearsal

**Decision.** A run may enter `ready-to-commit` only after the exact final proposal has executed successfully through the real mutation engine and the transaction has been rolled back.

**Reason.** Sidecar validators can prove identity, topology, and declared grant shape, but they cannot prove that all operation semantics, database constraints, projection behavior, and context construction will succeed together. The term “ready” was too strong for the old boundary.

**Consequence.** Proposal acceptance may now fail with a kernel error before a readiness transition is published. This is intentional fail-closed behavior.

## D157-2 — Preview and commit share one storage path

**Decision.** Refactor ordinary apply, preview, and prepared apply onto `Cube._execute_changeset` rather than maintaining a second simulation implementation.

**Reason.** A distinct dry-run engine would eventually diverge from commit. Exactness is easier to audit when the difference is one transaction outcome: rollback versus commit.

**Consequence.** Post-state inspection must happen inside the transaction. Any comparison failure raises and rolls back the change.

## D157-3 — Freeze execution material, not just proposal intent

**Decision.** Preparation freezes the normalized change-set, generated IDs, timestamp, event IDs, event rows/hashes, receipt, after-head, and returned contexts.

**Reason.** Recomputing fresh IDs or time at commit would prove only semantic similarity. The recovery problem requires one exact durable event chain that can be recognized after a crash.

**Consequence.** Preparation artifacts contain privileged execution detail and must be protected with the run directory.

## D157-4 — Derive model-omitted operation IDs deterministically

**Decision.** Generate omitted creator IDs from a domain-separated digest of proposal identity, operation position, prefix, and field.

**Reason.** Preparation validation may happen in another invocation or a historical snapshot. Fresh random IDs would make an otherwise identical proposal unreplayable.

**Consequence.** Explicit IDs remain supported. Determinism is scoped to one proposal and does not claim global semantic identity.

## D157-5 — Keep event IDs random but freeze them

**Decision.** Generate collision-resistant event IDs during the first rehearsal and store them in the preparation rather than deriving them from proposal content.

**Reason.** Event identity is an occurrence identity. Freezing preserves exact replay while avoiding a general claim that identical content should share one event ID.

## D157-6 — Authenticate preparation by a second rollback replay

**Decision.** Construction alone is insufficient; every preparation is independently replayed and compared before use.

**Reason.** This detects bugs or tampering in envelope assembly and gives status/commit/recovery one common validation primitive.

**Consequence.** Readiness is computationally more expensive, but turns are correctness-sensitive and local SQLite replay is bounded by the proposed change.

## D157-7 — Recovery verifies; it never reapplies

**Decision.** When the prepared `proposal_id` is already durable, commit retry enters a separate recovery path.

**Reason.** Reapplication would either duplicate events or depend on duplicate-ID refusal as an accidental recovery protocol. A durable change should instead be authenticated exactly.

**Consequence.** A durable change with the same ID but different payload, receipt, or event chain is a hard refusal, not an idempotent success.

## D157-8 — Reconstruct the request-head cube for late recovery

**Decision.** Validate old prepared contexts by making an in-memory SQLite backup, truncating it at an exact changeset boundary, rebuilding projections, and replaying there.

**Reason.** Later legitimate turns change contexts. Comparing an old preparation with the current live projection would produce false mismatches; trusting stored contexts would permit forged, rehashed sidecars.

**Consequence.** Historical snapshots are audit-only and isolated. The live cube is never rewound.

## D157-9 — Receipt delivery provenance is explicit but non-authoritative

**Decision.** `lacuna.turn-receipt.v3` binds the preparation digest and carries `delivery.mode`, materialization time, and whether historical reconstruction was needed.

**Reason.** Direct and recovered sidecar receipts have different operational histories even though they bind the same durable change.

**Consequence.** Delivery metadata does not attest to model identity, provider behavior, or truth.

## D157-10 — Use a hardened cooperative same-run lock

**Decision.** Hold one nonblocking advisory lock across each complete status, accept, or commit transition; reject unsafe lock-file type, mode, symlink, or link count.

**Reason.** Rev0156 explicitly required one parent but did not enforce same-run serialization. Manifest and artifact transitions span several writes and must not interleave.

**Consequence.** The lock remains local/cooperative. Distinct runs against one cube continue to rely on expected-head refusal, and hostile-host control remains outside the threat boundary.

## D157-11 — Publish preparation before readiness, but not before a full verifier pass

**Decision.** Solo/pair final proposal acceptance prepares immediately. Full mode prepares only after the independent verifier passes.

**Reason.** A full verifier is part of the selected workflow policy. Kernel executability must not turn an unreviewed candidate into a ready artifact.

**Consequence.** A verifier refusal is still terminal for that run; correction begins a fresh run rather than overwriting rejected history.

## D157-12 — Keep database/event schemas unchanged

**Decision.** Implement preparation, run locking, and receipt recovery as API/sidecar evolution without changing database schema 8 or event schema 1.

**Reason.** Existing ledger rows already contain the information needed for exact event-chain comparison and historical reconstruction.

**Consequence.** No migration is required. The exchange schema set grows and versioned consumers must adopt run v2 and receipt v3.

## D157-13 — Preserve the gift’s scope

**Decision.** Present this revision as stronger experimental and operational custody, not as evidence that Lacuna solves retcon generation or narrative quality.

**Reason.** Gwern’s central concerns include delayed commitment, path dependence, rubber reality, and empirical comparison. Exact readiness makes those experiments more reproducible, but generation/scoring remains external.

**Consequence.** Documentation continues to separate implemented governance from proposed comparative studies.
