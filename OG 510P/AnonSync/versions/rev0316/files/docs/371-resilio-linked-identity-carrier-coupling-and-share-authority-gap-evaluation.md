# Resilio linked-identity, carrier coupling, and share-authority gap evaluation

## Why this pass exists

The archive already had strong doctrine for capability artifacts, incoming requests, member grants, and linked-device exceptions.
What it still lacked was one direct current Resilio evaluation for a narrower seam:

> when the operator asks `what exact authority will this seat gain, and why?`, where does current Resilio actually answer that question?

This is another place where the non-clone reason becomes tighter.
Current official Resilio docs still show a useful, living product, but they also show that ordinary authority truth still leaks across several different concepts at once:

- linked identity
- subject family (`Standard` versus `Advanced`)
- delivery / claim lane (`key`, `link`, `QR`, browser-open, manual paste)
- special-case exceptions like linked read-only workarounds

## Current official Resilio evidence that matters here

Current official docs still show an active v3 line and still present two ordinary desktop-desktop approaches:

1. link devices with one identity for automated sharing across `My devices`
2. manually share folders via key / link / QR

They also still say that every folder added on one linked device automatically becomes available on all the other linked devices with full read-write access, and that when data is shared across your own devices linked to one identity all of those devices act as Owners.
That is a strong convenience story.

The same current docs also still say:

- only Owners can invite new users to an Advanced folder and only Owners can share Advanced folders
- Standard folders have no Owner permission level and can still be shared onward; peers with read-only access can only share read-only keys onward
- keys and links are not the same security story because keys do not use the approval mechanism while links can require approval, expiry, and use limits
- remembered approvals can be reused for `only new peers`, but policy can also force approval for `all peers`
- Advanced folders do not support linked-device read-only the way many operators would expect; the documented workaround is to use a Standard folder and a manual read-only key path instead

So the answer to `what right does this path create?` still does not belong to one stable product-owned page.

## What Resilio still gets right

### 1) Linked-device convenience is genuinely valuable

Resilio is still right that people want `my own seats` to behave differently from `someone else's seat`.
Automatic appearance across linked devices is genuinely useful.
AnonSync should not dismiss that.

### 2) Carrier flexibility is genuinely valuable

Resilio is also still right that a claim path may need to travel as copied text, QR, e-mail, browser wrapper, or manual paste.
Real operators benefit from this.

### 3) The docs are candid about some class cliffs

Resilio's docs do not fully hide the sharp edges.
They admit that Standard and Advanced subjects differ materially, that linked-device owner-like behavior has consequences, that Owner is special, that keys bypass link approval, and that some desired outcomes require a different family or a manual reconnect path.
That candor is useful.

## Why this is still a good reason not to clone them

### 1) Authority truth is still split across identity, subject class, and carrier

Current Resilio still makes the operator reconstruct one ordinary answer from several places:

- identity docs for what linked devices mean
- desktop-desktop docs for how linked devices auto-receive folders
- user-management docs for when linked seats act as Owners
- Standard-vs-Advanced docs for where onward share and mutation differ
- share-dialog docs for the key-vs-link approval split
- one-way/readonly docs for where the expected in-place narrowing is unavailable

That is too much archaeology for one ordinary question.

### 2) `my own seat` and `another claimant` are still not separated by one stable page

Resilio clearly intends a difference between those cases, but the product contract is still too distributed.
`linked with one identity` is not just a delivery shortcut.
It changes future scope, default authority, and how the seat participates in the subject.
The operator should not have to infer those consequences from a combination of identity guidance and subject-family caveats.

### 3) Carrier choice still changes more than transport ergonomics

A product can support many carriers without making carrier choice semantically loud.
But current Resilio still leaves meaningful governance differences nearby:

- keys have no approval mechanism
- links can carry approval, expiry, and use budgets
- browser-open may accelerate link claim, while manual paste is the fallback
- read-only onward sharing behaves differently from broader write/share cases

Those are not merely UI wrappers around one identical grant story.
A product should say so plainly.

### 4) Subject-family cliffs still answer questions the operator will treat as seat policy

When `can this seat share onward?`, `can this linked seat be read-only?`, or `can this grant be edited later?` depends materially on whether the subject is Standard or Advanced, the product should surface that as an explicit class cliff, not as trivia discovered from several docs.

### 5) Automation still risks looking like merged authority

Resilio's linked-device convenience is attractive precisely because it compresses work.
But it also risks turning `relationship` into `ambient merged authority` in the operator's head.
AnonSync should borrow the convenience while separating:

- relationship between seats
- future-arrival scope
- resulting per-seat rights
- onward-share ceiling
- later mutability

## The tighter AnonSync conclusion

AnonSync should borrow the following from Resilio more boldly:

- linking your own seats as a first-class convenience
- multiple claim/delivery lanes
- explicit approval policy choices
- honest admission that subject families can differ materially

But AnonSync should refuse the exact page contract whenever one ordinary authority answer still depends on:

- linked-identity folklore
- subject-family folklore
- carrier-specific folklore
- exception how-tos for in-place narrowing that is not actually in place
- later peer-list inspection to infer what the join path must have done

## The replacement pages this evaluation justifies

This pass therefore makes four page-shaped obligations concrete:

1. **Join consequence** — what exact right, future scope, and review story will this path create?
2. **Linked family** — what does being in this linked-seat family actually imply for future arrivals and owner domain?
3. **Onward share** — may this seat re-share, why, and where does that answer change?
4. **Claim lane** — are these lanes equivalent wrappers of one artifact or meaningfully different governance paths?

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that linked-device automation and carrier-flexible sharing are worth building, but it is also current evidence that ordinary authority truth still leaks across identity linkage, subject class, and claim lane. AnonSync should copy the practicality and refuse the scattered authority contract.
