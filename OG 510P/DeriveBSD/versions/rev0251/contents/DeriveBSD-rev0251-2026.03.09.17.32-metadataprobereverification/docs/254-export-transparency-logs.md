# Export transparency logs (prove what left the system)

DeriveBSD treats **sharing** as a first-class act (`export.receipt`), but receipts alone are *local evidence*:
an attacker with host access could delete or rewrite local receipts after the fact.

A **transparency log** provides *append-only, publicly/auditably consistent* history: you can prove an export
was recorded at (or before) a given time, and monitors can detect suspicious activity.

This doc adds an **optional** lane:
- `export.transparency.entry`: a minimal record of an export, suitable for append-only logging
- an `export.policy.transparency` section: whether logging is required and how much metadata is permissible

This is intentionally separate from *artifact signing transparency* (e.g. Sigsum/Rekor for build/sign events):
here we log **export events**, not build events.

## Goals

- Make “what was shared” tamper-evident over time, even if the host is compromised later.
- Allow **minimal metadata** logging (e.g. log hashes, not ticket ids) for sensitive environments.
- Make logging **policy-bound**: the export policy decides whether logging is required and what is logged.
- Produce verifiable proofs (inclusion proof / checkpoint) to attach to incident bundles.

## Non-goals

- This is not a single mandated log implementation.
- This does not require a public log; an organization can run an internal transparency log.
- This is not a “full data escrow” of exported bytes. Only **metadata** should be logged.

## Prior art to steal

- Sigstore Rekor (signature transparency log): https://docs.sigstore.dev/logging/overview/
- Rekor repo (APIs, inclusion proof tooling): https://github.com/sigstore/rekor
- Trillian transparent logging guide (general-purpose append-only logs): https://google.github.io/trillian/docs/TransparentLogging.html
- transparency.dev “verifiable transport layer” framing: https://transparency.dev/articles/logs-a-verifiable-transport-layer/

## New artifact: `export.transparency.entry`

A transparency entry binds (at minimum):
- exported artifact digest
- `export.receipt` digest
- export policy digest
- optional bundle plan digest
- log metadata (log uri, log index/uuid, inclusion proof/checkpoint)

See: `spec/export.transparency.entry.schema.json`.

Log proof shape (shared): `spec/transparency.proof.schema.json`.
This allows optional witness cosignatures over checkpoints (see `docs/187-witnessed-transparency-checkpoints.md`).

### Metadata profiles

Export policies may choose a `metadata_profile`:
- `minimal`: log only digests (artifact, receipt, policy, plan). Ticket ids and recipients are hashed or omitted.
- `standard`: permit logging a ticket id hash + recipient class (still avoid raw URIs/secrets).

The important design constraint: **a verifier should be able to verify log inclusion without learning more than policy permits**.

## Workflow sketch

1) Build bundle (optional): `bundle.plan` → bundle payload digest
2) Export: `export.receipt` emitted (local evidence)
3) Transparency log: commit `export.transparency.entry` (append-only)
4) Export completes only when policy says it completes:
   - if `export.policy.transparency.required = true`, the export is “done” only with inclusion proof/checkpoint

In incident handling, you attach:
- `export.receipt` (what we claim we exported)
- `export.transparency.entry` (proof it was logged)

## Open questions (intentionally left for RFC)

- What should be the “default” internal log primitive (Rekor-like, SCITT receipts, or an org-specific log)?
- Do we require periodic checkpoints to be pinned into the Derive store for offline verification?
- How do we handle log availability outages when policy requires logging?

See: `rfcs/RFC-0186-export-transparency-logs.md`.
