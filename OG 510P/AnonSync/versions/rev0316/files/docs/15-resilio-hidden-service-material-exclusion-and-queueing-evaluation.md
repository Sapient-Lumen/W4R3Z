# Resilio hidden service material, exclusion policy, mutation delay, and queueing evaluation

## Bottom line

A further current-doc pass makes the non-clone case more concrete, not less.
Resilio Sync still deserves respect on four more operator-important lines:

- it keeps per-share service material that lets a sync relationship stay portable with the bytes
- it supports real exclusion rules rather than pretending every file should sync
- it lets operators delay synchronization for conflict-prone file classes
- it now supports per-share download prioritization in v3.1.0

Those are not weak ideas.
They are good operator ideas.
But the same docs also show why AnonSync should not clone the exact interface contract.
Too much of the truth still lives in hidden folders, text files, JSON blobs, restart ritual, or queue behavior that the ordinary UI only describes partially.

## What current Resilio docs still get very right

### 1) Portable sync state does need explicit service material somewhere

Resilio is right that a sync relationship is not only `user files`.
There really are service files, identifiers, transient partials, ignore rules, and archive/versioning material that must exist somewhere if a peer is going to resume work honestly.
Pretending the runtime has no service material would only make recovery and portability worse.

### 2) Exclusion rules are ordinary, not exotic

Resilio is also right that operators need a way to say `do not even index these files`.
The current IgnoreList docs are refreshingly explicit that excluded files are not indexed and are not counted in the main size column.
That is real semantic difference, not cosmetic filtering.

### 3) Mutation-delay policy is useful

Resilio is right that file classes like Office, Adobe, and AutoDesk formats often need a small upload delay so the application and the sync engine stop fighting over half-settled writes.
The product instinct is correct: batching and lock-avoidance belong in the sync product.

### 4) Download order has become first-class enough to matter

Resilio is also right that queue order is sometimes operator intent, not internal trivia.
The v3.1.0 download-priority feature is evidence that `which files should come down first` is important enough to deserve a first-class control.

## Why this still is not a clone vote

### 1) Critical service material is still too hidden and too fragile as a page contract

The current docs still say every synced folder gets a hidden `.sync` directory, that deleting or moving it produces `Service files missing`, and that one repair path is removing the share, checking Archive, deleting `.sync`, and re-adding the share.
Another current warning doc still says the same error can come from running two Sync instances against the same folder or external drive.
That means the feature family is real, but the current contract still leaves ordinary operators learning about a critical identity-bearing object mostly through failure.

AnonSync should keep explicit service material, but refuse any contract where the primary public object is a hidden directory plus a later corruption recipe.

### 2) Exclusion truth is still spread between a hidden file, syntax folklore, and side effects

The IgnoreList docs still put exclusion policy in a hidden UTF-8 text file inside `.sync`, make it case-sensitive, preload defaults, and warn that peers may intentionally differ and therefore show different share sizes.
Those are all real truths.
But the ordinary operator answer still depends on opening and editing a hidden text artifact and remembering root-scope wildcard semantics.

AnonSync should keep powerful exclusion policy while refusing a contract where a hidden file is the main semantic home of scope, case-sensitivity, and impact accounting.

### 3) Delay policy still depends on storage-folder JSON and restart ritual

The delay docs still say FileDelayConfig lives in the storage folder, is edited directly as JSON, and requires restarting Sync.
That is a practical escape hatch, but not a page contract ordinary operators should clone.
The useful idea is `batch unstable file classes`; the weak contract is `edit this hidden config and restart`.

AnonSync should keep mutation-delay policy while refusing any interface that makes timing classes and delay windows live primarily in raw config material.

### 4) Queue priority still leaks implementation exceptions into the operator contract

The download-priority docs are honest but also revealing.
They say prioritization can come from either per-share preferences or a global power-user default, that manually-set share priority stops following later global changes, that only the active queue up to 50,000 files is prioritized, that some suspension exceptions exist, that non-splittable files do not fully obey the rules, and that UI ordering may still look alphabetical instead of actual priority order.
That is exactly the kind of feature AnonSync should borrow more boldly while refusing to clone the explanation surface.

AnonSync should keep queue-priority power while refusing any contract where the visible list, the effective order, and the reason a file did not move first can drift apart.

## The sharper AnonSync line

The fourth-wave Resilio answer is now:

> borrow the operator ideas, refuse the hidden-file and hidden-knob page boundary.

More concretely:

- borrow **explicit service material as a first-class concept**
- borrow **real exclusion policy with indexing consequences**
- borrow **file-class mutation delay where it avoids conflicts**
- borrow **download-order policy where operators actually care which work finishes first**
- refuse any page contract where those truths primarily live in hidden directories, text files, storage-folder JSON, restart ritual, or queue exceptions that the visible list cannot explain

## Replacement-page obligations created by this pass

If AnonSync is serious about not cloning, it now owes four more ordinary pages.

### 1) Service material

One page should answer:

- what service material exists for this subject and where it lives
- which parts are identity-bearing, disposable cache, archive/versioning, exclusion policy, or partial-transfer residue
- whether integrity is healthy, degraded, missing, duplicated, or foreign-owned
- what repair path preserves continuity versus forcing rebind

That is the role of `281`.

### 2) Exclusion policy

One page should answer:

- what rules currently exclude indexing or transfer
- which scope each rule applies to
- whether matching is case-sensitive or otherwise platform-sensitive
- what visible accounting changes those rules cause

That is the role of `282`.

### 3) Mutation delay

One page should answer:

- which file classes use a delay window
- why that class is delayed
- what pending mutations are currently waiting behind the delay window
- whether a mutation is delayed, blocked by lock conflict, or already eligible to ship

That is the role of `283`.

### 4) Download queue

One page should answer:

- what effective priority policy currently applies
- whether that policy came from local override, inherited default, or a temporary review
- what files are actually ahead right now and why
- which exceptions or unsplittable transfers prevent strict priority execution

That is the role of `284`.

## Result

This pass again makes the archive stricter in the useful way.
It does not reduce the case for learning from Resilio.
It improves the case by focusing on one more class of evidence:
Resilio still has good operator ideas here, but the same docs still leave too much meaning inside hidden machinery and power-user settings.
That is a good reason to borrow the ideas while writing better interface contracts.
