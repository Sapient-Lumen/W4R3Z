# Release transparency evidence and monitor-gate boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already had three useful transparency-shaped objects:

- `release.transparency.entry`
- `log.checkpoint.receipt`
- `transparency.monitor.snapshot`

and it already had the real publication authority lane:

- `release.authority.policy`
- `release.publish.receipt`

What this doc fixes is the boundary between them.
It also now assumes that witness trust is pinned by `witness.policy` rather than inferred from inline quorum integers or receipt contents.

## Accepted boundary

DeriveBSD keeps **release publication authority** and **release transparency evidence** separate.

The authority lane is still:

- `release.authority.policy`
- `release.publish.receipt`

The transparency-evidence lane is:

- `release.transparency.entry`
- `log.checkpoint.receipt`
- `transparency.monitor.snapshot`
- `witness.policy` (trusted input to checkpoint evaluation, not publication authority)

That means:

- being logged is not the same thing as being authorized
- a witnessed checkpoint is not the same thing as being authorized
- monitor state is not the same thing as being authorized
- witness policy is not the same thing as being authorized
- `release.publish.receipt` is still the authoritative answer

## `release.transparency.entry` is publication evidence only

`spec/release.transparency.entry.schema.json` now carries:

- `authority_semantics = publication-evidence-only`
- `authority_policy_digest`
- optional `checkpoint_receipt_digest`
- the actual `transparency.proof`

The entry is allowed to say *which* release capsule was logged and under *which* release-authority policy.
It is not allowed to say that publication was approved.

## `log.checkpoint.receipt` is checkpoint evidence only

`log.checkpoint.receipt` now carries:

- `authority_semantics = checkpoint-evidence-only`
- `witness_policy_digest`
- `quorum_verdict`

That means the receipt can say:

- what the checkpoint was,
- which witnesses signed it,
- and under which pinned witness policy the quorum was evaluated.

It still cannot replace the publication decision.

## `transparency.monitor.snapshot` is monitor-state evidence only

`transparency.monitor.snapshot` now carries:

- `authority_semantics = monitor-state-evidence-only`
- `summary_status`
- `checkpoint_receipt_digest`

This lets a publish receipt summarize whether the monitor gate was clean without letting the monitor snapshot become authority by itself.

## `release.authority.policy` may require transparency, but does not outsource authority

`release.authority.policy` may require:

- a release transparency entry,
- a checkpoint receipt,
- a pinned `witness_policy_digest`,
- bundled proofs,
- and/or a clean monitor gate.

Those requirements are still publication-policy requirements.
They do not move publication authority into the log, witnesses, or monitors.

## `release.publish.receipt` is the only gate summary join point

Publish receipts should not grow ad-hoc top-level transparency fields.
Instead they carry one `transparency_verification` summary object.

That summary may now record:

- the release transparency entry digest,
- the checkpoint receipt digest,
- monitor snapshot digests,
- `witness_policy_digest`,
- checkpoint `quorum_verdict`,
- the final transparency decision (`accepted`, `rejected`, `degraded`, `not-required`),
- and monitor summary status.

This is the only place where transparency evidence becomes a publish-time allow/reject summary.

## Product-shape fit (A–D without forks)

- **A / fleet host:** transparency can be required, mirrored, and monitored without letting external services silently become authority.
- **B / workstation:** transparency remains visible and explainable; shortfalls can be shown as gate summaries rather than hidden backend behavior.
- **C / general OS:** transparency can remain optional or adapter-shaped while the authority boundary stays explicit.
- **D / appliance factory / regulatory:** witnessed checkpoints and monitor outputs can be archived for audits without making external services the production authority path.

## Why this is the right narrow decision

This does not redesign release distribution.
It simply fixes the archive boundary so five concepts stop overlapping:

- authorized
- logged
- witnessed
- witness-policy-evaluated
- monitored

That is small, tight, and worth coding later because it makes future implementation choices cheaper instead of more ambiguous.

## Related docs

- `adrs/ADR-0078-release-transparency-evidence-and-monitor-gate-boundary.md`
- `docs/257-release-capsules-and-transparency.md`
- `docs/259-transparency-monitors-and-witness-gossip.md`
- `docs/260-release-authority-policy-and-key-management.md`
- `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`
- `docs/490-witness-policy-and-roster-quorum-boundary.md`
- `docs/229-evidence-spine-overview.md`
- `spec/release.authority.policy.schema.json`
- `spec/release.transparency.entry.schema.json`
- `spec/log.checkpoint.receipt.schema.json`
- `spec/transparency.monitor.snapshot.schema.json`
- `spec/release.publish.receipt.schema.json`

Last updated: 2026-03-07r219
