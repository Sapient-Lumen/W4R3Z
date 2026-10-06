# Origin labels + quarantine attributes ("where did this file come from?")

Modern systems already *try* to solve this:
- macOS uses quarantine xattrs (`com.apple.quarantine`) to trigger Gatekeeper checks.
- Windows attaches “Mark-of-the-Web” metadata (Zone.Identifier) to downloaded files.

DeriveBSD can do better because we control the whole pipeline and already treat **evidence as a first-class artifact**.

## Problem
Without a groundfloor mechanism, ecosystems regress to:
- “mystery bytes”: a file arrives and you cannot reliably answer **who/what introduced it**.
- ad-hoc warnings (or none) when opening untrusted formats.
- metadata stripping (zip/unzip/copy) that silently drops provenance.

## Goals
- Make origin/provenance **visible and stable**:
  - “this file originated from USB device X in quarantine domain Q”
  - “this PDF was downloaded via fetch domain F from URL U at time T”
- Make “open safely” the **default path**, not an app-specific feature.
- Ensure the label survives common workflows (copy, unzip, export/import) via **portalized I/O**.
- Make everything **policy-addressable and receipted**.

## Core objects

### 1) `content.origin` (evidence record)
A content-addressed record binding a file digest to a capture context.

Typical sources:
- `usb` (removable media via USB quarantine domain)
- `download` (fetch domain; browser/download-manager)
- `attachment` (mail/chat attachments)
- `share` (inter-domain data-transfer portal)
- `scanner` (document scanner / camera import)
- `manual` (operator asserted; should be rare)

Schema: `spec/content.origin.schema.json`.

### 2) `content.import.plan` and `content.import.receipt`
A uniform two-phase “ingest” API:
- plan = what you intend to do to the bytes before they become “normal files”
- receipt = what actually happened, with digests for all intermediate outputs

Schema: `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`.

### 3) Quarantine attribute
A file-local label (xattr/metadata) that points at an origin record (digest/id).

On BSD this is implementable with extended attributes (e.g. `extattr(2)`), or a ZFS xattr/SA-backed policy.

## System behavior (the “happy path”)

### Inbound surfaces all become “imports”
- USB mounts happen in a **quarantine domain**; bytes are pulled into the trusted domain only via `derive import …` (see `docs/279-usb-quarantine-and-removable-media-workflow.md`).
- Downloads are written into an Imports area with quarantine attribute + origin record (see `docs/201-network-egress-as-capability.md`).
- Data-transfer (clipboard / drag&drop / file share) emits an origin chain and import receipt (see `docs/205-data-transfer-portals-clipboard-and-dnd.md`).

### Opening quarantined content is mediated
Default: quarantined content is not opened “raw” by apps.
Instead:
1) the opener requests `portal.open` or `derive open`
2) policy decides:
   - sanitize first (`docs/267-sanitization-portal-and-disposable-sandboxes.md`)
   - allow direct open with explicit user acknowledgement
   - deny
3) a `content.import.receipt` is emitted (even for deny), so the system can explain why.

### Copy/unzip/export do not strip provenance
DeriveBSD should strongly bias toward portalized file moves:
- `derive cp` / file-manager copy uses a “copy portal” that preserves quarantine/origin labels.
- Archive extraction defaults to a disposable sandbox; each extracted file gets a derived origin chain (parent digest + entry path).
- Export flows may redact or drop labels only under explicit `export.policy` (see `docs/251-export-policies-and-support-bundle-portal.md`).

## Policy hooks
- Promise profile vocabulary should allow/deny:
  - `content.open.quarantined` (almost always denied)
  - `content.import` (allowed for import/sanitize tools)
- Policy can enforce “must sanitize” for certain MIME types and certain origins.
- Incident bundles should include:
  - origin records for recently imported items
  - the last N import receipts

## Failure modes to design against
- **Attribute stripping:** SMB/NFS/zip tools dropping xattrs → must be countered by portalized transfers and derived receipts.
- **Origin laundering:** apps writing a copy of content without carrying origin → default-deny direct write access to trusted areas; require “publish portal”.
- **Over-warning fatigue:** keep the default safe path (sanitize) fast and predictable.

## See also
- Sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`
- USB quarantine workflow: `docs/279-usb-quarantine-and-removable-media-workflow.md`
- Data-transfer portals: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- Export policy: `docs/251-export-policies-and-support-bundle-portal.md`
