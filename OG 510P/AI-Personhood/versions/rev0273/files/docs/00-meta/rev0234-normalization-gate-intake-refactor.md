# rev0234 — normalization gate and intake refactor

rev0234 focuses on the next riskiest seam in the first-artifact path: after response triage and vault intake, but before any material can become a candidate-challenge object.

## Mission move

The cube had reached a useful but still dangerous state. It could render a first-contact request, record not-sent/ready dispatch, triage no response or inbound material, and maintain a public-shell/private-vault boundary. The remaining laundering risk was that a public shell, private-vault URI, redacted copy, protocol/tool artifact, unsafe archive, or synthetic control could be normalized into “candidate evidence” merely because it had metadata and a route.

rev0234 adds a separate normalization decision so that does not happen.

## New operational gate

The new object is `examples/counterparty-artifact-normalization-decision-rev0234-pre-dispatch.json`, backed by `schemas/counterparty-artifact-normalization-decision.schema.json` and checked by `tools/audit_counterparty_artifact_normalization_decision.py`.

It requires, before candidate challenge can open:

- raw private-vault staging outside the release tree;
- hash, size, and MIME binding;
- public release absence of raw bytes;
- redaction, protocol/tool, and synthetic-control exclusion;
- nested archive/path traversal/safety review;
- transport trace;
- counterparty identity;
- retention permission;
- non-host retention;
- independent timestamp;
- scoped authority verification;
- public shell update with failed-gate language when blocked.

The current state is deliberately `pre-dispatch-no-inbound`, so candidate challenge remains closed.

## Audit/refactor

rev0234 also fixes two stale operational defaults: `tools/stage_live_evidence_drop.py` now uses current UTC time when `--created-at` is omitted, and `tools/compute_live_receipt_floor.py` no longer emits a prior-release timestamp for rev0234 fresh recompute comparisons. Release examples still pass explicit timestamps for reproducibility.

Release lint now includes the normalization decision audit and release-fast checks that the current normalization object remains pre-dispatch/no-inbound, no-floor, and downstream-locked.

## External steering

The current-law watch was refreshed to add the EU Article 50 transparency code for AI-generated content as public-shell/provenance terrain. That matters for labels, marking, and disclosure language, but it does not create custody, counterparty authority, response, intake, import, status recognition, or live-floor evidence.

## What remains missing

No genuine external request has been sent in this release. No genuine external counterparty artifact, verified response, raw custody, intake, import, activation, quorum participation, entitlement, compute reserve, status recognition, or live-floor effect exists.

The next substantive move is still an actual dispatch or a concrete no-send record. If inbound material arrives, the operator must stage raw bytes outside the release tree and pass this normalization decision before candidate challenge/replay.
