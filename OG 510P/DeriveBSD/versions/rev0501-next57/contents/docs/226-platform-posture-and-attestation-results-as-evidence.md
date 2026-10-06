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
## Product-shape default

The evidence/receipt model in this doc now has an explicit A–D default in `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`:

- **A** treats measured posture as receipted evidence that can gate sensitive admissions.
- **B** keeps measured posture visible/exportable and limits default gates to sensitive operations rather than ordinary local use.
- **C** keeps measured posture optional/exportable with explicit gates where chosen.
- **D** retains measured posture for production enrollment, maintenance access, and sensitive release decisions.

That means this doc is no longer just “collect some attestation objects.” It is the evidence substrate for a product-shaped admission story.

The consuming side is now pinned more tightly too: when an authoritative action receipt records a decisive attestation outcome, it should carry the exact decision tuple (`attestation_requirement_digest`, `attestation_receipt_digest`, `attestation_admission_policy_digest`) **and** `attestation_receipt_verdict` instead of pushing the final join into hidden policy-service state. The compact action-side summary is now a fixed mirror, not a rewrite: `accepted`→`pass`, `degraded`→`degraded`, `rejected`→`fail`. Degraded admission stays requirement-shaped too: `attestation.requirement.min_verdict = degraded` is the sole portable way to allow degraded posture in v0, and there is no hidden degraded-waiver lane. Ordinary issue/delivery lanes stay fail-closed on rejected posture as well: successful secret delivery or workload identity issuance cannot quietly carry `rejected`; explicit recovery must move into breakglass instead. Breakglass does not silently reopen ordinary attestation-gated authority afterward either: later ordinary secret/identity lanes must consume a fresh `attestation.receipt` issued after that breakglass `created_at` instead of reusing pre-breakglass evidence. That post-breakglass story is causally ordered too: the pinned `attestation.receipt.created_at` must be strictly later than the relevant breakglass receipt `created_at`, and the later ordinary receipt must not predate the pinned `attestation.receipt.created_at`.

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
- `scope.kind` should be explicit; routine authoring starts at `cohort`, with `deployment` or `host` reserved for exceptional rollouts or machine-specific containment.
- `boot.variance.mode` should also be explicit; baseline authoring is `manifest-replay-first`, while `strict-pcr-only` remains an exceptional posture for tightly controlled platforms.
- `attestation.reference.exception` is now the typed escape hatch for non-baseline references: it is timeboxed, approval-shaped, and keeps deployment/host or mixed/strict-PCR posture visible in the artifact instead of only in verifier-side state. `exception.renewal_posture` makes renewal explicit, `supersedes-prior-exception` requires `exception.supersedes_reference_digest`, and the archive does not rely on verifier row ordering to discover which renewed exception displaced which earlier one.
- `attestation.receipt.reference_digest` remains the exact digest of the reviewed reference actually used; selector precedence, overlap heuristics, or latest-matching selector folklore are not allowed to replace that exact digest.
- Reference values can be cohort/fleet-scoped (role, pool, hardware class), not per-host.

For the concrete boot-manifest object and the replay ergonomics story, see:
- `docs/313-boot-manifests-and-eventlog-replay.md`
- `spec/boot.manifest.schema.json`

### 2) `attestation.receipt` (attestation results / verifier-issued)

A signed verifier statement: “I checked evidence E under reference R (+ policy P), and the verdict is V.”

`attestation.receipt` is verifier evidence, not the final authority for issuing a secret, credential, or breakglass session. Consuming action receipts should summarize accepted/rejected posture via `attestation_verification`, but they may summarize, but they may not rewrite, the exact pinned verifier verdict: decisive uses now carry `attestation_receipt_verdict` so the same receipt trail shows both the compact authority decision and the mirrored `pass` / `degraded` / `fail` outcome. Successful ordinary issue/delivery lanes stay fail-closed on rejected posture and do not hide the override inside a normal receipt.

The receipt binds:
- subject identity (host / attester key id)
- exact identity provenance when `attester_key_id` is present, via `identity_provenance.attester_provision_receipt_digest`
- evidence digests (boot attestation, optional runtime measurement digests)
- reference digest (and optional policy digest)
- verdict + reason codes
- validity window / expiry
- optional obligations (“you may release secret S”, “quarantine this host”, etc.)
- correlation ids for joining with change receipts / incident bundles

Schema: `spec/attestation.receipt.schema.json`.

This is now intentionally direct: an attestation result that names an attester key should also name the exact attester-provision digest that made that key reviewable. Support and admission tooling should not have to reconstruct identity provenance from a registrar or inventory lookup after the fact.

### 3) `attestation.requirement` (gate input)

A small plan-like object used by gates to say:
- which reference/policy applies
- how fresh the receipt must be
- minimum acceptable verdict (“pass” vs “degraded-ok”)
- whether runtime integrity evidence is required

Schema: `spec/attestation.requirement.schema.json`.

When a deployment turns attestation into an admission gate, `attestation.admission.policy` is the typed map from action to `attestation.requirement`; the final allow/deny decision still belongs in the consuming action receipt via `attestation_verification`.

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
- latest `boot_attestation_digest` (if enabled)
- latest `attestation_reference_digest` (policy scope)
- latest `attestation_receipt_digests` (if present)

official support handoff can now carry `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests` on the typed bundle contract itself, so support cases can see exactly what was measured, what reference scope judged it, and what the verifier decided without falling back to verifier dashboards, portal screenshots, or ticket prose.

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

Post-breakglass resumption now stays exact-joined and same-host bound as well: when breakglass materially matters to a later ordinary secret or workload identity decision, the consuming receipt carries `relevant_breakglass_receipt_digest` so “latest breakglass wins” does not become the hidden resolver and so a cross-host join cannot quietly become the next hidden resolver. The joined `breakglass.receipt.session.host_id` must match the pinned `attestation.receipt.subject.host_id`; the exact breakglass join must still stay on the same host. Freshness is no longer prose-only or backend-reconstructed.
Last updated: 2026-03-21r382
