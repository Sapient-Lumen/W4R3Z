# Workstation cross-domain data-transfer floor

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Adapter→Shadow→Replace  

`docs/537-workstation-remoted-session-surface-boundary.md` already decided that clipboard, file selection, print, camera/microphone, and similar crossings stay outside the session surface.
This doc makes the next small but expensive cut:
**clipboard and file transfer stay separate brokered lanes, and the baseline workstation floor does not require ambient shared clipboard sync or cross-domain drag&drop.**

See also:
- ADR: `adrs/ADR-0128-workstation-cross-domain-datatransfer-floor.md`
- data-transfer portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`

## Why this needs a hard decision

Once the GUI boundary is host-owned and session-surface-first, cross-domain data movement becomes the next place ambient authority tries to sneak back in.
If the archive does not choose, people will naturally reach for the easiest thing:

- a hidden cross-domain clipboard sync service,
- ambient clipboard/history authority in the trusted host,
- cross-domain drag targets as a day-one expectation,
- or file movement disguised as “paste” and “open” behavior.

That would rebuild exactly the kind of invisible privilege expansion the workstation story is trying to prevent.

## Accepted baseline

For the ordinary workstation lane:

- there is **no ambient shared clipboard** across host/AppVM or AppVM↔AppVM boundaries
- cross-domain clipboard transfer is **explicit, directional, and single-delivery by default**
- the host clipboard is **host-local**; the cross-domain lane uses a separate broker/session/offer path
- ordinary workstation viability requires **bounded text clipboard transfer** plus **explicit file export/import**
- cross-domain drag&drop is **not baseline**
- in other words: **cross-domain drag&drop is not baseline** for the ordinary workstation lane
- clipboard/history-manager authority across compartment boundaries is not baseline and must not hide in the host
- Wayland clipboard-manager protocols remain privileged control surfaces, not baseline client behavior

The mental model should be “send this clipboard payload there,” not “all compartments share one clipboard now.”

## Practical transfer model

### Clipboard text / bounded payloads

The smallest useful ordinary lane is:

- source compartment requests export of text / bounded clipboard payload
- broker creates a typed offer/grant with MIME, size, expiry, and delivery posture
- destination compartment explicitly accepts or retrieves that offer
- broker emits a transfer receipt
- single-delivery grants exhaust by default

That keeps the common “copy a URL / token / snippet” use case workable without creating global shared state.

### Files stay a separate lane

Files should remain explicit export/import acts.
That may still use the same broker family and evidence style, but it is not the same thing as ambient clipboard sharing.

This matters because file authority is usually broader, longer-lived, and more review-sensitive than text transfer.

### Drag&drop is deferred

Bounded cross-domain drag&drop may become useful later.
But the archive should not pretend it is required before the basic workstation lane is coherent.

Cross-domain drag targets are implementation-heavy and easy to turn into hidden ambient data paths.
The baseline should optimize for explicit transfer first.

## Artifact decision: make delivery posture explicit

DeriveBSD already has typed data-transfer artifacts:

- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`

To keep the new floor implementable instead of rhetorical:

- grants must state a typed `delivery_mode`
- the baseline value is `single-delivery`
- receipts should say whether the grant was exhausted after use

That keeps “clipboard clears on delivery” or “multi-delivery exception” out of broker folklore and inside reviewable artifacts.

## What this buys

### 1) No stealth global clipboard

A host-side clipboard manager no longer becomes a stealthy ambient data broker across compartments.

### 2) Better receipts and support surfaces

A support/export surface can answer:

- which compartment offered the data
- which compartment accepted it
- whether it was clipboard text or file transfer
- what MIME and size policy applied
- whether the transfer was single-delivery and exhausted

That is much easier to reason about than “the clipboard happened to contain something at the time.”

### 3) A smaller workstation floor

The ordinary workstation lane only has to solve explicit transfer and explicit file movement.
It does **not** require cross-domain drag targets, cross-domain clipboard history sync, or a fully reconstructed host-native DnD/windowing substrate.

## What is explicitly not baseline

The ordinary workstation lane does **not** require:

- ambient host↔AppVM shared clipboard synchronization
- persistent cross-domain clipboard history as ordinary behavior
- cross-domain drag&drop as a hidden day-one requirement
- host clipboard managers with compartment-spanning privilege by default
- hidden helper daemons that mirror clipboard state between compartments

## Future bounded lane

A future bounded drag&drop or richer clipboard lane may still be useful.
But it should only arrive after an explicit RFC/ADR answers:

- how MIME/size/type policy stays visible,
- how clipboard/history authority stays reviewable,
- how single-delivery defaults are relaxed without recreating ambient state,
- and how receipts remain intelligible in support/export surfaces.

Until then, the archive should optimize for explicit transfer.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/537-workstation-remoted-session-surface-boundary.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`

Last updated: 2026-03-17r269
