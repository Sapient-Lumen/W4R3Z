# Doc catalog (generated)

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility

This page is generated from the contents of `docs/` and is meant as a navigation aid for humans and LLMs.

## Summary
- Total docs: **454**
- Docs with Tier/Profiles/Pillars metadata detected: **61**
- Full machine-readable catalog: `docs/_generated/doc_catalog.json`

## How to refresh
- `python3 tools/gen_doc_catalog.py --write`
- `python3 tools/check_generated_docs.py` (fails if this doc or the JSON catalog is stale)

## Meta-engineering docs (>=397)
These are expected to carry explicit Tier/Profiles/Pillars metadata and are the fastest way to regain project context.

| Doc | Title | Tier | Profiles | Pillars |
|---:|---|---|---|---|
| 397 | `docs/397-pattern-catalog.md` — DeriveBSD pattern catalog (how we prevent design sprawl) | A (Core meta-doc) | A, B, C, D | reproducibility, isolation, supply-chain, operability |
| 398 | `docs/398-zig-toolchain-wedge-and-cross-compilation.md` — Zig toolchain wedge (cross-compiling C/C++ dependencies without bespoke cross toolchains) | C (Optional lane) | A, B, C, D | reproducibility, supply-chain, operability |
| 399 | `docs/399-evidence-queries-and-fact-tables.md` — Evidence queries and fact tables (osquery-shaped ergonomics, but derived and receipted) | C (Optional lane) | A, B, C, D | operability, supply-chain |
| 400 | `docs/400-netgraph-and-netmap-as-derived-network-fabrics.md` — Netgraph + netmap/VALE as derived network fabrics (underused FreeBSD superpowers) | C (Optional lane) | A, C, D | isolation, operability |
| 401 | `docs/401-v0-cutline-and-feature-tiers.md` — v0 cutline + feature tiers (how DeriveBSD ships without becoming a monster) | A (Core meta-doc) | A, B, C, D | reproducibility, isolation, supply-chain, operability |
| 402 | `docs/402-adapter-lanes-and-strangler-discipline.md` — Adapter lanes + strangler discipline (interop without becoming forever-legacy) | A (Core meta-doc) | A, B, C, D | reproducibility, isolation, supply-chain, operability |
| 403 | `docs/403-swhid-fallback-and-long-term-source-availability.md` — SWHID fallback + long-term source availability (greenfield advantage) | C (Optional lane) | A, C, D | supply-chain, reproducibility |
| 404 | `docs/404-zfs-boot-environments-as-system-generations.md` — ZFS boot environments as system generations (receipt-backed) | B (Base) | A, B, C, D | operability, reproducibility |
| 405 | `docs/405-interactive-vm-tests-and-artifact-capture.md` — Interactive VM tests and artifact capture (NixOS/openQA-shaped) | C (Optional lane) | A, B, C, D | reproducibility, operability |
| 406 | `docs/406-uapi-fuzz-descriptors-and-conformance.md` — UAPI fuzz descriptors and conformance (syzkaller-shaped, registry-aligned) | C (Optional lane) | A, B, C, D | isolation, supply-chain, operability |
| 407 | `docs/407-spec-schema-conventions-and-evolution.md` — Spec schema conventions + evolution (keep artifacts legible) | A (Core meta-doc) | A, B, C, D | reproducibility, operability |
| 408 | `docs/408-abi-compatibility-lanes-linuxulator-vs-microvms.md` — ABI compatibility lanes: Linux emulation vs microVMs (Linuxulator / WSL lessons) | E (Adapter) | A, B, C | isolation, supply-chain, operability |
| 409 | `docs/409-zfs-encryption-and-key-management.md` — ZFS encryption + key management (data at rest, A–D viable) | B (Base) | A, B, C, D | isolation, supply-chain, operability |
| 410 | `docs/410-desktop-viability-checklist.md` — Desktop viability checklist (profile B must remain real) | C (Optional lane) | B | isolation, operability |
| 411 | `docs/411-product-profiles-as-compilation-target.md` — Product profiles as compilation targets (A–D, no forks) | A (Core meta-doc) | A, B, C, D | reproducibility, isolation, supply-chain, operability |
| 412 | `docs/412-product-profile-matrix.md` — Product profile matrix (A–D) | A (Core meta-doc) | A, B, C, D | reproducibility, isolation, supply-chain, operability |
| 413 | `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md` — ZFS replication: resume tokens, bookmarks, and receipted backups | C (Optional lane) | A, B, C, D | reproducibility, supply-chain, operability |
| 415 | `docs/415-risk-register-index.md` — Risk register index (generated) | A (Core) | A, B, C, D | operability |
| 416 | `docs/416-policy-trace-format-and-explain-surfaces.md` — Policy trace format + explain surfaces (stable, receipted, LLM-friendly) | B (Base) | A, B, C, D | operability, supply-chain, reproducibility |
| 417 | `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md` — Platform provenance + firmware lifecycle as derived ops (probe → plan → receipt) | B (Base) | A, B, C, D | supply-chain, operability, reproducibility, isolation |
| 418 | `docs/418-artifact-index.md` — Artifact index (generated) | A | A, B, C, D | operability, reproducibility |
| 419 | `docs/419-incident-timelines-as-derived-artifacts.md` — Incident timelines as derived artifacts (human-scale debugging) | B (Base) | A, B, C, D | operability, reproducibility, supply-chain |
| 420 | `docs/420-context-pack.md` — Context pack (generated) | A | A, B, C, D | operability, reproducibility |
| 421 | `docs/421-disposable-workspaces-and-template-microvms.md` — Disposable workspaces and template microVMs (Template → Lease → Dispose) | D (Research) | A, B, C | isolation, operability, reproducibility |
| 422 | `docs/422-invariant-registry-and-design-invariants.md` — Invariant registry and design invariants (Registry → Diff → Gate) | B (Base) | A, B, C, D | reproducibility, isolation, supply-chain, operability |
| 423 | `docs/423-persist-sets-and-ephemeral-root.md` — Persist sets + ephemeral root (impermanence) (Registry → Diff → Gate) | B (Base) | A, B, C, D | reproducibility, operability, isolation |
| 424 | `docs/424-forward-secure-event-log-sealing.md` — Forward-secure event log sealing (tamper-evident local evidence) | C (Optional lane) | A, B, C, D | supply-chain, operability |
| 425 | `docs/425-tpm-sealed-secrets-and-pcr-policies.md` — TPM-sealed secrets and PCR policies (optional lane) | C (Optional lane) | A, B, C, D | reproducibility, isolation, supply-chain, operability |
| 426 | `docs/426-store-gc-plans-and-receipts.md` — Store GC plans and receipts (retention as evidence) | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 427 | `docs/427-etc-config-diff-as-a-drift-surface.md` — /etc config diff as a first-class drift surface (OSTree + etcupdate lessons) | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 428 | `docs/428-fw-inventory-diff-as-drift-surface.md` — Firmware inventory diff as a drift surface (make platform posture reviewable) | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 429 | `docs/429-sysctl-diff-as-drift-surface.md` — Sysctl diff as a drift surface (review kernel knob changes) | B (Base) | A, B, C, D | isolation, operability, reproducibility |
| 430 | `docs/430-diff-surface-registry.md` — Diff surface registry (canonical review surfaces) | A (Core) | A, B, C, D | reproducibility, supply-chain, operability |
| 431 | `docs/431-build-stabilizers-and-determinism-normalizers.md` — Build stabilizers and determinism normalizers (optional lane) | C (Optional lane) | A, B, C, D | reproducibility, supply-chain, operability |
| 432 | `docs/432-sandbox-profile-diff-as-review-surface.md` — Sandbox profile diff as a drift surface (review least-authority changes) | B (Base) | A, B, C, D | isolation, operability, reproducibility |
| 433 | `docs/433-export-policy-diff-as-review-surface.md` — Export policy diff as a review surface (gate data egress drift) | B (Base) | A, B, C, D | operability, supply-chain, reproducibility |
| 434 | `docs/434-pki-trust-bundle-diff-as-review-surface.md` — PKI trust bundle diffs as review surfaces | B (Base) | A, B, C, D | supply-chain, operability, reproducibility, isolation |
| 435 | `docs/435-risk-flags-registry-and-gate-vocabulary.md` — Risk flags registry (stable gate vocabulary) | A (Core) | A, B, C, D | reproducibility, supply-chain, operability |
| 436 | `docs/436-boot-manifest-diff-as-review-surface.md` — Boot manifest diffs as a review surface (boot.manifest.diff) | B (Base) | A, B, C, D | reproducibility, supply-chain, operability, isolation |
| 437 | `docs/437-split-secrets-brokers.md` — Split secrets brokers (Split GPG / Split SSH style) | C (Optional lane) | A, B, C, D | isolation, operability, supply-chain |
| 438 | `docs/438-time-source-policy-diff-as-review-surface.md` — Time source policy diff as a review surface | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 439 | `docs/439-kmod-policy-diff-as-review-surface.md` — Kernel module policy diff as a drift surface (review privileged code injection) | B (Base) | A, B, C, D | isolation, supply-chain, operability, reproducibility |
| 440 | `docs/440-attestation-admission-policy-diff-as-review-surface.md` — Attestation admission policy diff as a review surface | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 441 | `docs/441-bundle-plan-diff-as-review-surface.md` — Bundle plan diff as a review surface | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 442 | `docs/442-exec-verify-policy-diff-as-review-surface.md` — Verified execution policy diff as a review surface | B (Base) | A, B, C, D | isolation, supply-chain, operability |
| 443 | `docs/443-boot-eventlog-canon-as-evidence-artifact.md` — Canonical boot event log as an evidence artifact | C (Optional lane) | A, B, C, D | supply-chain, operability |
| 444 | `docs/444-adapter-kill-policy-diff-as-review-surface.md` — Adapter kill policy diff as a review surface (`adapter.kill.policy.diff`) | B (Base) | A, B, C, D | reproducibility, isolation, supply-chain, operability |
| 445 | `docs/445-impurity-waiver-policy-diff-as-review-surface.md` — Impurity waiver policy diff as a review surface (`impurity.waiver.policy.diff`) | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 446 | `docs/446-trust-policy-diff-as-review-surface.md` — Trust policy diffs as review surfaces | A (Core) | A, B, C, D | supply-chain, operability |
| 447 | `docs/447-mirror-kit-manifest-as-evidence-artifact.md` — Mirror kit manifest as an evidence artifact | C (Optional lane) | A, B, C, D | supply-chain, operability |
| 448 | `docs/448-bundle-payload-manifest-as-evidence-artifact.md` — Bundle payload manifest as an evidence artifact | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 449 | `docs/449-lease-issue-and-use-receipts.md` — Lease issue + use receipts (make Broker→Lease→Receipt real) | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 450 | `docs/450-devfs-view-diff-as-review-surface.md` — Devfs view diff as a drift surface (review /dev authority changes) | B (Base) | A, B, C, D | isolation, operability, reproducibility |
| 451 | `docs/451-policy-module-diff-as-review-surface.md` — Policy module diff as a drift surface (review policy-code changes) | B (Base) | A, B, C, D | supply-chain, operability, reproducibility |
| 452 | `docs/452-sysctl-snapshot-as-evidence-artifact.md` — Sysctl snapshot as evidence (make drift explainable) | B (Base) | A, B, C, D | operability, isolation, reproducibility |
| 453 | `docs/453-preopen-map-diff-as-review-surface.md` — Preopen map diff as a review surface (Capsicum capability-set drift) | B (Base) | A, B, C, D | isolation, operability, reproducibility |
| 454 | `docs/454-intoto-slsa-adapter-lane.md` — In-toto / SLSA attestation export as an adapter lane (interop without forking evidence) | E (Adapter) | A, B, C, D | supply-chain, operability |
| 455 | `docs/455-microvm-launch-plans-and-receipts.md` — MicroVM lifecycle plans and receipts (making `derive-vmmd` spec-able) | A (Core) | A, B, C, D | isolation, operability, supply-chain |
| 456 | `docs/456-microvm-receipt-reason-code-registry.md` — MicroVM receipt reason-code registry (v0) | A (Core) | A, B, C, D | operability, isolation |

## Related tools
- `tools/gen_context_pack.py` (compact state summary)
- `tools/hygiene.py` (runs all lightweight checks)
- `tools/check_doc_metadata.py` (enforces metadata for meta docs)

Last updated: <generated>
