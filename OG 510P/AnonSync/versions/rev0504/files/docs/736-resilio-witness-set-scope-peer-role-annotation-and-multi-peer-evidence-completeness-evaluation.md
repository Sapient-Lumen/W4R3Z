# Resilio witness-set scope, peer-role annotation, and multi-peer evidence completeness evaluation

## Why this seam matters

Another current official Resilio pass exposes a stronger non-clone reason than `diagnostics exist`.
Current official docs are candid that the *right amount of evidence* depends on the incident class:

- the current `Peers aren't connecting` article still says to collect debug logs from **two peers** that cannot connect
- the current `My files don't sync` article still says that if the listed checks do not help, operators should collect logs from **all peers**
- the current `How can I improve data transfer/sync speed?` article still ends with the same **all peers** instruction for persistent speed trouble
- the current `Collecting debug logs automatically` guide still says the feedback text should explain the **role of that peer in the setup** (for example `source` or `destination`), the timestamp of the problem, and which shares/files are involved
- the current `Collecting debug logs manually` guide still says the operator should describe the issue, may need a support-upload route for larger logs, and is still working at packet level rather than one product-owned incident witness object
- the current `Resilio Sync 3.0 change log` still shows the live v3 line through `3.1.2.1076`

That candor is useful.
Resilio is not pretending that every failure wants the same capture scope.

The non-clone problem is still witness ownership.
One ordinary operator answer is still reconstructed too late:

> which peers actually matter for this incident, what role does each one play, what evidence do I need from each, and when is the witness set complete enough for an honest claim?

## What current official docs still get right

### 1) Different incident classes really do need different witness counts

Current docs still openly distinguish:

- **pairwise connectivity** problems, where two specific peers may be the right witness set
- **global or share-wide sync failures**, where the product asks for all peers
- **speed problems**, where the product again asks for all peers because one slow edge may not explain the whole topology

That is better than pretending one local log always tells the whole story.

### 2) Peer role is real diagnostic information

The current auto-log guide still asks the operator to tell support the role of the peer in the setup, such as `source` or `destination`.
That is a meaningful product truth.
A log file is weaker without role context.

### 3) Narrative context is still needed to interpret the capture

Current guides still ask for timestamps, issue description, and the share/file names involved.
That shows that `send logs` is not enough by itself.
The packet needs witness metadata.

## Where the current contract still fails

### 1) There is still no reviewed witness-set object

The operator still has to infer whether this incident wants:

- one local seat only
- one failing pair
- all peers in a share
- all peers in a route segment
- one source plus one destination plus one relay/bridge witness

That is too much reconstruction for one ordinary escalation decision.

### 2) Peer role is still prose instead of product state

Current docs are candid that peer role matters, but the role still gets narrated manually in feedback text.
The product does not publish one durable object that says:

- this peer is the current source witness
- this peer is the blocked destination witness
- this peer is only an observer or alternate source
- this peer is optional for the current question

Without that object, role truth lives in freeform notes.

### 3) Completeness is still folklore

The operator can gather some logs, maybe many logs, maybe all logs.
But the product still does not leave one page that says:

- which witnesses were required
- which witnesses were optional
- which required witnesses are still missing
- whether the current case may close honestly anyway
- whether a stronger claim is blocked only because the witness set is incomplete

### 4) Handoff quality still depends on social memory

If one operator collects logs from two peers and another later escalates, the product still does not preserve one durable receipt of the intended witness set and the witnesses actually obtained.
That weakens later review and makes contradictions harder to interpret.

## What AnonSync should do instead

AnonSync should keep the candor and reject the witness folklore.
The product should own four ordinary page families for this seam:

1. **Incident witness set page**
   - minimal participant set
   - peer role typing
   - required versus optional witnesses
   - evidence duty per participant

2. **Witness request page**
   - one reviewed evidence ask for one participant
   - role, capture window, artifact family, and privacy envelope
   - completion proof and failure reason

3. **Witness completeness review page**
   - required witnesses received versus missing
   - contradiction map across witnesses
   - strongest safe claim with current witness coverage

4. **Witness-set receipt page**
   - chosen witness set
   - actual returns
   - missing witnesses
   - claim ceiling and reopen boundary

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that different incidents need different witness counts and that peer role really matters. But it is not worth cloning the way the ordinary operator still has to infer who owes evidence, narrate peer role in prose, and remember whether `two peers`, `all peers`, or `some sampled peers` were actually enough for this case.

## New replacement pages added in this revision

- `737` Incident witness set page
- `738` Witness request page
- `739` Witness completeness review page
- `740` Witness-set receipt page
