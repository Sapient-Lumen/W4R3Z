# Doc catalog (generated)

**Tier:** A (Core)  
**Profiles:** A, B, C, D  
**Pillars:** operability, reproducibility

This page is generated from the contents of `docs/` and is meant as a navigation aid for humans and LLMs.

## Summary
- Total docs: **626**
- Docs with Tier/Profiles/Pillars metadata detected: **235**
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
| 526 | `docs/526-derived-base-sets-and-pkgbase-adapter-boundary.md` — Derived base sets and pkgbase adapter boundary | A (Core contract boundary) | A, B, C, D | reproducibility, supply-chain, operability |
| 527 | `docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md` — Verified lazy tree mount / materialization / evidence boundary | B (Base contract boundary) | A, B, C, D | reproducibility, isolation, operability |
| 528 | `docs/528-hardware-support-matrix-and-bundled-admission-boundary.md` — Hardware support matrix and bundled admission boundary | B (Base contract boundary) | A, B, C, D | isolation, supply-chain, operability |
| 529 | `docs/529-hardware-support-promotion-and-qualification-boundary.md` — Hardware support promotion and qualification boundary | B (Base contract boundary) | A, B, C, D | supply-chain, operability |
| 530 | `docs/530-hardware-support-qualification-receipt-boundary.md` — Hardware support qualification receipt boundary | B (Base contract boundary) | A, B, C, D | supply-chain, operability |
| 531 | `docs/531-hardware-support-qualification-profile-boundary.md` — Hardware support qualification profile boundary | B (Base contract boundary) | A, B, C, D | supply-chain, operability |
| 532 | `docs/532-hardware-support-qualification-freshness-boundary.md` — Hardware support qualification freshness boundary | B (Base contract boundary) | A, B, C, D | supply-chain, operability |
| 533 | `docs/533-hardware-support-qualification-status-boundary.md` — Hardware support qualification status boundary | B (Base contract boundary) | A, B, C, D | supply-chain, operability |
| 534 | `docs/534-hardware-support-conditions-and-known-limitations-boundary.md` — Hardware support conditions and known limitations boundary | B (Base contract boundary) | A, B, C, D | operability, isolation |
| 535 | `docs/535-hardware-support-qualification-target-scope-boundary.md` — Hardware support qualification target-scope boundary | B (Base contract boundary) | A, B, C, D | operability, reproducibility |
| 536 | `docs/536-workstation-display-composition-and-gpu-boundary.md` — Workstation display composition and GPU boundary | C (Optional lane) | A, B, C, D | isolation, operability |
| 537 | `docs/537-workstation-remoted-session-surface-boundary.md` — Workstation remoted session-surface boundary | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 538 | `docs/538-workstation-cross-domain-datatransfer-floor.md` — Workstation cross-domain data-transfer floor | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 539 | `docs/539-workstation-intent-routed-uri-opening-floor.md` — Workstation intent-routed URI opening floor | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 540 | `docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md` — Workstation role-bound intent targets and chooser floor | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 541 | `docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md` — Workstation role-slot bindings as a typed state boundary | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 542 | `docs/542-role-binding-diff-as-review-surface.md` — Role-binding diff as a review surface | B (Base) | A, B, C, D | isolation, operability |
| 543 | `docs/543-role-binding-event-as-durable-mutation-evidence.md` — Role-binding event as durable mutation evidence | B (Base) | A, B, C, D | isolation, operability |
| 544 | `docs/544-role-binding-consent-lane-for-interactive-workstation-mutations.md` — Role-binding consent lane for interactive workstation mutations | B (Base) | A, B, C, D | isolation, operability |
| 545 | `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md` — Role-binding policy-decision join for non-interactive mutations | B (Base) | A, B, C, D | supply-chain, operability |
| 546 | `docs/546-role-binding-diff-precondition-and-conflict-denial-boundary.md` — Role-binding diff precondition and conflict denial boundary | B (Base) | A, B, C, D | isolation, operability |
| 547 | `docs/547-role-binding-support-import-join-via-content-import-receipt.md` — Role-binding support-import join via content.import.receipt | B (Base) | A, B, C, D | operability, supply-chain |
| 548 | `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md` — Role-binding authority lanes are not invocation surfaces | B (Base) | A, B, C, D | operability, supply-chain |
| 549 | `docs/549-role-binding-policy-decisions-bind-exact-mutation.md` — Role-binding policy decisions must bind the exact mutation | B (Base contract boundary) | A, B, C, D | supply-chain, operability |
| 550 | `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md` — Role-binding policy decisions are short-lived and single-apply | B (Base contract boundary) | A, B, C, D | supply-chain, operability |
| 551 | `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md` — Role-binding policy decisions need unique instance identity | B (Base contract boundary) | A, B, C, D | supply-chain, operability |
| 552 | `docs/552-role-binding-policy-window-denials-need-typed-reasons.md` — Role-binding policy-window denials need typed reasons | B (Base contract boundary) | A, B, C, D | operability, supply-chain |
| 553 | `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md` — Role-binding denial precedence between policy-window and precondition checks | B (Base) | A, B, C, D | operability, isolation |
| 554 | `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md` — Role-binding policy-consumed denials point to the consuming event | B (Base) | A, B, C, D | operability, isolation |
| 555 | `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md` — Role-binding policy-consumed same-mutation retries collapse to already-applied | B (Base) | A, B, C, D | operability, isolation |
| 556 | `docs/556-role-binding-retries-need-a-stable-recovery-interpretation-field.md` — Role-binding retries need a stable recovery interpretation field | B (Base) | A, B, C, D | operability, isolation |
| 557 | `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md` — Role-binding policy-consumed denials carry a consuming-event digest | B (Base) | A, B, C, D | operability, supply-chain |
| 558 | `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md` — Role-binding policy-consumed denials carry the consuming binding digest | B (Base) | A, B, C, D | operability, supply-chain |
| 559 | `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md` — Role-binding policy-consumed denials carry the consuming diff digest | B (Base) | A, B, C, D | operability, isolation |
| 560 | `docs/560-role-binding-policy-consumed-denials-carry-consuming-previous-binding-digest.md` — Role-binding policy-consumed denials carry the consuming previous-binding digest | B (Base) | A, B, C, D | operability, isolation |
| 561 | `docs/561-role-binding-policy-consumed-denials-carry-consuming-event-action.md` — Role-binding policy-consumed denials carry the consuming event action | B (Base) | A, B, C, D | operability, isolation |
| 562 | `docs/562-relay-backed-publish-sessions-for-temporary-service-sharing.md` — Relay-backed publish sessions for temporary service sharing | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 563 | `docs/563-publish-session-audience-binding-and-publicness-posture-boundary.md` — Publish-session audience binding and publicness posture boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 564 | `docs/564-publish-session-end-conditions-and-no-auto-resume-posture-boundary.md` — Publish-session end conditions and no-auto-resume posture boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 565 | `docs/565-publish-session-session-scoped-locator-posture-boundary.md` — Publish-session session-scoped locator posture boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 566 | `docs/566-publish-session-redacted-locators-and-separate-secret-handoff-boundary.md` — Publish-session redacted locators and separate secret handoff boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 567 | `docs/567-publish-session-secret-handoff-lifetime-coupled-to-session-authority.md` — Publish-session secret-handoff lifetime coupled to session authority | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 568 | `docs/568-publish-session-secret-consumption-semantics-boundary.md` — Publish-session secret consumption semantics boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 569 | `docs/569-publish-session-support-peer-requires-support-session-authority-boundary.md` — Publish-session support-peer requires support-session authority boundary | B (Base) | A, B, C, D | isolation, operability |
| 570 | `docs/570-publish-session-access-model-posture-boundary.md` — Publish-session access-model posture boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 571 | `docs/571-publish-session-tailnet-reverse-forward-posture-boundary.md` — Publish-session tailnet reverse-forward posture boundary | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 572 | `docs/572-publish-session-audience-bound-human-shares-stay-relay-url-shaped.md` — Publish-session audience-bound human shares stay relay-url-shaped | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 573 | `docs/573-publish-session-audience-bound-shares-require-binding-hints.md` — Publish-session audience-bound shares require binding hints | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 574 | `docs/574-publish-session-public-webhook-shares-require-validation-hints.md` — Publish-session public-webhook shares require validation hints | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 575 | `docs/575-publish-session-endpoint-hints-follow-access-model.md` — Publish-session endpoint hints follow access model | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 576 | `docs/576-publish-session-relay-remote-locator-kind-follows-access-model.md` — Publish-session relay remote locator kind follows access model | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 577 | `docs/577-publish-session-relay-remote-locator-values-follow-locator-kind.md` — Publish-session relay remote locator values follow locator kind | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 578 | `docs/578-publish-session-destination-hint-follows-remote-locator.md` — Publish-session destination hint follows remote locator | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 579 | `docs/579-publish-session-url-hints-follow-endpoint-tuple.md` — Publish-session URL hints follow endpoint tuple | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 580 | `docs/580-publish-session-local-service-uri-hints-stay-loopback-shaped.md` — Publish-session local-service URI hints stay loopback-shaped | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 581 | `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md` — Publish-session published-endpoint hostnames stay host-shaped | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 582 | `docs/582-publish-session-path-prefixes-stay-normalized.md` — Publish-session path prefixes stay normalized | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 583 | `docs/583-publish-session-relay-url-hints-stay-https-shaped.md` — Publish-session relay-url hints stay https-shaped | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 584 | `docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md` — Publish-session relay uri-hint locators stay non-web-shaped | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 585 | `docs/585-publish-session-path-prefixes-stay-uri-path-safe.md` — Publish-session path prefixes stay URI-path-safe | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 586 | `docs/586-publish-session-authority-joins-follow-trigger.md` — Publish-session authority joins follow trigger | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 587 | `docs/587-publish-session-authority-stays-lease-addressable.md` — Publish-session authority stays lease-addressable | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 588 | `docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md` — Publish-session support-session triggers stay support-peer-shaped | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 589 | `docs/589-publish-session-secret-handoffs-follow-authn-mode.md` — Publish-session secret handoffs follow authn_mode | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 590 | `docs/590-publish-session-maintenance-triggers-stay-digest-empty.md` — Publish-session maintenance triggers stay digest-empty until a dedicated lane exists | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 591 | `docs/591-publish-session-validation-hints-stay-webhook-only.md` — Publish-session validation hints stay webhook-only | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 592 | `docs/592-publish-session-binding-hints-stay-lane-exact.md` — Publish-session binding hints stay lane-exact | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 593 | `docs/593-publish-session-organization-user-shares-stay-organization-scoped.md` — Publish-session organization-user shares stay organization-scoped | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 594 | `docs/594-publish-session-published-endpoint-surface-stays-lease-frozen.md` — Publish-session published endpoint surface stays lease-frozen | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 595 | `docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md` — Publish-session diagnostic artifacts stay off baseline envelope | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 596 | `docs/596-publish-session-notes-stay-off-baseline-envelope.md` — Publish-session notes stay off baseline envelope | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 597 | `docs/597-publish-session-visible-indicators-stay-durable-until-ended.md` — Publish-session visible indicators stay durable until ended | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 598 | `docs/598-publish-session-post-end-access-stays-fail-closed.md` — Publish-session post-end access stays fail-closed | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 599 | `docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md` — Publish-session revocation affordances stay same-surface durable | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 600 | `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md` — Publish-session return paths stay trusted-ui persistent | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 601 | `docs/601-publish-session-management-return-paths-stay-lease-exact.md` — Publish-session management return paths stay lease-exact | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 602 | `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md` — Publish-session post-end management return stays lease-exact-ended | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 603 | `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md` — Publish-session ended states stay terminal-cause exact | B (Cross-cutting product-shape decision) | A, B, C, D | isolation, operability |
| 604 | `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md` — Publish-session current contract stack and stale entrypoint firewall | B (Cross-cutting product-shape decision) | A, B, C, D | operability |
| 605 | `docs/605-workstation-file-open-import-and-bounded-document-roles.md` — Workstation file-open import join and bounded document roles | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 606 | `docs/606-workstation-imported-foreign-documents-stay-view-first.md` — Workstation imported foreign documents stay view-first | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 607 | `docs/607-workstation-working-copy-receipts-and-edit-route-joins.md` — Workstation working-copy receipts and edit-route joins | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 608 | `docs/608-workstation-working-copy-save-scope-and-no-implicit-source-writeback.md` — Workstation working-copy save scope and no implicit source write-back | B (Base contract boundary) | A, B, C, D | isolation, operability |
| 609 | `docs/609-workstation-working-copy-reintegration-stays-explicit-and-new-version-shaped.md` — Workstation working-copy reintegration stays explicit and new-version-shaped | B (Base contract boundary) | A, B, C, D | isolation, operability, supply-chain |
| 610 | `docs/610-workstation-successor-candidates-stay-immutable-and-resnapshot-shaped.md` — Workstation successor candidates stay immutable and resnapshot-shaped | B (Base contract boundary) | A, B, C, D | operability, isolation, supply-chain |
| 611 | `docs/611-workstation-candidate-supersession-stays-explicit-and-no-latest-wins.md` — Workstation candidate supersession stays explicit and no latest-wins | B (Base contract boundary) | A, B, C, D | operability, isolation, supply-chain |
| 612 | `docs/612-workstation-candidate-supersession-stays-same-origin-and-self-describing.md` — Workstation candidate supersession stays same-origin and self-describing | B (Base contract boundary) | A, B, C, D | operability, isolation, supply-chain |
| 613 | `docs/613-workstation-candidate-supersession-stays-head-exact-and-stale-target-fail-closed.md` — Workstation candidate supersession stays head-exact and stale-target fail-closed | B (Base contract boundary) | A, B, C, D | operability, isolation, supply-chain |
| 614 | `docs/614-workstation-stale-supersession-denials-carry-current-head-evidence-and-recovery-target.md` — Workstation stale supersession denials carry current-head evidence and recovery target | B (Base contract boundary) | A, B, C, D | operability, isolation, supply-chain |
| 615 | `docs/615-workstation-stale-supersession-recovery-stays-denial-joined-and-head-pinned.md` — Workstation stale supersession recovery stays denial-joined and head-pinned | B (Base) | B | isolation, operability, supply-chain |
| 616 | `docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md` — Remote assistance recording detail and export posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | operability, isolation |
| 617 | `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md` — Operator-access recording detail and export posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | operability, isolation |
| 618 | `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md` — Breakglass recording detail and export posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | operability, isolation |
| 619 | `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md` — Destructive reprovision evidence detail and export posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | operability, isolation, reproducibility |
| 620 | `docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md` — Restore plans and receipts stay quarantine-first and promotion-shaped | B (Cross-cutting product-shape decision) | A, B, C, D | operability, isolation, reproducibility |
| 621 | `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md` — Firmware inventory and mutation evidence detail and export posture by profile | B (Cross-cutting product-shape decision) | A, B, C, D | operability, supply-chain, reproducibility |
| 622 | `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md` — Trust-bundle apply receipts bind canonical bundles to runtime views | B (Cross-cutting evidence boundary) | A, B, C, D | supply-chain, operability, reproducibility |
| 623 | `docs/623-event-journal-digests-stay-chain-exact-and-seal-list-bound.md` — Event journal digests stay chain-exact and seal-list-bound | B (Cross-cutting evidence boundary) | A, B, C, D | operability, supply-chain, reproducibility |
| 624 | `docs/624-incident-bundles-carry-trust-bundle-apply-proof-by-digest.md` — Incident bundles carry trust-bundle apply proof by digest | B (Cross-cutting evidence boundary) | A, B, C, D | operability, supply-chain, reproducibility |
| 625 | `docs/625-incident-bundles-carry-event-seal-proof-by-digest.md` — Incident bundles carry event-seal proof by digest | B (Cross-cutting evidence boundary) | A, B, C, D | operability, isolation, supply-chain |
| 626 | `docs/626-incident-bundles-carry-restore-apply-proof-by-digest.md` — Incident bundles carry restore apply proof by digest | B (Base support/evidence contract) | A, B, C, D | operability, reproducibility, isolation |
| 627 | `docs/627-incident-bundles-carry-support-session-proof-by-digest.md` — Incident bundles carry support-session proof by digest | B (Cross-cutting evidence boundary) | A, B, C, D | operability, isolation, reproducibility |
| 628 | `docs/628-incident-bundles-carry-operator-session-proof-by-digest.md` — Incident bundles carry operator-session proof by digest | B (Cross-cutting evidence boundary) | A, B, C, D | operability, isolation, reproducibility |
| 629 | `docs/629-incident-bundles-carry-breakglass-proof-by-digest.md` — Incident bundles carry breakglass proof by digest | B (Cross-cutting evidence boundary) | A, B, C, D | operability, isolation, reproducibility |

## Related tools
- `tools/gen_context_pack.py` (compact state summary)
- `tools/hygiene.py` (runs all lightweight checks)
- `tools/check_doc_metadata.py` (enforces metadata for meta docs)

Last updated: 2026-03-21r359
