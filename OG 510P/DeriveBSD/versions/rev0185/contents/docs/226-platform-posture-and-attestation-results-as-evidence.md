# Platform posture + attestation results as evidence

Measured boot evidence (`boot.attestation`) is already an optional lane in DeriveBSD.
The missing piece most OS stacks bolt on late is: **typed attestation results** that can
be *reused* by update gates, secret release, admission control, and incident response.

Bake this in early as: **evidence → reference values → verifier receipts**.

This doc extends:
- `docs/176-measured-boot-attestation.md` (evidence production)
- `docs/223-secrets-and-key-management-as-evidence.md` (secret release gates)
- `docs/219-change-sets-and-apply-engine.md` (gates as steps)
- `docs/216-incident-snapshots-and-support-bundles.md` (posture snapshots)

## Goals

- Define a minimum set of **RATS-shaped** objects for platform posture:
  - Evidence: `boot.attestation` (+ optional runtime measurement evidence)
  - Reference values: `attestation.reference`
  - Attestation results: `attestation.receipt`
- Make posture checks *composable*:
  - a change-set can require an attestation receipt
  - a secret grant can require a receipt under a specific policy
  - incident bundles can include posture evidence digests safely
- Keep everything **policy-gated** and optional (no mandatory TPM).

### Confidential microVM attestations (TEE lane)

The same "reference → evidence → receipt" pattern applies to confidential microVMs that present TEE evidence (SEV-SNP/TDX/CCA).
DeriveBSD keeps this as a separate optional lane today (TEE adapters, verifier services), but the *operational* contract is identical: a relying party consumes a **signed receipt** rather than raw vendor blobs.

See: `docs/330-confidential-microvms-and-tee-attestation-as-evidence.md` and `spec/tee.attestation.reference.schema.json`, `spec/tee.attestation.evidence.schema.json`, `spec/tee.attestation.receipt.schema.json`.

## Why this matters (greenfield advantage)

Without first-class receipts, platforms end up with:
- “attestation happened somewhere” but nothing reusable or auditable
- per-team formats for “passed” vs “failed”
- secret release logic coupled to a specific attestation vendor
- incident bundles that miss the one artifact you needed: *what did the verifier think?*

So: standardize the receipt shape and correlation now.

## Evidence objects

### 1) `attestation.reference` (reference values / expected state)

A content-addressed object describing what “good” looks like *for a policy scope*:
- boot manifest digest(s) / deployment ref(s) that are acceptable
- PCR selection to quote (banks + indices)
- optional firmware inventory expectations
- optional runtime policy references (IMA/measurement allowlists)
- verifier hints (what to treat as variance, what is strict)

Schema: `spec/attestation.reference.schema.json`.

Notes:
- Prefer policies that **replay event logs** and compare to boot manifests, not brittle “golden PCRs”.
- Reference values can be fleet-scoped (role, pool, hardware class), not per-host.

For the concrete boot-manifest object and the replay ergonomics story, see:
- `docs/313-boot-manifests-and-eventlog-replay.md`
- `spec/boot.manifest.schema.json`

### 2) `attestation.receipt` (attestation results / verifier-issued)

A signed verifier statement: “I checked evidence E under reference R (+ policy P), and the verdict is V.”

The receipt binds:
- subject identity (host / attester key id)
- evidence digests (boot attestation, optional runtime measurement digests)
- reference digest (and optional policy digest)
- verdict + reason codes
- validity window / expiry
- optional obligations (“you may release secret S”, “quarantine this host”, etc.)
- correlation ids for joining with change receipts / incident bundles

Schema: `spec/attestation.receipt.schema.json`.

### 3) `attestation.requirement` (gate input)

A small plan-like object used by gates to say:
- which reference/policy applies
- how fresh the receipt must be
- minimum acceptable verdict (“pass” vs “degraded-ok”)
- whether runtime integrity evidence is required

Schema: `spec/attestation.requirement.schema.json`.

## Runtime integrity (optional extension)

Measured boot answers “what did you boot?”
Some deployments also need “what is still running / has changed?”

DeriveBSD should not hard-depend on a Linux-specific mechanism, but we should:
- reserve evidence slots for **runtime measurement logs** (IMA-shaped)
- allow a verifier to treat runtime evidence as optional or required by policy

Suggested pattern:
- runtime measurement evidence is a digest-referenced blob/object
- the verifier evaluates it and writes the result into `attestation.receipt.reasons`

This keeps the OS surface stable while allowing multiple collectors/agents.

## Integration points

### Secrets
Secret grants already support a `require_attestation` constraint.
Prefer upgrading the constraint to reference a requirement/receipt:
- `constraints.attestation_requirement_digest` (preferred)
- `constraints.attestation_receipt_digest` (pin to a specific receipt)
- keep `boot_attestation_digest` for “bring your own verifier” transitions

See: `docs/223-secrets-and-key-management-as-evidence.md`.

### Change sets / apply engine
Add a `require-attestation` step so posture gates are explicit in multi-step transitions.
The step references an `attestation.requirement` object.

This keeps “don’t apply this change on untrusted posture” as a durable artifact, not orchestration folklore.

### Incident bundles
Incident bundles should include:
- latest boot attestation digest (if enabled)
- latest attestation receipt digests (if present)
- reference digest (policy scope)

This makes support cases reproducible: you can see exactly what the verifier saw/decided.

### Structured event journal
Emit `attestation-event` records:
- receipt issued / expired
- verification failures (with coarse reason codes)
- “posture degraded” transitions
- “receipt used to unlock secret” transitions (without secret bytes)

Optional: treat posture as a time series (“durable attestation”) by chaining receipts and budgeting retention.
See: `docs/315-durable-attestation-and-posture-timelines.md`.

## Non-goals (v1)

- mandatory remote attestation for all hosts
- a single required runtime integrity mechanism
- embedding an attestation vendor into core (adapters live outside)

Last updated: 2026-02-26r91
