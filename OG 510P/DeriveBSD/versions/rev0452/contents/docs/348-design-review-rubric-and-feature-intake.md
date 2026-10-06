# Design review rubric: how we add features without creating an unkillable monster

DeriveBSD is a greenfield OS ecosystem. That’s a superpower and a trap.

This rubric is a *meta-engineering* tool: it forces new features to land as **small, typed, reviewable surfaces**
and prevents “ambient authority creep” and “unexplained mutable state” from becoming the default.

Use this for:
- RFCs
- major doc additions
- new schemas / new capability types
- new brokers / privileged services

## Intake template (copy into RFCs)

### 0) One-sentence pitch

What is the feature? What pain does it remove?

### 1) Scope and non-goals

- In scope:
- Explicitly not in scope:

### 1.4) Invariant impact (constitution check)

- Which **invariant(s)** from `invariant.registry` does this proposal rely on or modify?
- Does it weaken any invariant? If so, why is the entropy cost worth it?

See: `docs/422-invariant-registry-and-design-invariants.md`.

### 1.5) Pattern fit (meta-engineering)

- Which **pattern(s)** from the pattern catalog does this feature instantiate?
- If it does *not* fit existing patterns, what is the smallest new pattern we can add (and why is it worth the entropy)?

See: `docs/397-pattern-catalog.md`.

### 1.6) Tier and profile applicability (no forks)

- Which **tier** is this feature? (A/B/C/D/E; see `docs/401-v0-cutline-and-feature-tiers.md`)
- Which product profile(s) is it intended for by default? (A/B/C/D; see `docs/411-product-profiles-as-compilation-target.md`)
- If not universal: how is it expressed as a **profile default** or **optional lane**, and how is it policy-gated?

### 2) The contract surface

- What are the **typed objects** involved (schemas/IDL)?
- What are the **stable identifiers**?
- What is digest-bound (bytes/contract/channel)?
- Does this introduce a **new parser surface** (untrusted bytes → structured objects)? If so, where is it registered in `parser.registry` and what is the fuzz/conformance plan?
- Does this introduce or change a **crypto surface** (protocol/suite/library/key policy)? If so, where is it registered in `crypto.registry`, and what shows up in `crypto.diff`? See: `docs/391-crypto-surface-registry-and-agility-gates.md`.
- Does this introduce an **in-kernel programmable runtime or JITed rule engine** (e.g., a BPF-like lane)? If so, what is the default-off stance, and how is it brokered/lease-gated and represented in UAPI/parser/authority/boundary diffs? See: `docs/384-kernel-extensibility-bpf-and-jit-risk.md`.
- If this introduces a new **surface class** (API, UAPI, parser, authority-bearing handle kind): does it fit an existing registry/diff gate, or is a new registry needed? See: `docs/379-surface-registry-pattern.md`.
- If this feature makes **admission depend on remote attestation** (identity issuance, secrets unseal, fleet join, remote assist):
  - where is the gating declared in `attestation.admission.policy`, and which `attestation.requirement` does it reference?
  - See: `docs/388-remote-attestation-admission-and-enrollment.md`, `spec/attestation.admission.policy.schema.json`.
- If this feature enables **fault injection / chaos** in production:
  - is the capability lease-gated, and does it use `chaos.experiment.plan`/`chaos.experiment.receipt`?
  - Where does the new authority appear in `authority.diff`?
  - See: `docs/389-chaos-experiments-and-fault-injection-as-leases.md`.

### 3) Authority changes

- What new authority can be granted?
- Which **attenuation pattern** is used? (facet / proxy attenuator / membrane / lease)
- Which **revocation pattern** is used? (indirection / lease expiry / policy revocation event)
- If returned values can carry authority: what is the **deep attenuation** story? (membrane)

**Required review surfaces:**
- Where does it show up in blast-radius diffs?
- Where does it show up in `authority.graph` / `authority.diff`?
- Where does it show up in the `drift.bundle` summary (the default review attachment)? See: `docs/395-drift-bundles-and-review-summaries.md`, `spec/drift.bundle.schema.json`.
- If it introduces or changes crypto surfaces: where does it show up in `crypto.diff` and does blast-radius include a `crypto` section?
- If it introduces new non-exportable keys: where is the `crypto.key.policy` object and who can request operations? See: `spec/crypto.key.policy.schema.json`.
- If it adds/broadens parsers: where does it show up in `parser.diff`?
- If it adds or widens trust boundaries: where does it show up in `trust.boundary.diff` and what mitigations (policy/receipts/fuzz) constrain it?

