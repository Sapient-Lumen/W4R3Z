# ADR-0314: Removable-media local fallback first cut keeps mount authority host-controlled and the ingest lane disposable-jail-shaped

- Status: Accepted
- Date: 2026-03-26

## Context

`adrs/ADR-0313-removable-media-local-fallback-stays-storage-only-session-scoped-and-quarantine-first.md` already fixed the first dangerous ambiguity on imperfect B/C hardware:
the local fallback is storage-only, session-scoped, read-only-first, and quarantine-first instead of generic USB convenience.

That still left one implementation seam open:

> what should the *first buildable execution boundary* be for that fallback?

Leaving that vague keeps several costly choices unresolved at once:

- implementation work cannot tell whether to hand raw block-device nodes into a jail, build a microVM prerequisite before any fallback exists, or keep mount authority on the host,
- the archive risks quietly treating a jail as if it were equivalent to a device domain or microVM for filesystem-parser isolation,
- and docs can drift back into hand-wavy "the ingest lane mounts the device somehow" language that is too fuzzy to spec or code.

The archive already has enough existing pieces to choose a smaller first cut without inventing a new subsystem:

- `device.attach.*` already models the explicit storage session,
- `mount.view` already models a compiled read-only tree presented to a compartment,
- `devfs.view.plan` already models the minimal `/dev` view inside a jail,
- `content.import.plan` already models no-network disposable import work,
- and the archive already treats jails as an acceptable fallback for host-adjacent or early implementation lanes while stronger microVM/device-domain lanes remain preferred.

## Decision

1. **The first host-local removable-media fallback keeps attach and mount authority on the host.**
   The host performs the explicit read-only-first storage attach/mount steps and emits the `device.attach.*` / `device.detach.*` evidence.

2. **The first disposable ingest compartment is a no-network jail.**
   The initial implementation target for the imperfect-hardware fallback is a disposable jail, not a microVM prerequisite.

3. **The ingest jail receives a read-only mounted tree, not raw block device nodes.**
   The mounted removable-media tree is projected into the jail via `mount.view`, while `devfs.view.plan` stays minimal and block-empty for this lane.

4. **This is an implementation floor, not a claim that a jail equals a device domain or microVM.**
   Stronger controller-isolated device domains, microVM-based ingest lanes, or dedicated ingest stations remain preferred where available.
   This ADR only fixes the first implementable compatibility floor for imperfect B/C hardware.

5. **The canonical first-cut example stack is now explicit:**
   - `spec/examples/device.attach.grant.removable-media-local-ingest.json`
   - `spec/examples/devfs.view.plan.removable-media-local-ingest.json`
   - `spec/examples/mount.view.removable-media-local-ingest.json`
   - `spec/examples/content.import.plan.removable-media-local-ingest.json`

## Consequences

- The archive now has a finite first spec target for local removable-media fallback instead of three competing half-stories.
- Implementation work can start with explicit host-controlled attach/mount, a disposable no-network jail, and typed plan/receipt joins.
- The ingest jail no longer needs raw block-device authority in the first cut, which keeps the fallback narrower and easier to review.
- The archive stays honest that this does **not** solve filesystem-parser kernel risk the way a device domain or microVM can; it is a compatibility floor, not the strongest lane.

## What this ADR intentionally does not decide

This ADR does **not** settle:

- the final filesystem whitelist or per-format support matrix for the first cut,
- whether later B/C implementations should prefer a microVM-backed ingest lane when practical,
- exact trusted-UI prompt wording,
- or remembered approval posture beyond the already accepted session-scoped floor.

Those remain narrower follow-on decisions.
