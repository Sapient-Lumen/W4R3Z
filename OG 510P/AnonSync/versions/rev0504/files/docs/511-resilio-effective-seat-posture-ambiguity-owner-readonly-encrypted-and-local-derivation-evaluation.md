# Resilio effective seat posture ambiguity, narrow-seat mutation, encrypted ceilings, and local-derivation evaluation

## Why this pass exists

The archive already had stronger answers for subject class, join consequence, linked-seat narrowing, grant mutation, ciphertext custody, and same-host lineage.
What it still lacked was one explicit current Resilio evaluation for a more ordinary daily question:

> after all the linking, sharing, local derivation, and special-case setup is done, what can this seat actually do right now?

Current official Resilio docs are useful precisely because they remain candid that the answer is not one simple `connected` state.
They still document materially different effective postures:

- linked devices under one identity effectively act as Owners
- a desired read-only linked seat still requires a separate Standard-folder read-only-key ritual
- ordinary read-only peers can land bytes yet cannot propagate local edits back
- encrypted custody peers are read-only with forced overwrite behavior and no Selective Sync
- same-host local derivatives inherit a ceiling from the source and can silently narrow when the source narrows

That is real product honesty.
It is also another strong reason not to clone the page contract.

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- when you share data across your own devices linked to one identity, all of those devices act as Owners
- the common linked-device convenience path automatically makes folders available to all linked devices with full read-write access
- if you want one linked device to behave as read-only, the documented workaround is to create a Standard folder, copy the Read Only key, disconnect the already connected folder, manually paste the key, and choose a path
- for ordinary read-only peers, local edits do not sync back, and if the read-only peer changes a file, synchronization for that file is stopped on that peer unless overwrite behavior restores the source version
- encrypted backup peers with the F-key only are read-only, always have `Overwrite any changed files` active, and do not support Selective Sync
- local shares are self-only derivatives, cannot receive Owner, inherit only the source-share ceiling, cannot have their access changed through user management, and will lower if the source right is lowered
- if the source local share is disconnected or removed, the local share is also removed from Sync and does not automatically reconnect later

So the current product absolutely has effective seat postures.
The weakness is still page ownership.

## What Resilio still gets right

### 1) It admits that `connected` is not enough

Current docs still refuse the lie that every connected seat is semantically equivalent.
Owner, read-write, read-only, encrypted read-only, and local derivative seats all behave differently.
That candor is worth borrowing.

### 2) It admits that local mutation behavior is part of the contract

Current docs still say a read-only seat is not merely `view-only` in a vague sense.
They describe what happens when someone edits, deletes, renames, or adds files on that seat and how overwrite behavior changes the result.
That is exactly the right kind of concrete product truth.

### 3) It admits that derivatives inherit and narrow

Current docs still say a same-host local derivative does not become an independent sovereign share.
It inherits a ceiling, can lose power when the source loses power, and may disappear with the source.
That is valuable honesty about downward authority.

### 4) It admits that encrypted custody is a different posture, not merely a path option

Current docs still say encrypted peers are read-only, forced-overwrite, and non-selective-sync.
That makes encrypted custody a posture with hard ceilings, not only a transport flavor.

## Why this is still a good reason not to clone Resilio

### 1) The effective seat answer is still scattered across too many article families

The operator still has to cross-read at least:

- user management
- linking / linked-device guidance
- one-way sync behavior
- linked read-only workaround guidance
- encrypted folders
- local-share guidance

That is too much archaeology for one ordinary question:

> what can this seat actually do right now?

### 2) Capability, local mutation handling, and derivation are still not adjacent

Current Resilio may separately tell you:

- the seat is an Owner because it is linked
- the seat is read-only because you used a Standard-folder key workaround
- local edits will suspend synchronization for a file
- encrypted peers cannot decrypt and always overwrite changed files
- local derivatives inherit a lowered ceiling from the source

But it still does not own those truths on one stable page.
The operator must mentally combine them.

### 3) Effective posture is still too easy to mistake for requested posture

A share dialog may grant one permission.
A linked-family default may imply another.
A local derivative may inherit a narrower ceiling.
An encrypted peer may impose a still harder operational ceiling.
A product should say which posture is merely requested, which is effective now, and why.

### 4) Descendant blast radius is still special-case prose

Current local-share docs contain important posture truths:
source-right changes can narrow the derivative, source disconnect can remove the derivative, and manual reattachment may still be needed later.
That is derivative-governance truth, but it still arrives as article prose instead of one first-class rights graph.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- explicit acknowledgment that seats can hold materially different postures
- concrete local-mutation behavior rather than vague permission labels
- honest derivative-ceiling inheritance
- hard capability ceilings for opaque encrypted custody

But AnonSync should refuse the exact current page contract whenever one ordinary posture answer still depends on:

- linked-owner folklore
- read-only workaround folklore
- encrypted-folder caveats
- local-share inheritance prose
- later symptoms such as suspended files or grayed-out controls

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Effective seat posture** — what this seat can actually do now, with requested-versus-effective basis made explicit
2. **Local mutation on narrow seat** — what a local edit/delete/rename means on a seat that cannot propagate it normally
3. **Derived rights graph** — what descendants inherit, what routes they use, and what narrows automatically
4. **Seat posture receipt** — what durable proof captures the seat's effective posture, restrictions, and derivation basis

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that effective seat posture is a real product truth, but it is also current evidence that ordinary answers to `what can this seat actually do`, `what happens if someone edits locally here`, and `which descendants narrow with it` still leak across linked-device rules, read-only behavior notes, encrypted-folder caveats, and local-share articles. AnonSync should copy the candor and refuse the scattered posture contract.