See:
- authority engineering patterns: `docs/357-capability-attenuation-revocation-and-membranes.md`
- authority graph substrate: `docs/366-capability-graphs-and-authority-diff-surfaces.md`

### 4) Evidence spine integration

- What receipts/events are produced?
- What does “explain” look like for this feature?
- What is the retention policy / budget?

### 5) Failure modes and rollback

List failures in three buckets:
- **safe fail** (feature unavailable, system stays correct)
- **degraded** (reduced capability, recoverable)
- **unsafe** (data loss / integrity risk / privilege expansion)

For each:
- detection signal
- automatic response
- operator workflow
- rollback story

### 6) Operational ergonomics

- How does an operator *use* it?
- How do they *debug* it without mutating the base?
- What’s the “breakglass” story?

### 7) Interop and escape hatches

- What legacy workflow does this replace?
- What interop hooks are required?
- If this introduces an **adapter lane** (interop bridge): what is the Adapter → Shadow → Replace plan, and what is the bounded deprecation/removal story?
  See: `docs/402-adapter-lanes-and-strangler-discipline.md`, `docs/385-deprecation-policies-and-removal-receipts.md`.
- What escape hatch exists, and what evidence does it generate?

### 8) Performance and resource budgeting

- CPU/memory/IO/network budgets
- backpressure behavior
- worst-case amplification risks

### 9) Security model

- threat model deltas
- trust boundaries (include a `trust.boundary.diff` if new crossings appear)
- dependencies introduced

### 10) Migration plan

- upgrade path
- data migration plans/receipts
- downgrade story (if any)
- if compatibility breaks are introduced: include a `deprecation.notice` with a bounded EOL window and a migration strategy (dual-run/shim/rewrite). See: `docs/385-deprecation-policies-and-removal-receipts.md`, `spec/deprecation.notice.schema.json`.

### 11) Test plan

- correctness tests
- scenario/integration tests: if the change touches boot/network/activation/update paths, add (or update) a `test.scenario.manifest` gate and ensure the run is reproducible and debuggable (interactive driver + artifact capture). See: `docs/188-scenario-tests-multimachine.md`, `docs/405-interactive-vm-tests-and-artifact-capture.md`.
- policy regression vectors: does this introduce or change a policy surface? If so, where is the `policy.test.suite`, and what `policy.test.report` gate will prevent silent authority expansion? See: `docs/393-policy-tests-suites-and-mutation.md`.
- mutation/analysis (optional high-assurance lanes): if the surface is high-blast-radius (admission, secrets, remote assist), do we require mutation testing or automated policy analysis? See: `docs/394-policy-analysis-and-automated-reasoning.md`.
- chaos / fault injection
- reproducibility tests (if build lane)

## Acceptance checklist (reviewer view)

A feature is ready to land when:

- [ ] The smallest viable contract surface is identified and typed.
- [ ] Authority changes are explicit, diffable, and revocable.
- [ ] Authority deltas show up in blast-radius diffs and `authority.diff`.
- [ ] A `drift.bundle` is produced for the change and includes the relevant diffs/evidence (review starts from one object, not 12).
- [ ] New or broadened parsers are registered (`parser.registry`) and have a fuzz/conformance (or proof) story.
- [ ] New or changed crypto surfaces are registered (`crypto.registry`) and reviewable via `crypto.diff` (no silent algorithm drift).
- [ ] Policy surfaces ship with regression suites (`policy.test.suite`) and CI evidence (`policy.test.report`) for reviewable, repeatable drift control.
- [ ] High-blast-radius changes have an explicit integration scenario gate (`test.scenario.manifest`) with receipted runs and captured evidence (serial logs/screenshots) for debugging. See: `docs/405-interactive-vm-tests-and-artifact-capture.md`.
- [ ] Compatibility breaks include a `deprecation.notice` (bounded EOL + migration path) and removal is auditable via receipts.
- [ ] New or widened trust boundaries are captured as a `trust.boundary.diff` and linked to mitigations (policy ids, receipts, fuzz harnesses).
- [ ] If a new surface class is introduced, it follows the surface registry pattern (registry + diff + gate + receipt), or the design explains why not.
- [ ] Failure modes and rollback are written down, not implied.
- [ ] Evidence outputs exist and are queryable.
- [ ] Operational workflows are possible without “SSH and poke.”
- [ ] The design keeps the Derive core small (complexity lives at the edges).

## Where this plugs in

- Archive hygiene rule: every new subsystem must specify threat model impact, boundaries, and rollback.
  This rubric is the concrete mechanism.

See: `docs/98-archive-hygiene.md`, `docs/95-explainability-contract.md`, `docs/66-diff-and-review-workflows.md`.

Last updated: 2026-02-27r118