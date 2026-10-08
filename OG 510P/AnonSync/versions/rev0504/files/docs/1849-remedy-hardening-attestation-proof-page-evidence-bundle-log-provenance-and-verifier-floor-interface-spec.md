# Remedy-hardening-attestation proof page — evidence bundle, log provenance, and verifier floor

## Purpose

This page is the proof bundle behind the claim that a case which already achieved a bootstrap-reproducible hardened baseline may let a later verifier or successor confirm the same safety sentence independently.
It exists so later readers can inspect evidence freshness, provenance, coverage, and exported scars directly rather than inferring them from operational traces.

## Proof bundle

The proof page must preserve evidence for:

- source remedy-hardening-bootstrap result
- triggering cause family
- current hardening class
- named attestation audience
- required verifier cohort
- attestation bundle identifier
- bundle generation time
- evidence freshness horizon
- evidence expiry horizon
- history-horizon sufficiency evidence
- log provenance evidence
- log capture-mode evidence
- storage snapshot evidence
- startup-config snapshot evidence
- rebuild-proof evidence
- folder-type coverage evidence
- platform and version-lane coverage evidence
- successor-handoff evidence
- operator-memory dependence evidence
- exported scars evidence
- exported blocked-stronger-sentence evidence
- highest honest current verifier-ready sentence
- strongest blocked stronger verifier-ready sentence

## Proof sentence families

The page must support concise summaries such as:

- `the case is safe and bootstrap-reproducible, but not yet verifier-ready`
- `attestation is honest only for named lanes or named freshness windows`
- `the bundle is successor-safe, but not yet independent-third-party-safe`
- `logs exist, but provenance remains too operator-controlled for the stronger sentence`
- `the hardened baseline is now independently verifier-ready for the required cohort, with scars and expiry preserved`

## Stronger-sentence blockers

The page must explicitly name blockers such as:

- evidence horizon too short
- history horizon too narrow
- log capture started too late
- log rotation or replacement risk too high
- storage or config snapshot incomplete
- rebuild proof missing
- folder-type or lane coverage incomplete
- successor handoff not portable enough
- operator-memory dependence still material
- exported bundle omits scars or blocked stronger sentences
- evidence basis too weak

## Evidence handling rules

The proof page must never let these substitute for stronger proof:

- one calm current UI surface without bundle export
- one storage-folder copy without provenance and freshness summary
- one set of support logs without attestation scope and blocker summary
- one rebuild result without exported scars and blocked stronger sentences
- one successor briefing without durable verifier bundle
