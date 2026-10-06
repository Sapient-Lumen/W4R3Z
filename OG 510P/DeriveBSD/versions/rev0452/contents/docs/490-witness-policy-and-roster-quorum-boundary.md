# Witness policy and roster/quorum boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already had witness-cosigned checkpoints, monitor policy, and release-authority gating.
What it lacked was one compact answer to an expensive question:

> Which witnesses actually count, under what quorum, and what happens if they are unavailable?

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD keeps **witness trust** in one explicit policy object:

- `witness.policy`

and keeps **witnessed checkpoints** as evidence:

- `log.checkpoint.receipt`

That means:

- witness ids appearing in receipts do not silently change trust,
- monitor config does not silently become the source of truth,
- witness network/community discovery tables stay useful but non-authoritative,
- and `release.publish.receipt` remains the only authoritative publication answer.

## `witness.policy` is the authoritative witness-trust object

`spec/witness.policy.schema.json` is now the place where DeriveBSD records:

- which logs the policy applies to,
- which witness ids / keys count,
- operator-diversity groups,
- quorum thresholds,
- shortfall behavior for publish and consume,
- and optional rotation overlap constraints.

This keeps witness trust portable and reviewable.
A verifier does not need to ask a live service which witness ids count for a channel; it can pin the digest of a reviewed `witness.policy` object.

## `log.checkpoint.receipt` stays evidence-only, but must bind the policy

`log.checkpoint.receipt` remains checkpoint-evidence-only.
It still records the log-signed checkpoint plus witness signatures.

What changes is the contract:

- it must carry `witness_policy_digest`
- it must carry `quorum_verdict`

That makes the receipt answer two different questions cleanly:

- **what signatures were observed?**
- **against which local witness policy were they evaluated?**

## `transparency.monitor.policy` may consume witness policy, not redefine it

`transparency.monitor.policy` can point at `witness_policy_digest` for each watched log.
That lets monitors explain which witness roster/quorum contract they are using.

But monitor policy is no longer allowed to redefine witness trust with free-floating quorum integers.
The roster/quorum contract lives in `witness.policy`.

## `release.authority.policy` may require a pinned witness policy

When a release channel requires transparency, `release.authority.policy` may require:

- `require_transparency_entry`
- `require_checkpoint_receipt`
- `witness_policy_digest`
- optional clean-monitor gating

This means witness trust is part of the reviewed publication policy rather than hidden deployment config.

## `release.publish.receipt` is still the gate summary join point

`release.publish.receipt.transparency_verification` may summarize:

- the `release.transparency.entry` digest,
- the `log.checkpoint.receipt` digest,
- monitor snapshot digests,
- `witness_policy_digest`,
- and the checkpoint `quorum_verdict`.

This is the only place where the transparency lane becomes a publish-time allow/reject summary.
Witness policy still does not replace threshold publication authority.

## Product-shape fit (A–D without forks)

- **A / fleet host:** can pin mirrored/private witness policy digests and keep shortfall behavior non-folkloric.
- **B / workstation:** can explain witness shortfalls visibly rather than failing because a backend list changed.
- **C / general-purpose OS:** can consume public witness ecosystems while preserving explicit local trust policy.
- **D / appliance factory / regulatory:** can archive policy + receipt pairs as long-lived evidence without dynamic service assumptions.

## Why this is the right narrow decision

This does not redesign transparency or monitoring.
It only fixes the missing join object so the archive stops blurring:

- witness observations,
- witness trust,
- and publication authority.

That is a small, high-leverage change because it makes future implementation choices cheaper and more explainable.

## Related docs

- `adrs/ADR-0080-witness-policy-and-roster-quorum-boundary.md`
- `docs/282-witness-cosigning-checkpoints-and-witness-networks.md`
- `docs/259-transparency-monitors-and-witness-gossip.md`
- `docs/260-release-authority-policy-and-key-management.md`
- `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md`
- `spec/witness.policy.schema.json`
- `spec/log.checkpoint.receipt.schema.json`
- `spec/transparency.monitor.policy.schema.json`
- `spec/release.authority.policy.schema.json`
- `spec/release.publish.receipt.schema.json`

Last updated: 2026-03-07r219
