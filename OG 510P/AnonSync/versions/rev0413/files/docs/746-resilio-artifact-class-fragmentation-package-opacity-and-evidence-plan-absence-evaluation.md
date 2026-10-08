
# Resilio artifact-class fragmentation, package opacity, and evidence-plan absence evaluation

## Why this seam matters

Another current official Resilio pass exposes a stronger non-clone reason than `you can send logs`.
Current official docs are candid that *different questions want different artifacts*:

- the current `Send info to Support team` section still distributes separate guides for automatic logs, manual logs, mobile logs, crash reports / dumps, NAS core dumps, iperf3 testing, and log-size tuning
- the current `Collecting debug logs automatically` guide still says technical support is available exclusively for Resilio Sync Business customers, while Sync v3 users are directed to the community forum and Help Center for functionality help
- that same automatic-log guide still says log sending may fail and then routes desktops and NAS to manual collection while telling mobile peers to contact support
- the current `Collecting debug logs manually` guide still names artifact files such as `sync.log` and `sync.log.<some number>.zip`, and still lists different storage locations by platform and service mode
- the current `Collecting crash reports, mini-dumps and core dumps` guide still separates artifact family and collection steps by operating system instead of one product-owned package object
- the current `Collect debug logs on mobiles` guide still uses a hidden `.synclogs` folder and the `SNC.DBG.LOGS` key path
- the current `Measuring network performance with iperf3` guide still says Sync should be shut down completely on both peers during the tests
- the current `Increasing Debug Log size` guide still says logs rotate at `100 Mbytes` by default, keep only `sync.log` plus `sync.log.old`, may still be insufficient at 200 MB, and cannot be adjusted on mobile platforms
- the current `Resilio Sync 3.0 change log` still shows the live v3 line through `3.1.2.1076`

That candor is useful.
Resilio is not pretending that every escalation wants one generic blob.

The non-clone problem is still package ownership.
One ordinary operator answer is still reconstructed too late:

> what evidence classes are in this package, why are they here, what preconditions made them trustworthy, and what exactly left the machine?

## What current official docs still get right

### 1) Artifact family really does matter

Current docs still distinguish materially different evidence classes:

- recent debug logs
- manually scavenged log files
- mobile-specific log pulls
- crash reports, mini-dumps, and core dumps
- network measurements via iperf3
- larger-log configurations for high-volume incidents

That is better than pretending any captured file is equally diagnostic.

### 2) Collection preconditions are real

Current official docs still admit that usable evidence can depend on:

- enabling logging and restarting
- reproducing the issue long enough
- not closing the application/device before sending finishes
- shutting Sync down for network tests
- waiting for a crash before a dump exists
- changing log size in advance for noisy incidents

That is good.
It acknowledges that package quality depends on how the evidence was produced.

### 3) Transport route and artifact route are not the same thing

Current official docs still separate:

- automatic send
- manual e-mail/ticket attachment
- mobile hidden-folder collection
- OS-specific crash/dump harvesting
- external benchmarking tooling

That is a real workflow distinction.
Collection route changes what the package means and how complete it may be.

## Where the current contract still fails

### 1) There is still no reviewed evidence plan

The operator still has to infer whether this incident wants:

- one log packet only
- logs plus larger rotation settings
- logs plus crash material
- logs plus network benchmark
- one mobile hidden-folder pull instead of an ordinary desktop route

That is too much reconstruction for one ordinary escalation decision.

### 2) Package meaning is still spread across guide prose

Current docs are candid that artifact family matters, but the product still does not leave one durable object that says:

- which question each artifact family is meant to answer
- which participant or platform owes it
- which preconditions were satisfied
- which stronger questions remain unanswered even after collection

Without that object, package meaning lives in support instructions and memory.

### 3) Manifest membership is still opaque

The operator may know they `sent logs`, `attached dumps`, or `ran iperf3`.
The product still does not publish one inspected manifest that says:

- which exact files or measurements are in scope
- what came from where
- what sensitivity or path exposure remains
- what the current completeness ceiling is

### 4) Export receipts still under-describe what happened

If one operator changes log size, another collects a crash dump, and a third sends the bundle, the product still does not preserve one durable receipt tying plan, artifacts, manifest, and transport lane together.
That weakens later interpretation and makes stale packages harder to detect.

## What AnonSync should do instead

AnonSync should keep the candor and reject package archaeology.
The product should own four ordinary page families for this seam:

1. **Evidence plan page**
   - current diagnostic question
   - requested artifact families
   - preconditions and disruption budget
   - completeness ambition

2. **Artifact capture matrix page**
   - platform / participant rows
   - capture route and prerequisites
   - expected output and current return state
   - blocking incompatibilities

3. **Evidence manifest page**
   - actual members
   - sensitivity findings
   - completeness verdict
   - export readiness

4. **Evidence export receipt page**
   - plan version used
   - manifest version exported
   - transport lane and delivery state
   - stale/reopen boundary

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that artifact classes, capture preconditions, and transport routes really matter. But it is not worth cloning the way the ordinary operator still has to assemble package meaning from separate guides, hidden storage paths, and remembered support ritual.

## New replacement pages added in this revision

- `747` Evidence plan page
- `748` Artifact capture matrix page
- `749` Evidence manifest page
- `750` Evidence export receipt page
