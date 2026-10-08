# Resilio paused-label origin split and named-state drift evaluation

## Why this seam matters

Another current official Resilio pass exposes a stronger non-clone reason than a generic `pause is partial` note.
Current official docs still use the same visible word — **Paused** — across manual pause, global pause, and scheduler pause surfaces, but the documented signal matrix is not one stable thing.
The current `How to pause syncing` article still says pause means only bits download/upload are stopped, that zero-sized files and deletions still sync, and that new files are still rescanned and indexed so share size can keep increasing.
The current `Running Sync on schedule` article still says scheduled `Paused` means upload and download speed are zero, yet paused peers can still upload files to other non-paused peers while not downloading themselves; that same article still says deletions sync anyway and new files are still rescanned and indexed.
Current `Sync Preferences` still presents **Global Pause/Resume** and **Scheduler** as nearby ordinary controls, while the live Sync v3 line still runs through **3.1.2.1076**.

That is exactly the kind of truth AnonSync should not hide under one calm badge like `Paused`.
The product contract already has several materially different layers:

1. **visible state word** — the label the operator sees
2. **origin** — manual, scheduled, global, inherited, or emergency
3. **signal matrix** — outbound bytes, inbound bytes, deletes, indexing, discovery
4. **exception lanes** — zero-sized files, delete propagation, and origin-specific upload behavior
5. **safe sentence** — what the product may honestly promise from that state

Resilio is candid that selective pause semantics are real.
The non-clone problem is again workflow ownership.
The operator can still be pushed into multiple help pages before the product owns one ordinary answer to:

> **what exactly does `Paused` mean here, why does it mean that here, and what can still move anyway?**

## What current official docs still say

### 1) Manual/folder pause is already not a full freeze

The current `How to pause syncing` article still says:

- pause only stops bit upload/download work
- zero-sized files still sync
- deletions still sync
- new files are still rescanned and indexed
- share size can continue growing on a paused peer

So even the ordinary manual pause contract is already a matrix, not a stop-everything state.

### 2) Scheduled `Paused` keeps a different outbound lane alive

The current `Running Sync on schedule` article still says:

- `Paused` means both upload and download speed are zero
- only bits downloads are stopped
- paused peers can still upload files to other non-paused peers
- deletions still sync anyway
- new files are still rescanned and indexed

That means the **same visible word** can carry a different documented outbound rule depending on origin.

### 3) Preferences keep these controls adjacent without one unified semantic page

The current `Sync Preferences` article still presents **Global Pause/Resume** and **Scheduler** as ordinary nearby controls.
That is useful convenience.
But it also means a product must not assume the label explains the contract.
If origins differ, the visible state word must either narrow to one stable matrix or be explicitly qualified.

## Why AnonSync should not clone this contract

AnonSync should absolutely borrow Resilio's candor that pause-like controls are selective and that deletes, indexing, and some other lanes may remain alive.

AnonSync should **not** clone a contract where:

- one visible token like `Paused` can mean different signal matrices by origin
- manual pause and scheduled pause sound interchangeable while their documented outbound semantics differ
- deletes and indexing continue under a word that reads like a full freeze
- the operator discovers origin-specific exceptions only from support prose after a surprising result

The product should instead surface one ordinary answer before the user trusts the label:

> **Which exact signal matrix does this state word mean here, and is that matrix stable across all origins that reuse the word?**

## Product obligations this evaluation adds

AnonSync should add one explicit family around **named-state honesty**:

1. **State token posture** — visible word, origin, exact signal matrix, and strongest safe sentence
2. **State token change review** — before switching origins or reusing a word, show the semantic delta
3. **State token evidence** — prove which origin and matrix are actually active now
4. **State token receipt** — preserve the word, origin, matrix, and any origin-specific exceptions that were in force

## Tightened conclusion

Borrow Resilio's candor that pause is selective and origin-bearing.
Do not clone a product contract where one familiar visible word like `Paused` still hides **delete-through**, **indexing-through**, and **origin-dependent outbound semantics**.
