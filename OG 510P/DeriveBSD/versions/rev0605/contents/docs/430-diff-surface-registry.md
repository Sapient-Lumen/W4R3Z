# Diff surface registry (canonical review surfaces)

**Tier:** A (Core)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Registry→Diff→Gate, Bundles

DeriveBSD accumulates *many* reviewable diff surfaces as it grows.
This file is the **single canonical registry** of those diff artifacts.

Why this exists:
- **Stable review surface:** reviewers and tools can anchor on “the list of diffs that matter”.
- **Entropy control:** adding a new `*.diff` requires an explicit entry + rationale.
- **Bundle ergonomics:** drift bundles can say “these are the known diffs” and keep UX consistent.

This registry is intentionally short: it only lists **typed `*.diff` artifacts** with schemas under `spec/`.

See also:
- Drift bundles (the review funnel): `docs/395-drift-bundles-and-review-summaries.md`
- Surface registry pattern: `docs/379-surface-registry-pattern.md`
- Evidence spine overview: `docs/229-evidence-spine-overview.md`
- Risk flag vocabulary (reason codes for gates): `docs/435-risk-flags-registry-and-gate-vocabulary.md`

## Canonical diff surfaces

Each diff is a typed, deterministic-by-default artifact.
When diffs emit `risk_flags`, they should use canonical ids from `risk.flag.registry` (stable reason codes for UI + policy).
When a diff is optional, **policy** decides whether it is required for promotion.

