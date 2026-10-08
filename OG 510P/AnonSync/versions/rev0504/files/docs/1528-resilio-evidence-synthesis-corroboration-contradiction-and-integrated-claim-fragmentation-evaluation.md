# Resilio evidence synthesis, corroboration, contradiction, and integrated-claim fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- choose the next best discriminator
- capture and package evidence honestly
- preserve custody and redaction truth
- judge whether one packet is decision-grade for a named question
- request the cheapest useful supplement when one packet is not enough

What it still lacked was the next ordinary operator answer:

> now that several packets and witness planes exist, which ones genuinely reinforce one another, which just repeat the same root observation, which actively conflict, and what strongest integrated sentence survives the whole set together?

That is the seam this pass locks.
A product that can intake packets one by one but cannot synthesize them honestly still leaves too much truth in chat, analyst memory, and support folklore.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful witness planes, but mostly as separate surfaces rather than one synthesis workspace:

- `Send info to Support team` still groups mobile logs, iperf3, automatic log sending, manual log sending, crash reports, and NAS core-dump flows as separate support articles.
- `Collecting debug logs automatically` still asks for peer role, timestamps, detailed problem description, and affected shares/files, which can make one packet richer but still does not merge it with other witness types.
- `Collecting debug logs manually` still varies log retrieval by desktop, service principal, config `storage_path`, NAS, and Android lane, which means one packet may already come from a different world than another.
- `Collecting crash reports, mini-dumps and core dumps` still introduces a heavier artifact class with its own path, crash posture, and storage semantics.
- `Measuring network performance with iperf3` still adds a separate network-performance artifact that can be decisive for one question while being largely orthogonal to another.
- `Performance overview` still exposes short-window real-time graphs and peer/disk metrics useful for troubleshooting, but on a different surface from support packets.
- `Sync Main View (Desktop)` still exposes search, notifications, online-vs-total peer counts, current activity, and a 30-day History lane as yet another witness surface.
- `Errors & Troubleshooting` still clusters symptom and support pages as separate article families rather than a merged evidence-adjudication object.
- current support articles still say direct technical support is only for Sync Business and not Sync v3, which pushes even more synthesis burden back onto the operator.

## What current Resilio still gets right

### 1) It preserves witness diversity

Logs, dumps, performance tests, peer lists, history, warnings, and graphs are not collapsed into one bland blob.
That is worth borrowing.

### 2) It makes source-world differences real

Service-principal paths, config-defined storage paths, mobile capture lanes, NAS-local storage, and UI witness planes all matter.
That honesty is useful.

### 3) It reveals that one artifact rarely answers everything

A packet can be strong for one question and weak for another.
A network test can be decisive for throughput but not for state corruption.
A history lane can show activity but not root cause.
That realism matters.

## Where current Resilio still fragments the operator answer

### A) Synthesis still lives in the operator's head

Current Resilio exposes many evidence ingredients, but still leaves the receiver to decide informally which ones are independent and which are just restating the same situation from a new angle.
The synthesis judgment is implied, not normalized.

### B) Duplicate support and corroboration still blur together

A main-view peer count, a performance graph, and a log excerpt may all derive from the same underlying connectivity condition.
Current Resilio shows them separately, but still does not force the operator to say whether the support is genuinely independent.

### C) Contradictions still lack a canonical home

A packet that suggests healthy transport can coexist with a history lane that shows stalled or missing work.
A log packet from one world can coexist with a UI witness from another.
Current Resilio provides the artifacts, but still does not give one place to say which contradiction remains unresolved and how it caps the merged sentence.

### D) Weighting still has to be improvised

A crash dump, a 15-minute debug log, an iperf run with Sync shut down, a 30-day History view, and a 1-hour graph window do not all carry the same decisional force.
Current Resilio never really denies this, but still does not normalize the weighting contract.

## Hard product decision unlocked by this pass

AnonSync should compile every serious multi-packet reading into a first-class **evidence synthesis** object that separately expresses:

- target question and candidate stronger sentence
- participating packet and witness ids
- packet freshness and world fit for each source
- relation class between each source pair
- duplicate-versus-independent support judgment
- contradiction and open mismatch list
- discount reasons and supersession reasons
- weighted basis for the merged sentence
- strongest safe integrated sentence
- strongest blocked sentence and the conflict or gap still blocking it

## Replacement line for AnonSync

Borrow from Resilio:

- its candor that different witness planes really do matter
- its willingness to expose graphs, peer status, history, logs, dumps, and network tests as separate diagnostic ingredients
- its realism that some packets are platform-specific, world-specific, or question-specific

Do not clone from Resilio:

- any workflow where synthesis only happens in human memory
- any contract where packet count can masquerade as evidentiary strength
- any interface where duplicate support and independent corroboration blur together
- any product shape where contradictions remain visible only as scattered notes instead of merged-claim blockers

AnonSync should instead ship explicit pages for:

- evidence synthesis contract sheet
- corroboration and conflict review
- integrated-claim proof
- synthesis timeline
- synthesis lineage receipt
