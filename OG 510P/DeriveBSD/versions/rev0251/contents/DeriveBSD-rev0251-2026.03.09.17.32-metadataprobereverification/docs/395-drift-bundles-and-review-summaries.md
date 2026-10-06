# Drift bundles: one review object that summarizes all drift surfaces

DeriveBSD accumulates multiple *diffable drift surfaces* over time:
authority, contracts, kernel UAPI, parsers, trust boundaries, crypto, policy, resources, etc.

A recurring failure mode in real systems is not “lack of diffs”, but **too many diffs**:
reviewers see a wall of changes and miss the security-relevant deltas.

Greenfield advantage: produce a single, typed **drift bundle** (`drift.bundle`) that:
- links to the underlying diffs (authority/UAPI/parser/contract/etc.)
- contains a compact, machine-checkable summary
- is the default attachment to a release, rollout, or RFC review

This turns “did we look at the right diffs?” into “the one drift bundle was reviewed”.

## Shape (artifact)

A drift bundle is a JSON object:

- kind: `drift.bundle`
- references the two generations (or commits) being compared
- lists the diff artifacts that were generated
- includes summary metrics (counts + flags)
- optionally links evidence/gates (policy test reports, fuzz receipts, proofs)

Schema: `spec/drift.bundle.schema.json`  
Example: `spec/examples/drift.bundle.json`

## Why this is worth baking in

### 1) The “review funnel” becomes explicit

Instead of:
- “read 12 diffs and remember what matters”

We have:
- “review `drift.bundle`, drill into the linked diffs when needed”

### 2) Drift is normalized across lanes

Whether the change was:
- a host activation
- an AppVM template update
- a portal API expansion
- a kernel UAPI change

…review starts from the same place.

### 3) It enables mechanically-enforced review gates

A policy engine can gate on the drift bundle summary:
- “new parsers introduced” → require fuzz receipts
- “new trust boundary crossing” → require mitigations
- “crypto downgrade risk” → require two-person integrity
- “policy surface changed” → require `policy.test.report`

## Relationship to blast-radius diffs

`blast_radius.diff` is the umbrella report for “authority deltas”.

A drift bundle is an **index + summary** that links to the underlying diff artifacts.
It may include any subset of the canonical diff surfaces; **policy** decides which are required.

Canonical diff registry (the stable list): `docs/430-diff-surface-registry.md`.

Practical rule of thumb:
- Always include `blast_radius.diff` (human-first orientation).
- Include the specific diffs that explain the flags (authority/parser/uapi/contract/trust-boundary/crypto/closure).
- Attach optional “posture diffs” when they changed and your profile/policy cares: /etc (`etc.config.diff`), firmware (`fw.inventory.diff`), boot-critical closure (`boot.manifest.diff`), sysctls (`sysctl.diff`), kmod policy (`kmod.policy.diff`), policy modules (`policy.module.diff`), execution-integrity posture (`exec.verify.policy.diff`), adapter kill posture (`adapter.kill.policy.diff`), impurity waiver posture (`impurity.waiver.policy.diff`), sandbox posture (`sandbox.profile.diff`), preopen maps (`preopen.map.diff`), devfs view posture (`devfs.view.diff`), export boundary (`export.policy.diff`), trust policy (`trust.policy.diff`), trust bundles (`pki.trust.bundle.diff`), time source policy (`time.source.policy.diff`), attestation admission policy (`attestation.admission.policy.diff`), repro checks (`repro.check.receipt`).

The drift bundle is *not* a replacement for those diffs; it’s the *index and summary*.

See: `docs/106-blast-radius-diff.md`, `docs/379-surface-registry-pattern.md`.

## Suggested workflow hooks

- `derive diff --bundle <from> <to> --json` → emits `drift.bundle`
- `derive review <drift.bundle>` → renders a human view + links
- CI policy: “no promotion without a drift bundle + required evidence”

## Meta-engineering rule

If a new drift surface is introduced (new registry/diff pair), it must:
- be representable in `drift.bundle`
- have a summary metric that can be gated on

This keeps “review ergonomics” from regressing as features are added.

See: `docs/348-design-review-rubric-and-feature-intake.md`, `docs/379-surface-registry-pattern.md`.

Last updated: 2026-03-07r215