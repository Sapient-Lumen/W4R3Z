# Firmware inventory and mutation evidence detail and export posture by profile

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** operability, supply-chain, reproducibility  
**Patterns:** Registry→Diff→Gate, Plan→Apply→Receipt  

DeriveBSD already decided that firmware and UEFI mutation are typed, receipted, and profile-shaped.
This doc decides the smaller but expensive follow-on question:
**what evidence detail is normal to keep and share for firmware inventory and firmware/UEFI mutation in each product shape?**

This is intentionally **not** a new product-profile key.
It is the compiled consequence of the existing `firmware_updates`, `platform_provenance`, `evidence`, `evidence_exports`, and `high_risk_approvals` posture surfaces.

See also:
- ADR: `adrs/ADR-0211-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`
- firmware lane: `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`
- support-bundle joins: `docs/631-incident-bundles-carry-fw-update-proof-by-digest.md`, `docs/630-incident-bundles-carry-uefi-var-set-proof-by-digest.md`
- platform provenance lane: `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`
- firmware posture by profile: `docs/471-firmware-update-posture-by-profile.md`
- Secure Boot forcing function: `docs/337-secure-boot-certificate-rotation-and-fleet-trust.md`
- evidence posture: `docs/478-evidence-collection-posture-by-profile.md`
- export posture: `docs/466-export-boundary-posture-by-profile.md`
- high-risk approvals: `docs/474-high-risk-approval-posture-by-profile.md`

## Why this needs a hard decision

Firmware posture without an evidence/detail/export default is a drift engine.
The archive may say firmware mutation is planned and receipted, but implementation pressure still chooses what becomes routine:

- fleet tooling can normalize giant opaque vendor logs or silent helper output as the only “proof,”
- workstation support can bounce between no useful evidence and privacy-hostile raw efivar/blob export,
- general-purpose installs can inherit whichever helper stack happens to run first,
- and factory/regulatory flows can either overshare raw platform material or under-prove trust-root changes.

A coherent archive needs one durable answer to four questions:

- what firmware evidence is routine local truth?
- what stays authoritative when mutation actually occurred?
- when are raw vendor/helper/efivar artifacts only stronger side evidence?
- what is the smallest sufficient artifact allowed to leave the box or organization boundary by default?

## Accepted baseline

Across all profiles:

- `fw.inventory.receipt` is routine local platform evidence,
- `fw.inventory.diff` is the routine review surface whenever two inventory states are being compared,
- `fw.update.plan` → `fw.update.receipt` and `uefi.var.set.plan` → `uefi.var.set.receipt` remain the authoritative mutation lane,
- stage is never the same thing as applied success,
- Secure Boot / UEFI trust-root changes should be summarized and joined through digest-first mutation receipts rather than raw blobs by default,
- raw vendor updater logs, raw efivar blobs, raw Secure Boot databases, and raw capsule payload bytes are stronger side evidence rather than routine baseline export,
- and exported firmware evidence should prefer the smallest artifact that still explains what state existed or what mutation occurred.

That keeps firmware operable and reviewable without letting the lane silently become either invisible helper folklore or a universal raw-platform dump product.

## Product-shape defaults

| Profile | Local recording/detail default | External/share default | Practical meaning |
|---|---|---|---|
| **A fleet_host** | `fw-inventory-receipt-and-diff-routine-mutation-receipts-authoritative-raw-helper-artifacts-ticketed` | `redacted-encrypted-incident-scoped-export` | Fleet hosts keep digest-first inventory and diffs normal, mutation receipts authoritative, and raw helper/efivar artifacts as stronger attachments instead of default fleet export. |
| **B workstation** | `inventory-and-mutation-receipts-routine-trusted-ui-visible-digest-first-trust-root-summaries-no-ambient-raw-blob-export` | `recipient-visible-user-mediated-redacted-sharing` | Workstations keep humane, explainable firmware evidence by default: inventory and mutation receipts are routine, while raw blobs or vendor traces need an explicit stronger share path. |
| **C general_os** | `inventory-diff-and-mutation-receipts-normal-in-managed-lanes-adapter-dumps-explicit` | `explicit-redacted-export` | General-purpose installs keep managed digest-first evidence coherent without pretending every classic vendor tool inherits the full Derive export posture. |
| **D appliance_factory** | `inventory-diff-and-mutation-receipts-retained-offline-raw-platform-material-separately-approved` | `minimal-redacted-bundle-oriented-export` | Factory/regulatory lanes retain deterministic inventory/diff/mutation proof, while raw platform blobs stay locally retained or separately approved rather than becoming routine external evidence. |

