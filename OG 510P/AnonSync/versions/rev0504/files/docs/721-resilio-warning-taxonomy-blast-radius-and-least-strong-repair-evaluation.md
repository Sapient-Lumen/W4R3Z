# Resilio warning taxonomy, blast radius, and least-strong repair evaluation

## Why this seam matters

Another current official Resilio pass exposes a stronger non-clone reason than a generic `good troubleshooting docs` compliment.
Current official docs are actually fairly candid that a visible warning row is not one thing.
The current `Core warnings` article still separates tracker loss, low space on the default-folder-location disk, failed folder-list / identity sync, and license-management disablement.
The current `Service files missing / Cannot identify destination folder` article still says synchronization for that folder is suspended and that one repair path is remove/re-add after checking Archive and deleting `.sync`.
The current `Some internal tasks are taking time to complete` article still says the condition can be intermittent and recoverable rather than a hard stall.
The current `Time difference` article still says chronology trust is invalidated when peer clocks or timezone settings are wrong and that mobile devices may show only empty lists.
The current `Cannot download files` article still says a mesh may advertise files that later no peer still holds as full bytes.
The live Sync v3 line still runs through `3.1.2.1076`.

That candor is useful.
The non-clone problem is still warning ownership.
One ordinary operator answer is still reconstructed too late:

> **what kind of warning is this, how wide is it, what is the least-strong honest next rung, and what did acknowledging it actually change?**

## What current official docs still say

### 1) Resilio already distinguishes materially different warning classes

The current warning cluster already describes warnings with very different semantics:

- **recoverable hidden work** — `Some internal tasks are taking time to complete`
- **continuity damage** — `Service files missing`
- **chronology invalidation** — `Time difference`
- **source absence / ghost announcement** — `Cannot download files`
- **infrastructure / storage / identity-management conditions** — `Core warnings`

So the warning surface is already a taxonomy, even if the product does not compile it into one ordinary operator page family.

### 2) The blast radius changes by warning, but support prose still carries that answer

Current docs still imply very different scopes:

- `Service files missing` suspends synchronization **for that folder**
- `Time difference` invalidates chronology-sensitive comparison across peers and can empty mobile file lists
- `Cannot download files` is often a **subject/item-level** no-source problem rather than a full-seat failure
- `Some internal tasks...` can be **seat/resource pressure** without proving subject corruption
- `Core warnings` can describe account/identity sync trouble, tracker/bootstrap trouble, or storage-floor trouble

The operator still has to infer whether the current problem is item-scoped, subject-scoped, seat-scoped, or broader control-state damage.

### 3) The safest next rung is not the same across warnings

The current docs still imply very different least-strong actions:

- wait / observe for recoverable hidden work
- verify clocks for chronology invalidation
- restore a full source or accept absence for ghost-announced files
- disconnect/reconnect or remove/re-add for some local database or spine failures
- inspect identity/bootstrap/storage conditions for core warnings

That means a generic `Fix`, `Retry`, or `Dismiss` verb is too weakly typed.

### 4) Acknowledgement and repair residue still lack one durable product record

Current official docs still make it easy for an operator to remember only that a warning `went away`, not whether it:

- self-cleared after transient resource pressure
- was acknowledged without semantic repair
- required chronology repair
- required continuity reset
- still leaves residue or a claim ceiling afterward

## Why AnonSync should not clone this contract

AnonSync should borrow Resilio's candor that warning classes differ and that some warnings are recoverable while others are continuity-bearing.

AnonSync should **not** clone a contract where:

- one warning row does not publish its class and blast radius explicitly
- the least-strong safe next rung must be learned from scattered help pages
- acknowledgement can be mistaken for repair
- operators cannot reopen one durable record of what the warning meant, what changed, and what stronger sentence is still blocked

The product should instead own four ordinary surfaces:

1. **Warning page** — class, scope, safe sentence, and current seriousness
2. **Blocker scope** — seat / subject / item / hidden-state blast radius and unaffected neighbors
3. **Recovery rung** — least-widening repair ladder and escalation boundary
4. **Warning history** — acknowledgement, recurrence, residue, and proof continuity

## Tightened conclusion

Borrow Resilio's warning candor.
Do not clone a product contract where the operator still has to merge core-warning rows, one-off warning articles, and troubleshooting lore just to answer:

> **what kind of warning is this, how wide is it, what is the least-strong honest next move, and what did clearing it actually prove?**
