# ADR-0070: Trust-bundle posture by profile

Date: 2026-03-06
Status: Accepted

## Context

DeriveBSD already has the raw ingredients for a coherent trust-root lane:
`docs/304-trust-bundles-and-ca-injection-as-artifacts.md`,
`docs/327-shadow-trust-and-system-ca-governance.md`, and
`docs/434-pki-trust-bundle-diff-as-review-surface.md`
cover signed trust bundles, shadow-trust scans, deterministic renderers, and typed drift surfaces.

What the archive still lacked was a **product-default boundary** for how those pieces behave in each product shape.
Without that boundary, the same trust-bundle vocabulary drifts into contradictory expectations:

- fleet hosts either enforce purpose-scoped trust bundles with strong review, or quietly allow app-shipped root stores to bypass policy,
- workstations either become too rigid for enterprise roots and local development, or silently accept hidden trust-root injection,
- general-purpose systems cannot tell whether explicit local trust-store overrides are a first-class adapter or an embarrassing accident,
- and appliance/regulatory deployments claim controlled supply-chain posture while still relying on ad-hoc live CA edits.

## Decision

DeriveBSD will treat **trust-bundle posture** as a first-class, profile-shaped default captured in
`spec/examples/product.profiles.json` under `trust_bundles` and guarded by `tools/check_product_profiles.py`.

This posture covers the default handling of:

- whether trust anchors live in governed `pki-trust-bundle` artifacts or ambient files,
- whether purpose-scoped bundles are the default for high-risk lanes,
- whether trust-bundle drift must pass through typed diff/review surfaces,
- how extra roots / local overrides appear in human-facing systems,
- and whether shadow trust (embedded app bundles, private NSS DBs, bespoke CA files) blocks official lanes by default.

The default values are:

- **A / `fleet_host`**: `purpose-scoped-diff-gated-shadow-trust-blocking`
- **B / `workstation`**: `system-visible-trusted-ui-extra-roots`
- **C / `general_os`**: `system-preferred-explicit-local-override`
- **D / `appliance_factory`**: `fixed-purpose-offline-quorum-bundles`

## Meaning by profile

### A) Secure fleet host (`fleet_host`)

- Fleet trust roots are governed artifacts, not ambient per-app files.
- Purpose-scoped bundles for public internet, internal mTLS, update verification, and similar lanes are normal.
- Trust-bundle drift is reviewable through typed diffs and stronger gates; official fleet lanes treat shadow trust as a blocker unless explicitly waived.

### B) Secure workstation (`workstation`)

- The workstation exposes a visible system trust baseline instead of hiding trust-root state in app sandboxes.
- Extra enterprise/developer roots are allowed, but they must land through trusted UI and become reviewable bundle changes rather than shell folklore.
- General interactive apps should not silently carry their own invisible root stores as the baseline compatibility story.

### C) General-purpose OS (`general_os`)

- Governed system trust remains the preferred baseline.
- Explicit local CA files, app-specific bundles, or compatibility overrides remain viable as adapters.
- C keeps broad software viability without silently redefining stricter A/B/D defaults.

### D) Appliance factory / regulatory (`appliance_factory`)

- Production/manufacturing trust roots are fixed-purpose, digest-bound artifacts distributed through approved offline or strongly governed lanes.
- High-impact trust-bundle changes require stronger approval and do not rely on ad-hoc live injection.
- Factory/support media should carry the trust story with them instead of reaching out for convenience root edits during incidents.

## Consequences

### Positive

- The archive now has a stable answer to “are extra roots/ad-hoc trust stores allowed here?” across A–D.
- Fleet and factory lanes get a coherent supply-chain story: bundle drift is reviewable and shadow trust is not a hidden escape hatch.
- Workstation and general-purpose shapes keep viable corporate/developer/root-injection escape hatches without pretending those are ambient baseline behavior.

### Negative / trade-offs

- This adds one more stable profile knob that must remain small and guardrailed.
- The exact bundle encoding, renderer count, and shadow-trust scanner heuristics remain implementation work.
- Workstation/general-purpose users will still need humane explanations for extra-root review and compatibility overrides.

## Non-goals

This ADR does **not** decide:

- the canonical on-disk encoding for every trust bundle,
- the exact waiver artifact for shadow-trust exceptions,
- the exact trust portal API shape,
- or the exact renderer count/stack shipped on day-0.

Those remain implementation work or future RFC/ADR material.

## Why this shape

The coherence win is not “one giant system trust store for everything” and it is not “let every app ship roots forever.”
It is deciding that:

- A defaults to purpose-scoped, diff-gated trust bundles and blocks shadow trust in official fleet lanes,
- B defaults to a visible governed system trust baseline with trusted-UI review for extra roots,
- C defaults to governed system trust while preserving explicit local override as a real adapter,
- D defaults to fixed-purpose offline/strongly-approved trust bundles instead of live production CA editing.

That is enough to guide future specs and coding without prematurely freezing renderer formats, portal APIs, or scanner details.
