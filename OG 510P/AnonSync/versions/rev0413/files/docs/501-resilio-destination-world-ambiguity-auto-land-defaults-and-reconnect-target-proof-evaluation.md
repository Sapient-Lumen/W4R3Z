# Resilio destination-world ambiguity, auto-land defaults, and reconnect-target proof evaluation

## Why this pass exists

The archive already has strong doctrine for standing arrival templates, existing-bytes review, reconnect repair, encrypted custody, and typed intake routing.
What still remained under-explained was the seam between them:

> after the artifact family is known, how clearly does the product tell the operator **which destination world** is about to receive it, whether that world will auto-land bytes by default, and whether a later reconnect/manual bind is actually continuity repair or the start of a duplicate branch?

Current official Resilio docs still show a genuinely useful product.
They also still show that materially different destination outcomes are still governed by a small cluster of mode, default-root, reconnect, and mobile caveats that often live in separate help articles.

That is a good reason to adapt rather than clone.

## What current Resilio still gets right

### 1) It treats arrival posture as a real configuration surface

Current official docs still make clear that linked devices have three different synchronization modes:

- **Disconnected**
- **Selective Sync**
- **Synced**

That is good product honesty.
These are real destination postures, not cosmetic preferences.

### 2) It still admits that destination path choice and destination automation are different things

Current docs still say that:

- linking devices suggests a default folder location and a synchronization mode
- Disconnected mode delays byte movement and asks the operator where to put the folder when they later connect it
- Selective Sync or Synced modes automatically place new arrivals in the default storage location

That distinction matters.
It is a real product contract about where bytes will land and how much review the operator gets first.

### 3) It still openly supports intended continuation of pre-existing local bytes

Current docs still say that the operator can point an arriving folder at an already-existing directory.
They also still say that linked-device reuse works best when the destination seat is put in Disconnected mode first, or when an automatically-arrived folder is disconnected and then reconnected to the intended existing directory.

That is useful.
Resilio is not forcing needless re-download in every case.

### 4) It is candid about duplicate and encrypted-custody edge cases

Current docs still say that:

- reconnect can propose a default path different from the original path
- a same-name folder may then be created with an added index such as `(1)`
- Android may need `Simple mode` disabled to let the operator choose a location manually
- encrypted custody on linked devices should use `Disconnected` posture and a fresh empty target directory

That candor is valuable.
It proves the product knows destination-world mistakes are real.

## Where the current page shape still fails

### 1) Destination world is still inferred from mode and article memory

The operator still has to reconstruct whether this arrival is headed toward:

- an announce-only world
- a default-auto-land world
- a remembered continuity world
- an operator-picked manual world
- or an encrypted-custody world that must reject ordinary non-empty reuse

Current docs expose all those branches.
But the product still does not give them one typed **destination-world** verdict before commitment.

### 2) Auto-land and intended continuation still sit too close together

Current docs still make it possible for an arrival to auto-land into the default root when the operator really intended to rebind the arrival to an existing directory.
The help center explains how to repair that.
But the ordinary interface answer to `did this land in the right world, or just the default world?` is still too dependent on help-article ritual.

### 3) Reconnect truth still hides behind duplicate fallback

Current docs still say reconnect may draft a different default path and create a `(1)` sibling when a same-name folder already exists.
That is candid, but it still leaves too much product meaning in side effects.
A duplicated same-name directory is not an honest semantic category.
It is evidence that the interface failed to keep continuity-world choice explicit enough.

### 4) Encrypted custody introduces one more incompatible destination branch

Current docs still say encrypted custody on linked devices wants `Disconnected` posture and a fresh empty directory, while ordinary reuse flows may intentionally point at non-empty pre-existing bytes.
That means not every destination world is interchangeable.
The product should therefore classify destination-world type earlier than a generic folder chooser does.

## What AnonSync should do instead

AnonSync should preserve Resilio's useful flexibility and replace destination-world ambiguity with four ordinary product-owned pages:

1. **Destination world picker**
   - classify every admissible destination world before commitment
   - keep mode, default-root, remembered-root, and custody branch adjacent
   - make `auto-land` a reviewed consequence, not a surprise

2. **Destination world card**
   - summarize one world's posture, root history, bind rights, and strongest warnings
   - make ordinary workbench rows honest enough to compare

3. **Arrival reroute review**
   - handle `stop default auto-land and redirect this arrival` as a first-class move
   - make duplicate avoidance, remembered-root reuse, and manual bind intent explicit

4. **Destination commit receipt**
   - preserve which world was chosen, which route was rejected, what path intent was reviewed, and which deeper bind page followed

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is worth borrowing for its real arrival modes, its support for pre-existing-byte reuse, and its candor that reconnects, default roots, mobile simplifications, and encrypted custody materially change where bytes can land. It is not worth cloning the way ordinary destination-world truth still leaks across synchronization-mode docs, duplicate-folder troubleshooting, reconnect guidance, Android `Simple mode` exceptions, and encrypted-folder caveats instead of one stable product-owned page family.

## New replacement pages added in this revision

- `502` Destination world picker
- `503` Destination world card
- `504` Arrival reroute review
- `505` Destination commit receipt
