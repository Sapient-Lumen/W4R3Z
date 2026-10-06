# ADR-0128: Workstation cross-domain clipboard/file-transfer floor

Date: 2026-03-17
Status: Accepted

## Context

`adrs/ADR-0127-workstation-remoted-session-surface-boundary.md` fixed the GUI floor for profile **B** as a remoted session surface and deliberately kept clipboard, drag&drop, file selection, printing, and similar crossings out of that surface.

One daily-use boundary was still too vague:

- does the workstation lane quietly assume an ambient shared clipboard across host and AppVMs?
- does cross-domain drag&drop become an invisible day-one requirement?
- do clipboard managers/history daemons in the trusted plane quietly become ambient data brokers across compartments?

If DeriveBSD does not choose now, the archive will drift toward the weakest answer: hidden clipboard mirroring, invisible drag targets, and “it probably went through the host somehow” instead of explicit authority and evidence.

Current desktop practice already points in a narrower direction. Wayland intentionally treats clipboard-manager/data-control surfaces as privileged. Portal-style file transfer APIs use explicit session keys and one-off retrieval flows instead of ambient global state. Qubes also keeps inter-qube clipboard handling explicit instead of making all compartments share one clipboard.

We need a small decision that keeps workstation ergonomics plausible without recreating ambient cross-domain state.

## Decision

For profile **B** (secure workstation), the baseline data-transfer floor is now:

1. There is **no ambient shared clipboard** across host/AppVM or AppVM↔AppVM boundaries.
2. Cross-domain clipboard transfer is **explicit, directional, brokered, and single-delivery by default**.
3. Ordinary workstation viability only requires **bounded text clipboard transfer** and **explicit file export/import**. Cross-domain drag&drop is not baseline.
4. The host clipboard remains a **host-local** surface for trusted host UI rather than a global cross-domain namespace.
5. Clipboard-manager/history authority across compartments is **not baseline**.
6. The existing `ui.datatransfer.grant` / `ui.datatransfer.receipt` artifacts are the canonical evidence surface for this lane, and they now carry explicit single-vs-multi delivery posture instead of leaving that as broker folklore.

## Consequences

- The archive no longer treats “clipboard works” as shorthand for shared global clipboard state.
- Profile **B** gets a smaller, reviewable floor: explicit brokered transfer rather than ambient synchronization.
- The trusted plane does not quietly become a cross-domain clipboard-history service.
- Any future richer drag&drop or clipboard-manager lane must arrive as a bounded adapter/RFC, not as hidden convenience plumbing.

## Profile effects

- **A** should usually deny or tightly scope clipboard/file transfer outside maintenance/admin lanes.
- **B** gets explicit brokered text/file transfer with typed evidence and single-delivery default semantics.
- **C** may later offer broader convenience adapters, but that must not redefine the workstation floor.
- **D** should keep data-transfer lanes minimal, auditable, and maintenance-shaped.

## Not decided here

This ADR does **not** decide:

- the exact broker transport or chooser UX,
- whether future bounded drag&drop is worth standardizing,
- whether future cross-domain clipboard history is ever justified,
- or the exact policy syntax for bulkier multi-delivery exceptions.

Those remain later RFC/ADR topics.

## References / wiring

- data-transfer portal model: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- workstation host/AppVM boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- workstation session-surface boundary: `docs/537-workstation-remoted-session-surface-boundary.md`
- new boundary doc: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- desktop viability checklist: `docs/410-desktop-viability-checklist.md`
- evidence objects: `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`
