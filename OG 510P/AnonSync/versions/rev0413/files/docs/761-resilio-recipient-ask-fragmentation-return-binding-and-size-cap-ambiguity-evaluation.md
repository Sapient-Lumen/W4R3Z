# Resilio recipient-ask fragmentation, return binding, and size-cap ambiguity evaluation

## Why this seam matters

Another current official Resilio pass exposes a tighter non-clone reason than `pick the right escalation lane` or `keep a public summary linked to a private packet`.
Current official docs are also candid that **a later recipient ask changes what the operator now owes**:

- the current `Collecting debug logs automatically` guide still tells the operator to indicate in feedback text which support ticket the logs refer to, along with role, timestamps, detailed description, and affected shares/files
- the current `Collecting debug logs manually` guide still says to attach logs in reply to the support ticket, upload logs through the support web portal, mention the forum link if redirected from Forums, and ask support for a larger upload link if the 20 MB attachment limit is exceeded
- the current `Collect debug logs on mobiles` guide still routes collection through a hidden `.synclogs` folder after the `SNC.DBG.LOGS` action instead of any product-owned return packet
- the current `Collecting core dump on NAS devices` guide still ends with manually moving the dump to a NAS public folder, downloading it through the NAS WebUI, and sending it onward
- the current `Collecting crash reports, mini-dumps and core dumps` guide still spreads return expectations across platform-specific file locations and a final `send the gzipped coredump to us` style instruction
- the current `Resilio Sync 3.0 change log` still shows the live v3 line through `3.1.2.1076`

That candor is useful.
Resilio is not pretending that every follow-up request can be satisfied by the same file, lane, or size budget.

The non-clone problem is still **recipient-ask ownership**.
One ordinary operator answer is still reconstructed from prose, ticket numbers, reply chains, size limits, and remembered portal steps:

> what exactly did the recipient ask for, what return package would satisfy that ask without oversharing, which token or reply chain binds the return to the case, and what still remains unsatisfied afterward?

## What current official docs still get right

### 1) A later ask is materially different from the original send

Current docs still imply that:

- initial contact and follow-up evidence return are different acts
- a recipient may want logs, dumps, or another artifact class after the first conversation already exists
- return shape depends on the channel and the requested artifact class
- one ticket, forum thread, or support exchange may generate multiple later asks

That is better than pretending one original export permanently solved the case.

### 2) Binding tokens matter

Current docs still admit this indirectly by asking for:

- the support ticket number in automatic feedback
- a reply to the existing support ticket when sending logs manually
- the forum link when the operator came from Forums

That is good evidence that **return binding** is a real product need, not documentation trivia.

### 3) Return lanes have practical constraints

Current docs still make clear that:

- attachment size caps can invalidate the obvious return path
- a bigger upload link may be needed later from support
- some artifact classes require portal upload, email reply, or separate transfer rituals
- mobile and NAS capture routes can produce awkward intermediate files that are not yet a reviewed return packet

That is useful candor.
Operators really do need to know whether the current return path is viable.

## Where the current contract still fails

### 1) The ask itself is still not a first-class object

Current docs still do not leave one product-owned record saying:

- who asked
- what exact artifacts or explanations were requested
- what binding token or reply chain must carry the answer back
- what format, lane, or size limit constrains the return
- when the ask should count as fully satisfied, partially satisfied, or blocked

So operators improvise with copied ticket numbers and memory.

### 2) Satisfaction and overdelivery are still easy to confuse

If support asked for logs from one peer, a dump from another machine, or a smaller/sanitized packet, the product still does not leave one review object that says:

- what exact ask is covered by the prepared return
- what requested members are still missing
- what extra material would exceed the ask or widen disclosure unnecessarily
- what stronger sentence about satisfaction is still unsupported

### 3) Reply-chain viability is still partly folklore

Current docs still imply several return bindings, but the product does not preserve one durable verdict of:

- whether the current return belongs in an existing reply chain
- whether a portal upload is mandatory or merely allowed
- whether an upload-link request must happen first because of size limits
- whether the current ask can be satisfied at all from the present surface or device

### 4) The receipt still overfocuses on send success

Even if files are attached or uploaded, the product still does not publish one durable receipt saying:

- which ask version this return answered
- which members were actually included
- which binding token was used
- which request clauses remain open
- whether the return was complete, partial, blocked, or redirected

## What AnonSync should do instead

AnonSync should keep the candor and reject prose-only follow-up requests.
The product should own four ordinary page families for this seam:

1. **Recipient ask page**
   - requester identity or lane
   - asked-for artifacts and explanations
   - binding token / reply-chain requirement
   - deadline or urgency if any

2. **Ask fulfillment review page**
   - request coverage
   - missing members
   - extra-disclosure warnings
   - strongest supported satisfaction sentence

3. **Return lane review page**
   - reply chain vs new upload
   - attachment cap
   - portal / upload-link requirement
   - current-surface feasibility

4. **Ask fulfillment receipt page**
   - ask version answered
   - returned members
   - binding proof
   - residual gaps and reopen boundary

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that follow-up requests have binding tokens, size limits, and artifact-specific return lanes. But it is not worth cloning the way the operator still has to reconstruct the ask, the satisfying return, and the remaining gaps from ticket prose, forum links, and portal ritual instead of reopening one durable ask object.

## New replacement pages added in this revision

- `762` Recipient ask page
- `763` Ask fulfillment review page
- `764` Return lane review page
- `765` Ask fulfillment receipt page
