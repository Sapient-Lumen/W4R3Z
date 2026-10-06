# Adapter lanes + strangler discipline (interop without becoming forever-legacy)

**Tier:** A (Core meta-doc)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, supply-chain, operability
**Patterns:** Adapter→Shadow→Replace  

A greenfield OS still has to interoperate with the world:

- ports/pkg ecosystems
- OCI registries
- full TUF metadata
- pkgbase-style “base as packages”
- foreign binary compatibility views

The failure mode is **forever adapters**:
interop layers that quietly become the real system, are impossible to delete, and accumulate ambient authority.

This doc defines an **adapter lane discipline** so DeriveBSD can use existing ecosystems without being owned by them.


## 1) What an adapter lane is

An **adapter lane** is a bounded subsystem that:

- imports an external format or workflow
- normalizes it into DeriveBSD objects
- emits explicit evidence about what it did

Adapters are not “just helpers.” They are **trust boundaries** and must be treated as such.

Examples already in the archive:
- in-toto/SLSA attestation export adapter (killable ecosystem interop for provenance tooling) (`docs/454-intoto-slsa-adapter-lane.md`)
- ports/pkg adapter lane (`docs/108-ports-pkg-adapter-lane.md`)
- full TUF metadata adapter (`docs/203-full-tuf-metadata-adapter.md`)
- OCI as an optional transport (`adrs/ADR-0021-oci-as-optional-transport.md`, `docs/133-bootable-oci-host-images-bootc-lessons.md`)
- compat views for foreign binaries (`docs/105-compat-view-foreign-binaries.md`)


## 2) Adapter invariants (non-negotiables)

### 2.1) Adapters must be *explicit* in the pipeline
No silent “auto-detected” adapter behavior.

- Specs must name the adapter
- Plans must include the adapter’s actions
- Receipts must record the adapter’s results

If the system can’t say “this was produced via the XYZ adapter,” it is not reviewable.


### 2.2) Adapters live behind Quarantine → Promote
External bytes and metadata are untrusted by default.

- imports land in quarantine
- origin labels are attached
- promotion is policy-driven

See: `docs/280-origin-labels-and-quarantine-attributes.md`, `docs/61-channel-metadata-tuf-inspired.md`.


### 2.3) Adapters must have drift surfaces
Adapters change the system by importing *someone else’s* churn.
That churn must show up in review:

- **closure diffs** (new code ingestion)
- **parser diffs** (new/broadened decode surfaces)
- **authority diffs** (new authority-bearing handles)
- **trust boundary diffs** (new crossings)

See: `docs/395-drift-bundles-and-review-summaries.md`, `docs/396-closure-diffs-and-new-code-surfaces.md`.


### 2.4) Adapters must have a “strangler” plan
The goal is never “adapter forever.”

Use the strangler discipline:

1) **Adapter**: import external ecosystem outputs into DeriveBSD objects.
2) **Shadow**: run native and adapter paths side-by-side when possible and compare results.
3) **Replace**: promote the native path and deprecate the adapter.

This prevents the common trap: “we’ll clean it up later” becomes “it’s now mission critical.”


### 2.5) Adapters must be killable by policy

Interop is only acceptable if operators can *turn it off* without a fork.

- Adapter posture must be an explicit, versioned policy object: `adapter.kill.policy`
- Adapter posture drift must be reviewable: `adapter.kill.policy.diff` (Registry→Diff→Gate)
- Emergency disables use breakglass, but still emit receipts and include the diff in the next drift bundle

See: `docs/444-adapter-kill-policy-diff-as-review-surface.md`, `docs/395-drift-bundles-and-review-summaries.md`.


## 3) The Adapter → Shadow → Replace pattern

### Phase A: Adapter
Minimum requirements:

- stable typed inputs/outputs
- a receipt that includes:
  - source identity (origin labels)
  - translation options / policy knobs
  - output digests
  - warnings about lossy transforms


### Phase B: Shadow
Shadow mode is a greenfield superpower.
If you can afford to compute both, you can treat disagreements as a first-class signal:

- generate outputs via adapter and native implementations
- compute a diff object
- gate promotion on “acceptable divergence”

This is how you avoid “migration week” disasters.


### Phase C: Replace
Replacement is only credible if:

- a deprecation notice exists (bounded EOL)
- removal is receipted
- operators have an escape hatch (limited-time compat mode) with evidence

See: `docs/385-deprecation-policies-and-removal-receipts.md`.


## 4) How to keep adapters from expanding authority

Adapters are often where ambient authority leaks in:

- “the adapter needs network access”
- “the adapter needs to invoke arbitrary tools”
- “the adapter needs to write outside the store”

DeriveBSD’s stance:

- adapters run in sandboxed, least-authority compartments
- network egress is brokered (leases) even for adapters
- file writes are confined to declared outputs

See: `docs/281-network-egress-broker-and-consent.md`, `docs/294-oblivious-sandboxing-launchers.md`.


## 5) Review rubric hook

Any new adapter lane must answer:

- what is the external churn source?
- what is the translation contract?
- what evidence is emitted?
- what is the strangler plan?

This is a required section of feature intake.

See: `docs/348-design-review-rubric-and-feature-intake.md`.


Last updated: 2026-02-28r176
