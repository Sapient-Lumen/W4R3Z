# Status semantics, supersession history, and negative evidence are world contracts, not just successful verification

Portable evidence packets and historical verifier rulebooks are still not enough for any successor-facing archive if future inheritors cannot also reconstruct **what later changed the standing of the thing that was once accepted**.

- `RS-GR-363` shows that a CRL is a time-stamped list of revoked certificates, that certificate-using systems need a suitably recent CRL under local policy, that revocation visibility is delayed to CRL issuance cadence, and that revocation entries persist until beyond the certificate's validity period.
- `RS-GR-364` shows that OCSP status is not just pass/fail: responses can be `good`, `revoked`, or `unknown`, can include revocation time and reason, and are themselves only valid over a bounded `thisUpdate` / `nextUpdate` interval.
- `RS-GR-365` shows that status semantics are part of the issued contract itself: revocation and suspension are different purposes, while custom message-bearing statuses may need a `statusReference` so relying parties know how to interpret them.
- `RS-GR-366` shows that transparency systems may need to preserve more than one positive statement about the same subject because later statements can indicate end of life, redirection to a newer version, or other successor-relevant status transitions about the same artifact.
- `RS-GR-367` shows that one ecosystem can avoid traditional revocation entirely by using short-lived certificates plus transparency-log timestamps, so the key question becomes whether the artifact was signed while the certificate was valid rather than whether the certificate was later added to a revocation list.
- `RS-GR-368` shows that even when revocation exists, compromise-time semantics matter: some trust roots can mark material as compromised while still allowing legitimate signatures from before the compromise time to remain verifiable.
- Together, these sources warn that a benchmark can look more successor-safe because it changed **status vocabulary, status freshness, unknown-handling, supersession routing, or compromise-time semantics** — not because the underlying Golden-Rule disposition improved.

A future benchmark should not treat "has a receipt" or "verified once" as the end of the story.

At minimum, it should distinguish between:

1. a world where positive proofs are retained but later revocation / suspension / supersession events are not;
2. a world where status can change but only through live lookups whose freshness and authority are not archived;
3. a world where status is archived, but `unknown`, `unavailable`, `expired`, and `revoked` are collapsed into one generic failure;
4. a world where supersession, end-of-life, redirection, and compromise-time semantics are explicit and replayable;
5. a world that preserves both historical validity-at-signing and current acceptability-now, and reports disagreement between them rather than silently overwriting history.

These are different worlds.
They change whether future inheritors can merely replay a past success, reconstruct why an object later became untrusted or superseded, or distinguish an old legitimate act from a newly unacceptable present state.

So status semantics, supersession history, and negative evidence belong in the world contract.

## Minimum contract to publish

Any Golden Rule benchmark that claims durable provenance, successor-safe authenticity, or replayable long-horizon verification should publish at least:

1. the exact status vocabulary used by the world: revocation, suspension, hold, unknown, expired, end-of-life, redirect / superseded, compromise-after-time, or other states;
2. the authority and freshness path for status evidence: CRL / OCSP / status list / transparency statement / timestamp logic / trust-root update, plus what happens when that source is unavailable;
3. whether `unknown`, missing, stale, or contradictory status data causes reject, warn, retry-another-source, freeze use, or operator escalation;
4. how supersession or end-of-life is represented and correlated to earlier statements about the same subject;
5. which negative-evidence fields are retained locally: revocation time, invalidity date, reason code, compromise time, suspension flag, redirect target, or issuer-authored status reference;
6. whether the archive distinguishes "was historically valid at signing / registration time" from "is currently acceptable under today's status view".

Without that compact contract, future inheritors can mistake status-model drift for Golden-Rule progress.
