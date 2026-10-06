# Printing portal as capability grants (print without ambient access)

Printing is deceptively powerful:
- it can exfiltrate data off-device
- it can reveal document names and metadata
- it is often implemented with ambient access to a spooler or device

A greenfield OS should model printing as a portal:
- broker mediates settings and destination selection
- the app receives a **print capability**, not spooler-wide access
- job submission is **receipted** and can be audited

## Lessons to steal

- XDG Desktop Portal **Print**: apps call PreparePrint (settings), then Print (submit).  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Print.html

## Proposal (DeriveBSD)

### 1) Prepare phase (interactive)
App requests printing with:
- document metadata (title optional, can be redacted)
- supported page setup / duplex / color capabilities

Broker returns `ui.print.grant` containing:
- chosen destination profile (printer / PDF export / remote queue)
- settings bundle digest (canonicalized)
- optional “remember” binding in portal.permission.grant

### 2) Print phase (submit)
App submits a document payload (or an artifact digest) to the broker under the grant:
- the broker spools on the app’s behalf
- the app never gains ambient access to the spooler

### 3) Receipts
Broker emits `ui.print.receipt`:
- job id (local)
- destination class (local printer / file / remote)
- bytes submitted (optional; policy-controlled)
- redaction transform digest if applied (see `docs/195-deterministic-redaction-transforms.md`)

## Schemas

- `spec/ui.print.grant.schema.json`
- `spec/ui.print.receipt.schema.json`

## Integration points

- Portal conventions: `docs/210-portal-sessions-and-permission-store.md`
- Redaction: `docs/195-deterministic-redaction-transforms.md`
- File chooser + bookmarks for “export to PDF”: `docs/198-persistent-file-capabilities-bookmarks.md`
