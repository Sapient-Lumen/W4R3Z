# Resilio bind-outcome ambiguity, existing-tree merge, and duplicate-branch proof evaluation

## Why this pass exists

`496` through `505` now make AnonSync earlier and clearer than Resilio about **what artifact arrived** and **which destination world it is about to touch**.
What still remained under-owned was the next ordinary question:

> after the world and target tree are chosen, what exact **branch outcome** is the operator about to create here — same-lineage attach, merge into existing bytes, duplicate sibling branch, blocked same-ID collision, or empty-only ciphertext landing?

Current official Resilio docs still show a genuinely flexible product.
They also still show that branch outcome is often reconstructed from several articles instead of one stable reviewed surface.
That is a good reason to adapt rather than clone.

## What current Resilio still gets right

### 1) It really does support pre-populated existing-byte adoption

Current official docs still openly say that two pre-populated folders can be connected.
They also still say that when peers compare trees:

- identical files with identical hashes are not re-synced
- same-path files with different hashes let the latest timestamp win
- other files are merged into the tree and exchanged

That is useful product behavior.
Resilio is not pretending every bind must start empty.

### 2) It still distinguishes linked-device and cross-identity branches

Current docs still say there is a special workflow difference between:

- devices with different identities, where manual key/link claim points at an existing directory
- linked devices, where the destination often wants `Disconnected` posture first or a disconnect/reconnect ritual before the existing directory is chosen

That distinction matters because branch shape is not only about bytes.
It is also about cohort posture and how the target tree was reached.

### 3) It is candid that default auto-land can create duplicate siblings

Current docs still say linked devices in `Selective Sync` or `Synced` mode auto-create arrivals in the default location, and if a same-name folder already exists there the newly created one may gain an added index such as `(1)`.
The repair advice is to disconnect and reconnect the folder to the intended location.

That candor is valuable.
It proves the product knows duplicate-branch accidents are real.

### 4) It still distinguishes same-ID collision from ordinary non-empty reuse

Current docs still say Sync recognizes a share by `.sync/ID`, that the same share cannot be added twice on the same device, and that the error can mean either:

- the same physical folder is already syncing under another artifact
- or the same key/link is already connected through another path on this device

That is useful honesty.
It means `non-empty target` and `same subject already present here` are not the same case.

### 5) It still keeps encrypted custody as an empty-only branch

Current encrypted-folder docs still say encrypted targets should be fresh empty directories.
That means some target trees are not merge candidates at all.
They are blocked unless the operator chooses a fresh ciphertext landing branch.

## Where the current page shape still fails

### 1) Non-empty confirmation still hides several materially different outcomes

Current docs still let one small `folder is not empty` confirmation stand in for too many branch meanings:

- attach to the intended same lineage
- merge divergent existing trees
- accept timestamp-winner overwrite risk
- or proceed in a way that will later look like accidental duplicate repair

Those are not one semantic outcome.

### 2) Duplicate sibling names still become the first proof of the wrong branch

Current docs still explain duplicate `(1)` folders after the fact.
That is support candor, not interface ownership.
The product should classify `this will fork a new sibling branch` before commit, not let the filesystem teach the lesson afterward.

### 3) Same-ID collision still lives in a separate warning article

Current docs still keep the `.sync/ID` uniqueness truth in a dedicated error page.
That means the ordinary answer to `is this target already the same subject somewhere else on this seat?` is still partly troubleshooting knowledge rather than ordinary bind review.

### 4) Empty-only ciphertext rules still sit beside ordinary reuse rules

Current docs still support both ordinary existing-tree reuse and empty-only encrypted landing, but they do not own those branch classes through one shared reviewed grammar.
That makes the operator remember which target chooser is acting like `attach/merge` and which chooser is acting like `fresh ciphertext only`.

## What AnonSync should do instead

AnonSync should keep Resilio's flexibility and replace branch-outcome ambiguity with four ordinary product-owned pages:

1. **Bind outcome review**
   - classify the proposed commit as `attach`, `merge`, `fork`, `blocked-same-id`, or `empty-only-required`
   - keep world choice adjacent to branch consequence

2. **Existing tree evidence**
   - summarize local tree evidence before commitment
   - keep same-ID proof, lineage hints, non-empty shape, and conflict classes visible

3. **Branch consequence compare**
   - compare the current branch against safer alternatives such as `attach to remembered tree`, `fork deliberately`, or `stop and choose empty ciphertext root`

4. **Bind outcome receipt**
   - preserve selected branch class, strongest evidence used, rejected alternatives, and next review handoff

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is worth borrowing for its real support of pre-populated reuse, its honesty about timestamp-winner merge behavior, its candor that same-name duplicates can appear, and its explicit `.sync/ID` uniqueness model. It is not worth cloning the way ordinary branch-outcome truth still leaks across pre-populated-folder guidance, duplicate-folder troubleshooting, same-ID warnings, manual-location notes, and encrypted-folder caveats instead of one stable product-owned page family.

## New replacement pages added in this revision

- `507` Bind outcome review
- `508` Existing tree evidence
- `509` Branch consequence compare
- `510` Bind outcome receipt
