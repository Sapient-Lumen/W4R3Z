# Resilio evidence intake, sufficiency, and supplement-loop fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- choose the next best fact to capture
- package captured artifacts into typed evidence packets
- preserve redaction cost, custody, and export truth
- distinguish `sent`, `received`, `opened`, `validated`, and `usable`

What it still lacked was the next ordinary operator answer:

> a packet has arrived; is it actually sufficient for a decision, what is stale or mismatched about it, what one supplement request would improve it most, and what claim ceiling survives if no supplement ever comes?

That is the seam this pass locks.
A product that can export packets honestly but cannot intake them honestly still leaves too much truth in email back-and-forth, support folklore, and vague `please send more logs` habits.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful intake ingredients, but mostly as separate capture/export instructions rather than one intake workspace:

- `Collecting debug logs automatically` still says the feedback text should identify the support ticket, peer role, timestamps, problem description, and names of shares or files, and it still keeps `Include logs` as a distinct step.
- `Collecting debug logs manually` still requires enablement, restart, reproduction, and at least 15 minutes of post-repro collection, while also capping ordinary attachments at 20 MB and telling operators to ask for an upload link if logs are larger.
- `Increasing Debug Log size` still says logs rotate at `log_size` and that even the default 200 MB retained window can sometimes be insufficient to capture an issue, which makes capture completeness and loss-window questions real.
- `Power user preferences` still says `log_size` defaults to 100 MB and `log_ttl` to 7 days, and it still warns that older versions may miss or deprecate some settings.
- `Collect debug logs on mobiles` still routes mobile capture through a hidden `.synclogs` folder after a special debug action, which means a mobile packet can arrive with a very different artifact class and collection path.
- `Where to collect logs on NAS?`, `How to collect logs on NAS manually?`, and `Collecting core dump on NAS devices` still show that support-facing packets may begin as whole internal-data copies, later be cleaned down to selected files, or be moved through public folders for download.
- `Collecting crash reports, mini-dumps and core dumps` still shows that dump classes vary by platform, service principal, and crash path, so not every packet is equally decision-grade for every question.
- `Measuring network performance with iperf3` still adds another possible support artifact class whose value depends on the fact pattern and on shutting Sync down during the test.
- the `Send info to Support team` section still groups these articles as a cluster rather than one intake-and-sufficiency workflow.

## What current Resilio still gets right

### 1) It is explicit that more context matters

Ticket number, timestamps, peer role, share/file names, and problem description are all requested explicitly.
That is worth borrowing.

### 2) It admits that capture windows can fail

Fifteen-minute post-repro collection, log rotation, attachment-size limits, and platform-specific storage paths all reveal that a packet may be real yet still incomplete.
That honesty matters.

### 3) It preserves artifact diversity

Logs, dumps, mobile captures, NAS copies, and iperf results are not treated as one blob.
That is useful.

## Where current Resilio still fragments the operator answer

### A) Intake sufficiency still has to be inferred from collection instructions

Current Resilio explains how to gather artifacts, but still leaves the receiver to decide informally whether the packet actually answers the live question.
The sufficiency judgment is implied, not normalized.

### B) `Readable` and `decision-grade` still blur together

A packet can arrive, open, and even validate structurally while still missing the only time window, peer role, or world-match fact that matters.
Current Resilio exposes these ingredients, but still does not compile them into one intake verdict.

### C) Supplement requests are still mostly free-text

Current official instructions ask for more detail and sometimes different artifacts, but still do not give the operator one place to say:

- what exact gap remains
- why this gap blocks the stronger sentence
- what cheapest supplement would raise the ceiling most
- what weaker sentence survives if no supplement comes back

### D) Packet mismatch is visible, but not unified

Wrong version window, wrong service principal, wrong source world, rotated-away logs, mobile-only capture, oversized logs, or a test run with Sync still active can all weaken intake truth differently.
Current Resilio shows the ingredients, but still does not normalize them into one intake object.

## Hard product decision unlocked by this pass

AnonSync should compile every serious received evidence packet into a first-class **evidence intake** object that separately expresses:

- intake target question or claim
- received packet ids and claimed artifact classes
- freshness and capture-window fitness
- world and scope match
- transform/redaction limits that still matter at decision time
- structural validation status
- analytic sufficiency status
- cheapest next supplement request
- supplement deadline or expiry
- surviving weaker sentence if supplement never arrives

## Replacement line for AnonSync

Borrow from Resilio:

- its candor that good support packets need timestamps, peer role, share/file names, and reproduction windows
- its honesty about rotation, size limits, platform-specific storage, and artifact diversity
- its recognition that a packet may need a different collection channel when automatic sending fails

Do not clone from Resilio:

- any workflow where sufficiency lives only in reviewer memory
- any contract where `packet received` is allowed to masquerade as `packet answers the question`
- any interface where supplement requests can be vague instead of gap-specific and burden-aware
- any product shape where a stale, wrong-world, or rotated-away packet quietly keeps the same claim ceiling

AnonSync should instead ship explicit pages for:

- evidence intake contract sheet
- intake sufficiency review
- supplement request proof
- intake timeline
- intake lineage receipt
