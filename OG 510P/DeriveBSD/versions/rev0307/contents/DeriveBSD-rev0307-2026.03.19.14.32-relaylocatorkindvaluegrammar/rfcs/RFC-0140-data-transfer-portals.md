# RFC-0140: Data transfer portals (clipboard / drag&drop)

Status: **Draft**  
Last updated: 2026-02-24

## Problem

Clipboard and drag&drop are cross-app channels.

If they are ambient, you get:
- silent exfiltration (clipboard sniffing)
- “clipboard manager” privilege escalation paths
- inability to apply deterministic redaction for sharable artifacts

DeriveBSD needs a first-class **capability-mediated data transfer** primitive.

## Proposal

Add an optional *DataTransfer portal* lane:

- a host broker issues leased handles for:
  - read clipboard (paste)
  - write clipboard (copy)
  - drag&drop offers (gesture-bound)
- grants can carry constraints:
  - MIME types, size limits, TTL
  - optional `redaction.transform` digest binding
- optionally emit `ui.datatransfer.receipt` evidence for auditing

This is aligned with the existing portal model (`docs/179`) and redaction evidence (`docs/195`).

## Spec objects

- `ui.datatransfer.grant`
- `ui.datatransfer.receipt`

See: `docs/205-data-transfer-portals-clipboard-and-dnd.md`.

## Open questions

- UX for “clipboard manager” role and explicit consent
- how to represent “foreground focus” constraints in non-GUI contexts
- interop mapping to Wayland/XDG portal APIs for desktop environments
