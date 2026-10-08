# Resilio topology, locality, and removable-media evaluation

## Why this pass matters

Current official Resilio Sync docs are again useful for AnonSync precisely because they are candid about several topology and target-fit truths that many products blur.
They still say all of the following:

- a nested child folder can be shared separately, but parent and child are treated as separate shares, both must have Read & Write or Owner permissions, Selective Sync must be disabled on both, and peers holding only the parent will not seed peers holding only the child
- that same nested topology can cause the child subtree to be indexed and rescanned twice on the source peer, while child changes can still propagate onward through the parent share to another peer
- same-host local sharing is a real feature, but it is desktop-only, entitlement-bound, self-only, and explicitly warns against choosing a subdirectory or ancestor of the source because that creates syncing loops
- local shares can target USB and network paths, inherit only a narrowed permission ceiling from the source, do not use tracker/relay/LAN discovery, are removed when the source is disconnected or removed, and do not automatically reconnect when the source later returns
- Android removable storage is also real, but the crucial grant step is not an ordinary path pick: Sync must be granted access to the SD-card root through the provider view before the product can later select the actual folder location
- Simple Mode on Android hides `ExternalSD`, forces new shares into internal storage, and can create `(1)` duplicates, so a seemingly small convenience toggle actually changes storage topology and admissible targets
- `Folder not empty`, `Selected folder is already added`, and move/reconnect guidance still carry real continuity meaning about when a target is a safe rebind, a conflicting existing bind, or a potentially destructive merge

That is a strong product to learn from.
It is also a concrete reason not to clone the page contracts.

## What Resilio gets right

### 1) It admits that topology is not just a path string

Current docs still say child shares, parent shares, same-host local copies, and pre-populated existing folders all behave differently.
That is useful honesty.
A product that hides those differences behind one `Connect here` ritual would be worse.

### 2) It admits that same-host work is still real sync work

Current docs still say a local share is self-only, inherits source limits, can target USB/network paths, and can disappear with the source.
That is important candor.
It prevents the operator from assuming a same-host copy is automatically an independent branch.

### 3) It admits that provider-root permission is different from folder choice

Current Android SD-card docs still distinguish one-time provider-root access from later folder selection.
That is exactly the kind of grant truth products often blur.

### 4) It admits that target disappearance changes continuity

Current move/reconnect, local-share, and warning docs still make clear that a target returning later might be a safe rebind, a stale conflicting bind, or a fresh merge risk.
That is the right kind of honesty.

## Why we still should not clone it

The core problem is not lack of truth.
The core problem is **where the truth lives**.

Resilio still makes the operator reconstruct one ordinary answer from several separate article families:

- *what topology am I creating: disjoint share, child share, same-host derivative, or conflicting duplicate bind?*
- *who actually seeds whom here: remote peers directly, a parent share indirectly, or only self through a source edge?*
- *did I really grant the removable medium/provider, or did I only walk to a path that still lacks write authority?*
- *if this target vanishes and later returns, do I have continuity, a safe rebind, or a new-world merge problem?*

Those should not be FAQ-navigation questions.
They should be ordinary product pages.

## The AnonSync borrow line

Borrow from current Resilio:

- explicit candor that parent/child overlap changes seeding and indexing behavior
- explicit candor that same-host local edges are self-only and source-coupled
- explicit candor that provider-root grant is a real review step distinct from path selection
- explicit candor that disappearing targets and returning targets can change continuity truth

Adapt into AnonSync:

- one first-class page for **topology admission**
- one first-class page for **local edge review**
- one first-class page for **provider grant**
- one first-class page for **removable-target continuity**

## The replacement principle

AnonSync should never let `add`, `connect`, `store on SD`, `sync locally`, or `reconnect here` stand in for topology truth.
Every surface that creates or re-binds a target should be able to answer four questions directly:

1. what graph relation am I creating?
2. what route will actually carry bytes?
3. what grant proves this target is writable and durable enough for the promise?
4. if the target disappears and later returns, what continuity grade survives?

That is the tighter reason not to clone current Resilio page contracts in this part of the product.
