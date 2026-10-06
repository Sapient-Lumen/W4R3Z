# Doc catalog (generated)

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility

This page is generated from the contents of `docs/` and is meant as a navigation aid for humans and LLMs.

## Summary
- Total docs: **522**
- Docs with Tier/Profiles/Pillars metadata detected: **131**
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
| 457 | `docs/457-workstation-host-ui-and-appvm-boundary.md` — Workstation host UI and AppVM boundary | B (Cross-cutting product-shape decision) | B | isolation, operability |
| 458 | `docs/458-removable-media-and-usb-posture-by-profile.md` — Removable media and USB posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, supply-chain, operability |
| 459 | `docs/459-outbound-network-posture-by-profile.md` — Outbound network posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 460 | `docs/460-inbound-listen-posture-by-profile.md` — Inbound listen posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 461 | `docs/461-remote-assistance-posture-by-profile.md` — Remote assistance posture by profile | C (Optional lane) | A, B, C, D | isolation, operability |
| 462 | `docs/462-private-key-and-crypto-op-posture-by-profile.md` — Private-key and crypto-operation posture by profile | C (Optional lane) | A, B, C, D | isolation, supply-chain, operability |
| 463 | `docs/463-human-identity-and-home-state-posture-by-profile.md` — Human identity and home-state posture by profile | C (Optional lane) | A, B, C, D | isolation, operability |
| 464 | `docs/464-backup-and-restore-posture-by-profile.md` — Backup and restore posture by profile | C (Optional lane) | A, B, C, D | operability, isolation, supply-chain |
| 465 | `docs/465-data-at-rest-posture-by-profile.md` — Data-at-rest posture by profile | C (Optional lane) | A, B, C, D | isolation, operability, supply-chain |
| 466 | `docs/466-export-boundary-posture-by-profile.md` — Export boundary posture by profile | C (Optional lane) | A, B, C, D | operability, isolation, supply-chain |
| 467 | `docs/467-operator-access-posture-by-profile.md` — Operator-access posture by profile | C (Optional lane) | A, B, C, D | isolation, operability |
| 468 | `docs/468-trustworthy-time-posture-by-profile.md` — Trustworthy-time posture by profile | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 469 | `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md` — Platform provenance and attestation-admission posture by profile | B (Base) | A, B, C, D | supply-chain, isolation, operability |
| 470 | `docs/470-workload-identity-and-credential-issuance-posture-by-profile.md` — Workload identity and credential-issuance posture by profile | B (Base) | A, B, C, D | isolation, supply-chain, operability |
| 471 | `docs/471-firmware-update-posture-by-profile.md` — Firmware-update posture by profile | B (Base) | A, B, C, D | supply-chain, operability, reproducibility |
| 472 | `docs/472-update-delivery-and-release-posture-by-profile.md` — Update-delivery and release posture by profile | B (Base) | A, B, C, D | supply-chain, operability, reproducibility |
| 473 | `docs/473-installation-and-recovery-posture-by-profile.md` — Installation-and-recovery posture by profile | B (Base) | A, B, C, D | operability, reproducibility, isolation |
| 474 | `docs/474-high-risk-approval-posture-by-profile.md` — High-risk approval posture by profile | B (Base) | A, B, C, D | supply-chain, operability, isolation |
| 475 | `docs/475-kernel-mutation-posture-by-profile.md` — Kernel mutation posture by profile | B (Base) | A, B, C, D | isolation, operability, reproducibility |
| 476 | `docs/476-device-authority-posture-by-profile.md` — Device authority posture by profile | B (Base) | A, B, C, D | isolation, operability |
| 477 | `docs/477-network-topology-posture-by-profile.md` — Network topology posture by profile | B (Base) | A, B, C, D | isolation, operability |
| 478 | `docs/478-evidence-collection-posture-by-profile.md` — Evidence collection posture by profile | B (Base) | A, B, C, D | operability, isolation |
| 479 | `docs/479-hardware-compatibility-posture-by-profile.md` — Hardware compatibility posture by profile | B (Base) | A, B, C, D | isolation, operability |
| 480 | `docs/480-trust-bundle-posture-by-profile.md` — Trust-bundle posture by profile | B (Base) | A, B, C, D | supply-chain, operability, reproducibility |
| 481 | `docs/481-support-bundle-contract-and-timeline-first-handoff.md` — Support-bundle contract and timeline-first handoff | B (Base) | A, B, C, D | operability, reproducibility, isolation |
| 482 | `docs/482-boot-code-admission-and-constrained-overrides.md` — Boot code admission and constrained overrides | B (Base) | A, B, C, D | supply-chain, operability, reproducibility, isolation |
| 483 | `docs/483-destructive-reprovisioning-and-reset-authority.md` — Destructive reprovisioning and reset authority | B (Base) | A, B, C, D | operability, reproducibility, supply-chain |
| 484 | `docs/484-origin-label-authority-and-anti-laundering-boundary.md` — Origin label authority and anti-laundering boundary | B (Base) | A, B, C, D | operability, supply-chain, isolation |
| 485 | `docs/485-stratum-stack-and-runtime-composition-boundary.md` — Stratum stack and runtime composition boundary | B (Base) | A, B, C, D | isolation, supply-chain, operability |
| 486 | `docs/486-exec-integrity-authority-and-verified-execution-boundary.md` — Exec integrity authority and verified-execution boundary | B (Base) | A, B, C, D | isolation, supply-chain, operability |
| 487 | `docs/487-keyless-identity-evidence-and-offline-verification-boundary.md` — Keyless identity evidence and offline-verification boundary | B (Base) | A, B, C, D | supply-chain, operability |
| 488 | `docs/488-release-transparency-evidence-and-monitor-gate-boundary.md` — Release transparency evidence and monitor-gate boundary | B (Base) | A, B, C, D | supply-chain, operability |
| 489 | `docs/489-supplychain-verification-evidence-and-publish-gate-boundary.md` — Supplychain verification evidence and publish-gate boundary | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 490 | `docs/490-witness-policy-and-roster-quorum-boundary.md` — Witness policy and roster/quorum boundary | B (Base) | A, B, C, D | supply-chain, operability |
| 491 | `docs/491-vulnerability-verification-evidence-and-publish-gate-boundary.md` — Vulnerability verification evidence and publish-gate boundary | B (Base) | A, B, C, D | supply-chain, operability |
| 492 | `docs/492-attestation-results-evidence-and-admission-issue-boundary.md` — Attestation results evidence and admission-issue boundary | B (Base) | A, B, C, D | isolation, supply-chain, operability |
| 493 | `docs/493-temporary-authority-grant-lease-and-use-boundary.md` — Temporary authority grant / lease / use boundary | B (Base) | A, B, C, D | isolation, operability, supply-chain |
| 494 | `docs/494-authority-budget-policy-check-and-exception-boundary.md` — Authority budget / check / exception boundary | B (Base) | A, B, C, D | isolation, operability |
| 495 | `docs/495-frontend-source-compile-receipt-and-canonical-ir-boundary.md` — Frontend source / compile receipt / canonical IR boundary | B (Base) | A, B, C, D | reproducibility, supply-chain, operability |
| 496 | `docs/496-store-retention-and-gc-posture-by-profile.md` — Store retention and GC posture by profile | B (Base) | A, B, C, D | operability, reproducibility, supply-chain |
| 498 | `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md` — Safe-open support-bundle intake and incident-reproduction boundary | B (Base) | A, B, C, D | isolation, operability, reproducibility |
| 499 | `docs/499-fuzz-target-classes-and-flake-aware-promotion-gate-boundary.md` — Fuzz target classes and flake-aware promotion-gate boundary | B (Base) | A, B, C, D | isolation, supply-chain, operability |
| 500 | `docs/500-derive-unit-source-compile-receipt-and-runtime-boundary.md` — Derive unit source / compile receipt / runtime boundary | B (Base) | A, B, C, D | reproducibility, isolation, operability |
| 501 | `docs/501-product-profile-default-vocabulary-boundary.md` — Product-profile default vocabulary boundary | B (Base) | A, B, C, D | reproducibility, isolation, operability |
| 502 | `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md` — Support-bundle intake typed plan / receipt shapes | B (Base) | A, B, C, D | isolation, operability, reproducibility |
| 503 | `docs/503-telemetry-is-not-a-product-profile-default-boundary.md` — Telemetry is not a product-profile default boundary | B (Base) | A, B, C, D | operability, isolation |
| 504 | `docs/504-dns-receipt-detail-and-export-posture-by-profile.md` — DNS receipt detail and export posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | operability, isolation |
| 505 | `docs/505-network-learn-audit-convergence-contract.md` — Network learn/audit convergence contract | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 506 | `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md` — Packet capture / raw sockets / fast packet I/O boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 507 | `docs/507-packet-capture-session-and-summary-first-export-boundary.md` — Packet capture session and summary-first export boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 508 | `docs/508-packet-capture-summary-review-surface-boundary.md` — Packet capture summary review-surface boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 509 | `docs/509-packet-capture-selector-compiler-boundary.md` — Packet capture selector compiler boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 510 | `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md` — Packet capture local-artifact metadata and retention boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 511 | `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md` — Packet-capture strong-artifact safe-open intake and normalize-before-promotion boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 512 | `docs/512-packet-capture-normalization-redaction-receipt-boundary.md` — Packet-capture normalization redaction-receipt boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, supply-chain |
| 513 | `docs/513-packet-capture-evidence-joins-in-incident-bundles-boundary.md` — Packet-capture evidence joins in incident bundles boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 514 | `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md` — Packet-capture export proof-chain and compiled profile posture boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 515 | `docs/515-packet-capture-strong-export-approval-evidence-boundary.md` — Packet-capture stronger export approval evidence boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 516 | `docs/516-packet-capture-strong-export-transport-boundary.md` — Packet-capture stronger export transport-boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 517 | `docs/517-packet-capture-strong-export-digest-stability-boundary.md` — Packet-capture stronger export digest-stability boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, isolation |
| 518 | `docs/518-packet-capture-strong-export-recipient-acceptance-boundary.md` — Packet-capture stronger export recipient-acceptance boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, isolation |
| 519 | `docs/519-packet-capture-strong-export-destination-bound-approval-boundary.md` — Packet-capture stronger export destination-bound approval boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 520 | `docs/520-packet-capture-strong-export-recipient-digest-confirmation-boundary.md` — Packet-capture stronger export recipient-digest confirmation boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, supply-chain |
| 521 | `docs/521-packet-capture-strong-export-remote-object-continuity-boundary.md` — Packet-capture stronger export remote-object continuity boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, supply-chain |
| 522 | `docs/522-packet-capture-strong-export-remote-validator-continuity-boundary.md` — Packet-capture stronger export remote-validator continuity boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, supply-chain |
| 523 | `docs/523-packet-capture-strong-export-remote-protection-posture-boundary.md` — Packet-capture stronger export remote-protection posture boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, supply-chain |
| 524 | `docs/524-packet-capture-strong-export-remote-locator-continuity-boundary.md` — Packet-capture stronger export remote-locator continuity boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, supply-chain |
| 525 | `docs/525-packet-capture-strong-export-remote-reverification-boundary.md` — Packet-capture stronger export remote reverification boundary | B (Cross-cutting product-shape decision) | A, B, C, D | operability, supply-chain |

## Related tools
- `tools/gen_context_pack.py` (compact state summary)
- `tools/hygiene.py` (runs all lightweight checks)
- `tools/check_doc_metadata.py` (enforces metadata for meta docs)

Last updated: 2026-03-09r254
