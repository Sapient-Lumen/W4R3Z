# Resilio same-host instance namespace and overlap admission evaluation

## Why this pass exists

The archive already had runtime profile, control-surface grade, policy provenance, hidden-spine integrity, and same-host multi-instance interface sketches.
What it still did not own cleanly enough was one ordinary operator question that sits underneath many of those pages:

- am I reopening the same seat or launching a sibling runtime
- which storage root is actually authoritative right now
- does this browser/control surface belong to the runtime I think it does
- will this launch preserve the same identity, shares, and logs or start clean
- if I point this runtime at that folder, is it a safe reopen, a safe sibling namespace, or a continuity-corrupting overlap

Current official Resilio docs still make that seam materially real.
They still say Linux may run multiple instances, but later instances need manual transmission/reception ports.
They still say CLI and config launches can define storage explicitly, and that without an explicit storage root a local `.sync` storage directory is created from the current launch context.
They still say service-account changes on Windows can surface a different storage root and therefore a different visible share roster.
They still say a v3 update with non-default `/config` or `/storage` usage must relaunch with the same parameters and the same user if the operator wants configuration preserved.
And they still say that running two instances on the same computer against the same folder can corrupt continuity-bearing hidden state and suspend synchronization.

That candor is useful.
The problem is that the ordinary answer still depends on article memory.

## What current Resilio still gets right

Current official docs still publish several truths worth borrowing.

- **Same-host multiple runtimes are admitted as real.** Current Linux docs still say multiple instances are possible and later instances need manually separated data ports.
- **Storage root is treated as materially real.** Current Linux, Windows CLI, config-mode, and storage-folder docs still say the storage directory holds settings, identity details, databases, and logs.
- **Launch parameters are not disguised as cosmetic.** Current CLI and config docs still expose `/config`, `/storage`, `--config`, `--storage`, and `storage_path` as namespace-defining choices.
- **Service-account shifts are candidly shown as storage-world shifts.** Current service and troubleshooting docs still show that Local System / Local Service / current-user service variants can surface different storage roots and therefore different visible state.
- **Continuity damage is admitted when overlap occurs.** Current `Service files missing` guidance still says two instances on the same computer, or external storage reused by two instances, can corrupt hidden service files and force a remove/re-add lane.
- **Subject duplication on one device is not hand-waved away.** Current `Selected folder is already added` guidance still says only one folder with the same `.sync/ID` can exist on a device.
- **The current v3 line is still live.** Official docs still show the v3 line through `3.1.2.1076` dated 31/Oct/2025.

That is good candor.
Resilio still admits that `same host` is not one flat runtime story.

## Where current Resilio still stays too article-shaped

### 1. Namespace identity still depends on operator archaeology

The ordinary operator should not have to reconstruct from several articles whether the active runtime namespace is determined by:

- current-user default storage
- explicit `/storage` or `--storage`
- config-owned `storage_path`
- service storage for a specific account
- clean service install versus migrated install
- replacement of a binary launched later with the same or different parameters

Yet current official docs still spread those pieces across Linux, CLI, config-mode, service, storage-folder, and update articles.

### 2. A new control surface can still look like continuity even when it is sibling state

Current official docs still admit that a service/account switch or clean service install can open WebUI with no old shares visible because a different storage root is active.
That is materially different from `same seat reopened`.
But the current explanation still lives mostly in admin/troubleshooting text rather than one workflow-owned page that makes the new namespace explicit before the operator keeps going.

### 3. Overlap damage still appears too late in the story

Current official docs still explain overlap damage mainly in repair language: if two instances touch the same folder, hidden service files can be corrupted and synchronization suspended.
That is honest.
But it is still too late.
The product contract should prevent the overlap from looking like a plausible attach in the first place.

### 4. State-preservation promises still depend on parameter discipline the product does not own

Current official update guidance still says non-default launches should preserve the same user and same parameters if the operator wants existing configuration preserved.
That is sensible.
But it means `updating Sync` is not one honest verb by itself.
The real question is whether the next runtime still points at the same namespace.

### 5. Subject attach safety is still not one reviewed host-local decision

Current official docs still separately explain:

- one ID cannot exist twice on the same device
- same-folder overlap can corrupt `.sync`
- `.sync` is critical and must not be moved separately
- config/service/current-user launches may point at different state roots

Put together, those facts mean same-host attach safety is not a simple folder-picker action.
It is a namespace admission problem.
The product should own that directly.

## The tighter non-clone decision

Borrow Resilio's candor that same-host runtimes are materially distinct namespaces with real storage, identity, and continuity consequences.
Do **not** clone a product contract where operators still have to reconstruct from Linux, CLI, config, service, update, and repair articles whether they reopened the same seat, forked a sibling runtime, or created a corrupting overlap.

## What AnonSync should do instead

AnonSync should treat same-host runtime identity as a first-class reviewed object.
Every serious launch, service-account switch, config/storage mutation, and local folder attach should answer five things in one place:

1. **namespace identity** — which runtime/storage/identity world is active now
2. **lineage** — whether this continues a known namespace or creates a sibling runtime
3. **surface binding** — which control endpoint and logs belong to this namespace
4. **subject overlap verdict** — which local subjects are safe to reopen, duplicated, blocked, or collision-prone
5. **safe language** — what the product is and is not allowed to say about continuity

## New page obligations from this pass

The archive now needs four more workflow-owned pages:

- **Instance namespace review**
- **Sibling runtime roster**
- **Overlap admission review**
- **Instance namespace receipt**

Those pages should sit beside runtime profile, control-surface grade, policy provenance, and spine integrity pages — not underneath a support lane.
