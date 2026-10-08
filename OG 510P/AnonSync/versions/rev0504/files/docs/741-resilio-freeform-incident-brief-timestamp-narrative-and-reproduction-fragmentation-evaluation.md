# Resilio freeform incident brief, timestamp narrative, and reproduction fragmentation evaluation

## Why this seam matters

Another current official Resilio pass exposes a stronger non-clone reason than `logs can be sent`.
Current official docs are candid that raw artifacts are not enough by themselves:

- the current `Collecting debug logs automatically` guide still says the operator should **reproduce the issue**, let Sync collect logs for **at least 15 minutes**, and explain in feedback text what the log refers to
- that same guide still says the feedback should include the **role of that peer in the setup**, the **timestamp** for the observed problem, the **problem description in detail**, and the **share/file names** involved
- that same guide still says the operator should not close the application or device until log sending is confirmed complete
- the current `Collecting debug logs manually` guide still says the operator should **describe the issue**, and if redirected from Forums should also mention the **forum link**
- the current `My files don't sync` article still routes the operator through peers, warnings, history search, and queues before the case is mature enough for heavier capture
- the current `Peers aren't connecting` article still ends with a pairwise escalation ask, which implies a specific failing event and failing pair even though the brief for that event is not a first-class product object
- the current `Resilio Sync 3.0 change log` still shows the live v3 line through `3.1.2.1076`

That candor is useful.
Resilio is not pretending that logs interpret themselves.
The operator is still expected to supply event context.

The non-clone problem is still capture-brief ownership.
One ordinary operator answer is still reconstructed too late:

> what exact symptom are we trying to catch, when did it happen, which subjects and participants define the event, and what coordinated run would make the next evidence window actually usable?

## What current official docs still get right

### 1) Event context is real evidence, not decoration

Current guides still ask for:

- peer role
- timestamp of the problem observed
- problem description in detail
- names of affected shares/files
- support-ticket or forum context when relevant

That is good.
It admits that artifact files need a case brief.

### 2) Reproduction is a separate step from capture activation

Current official docs still separate:

- enabling debug logging
- restarting to ensure it is active
- reproducing the issue
- waiting long enough to collect useful logs
- actually sending the packet

That is better than pretending `enable logs` and `usable evidence exists` are the same fact.

### 3) Delivery completion is not trivial

The current automatic-send guide still says operators should keep the app or device open until sending is reported done.
That is a meaningful transport truth.
A packet may exist locally while the send is still incomplete.

## Where the current contract still fails

### 1) The incident brief is still freeform prose

Current official docs still ask the operator to write the key meaning manually into feedback text or email.
The product does not preserve one structured brief that says:

- observed symptom
- strongest current explanation
- time anchors
- affected subjects
- relevant participants
- what outside readers should and should not infer yet

Without that object, the case brief lives in prose that is easy to omit, rewrite, or lose.

### 2) Timestamps are still mentioned but not owned

Current guides still ask for the timestamp of the observed problem.
But the product does not leave a durable symptom bookmark that later pages can reuse.
That means the same time anchor may have to be retyped into:

- feedback text
- manual upload notes
- forum handoff
- later internal escalation

### 3) Reproduction is still ritual instead of a reviewed run object

Current docs still tell the operator to reproduce the issue and let logging run.
But the product does not publish one shared object for:

- which participants are supposed to be ready
- which symptom should count as `caught`
- which dwell window makes the run usable
- what counts as `no symptom reproduced` versus `capture failed`
- whether the resulting evidence window is strong enough to interpret

### 4) Handoff quality still depends on social memory

If one operator enables logging, another performs the reproduction, and a third sends the packet, the product still does not leave one durable receipt for the brief and the coordinated run.
That weakens later interpretation and makes stale packets harder to spot.

## What AnonSync should do instead

AnonSync should keep the candor and reject the prose ritual.
The product should own four ordinary page families for this seam:

1. **Incident brief page**
   - problem statement
   - time anchors
   - affected subjects
   - strongest safe summary

2. **Symptom bookmark page**
   - one observed event anchor
   - time quality and source
   - capture alignment for later runs

3. **Coordinated capture run page**
   - participants ready state
   - steps to reproduce
   - success window and dwell floor
   - partial-failure semantics

4. **Capture brief receipt page**
   - claimed symptom
   - actual run
   - usable evidence window
   - reopen and stale boundary

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that logs need role, timestamp, subject, and reproduction context. But it is not worth cloning the way the operator still has to type the case brief into feedback prose and remember whether the reproduction run actually caught the target symptom inside a usable evidence window.

## New replacement pages added in this revision

- `742` Incident brief page
- `743` Symptom bookmark page
- `744` Coordinated capture run page
- `745` Capture brief receipt page
