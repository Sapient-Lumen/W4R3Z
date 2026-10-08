# Resilio seat-posture mutation ambiguity, rebind rituals, local-share cascades, and class-impossible changes evaluation

## Why this pass exists

The archive already had stronger answers for grant mutation, bind outcome, effective seat posture, and derived rights.
What it still lacked was one explicit current Resilio evaluation for a more operator-urgent question:

> when I want this seat to behave differently, is that change a live edit, a rebind ritual, a remove-and-reshare operation, an automatic cascade, or an impossible request?

Current official Resilio docs are useful precisely because they are still candid that these are not one family of action.
They still document materially different posture-mutation paths:

- Advanced folders can change peer permissions on the fly
- Standard folders cannot mutate permissions live and instead require remove-and-readd with a new key
- linked devices act as Owners by default, so making one linked seat read-only still requires a separate Standard-folder read-only-key path with disconnect plus manual reconnect
- local shares cannot receive Owner, cannot change permission through user management, and must be removed and re-shared to change their local permission
- local-share descendants can narrow automatically when the source narrows and can disappear when the source disconnects
- some ceilings are simply class-impossible, such as sharing an encrypted-key-only local child further as another local share

That is real product honesty.
It is also another strong reason not to clone the page contract.

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line through `3.1.2.1076`.
They also still say all of the following:

- on-the-fly permission changes are available only for Advanced folders
- Standard folders do not support on-the-fly permission changes and instead need removal and re-add with a new key
- when devices are linked under one identity, all linked devices act as Owners and all folders become automatically available there
- if one linked seat should instead be read-only, the documented path is to create a Standard folder, copy the read-only key, disconnect the already connected folder, manually paste the key, and choose a location
- local shares cannot receive Owner, cannot have their access changed through user management, and must be removed from Sync and re-shared to change permissions
- if the source share is narrowed, the local share lowers with it automatically
- if the source share is disconnected or removed, the local share is also removed and does not automatically reconnect later

So the current product absolutely has posture-mutation truth.
The weakness is still page ownership.

## What Resilio still gets right

### 1) It admits that not every posture change is a live edit

Current docs still plainly say some changes are live Advanced-folder mutations while others are not.
That honesty matters.
A weaker product would blur all of them into one fake `edit permissions` action.

### 2) It admits that convenience linking and narrow posture are in tension

Current docs still say linked devices auto-behave broadly, and that narrowing one linked seat to read-only requires stepping out into a different Standard-folder key path.
That is awkward, but it is honest.
It proves that requested posture and linked-family convenience are not the same thing.

### 3) It admits that descendants have their own mutation rules

Current docs still say local shares have a derivative lifecycle:
some narrowing cascades automatically, some permission changes are impossible in place, and source removal can delete the descendant presence entirely.
That is valuable governance truth.

### 4) It admits that some posture requests are simply blocked by class

Current docs still say a local share cannot receive Owner and an encrypted-key-only peer cannot be shared locally.
That makes `blocked by subject class` a real operator answer, not an embarrassing edge case.

## Why this is still a good reason not to clone them

### 1) Posture-change mechanism is still scattered across article families

The operator still has to cross-read at least:

- user management
- Standard-vs-Advanced comparison
- linked-device docs
- linked read-only workaround guidance
- local-share guidance

That is too much archaeology for one ordinary question:

> how do I change this seat's posture, and what kind of operation is it really?

### 2) The product still hides mechanism class behind similar-looking verbs

Current Resilio may separately tell you:

- a permission can be changed live
- another permission needs a new key
- a linked-seat narrowing needs disconnect plus manual reconnect
- a local derivative change needs remove plus re-share
- a source downgrade will narrow descendants automatically
- some promotions are impossible at all

But it still does not own those truths on one stable change page.
The operator must mentally classify the mechanism.

### 3) Effective result and required manual work are still too easy to confuse

A person can ask for `make this seat read-only` and receive one of several realities:

- same subject, live mutation
- same seat, different Standard-folder subject
- local derivative recreation
- downstream auto-narrowing only
- blocked request

A product should say which one is happening before anything is committed.

### 4) Cascade and residue still arrive as later surprises

Current local-share docs contain important mutation truths:
source-right changes can lower descendants, source disconnect can remove descendants, and later reconnect does not restore them automatically.
That is not troubleshooting trivia.
It is posture-change blast-radius truth that should be visible before the change.

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- honest distinction between live mutation and reissue/rebind class
- explicit admission that linked-family convenience can conflict with narrower seat posture
- honest descendant-cascade behavior when a source right narrows or disappears
- explicit `blocked by class` outcomes instead of fake universal editability

But AnonSync should refuse the exact current page contract whenever one ordinary posture-change answer still depends on:

- folder-class folklore
- linked-device workaround folklore
- local-share derivative folklore
- later descendant breakage to infer blast radius
- manually remembering which requests are impossible at all

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Seat posture change review** — what posture delta is requested, and which mechanism class actually applies?
2. **Posture transition forecast** — what current and future powers, bytes, and manual steps follow from this change?
3. **Posture cascade graph** — which descendants auto-narrow, disappear, or need manual rebind?
4. **Seat posture change receipt** — what change was requested, what actually happened, and what unfinished work remains?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that posture changes are not all the same operation, but it is also current evidence that ordinary answers to `can I change this live`, `is this really a rebind`, `what descendants narrow`, and `what requests are impossible` still leak across folder-class docs, linked-device workarounds, and local-share articles. AnonSync should copy the candor and refuse the scattered mutation contract.
