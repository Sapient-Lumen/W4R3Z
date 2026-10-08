# Resilio pause, quiescence ambiguity, and partial-stop truth evaluation

## Why this pass exists

The archive already had strong pages for severance, claim ceilings, destination worlds, bind outcomes, and seat posture.
Those explain what happens when an operator truly disconnects, removes, or narrows authority.
What they still did not own tightly enough is a much more ordinary maintenance gesture:

- `pause`
- `resume later`
- `hold activity while I work`
- `stop this from moving for now`

Current official Resilio docs still make that seam real.
They are useful because they do **not** pretend pause means universal stillness.
But they still leave too much reconstruction work around what `paused` actually allows to continue.

## What current Resilio still gets right

Current official docs are still candid that pause is **not** full quiescence.

The load-bearing truths they still publish include:

- **Pause is scoped to transfer behavior, not all state change**: current `How to pause syncing` docs still say pause means only bits download/upload are stopped.
- **Deletion is still not fully paused**: those same docs still say file deletion will be synced either way.
- **Zero-sized/control-shaped items still move**: current pause docs still say zero-sized files will be synced either way.
- **Detection and indexing still continue**: current pause docs still say new files will be rescanned and indexed and share size will increase accordingly on paused peers.
- **Scheduler-language still confirms partial stop rather than full freeze**: current `Running Sync on schedule` docs still say `Paused` means upload/download speed is zero while zero-sized files, deletions, and rescans still continue.
- **Implementation history shows this seam is real, not theoretical**: the still-published historical change log still records a fix for `Sync stopping indexing if folder paused`, which implies paused-state semantics have been subtle enough to break in production.

That is useful honesty.
Resilio is not lying that a pause icon means deep freeze.

## Where current Resilio still stays too article-shaped

### 1. `Paused` still sounds stronger than the documented contract

Ordinary operators hear `paused` and often infer one of these stronger meanings:

- nothing is moving
- nothing is being learned
- nothing can disappear
- no outward consequence can still occur
- this is safe for maintenance, surgery, or evidence capture

Current docs still explicitly undercut those assumptions.
That is good.
But the product contract still leaves the operator to discover that by reading help text rather than by reviewing a phase-by-phase stop vector at the moment they choose pause.

### 2. Two official pages still describe the residual behavior differently

Current official docs stay aligned on the big idea that pause is partial, but they still diverge in the ordinary-language details.
One current page says paused peers will not download or upload anything.
Another current page says paused peers can still upload to non-paused peers while not downloading.
Both still say deletions, zero-sized files, and rescans continue.

That means even the official material still leaves enough ambiguity that an operator may not know the exact continued-activity contract without deeper reconciliation.
AnonSync should not clone a product shape where the safe maintenance sentence still depends on cross-reading two pause articles.

### 3. Pause, disconnect, and true containment remain too easy to blur

Current Resilio docs still provide all three ideas somewhere:

- pause as partial traffic suppression
- disconnect as seat-local sync severance
- remove as linked-cohort removal

Those are materially different.
But the interface contract still makes it too easy for an operator to reach for `Pause` when what they actually need is one of:

- no more byte ingress here
- no more byte egress here
- no more delete propagation
- no more local detection/indexing
- no more participation at all
- safe evidence capture for maintenance

That distinction is still under-owned.

### 4. There is still no durable quiescence receipt

Current docs explain behavior, but the product still does not seem to emit one stable receipt that says:

- requested stop phrase
- effective stop class
- phases truly stopped
- phases still live
- stronger forbidden overstatement
- stronger action needed for full quiescence

That is still too much memory burden for ordinary maintenance and incident work.

## What AnonSync should do instead

AnonSync should treat `pause` as a reviewed **quiescence request** rather than a generic toggle.
The product should own four page families:

1. **Quiescence review**
   - requested stop phrase versus effective stop class
   - per-phase stop forecast before commit
   - better alternative when pause is too weak

2. **Residual activity matrix**
   - send bytes, receive bytes, deletions, zero-byte/control events, detection/indexing, other still-live phases
   - support, uncertainty, and counterfactual comparison

3. **Pause language substitution**
   - rewrite unsafe phrases like `frozen`, `stopped`, or `quiet` into earned product language
   - attach caveats to the sentence instead of hiding them in help prose

4. **Quiescence receipt**
   - what was requested
   - what was actually stopped
   - what remained live
   - what stronger action would be needed for true stillness or maintenance isolation

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that `pause` is a partial stop rather than a magical freeze. But it is not worth cloning the way current operators still have to infer the real quiescence contract — and even reconcile differing pause-language details — from several help pages instead of getting one stable phase-owned review and receipt family.

## New replacement pages added in this revision

- `532` Quiescence review
- `533` Residual activity matrix
- `534` Pause language substitution
- `535` Quiescence receipt