| Diff kind | What it compares | Typical gates / evidence hooks | Wiring doc | Notes |
|---|---|---|---|---|
| `blast_radius.diff` | Umbrella summary of authority + contract drift | Promotion requires review; can require fuzz receipts / policy reports when flags trip | `docs/106-blast-radius-diff.md` | High-level “what changed” surface (human-first). |
| `authority.diff` | Authority graph deltas (capabilities/edges) | New risk tags/parsers → require mitigation/evidence; two-person integrity for broadening | `docs/374-authority-diff-schema-and-review-workflows.md` | Core capability creep control surface. |
| `parser.diff` | New/changed parsers (inputs that create authority edges) | New parsers → fuzz receipts; corpus additions; parser quarantine lane | `docs/376-parser-surface-registry-and-fuzz-gates.md` | Keeps “new parser = new attack surface” explicit. |
| `uapi.diff` | Kernel/user ABI/API surface deltas (syscalls, ioctls, sysctls-as-UAPI, etc.) | UAPI deltas → require compatibility notes, sandbox tests, regression receipts | `docs/362-uapi-surface-registry-and-compat-gates.md` | Treat kernel/user boundary drift as reviewable. |
| `contract.diff` | Declared contracts (service promises, portals, RPC endpoints) | Contract expansion → require authority diff narrowing proof or new mitigations | `docs/370-contract-registries-and-api-diff-gates.md` | Keeps interop APIs gateable. |
| `sandbox.profile.diff` | Sandbox promise profile deltas (`sandbox-profile` → `sandbox-profile`) | New promises/egress/listen/portal surfaces → require review; can require authority-diff narrowing proof | `docs/432-sandbox-profile-diff-as-review-surface.md` | Least-authority posture diff surface (human-first). |
| `preopen.map.diff` | Capsicum preopen map posture drift (`preopen.map` → `preopen.map`) | New handles/egress or broadened rights → require review; strict profiles can require two-person integrity | `docs/453-preopen-map-diff-as-review-surface.md` | Makes capability-set drift gateable (oblivious sandboxing ergonomics). |
| `devfs.view.diff` | Devfs view posture drift (`devfs.view.plan` → `devfs.view.plan`) | Exposure of sensitive device classes (raw disks, packet capture, input/HID) → require review; strict profiles can require two-person integrity | `docs/450-devfs-view-diff-as-review-surface.md` | Makes `/dev` authority drift gateable (device nodes are authority). |
| `trust.boundary.diff` | Trust-boundary crossings added/removed/reshaped | Boundary crossings → require explicit mitigations + evidence plan | `docs/380-trust-boundary-graphs-and-threat-diff.md` | Prevents “quiet” trust erosion. |
| `trust.policy.diff` | Trust policy drift (`trust-policy` → `trust-policy`) | Key set drift or target-rule/channel relaxations → require review; strict profiles can require two-person integrity | `docs/446-trust-policy-diff-as-review-surface.md` | Makes “what signatures/attestations are accepted?” drift legible. |
| `pki.trust.bundle.diff` | Trust bundle drift (`pki-trust-bundle` → `pki-trust-bundle`) | New/removed anchors or broadened constraints/distribution → require review; high-assurance profiles can require two-person integrity | `docs/434-pki-trust-bundle-diff-as-review-surface.md` | Makes trust root drift legible (anchors + constraints + applicability). |
| `crypto.diff` | Crypto surface registry drift (algorithms/suites/keys/policies) | Downgrades or new primitives → two-person integrity; compliance lanes | `docs/391-crypto-surface-registry-and-agility-gates.md` | Makes crypto changes legible. |
| `closure.diff` | Closure / input set changes (what code/content is in the build) | New sources → quarantine/promote receipts; rebuild evidence | `docs/396-closure-diffs-and-new-code-surfaces.md` | Supply-chain ingress drift surface. |
| `impurity.waiver.policy.diff` | Impurity waiver policy drift (`impurity.waiver.policy` → `impurity.waiver.policy`) | Waiver additions/scope broadenings/expiry extensions or default-mode relaxation → require review; strict profiles can require two-person integrity | `docs/445-impurity-waiver-policy-diff-as-review-surface.md` | Keeps “known impurity” explicit, time-bounded, and gateable. |
| `etc.config.diff` | `/etc` drift between generations | Non-empty drift → require review; optionally require `etcupdate(8)`/merge receipts | `docs/427-etc-config-diff-as-a-drift-surface.md` | Stops config folklore; makes divergence explicit. |
| `fw.inventory.diff` | Firmware/platform posture drift (UEFI inventory, Secure Boot digests, etc.) | Platform drift → require review; compliance evidence | `docs/428-fw-inventory-diff-as-drift-surface.md` | Turns “firmware changed” into a typed diff. |
| `boot.manifest.diff` | Boot-critical component digest drift (`boot-manifest` → `boot-manifest`) | Loader/kernel/cmdline drift → require review; high-assurance profiles can require two-person integrity and a `repro.check.receipt` | `docs/436-boot-manifest-diff-as-review-surface.md` | Makes boot-critical closure drift legible (human-first). |
| `time.source.policy.diff` | Time source posture drift (`time-source-policy` → `time-source-policy`) | Quorum/bootstrap relaxation or trust-root drift → require review; high-assurance profiles can require two-person integrity and a `time.sync.receipt` | `docs/438-time-source-policy-diff-as-review-surface.md` | Makes time-source policy drift legible (sources + quorum + bootstrap). |
| `attestation.admission.policy.diff` | Attestation admission policy drift (`attestation-admission-policy` → `attestation-admission-policy`) | Rule removals or requirement changes → require review; strict profiles can require two-person integrity | `docs/440-attestation-admission-policy-diff-as-review-surface.md` | Makes “what is attestation-gated?” drift legible. |
| `sysctl.diff` | Planned sysctl posture drift (`sysctl.plan` → `sysctl.plan`) | Risky knob changes → require review; optional classification/risk flags | `docs/429-sysctl-diff-as-drift-surface.md` | Kernel knob posture is a fact, not folklore. |
| `kmod.policy.diff` | Kernel module policy drift (`kmod-policy` → `kmod-policy`) | Runtime-load enablement or allow/deny rule drift → require review; strict profiles can require two-person integrity | `docs/439-kmod-policy-diff-as-review-surface.md` | Makes privileged code allowlists gateable. |
| `policy.module.diff` | Policy module drift (`policy-module` → `policy-module`) | Hostcalls expanded or limits relaxed → require review; strict profiles can require two-person integrity | `docs/451-policy-module-diff-as-review-surface.md` | Makes policy-code drift gateable (hostcalls are authority). |
| `exec.verify.policy.diff` | Execution-integrity policy drift (`exec.integrity.policy` → `exec.integrity.policy`) | Disable/relax enforcement, broaden execution sources, or add exceptions → require review; strict profiles can require two-person integrity | `docs/442-exec-verify-policy-diff-as-review-surface.md` | Keeps authoritative execution-integrity posture drift gateable while preserving the historic diff kind name. |
| `adapter.kill.policy.diff` | Adapter kill policy drift (`adapter.kill.policy` → `adapter.kill.policy`) | Adapter enablement, scope broadening, or default-mode relaxation → require review; strict profiles can require two-person integrity | `docs/444-adapter-kill-policy-diff-as-review-surface.md` | Makes interop kill switches gateable (Adapter→Shadow→Replace). |
| `export.policy.diff` | Export boundary posture drift (`export.policy` → `export.policy`) | Consent/encryption/recipient/rule broadening → require review; can require two-person integrity | `docs/433-export-policy-diff-as-review-surface.md` | Makes data egress drift legible. |
| `bundle.plan.diff` | Bundle plan drift (`bundle.plan` → `bundle.plan`) | Scope/include/transform binding drift → require review; strict profiles can require two-person integrity | `docs/441-bundle-plan-diff-as-review-surface.md` | Makes support bundle selection + transforms gateable. |
| `intent.role.binding.diff` | Remembered role/default drift (`intent.role.binding` → `intent.role.binding`) | Default-target changes or chooser-enrollment broadening/narrowing → require review; workstation trusted settings/admin UX and strict profiles can attach it to drift bundles | `docs/542-role-binding-diff-as-review-surface.md` | Keeps browser/mail role ownership changes explainable without a giant settings journal. |

## Rule: adding a new diff surface

If you add a new `*.diff` artifact, you must:
1) Add the schema + example (both are required):

```
spec/<kind>.diff.schema.json
spec/examples/<kind>.diff.json
```

2) Add exactly one row to the table above (keep it crisp), including:
   - the diff kind
   - one primary wiring doc that explains gates and bundle attachment

3) Wire the diff into the review funnel:
   - `docs/395-drift-bundles-and-review-summaries.md` (how it shows up in `drift.bundle`)
   - any lane doc that explains when it is required (Tier/profile/policy)

4) Add the doc(s) to discovery wiring (`docs/00-index.md` “New in …”, and relevant reading paths).

Guardrails:
- `python3 tools/check_diff_surface_registry.py` ensures this registry stays aligned with diff schemas under `spec/` (files ending in `.diff.schema.json`).
- `python3 tools/check_diff_surface_registry_wiring.py` ensures each diff row includes a real wiring doc path.
- `python3 tools/check_diff_wiring_risk_flags.py` incrementally requires wiring docs to declare a `## Risk flags` section (or be explicitly allowlisted), so gates/review UI have a stable jump-to reason-code surface.
- `python3 tools/check_risk_flag_typical_sources.py` ensures the canonical risk-flag registry’s `typical_sources` point at real artifact schemas and that `*.diff` sources are listed in this registry (prevents phantom/typo drift).

Last updated: 2026-03-17r272
