# ADR-0211: Firmware inventory and mutation evidence detail and export posture by profile

- Status: Accepted
- Date: 2026-03-21

## Context

`docs/471-firmware-update-posture-by-profile.md` already fixed **who gets what default firmware-mutation authority posture** across A–D:

- A keeps firmware mutation policy-gated and maintenance-shaped,
- B keeps apply trusted-UI-visible and consent-first,
- C keeps managed firmware lanes preferred while classic vendor tooling stays explicit adapter territory,
- and D keeps production firmware offline-staged by default.

`docs/321-firmware-updates-and-uefi-variables-as-evidence.md` and `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md` already fixed that the lane is typed and receipted:

- `fw.inventory.receipt` and `fw.inventory.diff` exist,
- `fw.update.plan` / `fw.update.receipt` and `uefi.var.set.plan` / `uefi.var.set.receipt` are official artifacts,
- and staging is not the same as applied success.

But one expensive ambiguity remained:

**what evidence/detail/export posture should firmware inventory and firmware/UEFI mutation normalize in each product shape?**

Without that answer:

- fleets drift toward giant opaque vendor updater logs or invisible background mutation folklore,
- workstations oscillate between “show nothing” and privacy-hostile raw efivar/blob export,
- general-purpose installs inherit whichever helper stack happens to be present,
- and factory/regulatory lanes either overshare raw platform blobs or under-prove what trust roots changed.

That ambiguity is dangerous because firmware posture sits at the join of several already-decided defaults (`firmware_updates`, `platform_provenance`, `evidence`, `evidence_exports`, `high_risk_approvals`) and because the 2026 Secure Boot certificate-refresh pressure turns UEFI trust-root state into an operational question rather than a niche firmware footnote.
This ADR therefore fixes the compilation target **without** inventing a new `product.profiles.defaults` key for firmware evidence or export detail.

## Decision

1. Keep **digest-first inventory** normal across all profiles.
   `fw.inventory.receipt` is routine local evidence, and `fw.inventory.diff` is the routine review surface whenever two inventory states are being compared.

2. Keep **mutation evidence** authoritative and distinct from inventory.
   `fw.update.plan` / `fw.update.receipt` and `uefi.var.set.plan` / `uefi.var.set.receipt` remain the authoritative proof of attempted or applied mutation. Inventory verifies state; it does not replace the mutation receipts.

3. Keep **routine evidence** distinct from **raw side evidence**.
   Raw vendor updater logs, raw efivar blobs, raw Secure Boot databases, and raw capsule payload bytes are stronger side evidence rather than routine baseline export. The ordinary exported truth is summary/digest-first receipts plus joined diffs, not a universal raw-platform dump.

4. Compile the profile-shaped default as follows:
   - **A:** `fw.inventory.receipt` plus `fw.inventory.diff` are routine fleet evidence; `fw.update.receipt` / `uefi.var.set.receipt` are mandatory mutation truth; raw helper logs or efivar dumps stay ticketed stronger attachments rather than default fleet export.
   - **B:** inventory and mutation receipts are routine and should be trusted-UI-visible or at least explainable to the human; Secure Boot / UEFI trust-root changes export as digest-first summaries by default; raw blobs or vendor traces require an explicit stronger share path.
   - **C:** Derive-managed firmware lanes keep inventory/diff/mutation receipts normal, while classic vendor-tool or firmware-helper outputs remain explicit adapter evidence rather than inherited baseline truth.
   - **D:** inventory, diffs, and mutation receipts are retained as deterministic production evidence; routine export stays minimal, redacted, and bundle-oriented, while raw platform blobs remain locally retained or separately approved stronger artifacts.

5. Treat **exported firmware evidence** as the smallest sufficient artifact.
   The normal share/export is the relevant `fw.inventory.receipt`, `fw.inventory.diff`, `fw.update.receipt`, and/or `uefi.var.set.receipt` plus joined approval or platform-report digests needed to explain the act. Raw platform material is opt-in stronger evidence, not the default product truth.

6. Keep **trust-root change proof** stronger than ordinary inventory drift.
   Secure Boot keyset/db/dbx changes must remain visible in digest-first summaries and joined `uefi.var.set.receipt` evidence rather than being flattened into “firmware version changed somewhere.”

## Consequences

- DeriveBSD now has one coherent answer for what normal firmware evidence looks like locally and what it looks like when shared.
- Fleet and factory lanes keep enough proof to answer “what trust roots or firmware changed?” without normalizing raw-platform dump export.
- Workstations keep humane, explainable firmware evidence without turning routine support into efivar archaeology.
- General-purpose compatibility remains possible, but adapter evidence no longer silently redefines the managed baseline.

## What this does not decide

This ADR does **not** decide:

- the final firmware-helper stack (`fwupd`, custom workers, BMC helpers, EFI apps, etc.),
- the exact raw side-evidence attachment taxonomy,
- the exact recipient-acceptance or transport flow for stronger firmware exports,
- retention windows for locally kept raw blobs,
- or the final trusted-UI wording for B.

No new `product.profiles.defaults` key is introduced.
Those remain implementation or follow-on export-contract topics as long as the archive preserves digest-first routine evidence, keeps mutation receipts authoritative, and treats raw platform material as stronger side evidence instead of baseline export.
