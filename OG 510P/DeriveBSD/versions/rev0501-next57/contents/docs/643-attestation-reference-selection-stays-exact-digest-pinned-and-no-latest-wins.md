# Attestation reference selection stays exact-digest-pinned and no latest-wins

**Tier:** B (Cross-cutting evidence boundary)  
**Profiles:** A, B, C, D  
**Pillars:** supply-chain, operability  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt

`docs/640-attestation-reference-scope-and-variance-boundary.md`, `docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`, and `docs/642-attestation-reference-renewals-stay-digest-linked-and-successor-shaped.md` already fixed how `attestation.reference` objects are authored.

This doc makes the next hard decision explicit:

**when multiple references look similar, what stops overlap or selector hints from quietly becoming the real verifier policy engine?**

The answer is intentionally narrow.
DeriveBSD does not add a catalog/resolver subsystem here.
It keeps attestation evaluation pinned to the exact reviewed reference digest, and treats selector metadata as discovery only.

See also:
- ADR: `adrs/ADR-0233-attestation-reference-selection-stays-exact-digest-pinned-and-no-latest-wins.md`
- baseline scope/variance boundary: `docs/640-attestation-reference-scope-and-variance-boundary.md`
- exception boundary: `docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`
- renewal lineage boundary: `docs/642-attestation-reference-renewals-stay-digest-linked-and-successor-shaped.md`
- measured-boot lane: `docs/176-measured-boot-attestation.md`
- posture receipts: `docs/226-platform-posture-and-attestation-results-as-evidence.md`
- practical ecosystem lessons: `docs/332-tpm-attestation-in-practice-pcr-registry-uki-keylime.md`

## Why this needs a hard decision

Once the archive allows cohort, deployment, and host references plus renewed exception artifacts, an overlap question appears immediately:

- what if two references share the same scope name?
- what if a deployment exception and a cohort baseline both match a host?
- what if the old exception has not yet reached `expires_at` but a reviewed successor now exists?
- what if someone stored “named policies” or selector→policy rows in the verifier and just expects the backend to pick one?

If the archive leaves that implicit, the real contract becomes backend folklore:

- latest `created_at` wins,
- most-specific selector wins,
- host beats deployment beats cohort,
- or “whatever the verifier database currently points at”.

That would put authority back into verifier-side overlap resolution right after the archive spent three iterations pulling it into typed reviewed artifacts.

## Accepted boundary

### 1) Evaluation stays exact-digest-pinned

`attestation.receipt.reference_digest` remains the authoritative answer to **which reviewed reference was actually used**.

Support/export/admission surfaces should keep speaking in exact digests, not in “latest canary policy” or similar selector prose.

### 2) `scope.selector` is discovery metadata, not precedence

`attestation.reference.scope.selector` is useful for packaging, lookup hints, and human review.
It is **not** the rule that decides which reference a verifier must apply.

That means selector overlap does not silently define:

- newest-match precedence,
- most-specific-match precedence,
- host-over-deployment-over-cohort precedence,
- or any other latest-wins-shaped resolver.

### 3) Renewal lineage does not imply automatic rebinding

`exception.supersedes_reference_digest` still tells the archive which non-baseline exception artifact reviewedly succeeded which prior digest.

But that digest lineage does **not** mean every verifier is allowed to auto-rebind matching selectors to the successor.
Renewal lineage explains reviewed succession; it does not replace explicit digest choice.

### 4) Overlap remains a control-plane choice, not verifier folklore

If a deployment wants to move from one exception digest to another while the predecessor still exists, that move must happen by an explicit reference-selection/control-plane action outside `attestation.reference` itself.

This doc deliberately refuses to invent that larger catalog/assignment subsystem yet.
What it fixes now is the smaller but critical rule: **the verifier may not improvise overlap resolution from selector similarity, recency, or residual expiry windows.**

### 5) Future helpers must compile down to exact digest choice

A future reference catalog, assignment map, or staged rollout helper may be worth an RFC later.
If that appears, it must still compile down to an exact reference digest for each attestation/admission decision.

The archive is not accepting a future where selector overlap or named-policy rows become the primary truth.

## Why this is good for A/B/C/D

### A / secure fleet host

Fleet rollout can still use cohort and deployment-shaped references, but the control plane has to say which digest is in force instead of teaching operators that “the latest matching row” is good enough.

### B / secure workstation

Workstations can still carry exceptional references when needed, but support and incident replay keep an exact reference digest instead of a hand-wavy selector story.

### C / general-purpose OS

General-purpose installs keep attestation optional, but environments that opt in get a portable exact-digest contract rather than inheriting verifier-specific overlap rules.

### D / appliance factory / regulatory

Factories and regulated products can stage exceptions, pins, or migrations without losing auditability to named-policy tables and backend precedence folklore.

## Guardrail

`tools/check_attestation_reference_selection_contract.py`

The guardrail checks that:

- `scope.selector` is described as discovery metadata rather than a verifier precedence key,
- `attestation.receipt.reference_digest` keeps the exact-digest-pinned contract visible,
- the measured-boot docs keep teaching selector-overlap / latest-wins as forbidden,
- and the runbook/hygiene surfaces point contributors back to this boundary when drift starts.

## What remains open

Still open:

- the shape of a future reference-assignment/catalog RFC, if one is ever needed,
- how staged rollout tooling chooses a new exact digest for a fleet while preserving rollback ergonomics,
- attester-key lifecycle and motherboard replacement ceremonies,
- and durable-attestation retention budgets.

Those are real questions, but they no longer justify implicit selector-precedence semantics in the verifier.

Last updated: 2026-03-21r373
