# Resilio decision portfolio, prioritization, dispatch, and starvation fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- synthesize several evidence packets into one integrated claim
- turn that claim into one honest decision charter
- separate allowed action from blocked stronger action
- preserve residual uncertainty and escalation posture

What it still lacked was the next ordinary operator answer:

> when several candidate decisions are all real enough to matter, which one actually goes now, which one is deliberately held, and what watch-only item is quietly aging toward starvation?

That is the seam this pass locks.
A product that can threshold one case honestly but cannot prioritize several at once still leaves too much truth in inbox motion, remembered annoyance, and analyst courage.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful attention surfaces, but mostly as separate signals rather than one cross-case dispatch workspace:

- `Sync Main View (Desktop)` still gives the operator filters for connected and disconnected shares, search, configurable columns, a 30-day History lane, visible peer/activity status, and a notification bell for approval requests or other events.
- `How do I perform a search in Sync?` still shows that search spans folders/files, connected devices, and users.
- `Core warnings` still clusters several warning families that may all matter at once.
- `Errors and warnings` and the broader `Errors & Troubleshooting` category still present issue families as separate article groups.
- `Some internal tasks are taking time to complete` still makes `watch and wait` a real posture because background operations may recover without immediate heavy intervention.
- `Performance overview` still exposes 1-minute, 10-minute, and 1-hour graphs that can influence urgency without becoming a dispatch rule.
- deeper artifact pages like `Collecting debug logs manually`, `Collecting crash reports, mini-dumps and core dumps`, and `Measuring network performance with iperf3` still define heavier investigative rungs that can compete for scarce attention.

## What current Resilio still gets right

### 1) It gives the operator many useful attention signals

Notifications, warnings, search, activity state, history, and graphs are all real clues.
That is worth borrowing.

### 2) It preserves that not every live thing deserves the same response

Some issues may self-recover.
Some deserve a watch posture.
Some call for immediate action.
Some justify heavy evidence capture.
That difference matters.

### 3) It keeps the practical surfaces lightweight

Filters, search, history, and warning pages are fast to inspect.
That operational lightness is useful.

## Where current Resilio still fragments the operator answer

### A) Priority still lives mostly in the reader's head

The product and docs show many things that may matter, but still do not compile them into one durable answer about which item wins dispatch right now.

### B) Signal presence is not the same as dispatch order

A lit bell, a warning, a graph spike, or a stalled queue may all feel urgent.
But current Resilio surfaces do not turn those signals into one explicit priority basis that can be reviewed later.

### C) Watch-only work can quietly starve

Resilio does acknowledge that some states can recover on their own.
But the operator still has to remember that a watch item exists, how long it has been waiting, and when patience has become neglect.

### D) Heavy capture can compete with lighter work without one portfolio explanation

Debug logs, crash artifacts, and iperf runs are real work.
Current Resilio pages explain how to perform them, but not one portfolio rule for when they should displace lighter or safer work already waiting.

### E) Preemption is more implicit than explicit

The operator can always change their mind.
But current Resilio surfaces do not preserve one first-class statement of what got displaced and why.

## What AnonSync should borrow

- many useful attention signals
- lightweight scanning surfaces
- candid acknowledgment that some issues deserve monitoring rather than immediate mutation
- practical investigative ladders

## What AnonSync should not clone

AnonSync should not clone a world where the operator must build dispatch order privately from separate warnings, bells, searches, graphs, history, and support articles.
It should not leave the following questions scattered across UI fragments and KB pages:

- which candidate decision goes now?
- which candidate is real but deliberately held?
- what factor actually made one item outrank another?
- what attention budget constrained the choice?
- what watch item is aging toward starvation?
- what exactly was preempted when a hotter case arrived?

## Product requirement extracted from this evaluation

AnonSync should own one stable page family for **decision portfolios**.
That family should make it ordinary to publish:

- candidate set
- priority factors
- explicit attention budget
- lane assignment across now / next / later / watch / hold / frozen
- dispatch winner and displaced work
- starvation guard
- preemption and reevaluation triggers

## Bottom line

Current Resilio still deserves credit for exposing many useful attention signals and practical troubleshooting surfaces.
But it still does not own one operator-facing answer to:

> when several live decisions all matter, what actually goes now, what stays held, and what waiting item is about to be forgotten?

That is why this seam belongs on the non-clone side.
