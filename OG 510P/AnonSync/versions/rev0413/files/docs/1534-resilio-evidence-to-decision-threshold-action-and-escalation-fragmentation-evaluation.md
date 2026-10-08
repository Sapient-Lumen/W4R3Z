# Resilio evidence-to-decision threshold, action, and escalation fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- intake packets honestly
- request the cheapest useful supplement
- synthesize several witness planes into one bounded integrated claim
- preserve conflict, contradiction, and synthesis ceiling

What it still lacked was the next ordinary operator answer:

> given the synthesized evidence we actually have right now, what is that enough to do, what stronger action is still blocked, and should the next move be act, monitor, ask, defer, or escalate?

That is the seam this pass locks.
A product that can merge evidence but cannot turn it into a thresholded decision still leaves too much truth in analyst courage, improvised escalation, and support folklore.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful witness planes and troubleshooting rungs, but mostly as separate surfaces rather than one decision-threshold workspace:

- `My files don't sync` still tells operators to inspect peers, status warnings, History, and upload/download queues, and then fan out into different possible next steps.
- `Some internal tasks are taking time to complete` still explains that some states can simply reflect background work, which makes `wait` or `monitor` a real route rather than a failure to decide.
- `Peers aren't connecting` still breaks one symptom into several materially different branches around multicast, firewall, routing, proxy, relay, and predefined hosts.
- `Performance overview` still exposes 1-minute, 10-minute, and 1-hour graphs that inform judgment but do not themselves declare what threshold is cleared.
- `Errors & Troubleshooting` still clusters warnings, self-help guides, and support-artifact pages as separate article families.
- `Collecting debug logs automatically` and `Collecting debug logs manually` still define a heavier evidence-capture burden, including enablement, restart, reproduction, and post-repro wait time.
- `Collecting crash reports, mini-dumps and core dumps` still defines a deeper escalation rung.
- `Measuring network performance with iperf3` still adds another specialized evidence rung and requires Sync to be completely shut down during the test.
- support articles still say direct technical support is available only for Sync Business and not Sync v3, which increases the importance of operator-side threshold judgment.

## What current Resilio still gets right

### 1) It admits that not every symptom needs the same next move

Some issues point toward waiting, some toward configuration checks, some toward network diagnosis, and some toward deep capture.
That is worth borrowing.

### 2) It preserves burden differences between rungs

Looking at warnings is cheaper than restarting with debug logging.
An iperf3 run is different from a history check.
A core dump is much heavier than a queue glance.
That honesty matters.

### 3) It keeps troubleshooting practical

The articles are not abstract.
They tell operators real next moves.
That practical candor is valuable.

## Where current Resilio still fragments the operator answer

### A) Threshold truth still lives in the reader's head

The operator can usually find relevant pages, but still must decide privately whether the current evidence is enough to:

- wait and observe
- ask one more discriminating question
- perform a bounded repair
- escalate for deeper artifacts
- publish a conclusion

The docs give ingredients and ladders, but not one explicit threshold object.

### B) Claim strength and action readiness are not compiled together

A graph can be suggestive.
A warning can be actionable.
A log can be rich but stale.
A support artifact can be costly but still inconclusive.
Current Resilio surfaces do not compile those facts into one sentence about what action is justified now.

### C) `no decision yet` is not owned as a product state

The docs can imply patience or deeper investigation, but the product shape still pushes the operator to infer whether unresolved uncertainty is acceptable or disqualifying.

### D) Escalation burden is described more clearly than escalation justification

Resilio explains how to gather logs, dumps, and tests.
It is less explicit about when those rungs are proportionate given the actual uncertainty left.

## What AnonSync should borrow

- typed troubleshooting ladders
- practical next-step candor
- burden honesty across light and heavy evidence rungs
- separate witness surfaces rather than one vague health badge

## What AnonSync should not clone

AnonSync should not clone a world where the operator must translate synthesized evidence into action mainly through private judgment.
It should not leave the following questions scattered across warnings, articles, and support instructions:

- what threshold is actually cleared?
- what action verb is justified now?
- what stronger verb stays blocked and why?
- what uncertainty budget remains too large to spend?
- what next fact or event would most efficiently change the threshold?

## Product requirement extracted from this evaluation

AnonSync should own one stable page family for **decision charters**.
That family should make it ordinary to publish:

- target decision
- evidence basis used
- current claim ceiling
- action threshold cleared
- uncertainty budget remaining
- allowed next verb
- blocked stronger verb
- reopen trigger and escalation trigger

## Bottom line

Current Resilio still deserves credit for exposing useful evidence planes and real troubleshooting ladders.
But it still does not own one operator-facing answer to:

> given the synthesized evidence we have right now, what is it actually enough to do?

That is why this seam belongs on the non-clone side.
