# Workstation richer data-transfer lanes mint distinct artifact families

**Tier:** B (Base contract boundary)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Broker→Lease→Receipt, Quarantine→Promote  

`docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md` already froze the ordinary reviewed workstation transfer lane as the portable baseline, complete enough to implement, and made broader transfer ideas RFC-first.

This doc makes the next small but high-leverage cut explicit:
**future richer workstation transfer lanes must mint distinct artifact families instead of widening or variant-switching the ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt` family.**

See also:
- ADR: `adrs/ADR-0262-workstation-richer-datatransfer-lanes-mint-distinct-artifact-families.md`
- ordinary baseline stop-point: `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- transfer floor: `docs/538-workstation-cross-domain-datatransfer-floor.md`
- portal notes: `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- host/UI boundary: `docs/457-workstation-host-ui-and-appvm-boundary.md`
- anti-laundering boundary: `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- open questions / risk register: `docs/266-open-questions-and-risk-register.md`
- canonical ordinary schemas: `spec/ui.datatransfer.grant.schema.json`, `spec/ui.datatransfer.receipt.schema.json`

## Why this needs a hard decision

Freezing the ordinary lane is not enough if the archive later lets a richer lane sneak back in by saying:

- “it is still `ui.datatransfer.grant`, just with one more mode”
- “it is still `ui.datatransfer.receipt`, just with a broader interpretation”
- or “this profile treats the same artifact family as stronger/broader authority”

That would collapse the clean boundary the archive just paid to build.
Detached support/export would have to rediscover which family of authority a transfer artifact *really* meant from local policy history instead of from the artifact boundary itself.

## Decision

For workstation cross-domain transfer:

- the ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt` family remains the frozen portable baseline
- future richer transfer lanes are still RFC-first
- and those richer lanes must mint **distinct artifact families** rather than widening or variant-switching the ordinary one

Concretely, the archive should **not** treat any of the following as acceptable ordinary-lane evolution:

- a new top-level `transfer_class` or similar discriminator on the ordinary baseline family
- new richer-lane meanings hidden behind profile-specific interpretation of the same artifacts
- successor continuity fields that quietly mean ordinary transfer in some cases and richer transfer in others
- new richer transfer semantics that rely on the ordinary grant/receipt kind strings staying the same

If a richer lane is worth building, it must arrive as a visibly different family with its own schemas, examples, discovery wiring, and RFC/ADR trail.

## Why this is the right stop-point

### 1) Portable evidence stays legible

Support/export tooling can keep reading ordinary `ui.datatransfer.*` artifacts as the boring reviewed-transfer floor instead of performing policy archaeology.

### 2) Future richer lanes stay honest

A richer lane can still justify itself, but it must admit that it is a different authority family instead of “just one more option” on the ordinary baseline.

### 3) Product-shape portability stays intact

A/B/C/D can all share one narrow ordinary reviewed-transfer family while any later richer lane must justify profile/tier fit explicitly.

## Research note

This split matches current mediated-file-access practice in other ecosystems. XDG separates file chooser, long-lived document export, and copy-paste/drag-and-drop file transfer into distinct portal interfaces rather than one ambient or one-size-fits-all file authority surface. Android likewise keeps the Photo Picker’s selected-media lane separate from the broader Storage Access Framework document/provider lane. See the official references in `docs/32-curated-references.md`.

## What remains intentionally open

This doc does **not** choose which richer lane should come first.
It only fixes the intake rule:
if a richer lane is accepted later, it must look like a different artifact family instead of a quiet widening of the ordinary one.

## Related docs

- `docs/205-data-transfer-portals-clipboard-and-dnd.md`
- `docs/410-desktop-viability-checklist.md`
- `docs/457-workstation-host-ui-and-appvm-boundary.md`
- `docs/484-origin-label-authority-and-anti-laundering-boundary.md`
- `docs/538-workstation-cross-domain-datatransfer-floor.md`
- `docs/671-workstation-ordinary-datatransfer-baseline-stays-frozen-and-richer-lanes-are-rfc-first.md`
- `spec/ui.datatransfer.grant.schema.json`
- `spec/ui.datatransfer.receipt.schema.json`

Last updated: 2026-03-22r402