These are compiled product-shape defaults, not a new `product.profiles.defaults` key.
They are the default meaning of existing firmware/platform/evidence/export/approval posture surfaces when firmware inventory or mutation is in play.

## What this fixes by profile

### A) Secure fleet host

Default: inventory receipts and diffs are routine; mutation receipts are authoritative; raw helper artifacts are ticketed stronger evidence.

- Fleet firmware posture needs crisp answers to “what version/trust-root state is on this host now?” and “what exactly changed during maintenance?”
- That makes `fw.inventory.receipt` and `fw.inventory.diff` normal, with `fw.update.receipt` / `uefi.var.set.receipt` as the mandatory mutation truth.
- Raw updater JSON, helper stderr, or efivar dumps may still matter for hard incidents, but they should not become the default exported fleet story.
- External sharing therefore stays incident-scoped, encrypted, and redacted by default.

### B) Secure workstation

Default: inventory and mutation receipts are routine and human-explainable; trust-root changes export as digest-first summaries; no ambient raw-blob export.

- Workstations are where firmware evidence most easily drifts into either total opacity or privacy-hostile support exports.
- The archive still needs proof that firmware state and trust-root changes were made visible and explainable to the person holding the device.
- So B keeps digest-first inventory and mutation receipts as the normal lane, keeps Secure Boot / UEFI trust-root changes summary-first by default, and treats raw blobs or helper traces as an explicit stronger share path.
- Sharing remains recipient-visible, user-mediated, and redaction-aware.

### C) General-purpose OS

Default: inventory/diff/mutation receipts are normal in managed lanes; adapter dumps stay explicit.

- C needs coherent firmware evidence without pretending one helper stack or firmware service owns the whole machine.
- Derive-managed firmware flows should still leave useful inventory, diff, and mutation receipts.
- Classic vendor utilities or helper-specific traces remain explicit adapter evidence, not ambient baseline truth.
- Export stays explicit and redacted rather than “the updater uploads whatever it wrote somewhere.”

### D) Appliance factory / regulatory

Default: inventory, diffs, and mutation receipts are retained as deterministic production evidence; raw platform blobs are separately approved stronger artifacts.

- D often needs durable proof of approved firmware state and trust-root mutation more than it needs expansive raw platform export.
- Typed inventory/diff/mutation evidence therefore remains routine and retained.
- Raw capsule bytes, helper traces, or efivar dumps may still be kept locally or under separate approval, but they are not the default external production artifact.
- Export remains minimal, redacted, and bundle-oriented.

## Cross-profile invariants

Regardless of profile:

- `fw.inventory.receipt` is normal local evidence,
- `fw.inventory.diff` is the preferred review surface for firmware/platform drift,
- `fw.update.receipt` and `uefi.var.set.receipt` are the authoritative mutation proof,
- inventory does not replace mutation receipts,
- raw platform material must not be smuggled into routine support or fleet export paths as the default “proof,”
- and trust-root changes must remain visible as digest-first summaries and joined mutation evidence.
- official support handoff now uses `fw_inventory_diff_digest` for reviewed firmware/platform drift proof instead of treating screenshots or dashboard comparisons as the routine export truth.
- official support handoff now uses `fw_update_receipt_digests` for exact firmware-update proof instead of treating updater dashboards or helper stdout as the routine export truth.
- official support handoff now uses `uefi_var_set_receipt_digests` for UEFI-variable mutation proof instead of treating raw efivar dumps or helper stdout as the routine export truth.

## What remains open

This doc does **not** freeze:

- exact raw side-evidence attachment kinds,
- exact retention windows for raw platform material,
- exact transport/recipient-acceptance rules for stronger firmware exports,
- the final helper stack,
- or the final trusted-UI wording on B.

Those are future implementation/spec questions.
The product-shaped default for firmware evidence/detail/export is the hard part worth locking now.

## Why this is worth locking now

This is a coherence move, not a new subsystem.
It keeps DeriveBSD viable across all four product shapes without forcing fleet maintenance, workstation support, general-purpose compatibility, and factory/regulatory audit to choose between invisible firmware folklore and universal raw-platform export.

Last updated: 2026-03-21r362