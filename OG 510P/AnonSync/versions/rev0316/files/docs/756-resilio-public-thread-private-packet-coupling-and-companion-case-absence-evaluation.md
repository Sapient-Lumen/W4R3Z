# Resilio public-thread/private-packet coupling, companion-case absence, and redaction-boundary evaluation

## Why this seam matters

Another current official Resilio pass exposes a tighter non-clone reason than `some routes are public and some are private`.
Current official docs are candid that **discussion and evidence do not always travel in the same lane**:

- the current `I still have questions, where can I get answers?` article still sends users toward the community forum while also saying they can contact support, with PRO users first to get response and FREE users answered to the extent possible
- the current `Collecting debug logs automatically` guide still tells the operator to indicate in feedback text which support ticket the logs refer to, plus role, timestamp, detailed description, and affected shares/files
- the current `Collecting debug logs manually` guide still says that if the operator was redirected there from Forums, they should mention the forum link when sending logs through the support web portal
- the same current log/crash/dump guides still repeat the Business-only direct-support language for technical support while Sync v3 functionality help is routed toward forum/help-center self-service and payments/licensing toward a web form
- the current `Resilio Sync 3.0 change log` still shows the live v3 line through `3.1.2.1076`

That candor is useful.
Resilio is not pretending that one public thread and one private packet are the same audience situation.

The non-clone problem is still companion-case ownership.
One ordinary operator answer is still reconstructed from prose, pasted links, and remembered ticket numbers:

> what part of this case is safe for a public/help lane, what part belongs only in a private packet, and what durable object proves these two artifacts are about the same incident?

## What current official docs still get right

### 1) Audience split is real

Current docs still imply that:

- a public/community discussion may be the right place to ask the question
- private evidence packets may still be needed to support that question
- billing/licensing lanes are a different audience again
- not every detail belongs in every route

That is better than pretending a single `send` action solves both discussion and evidence.

### 2) Cross-lane references matter

Current docs still admit this indirectly by asking for:

- the support ticket number inside automatic feedback text
- the forum link inside manual-log submissions when the operator came from Forums
- descriptive prose that binds the packet to a specific issue report

That is good evidence that companion linkage is a real product need, not a documentation accident.

### 3) Public summary and private artifacts have different shapes

A forum thread wants a readable problem summary and maybe steps or observations.
A private ticket or upload lane may want logs, dumps, timestamps, and affected subjects.
Current official docs at least hint at this by splitting self-serve discussion routes from artifact collection guides.

## Where the current contract still fails

### 1) The operator still has to invent the companion object

Current docs still do not leave one product-owned record saying:

- this is the public-safe summary
- this is the private evidence packet
- this is how they are linked
- this is which details were intentionally withheld from the public side
- this is what follow-up should continue in which lane

So operators improvise with pasted URLs, ticket numbers, and memory.

### 2) Redaction boundary is still mostly folklore

The docs still imply different audiences, but the product does not leave one review object that says:

- what may safely be visible in a public/community thread
- what is too sensitive, too raw, or too machine-oriented for that lane
- what must remain in the private packet only
- whether the public summary is too vague after redaction to stay useful

### 3) Continuation can still fork silently

When a public thread produces a private packet, or a private packet needs a public summary, the product still does not preserve one durable chronology of:

- which artifact came first
- whether the later packet actually answers the public question
- whether a recipient or helper now needs another sanitized summary
- whether the case should continue publicly, privately, or both

### 4) Delivery can still overclaim continuity

A posted summary and an uploaded packet are different acts.
Even if both succeed, the product still does not publish one durable receipt saying:

- which public artifact exists
- which private artifact exists
- what cross-reference joined them
- what audience each artifact was shaped for
- what kind of continuation is now expected

## What AnonSync should do instead

AnonSync should keep the candor and reject prose-linked companion cases.
The product should own four ordinary page families for this seam:

1. **Companion case page**
   - public summary and private packet siblings
   - audience split
   - linkage identity
   - continuation state

2. **Public summary review page**
   - public-safe statement
   - redaction boundary
   - minimum useful claim
   - stronger forbidden sentence

3. **Private companion linkage page**
   - companion reference
   - packet purpose
   - cross-lane mapping
   - withheld details and why

4. **Companion-case receipt page**
   - posted summary
   - private packet state
   - linkage proof
   - continuation / reopen boundary

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that public discussion, private evidence, and billing/licensing contacts are different audience situations. But it is not worth cloning the way the operator still has to tie forum links, ticket numbers, support prose, and private packets together by hand instead of reopening one durable companion-case object.

## New replacement pages added in this revision

- `757` Companion case page
- `758` Public summary review page
- `759` Private companion linkage page
- `760` Companion-case receipt page

