# Data transfer portals (clipboard / drag&drop) as capability grants

Clipboard and drag&drop are *cross-app data channels*.
If they are ambient, sandboxing collapses.

Historically:
- on **X11**, any client on a display can read the clipboard (and worse, log keys)
- on **Wayland**, clipboard access is restricted to foreground apps; clipboard managers require privileged protocols and explicit consent

DeriveBSD should treat “copy/paste” as a **portal-shaped capability acquisition**.

## Lessons to steal

- **XDG Desktop Portals** define a Clipboard portal interface for sandboxed apps:
  - apps request clipboard access for a session
  - the host broker mediates what is allowed  
  Reference: https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.Clipboard.html

- Wayland compositors intentionally restrict clipboard access; “data-control” protocols for clipboard managers are privileged and should be opt-in.  
  Reference: https://wayland.app/protocols/wlr-data-control-unstable-v1

## Model

### 1) A DataTransfer broker issues scoped handles

A host-side `derive-datatransferd` broker (name placeholder):

- issues **leased** handles for:
  - read clipboard (paste)
  - write clipboard (copy)
  - drag&drop offers (explicit user gesture)
- enforces constraints:
  - MIME types
  - max bytes / rate limits
  - time-to-live
  - optional redaction transform profile

### 2) Redaction and privacy are first-class

Clipboard is a common exfil channel.
If DeriveBSD is going to produce sharable artifacts (capsules, receipts), it should also be able to produce sharable clipboard transfers.

Integrate:
- deterministic redaction transforms: `docs/195-deterministic-redaction-transforms.md`
- portal consent receipts: `docs/185-portal-consent-and-audit-receipts.md`

### 3) Shape this as “data offers”, not “global state”

Rather than a single global clipboard, model clipboard entries as **offers**:

- a producer creates an offer with constraints
- a consumer obtains a read handle to a specific offer via the broker
- offers expire (or are revoked) by default

This matches the “authority is explicit” philosophy and makes auditing easier.

## Evidence objects

- `ui.datatransfer.grant` — leased grant to read/write an offer (or create an offer)
- `ui.datatransfer.receipt` — record that a transfer occurred under a grant (optional policy knob)

Schemas:
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`

## Practical ergonomics (so people actually use it)

- provide a tiny `derive-clip` tool that speaks to the broker for terminal apps (like `wl-copy` / `wl-paste`)
- allow a “clipboard manager” role via explicit policy + visible consent, rather than hidden privileged protocols
- attach redaction transforms by digest to grants (“this paste path always strips tokens”)

See also:
- portals/powerbox: `docs/179-portals-and-powerbox.md`
- intent routing (“open/share” can be implemented via offers): `docs/199-intent-routing-and-plumbing.md`
- origin labels + quarantine attributes (for file-offers/import flows): `docs/280-origin-labels-and-quarantine-attributes.md`
