# Adapter kill policy diff as a review surface (`adapter.kill.policy.diff`)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, isolation, supply-chain, operability
**Patterns:** Adapter→Shadow→Replace, Registry→Diff→Gate, Plan→Receipt

Interop is unavoidable (ports/pkg, OCI, full TUF), but “compat forever” is a trap.
DeriveBSD’s non-negotiable adapter discipline includes a hard requirement: **every adapter lane must be killable by policy**.

This doc introduces a small, typed control surface:

- `adapter.kill.policy` (the kill switch and phase selector)
- `adapter.kill.policy.diff` (a stable review surface for drift bundles + gates)

This keeps A–D viable without forks: profiles can **forbid adapters by default**, allow specific adapters temporarily, or require two-person integrity for any enablement.


## 1) What the policy controls

## The artifacts

Primary review surface: `adapter.kill.policy.diff`

Schema (policy): `spec/adapter.kill.policy.schema.json`  
Example (policy): `spec/examples/adapter.kill.policy.json`

Schema (diff): `spec/adapter.kill.policy.diff.schema.json`  
Example (diff): `spec/examples/adapter.kill.policy.diff.json`

`adapter.kill.policy` is the single object that answers:

- which adapters exist (by `adapter_id`)
- which phase they are in (`disabled` / `adapter` / `shadow` / `replace`)
- where they are allowed to run (`scopes`: `import` / `install` / `runtime`)
- whether a compatibility mode is time-bounded (`expires_at`)

Design intent:
- **Default deny** (`default_mode: disabled`) keeps unknown adapters from becoming ambient.
- `disabled` is the **kill switch**.
- `shadow` is the greenfield superpower: run both paths and compare.
- `replace` is high leverage: treat it as a reviewable posture change, not a “ship it” toggle.


## 2) Why a typed diff exists

Without a diff, adapter posture drift becomes folklore:

- “OCI got turned on for a while”
- “Linux ABI compat is enabled on some machines”
- “we’re still using the full-TUF adapter because the native lane slipped”

`adapter.kill.policy.diff` makes this drift mechanical:

- **Stable review surface** for “interop toggles”.
- **Gateable** enablement and scope broadening.
- **Bundle-friendly** evidence attachment: the diff can be included in `drift.bundle.artifacts` alongside closure/parser/authority diffs.


## 3) Tiering and product-shape viability

- **Tier B (Base):** the policy + diff surface exist so operators can disable/enable adapters explicitly.
- **Tier E (Adapter):** each specific adapter implementation remains optional and can be absent from an image/profile.

Profiles use this surface differently:
- **Fleet host / appliance factory:** default deny; two-person integrity for any enablement; forbid `runtime` scopes unless explicitly justified.
- **Workstation / general OS:** allow specific adapters in `import`/`install` scopes by policy; keep `runtime` as a deliberate exception.


## 4) Wiring into drift bundles + gates

When adapter posture changes, include `adapter.kill.policy.diff` in the drift bundle:

- `drift.bundle.artifacts[]` entry with `kind: adapter.kill.policy.diff`
- pair it with the **real consequences** of enabling the adapter:
  - `closure.diff` (new code ingestion)
  - `parser.diff` (new decode surface)
  - `authority.diff` (new authority-bearing handles)
  - `trust.boundary.diff` (new crossings)

Policy can then gate promotion on the diff’s `summary.risk_flags` using the canonical risk-flag registry.


## Risk flags

The diff summary should emit stable reason codes (from the canonical risk-flag registry) so gates and reviewers have consistent semantics:

- `adapter-enabled`: an adapter moved from disabled to an active mode.
- `adapter-shadow-enabled`: an adapter entered shadow mode (still a posture change; compare receipts are expected).
- `adapter-replace-enabled`: an adapter entered replace mode (high leverage; treat like a migration cutover).
- `adapter-default-mode-relaxed`: the default adapter posture moved away from deny-by-default.
- `adapter-scope-broadened`: an adapter gained a broader scope (especially runtime).


## 6) Research note: “strangler” is a real pattern, not vibes

The Adapter → Shadow → Replace discipline is the OS equivalent of the Strangler Fig pattern: bounded coexistence, measurable divergence, and a credible removal path.

Reference (curated): https://martinfowler.com/bliki/StranglerFigApplication.html


Last updated: 2026-02-28r172
