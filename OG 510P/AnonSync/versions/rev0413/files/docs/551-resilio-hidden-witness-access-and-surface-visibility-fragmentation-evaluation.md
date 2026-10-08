# Resilio hidden witness access, surface visibility, and proof-presentness evaluation

## Why this pass exists

The archive already had locality, horizon, cleanup, and preservation pages.
What it still did not own tightly enough was the ordinary operator question that survives all of those:

- does the witness still exist
- can I actually inspect it from **this** surface
- is it merely hidden, or truly inaccessible here
- do I need a different seat, a file browser, or a different workflow before I can safely claim recovery is still available

Current official Resilio docs still make that seam very real.
They are candid that Archive exists, that it lives in hidden `.sync/Archive`, that desktop UI and file-browser access are not the same thing, that WebUI still relies on file-browser access to the hidden path, and that iOS does not provide Archive access at all.
They are also candid that `.sync` is critical state and that uninstall can leave previously shared folders and hidden archived files behind.

That honesty is useful.
The problem is that the product still leaves one everyday answer too article-shaped:

> `does the witness exist here, and can I actually reach it from the surface I am standing on right now?`

## What current Resilio still gets right

Current official docs still publish several truths that are operationally valuable.

- **Archive is described as a real witness, not a vague magic undo.** Current `Using Archive for file versioning and restoring deleted files` docs still say old or deleted copies are moved to Archive on other peers connected to the share, manual restore is required, and History is still needed to learn which peer made the change.
- **Surface access is not falsely flattened.** Those same docs still say desktop users can open Archive from Sync UI, Android and WebUI rely on file-browser access to hidden `.sync/Archive`, and Archive is not available for access on iOS.
- **Hidden witness location is stated plainly.** Current `.sync` docs still say every synced folder receives a hidden `.sync` folder by default, and that Archive lives inside it together with the share identifier and other service files.
- **Critical hidden state is called critical.** The same docs still say deleting `.sync` causes `Service files missing`, and `.sync` should not be moved separately from the shared folder.
- **Uninstall is not misrepresented as evidence cleanup.** Current uninstall docs still say desktop uninstall removes the program but not previously shared folders, while Mac guidance explicitly warns that hidden `.sync/Archive` may remain and should be removed manually if the operator wants it gone.
- **The current v3 line is still live.** Official docs still show the v3 line through `3.1.2.1076` dated 31/Oct/2025.

That is strong candor.
Resilio is still willing to admit that evidence can exist, remain hidden, survive app removal, and yet still not be equally reachable from every surface.

## Where current Resilio still stays too article-shaped

### 1. Existence and inspectability are still separate memories

The ordinary operator does not only need to know that a witness exists somewhere.
They need to know whether:

- it is inspectable from the current seat
- it is inspectable from the current UI surface
- the next step is `open here`, `switch surface`, `switch seat`, or `admit this surface cannot show it`

Current Resilio still exposes those truths across Archive, `.sync`, uninstall, and troubleshooting docs rather than one reviewed visibility contract.

### 2. Hidden-state access still arrives as filesystem trivia

Current docs are candid that `.sync` is hidden and critical.
But that still leaves operators reconstructing one practical answer from filesystem literacy:

- where the witness really lives
- whether the product can open it directly
- whether WebUI can actually show it
- whether iOS can only talk *about* recovery rather than inspect the witness itself

AnonSync should not make hidden-path literacy the main way recovery evidence becomes real.

### 3. Post-cleanup proof can still exist without current-surface reach

Current official docs now clearly imply a distinction that deserves its own product-owned page family:

- witness exists
- witness survives
- witness is reachable from this surface
- witness is reachable only from another seat or lower-level tool

That distinction matters because cleanup, uninstall, and restore language becomes misleading if `exists somewhere` silently substitutes for `you can inspect and act on it here`.

## What AnonSync should do instead

AnonSync should separate **proof existence** from **proof inspectability** and make that visible before strong recovery or deletion language appears.

The product should own four page families:

1. **Evidence visibility review**
   - current seat, current surface, and current witness classes
   - visible now versus hidden but reachable versus off-surface versus unavailable here
   - strongest safe current sentence

2. **Hidden witness surfacing**
   - safe open ladder for Archive, service-state, hidden-path, and residual local witness
   - exact risk if the surfacing step itself can weaken or destroy proof

3. **Surface handoff**
   - when the current surface cannot inspect the witness directly
   - best next host or next surface
   - what can still be claimed before the handoff completes

4. **Evidence access receipt**
   - what was visible now
   - what still exists but remained hidden
   - which surface was chosen for deeper inspection
   - stronger forbidden claims such as `recoverable here` when only `recoverable elsewhere` is proved

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that Archive and hidden service state are real and sometimes survive cleanup or uninstall. But it is not worth cloning the way current operators still have to infer whether proof is actually inspectable from the surface they are using, or only exists in hidden paths, on another seat, or not on iOS at all.

## New replacement pages added in this revision

- `552` Evidence visibility review
- `553` Hidden witness surfacing
- `554` Surface handoff
- `555` Evidence access receipt
