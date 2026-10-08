# Preseed reuse, dedup proof, and local-block witness interface spec

## Purpose

The archive already had pre-existing-material reconciliation, byte-witness, and staged-transfer language.
What it still lacked was one explicit contract for a subtler question:

> when the product claims it can avoid re-downloading bytes because local material already exists, what page proves whether it is hashing, reusing blocks, falling back to full transfer, or silently starting over?

Current official Resilio docs make this seam sharper than a generic `fast sync` claim would.
They still say only changed pieces are usually transferred, but if changes shift all pieces the whole file will be re-synced.
They still say a receiving peer may hash local files for pre-seeded folders, may copy local file blocks instead of re-downloading them, and may increase disk usage while doing so.
They also still expose power-user settings where lazy indexing delays hash calculation until another peer requests it, where small files may be transferred as direct torrents and restart from the beginning after interruption, and where some optimization choices explicitly trade verification work for simpler re-download behavior.

That is useful capability.
It is still not a good public reuse-proof contract.

## Core decision

AnonSync should make **local reuse claims** first-class.

Every adoption, reconnect, or large update that may reuse local bytes must expose:

- what local material is being considered as a candidate witness
- what proof has or has not been established yet
- whether reuse is piece-level, file-level, or impossible
- whether interruption would resume from checkpoint or restart from zero
- what local disk and CPU cost is being paid to avoid network cost

If the product still says `already have these files` without proving what was actually reused, the interface is not explicit enough.

## Why this matters

Current Resilio docs still reveal seven truths AnonSync should not clone:

- pre-seeded acceptance can still begin as optimistic local hashing rather than proved equivalence
- deduplication can still amplify local disk work while looking like a quiet network stall
- piece-level reuse and whole-file fallback are still materially different outcomes
- shift-heavy edits can still invalidate piece alignment and trigger full resend
- some optimization modes still trade stronger continuity for faster small-file transfer with restart-from-zero risk
- lazy hashing can move proof later in time than operators expect
- `download avoided` and `network quiet` are not the same truth

AnonSync should therefore keep one stronger rule:

> every reuse claim must publish witness strength, fallback risk, and local resource cost before the operator mistakes hope for proof.

## Fixed review order

Every non-trivial reuse incident should render the same sections in the same order:

1. **Candidate witnesses now**
2. **Reuse class and fallback boundary**
3. **Local cost versus network cost**
4. **Receipt and replay promise**

### 1) Candidate witnesses now

This section should show:

- which local files or blocks are candidates for reuse
- source of candidacy: pre-seeded target, same-device duplicate, history cache, local block pool
- witness strength: `announced only`, `mtime-size match`, `hashed equal`, `piece-map proven`, `full-file proven`
- any missing proof still required

The operator must be able to answer: **what local material is being trusted, and how strongly?**

### 2) Reuse class and fallback boundary

This section should show:

- reuse class: `none`, `file-level`, `piece-level`, `mixed`
- whether a shifted edit will force full resend
- whether the active transfer mode can resume from checkpoint or restart from zero after interruption
- any policy or target feature that disables reuse

The operator must be able to answer: **what exactly will be reused, and when does the system fall back to more expensive transfer?**

### 3) Local cost versus network cost

This section should show:

- expected local read/hash/copy burden
- expected network bytes avoided or still required
- whether the current bottleneck is local verification rather than remote fetch
- whether the workload is safe to continue on this host budget

The operator must be able to answer: **what resource bill is being paid to obtain this reuse?**

### 4) Receipt and replay promise

This section should show:

- final witness class reached
- actual bytes reused locally
- actual bytes fetched remotely
- whether fallback occurred
- the durable proof record for CLI/API parity

The operator must be able to answer: **did the product really reuse local material, and how much?**

## Main surface

The subject workspace should expose a **Local reuse** card with:

- count of candidate objects
- strongest witness class achieved so far
- bytes locally reused
- bytes still requiring fetch
- a drill-in action: `Inspect reuse proof`

## Detailed surface

The detailed page should have five panes.

### Pane A — Candidate table

Columns:

- object
- candidate source
- witness class
- reuse class
- fallback risk

### Pane B — Piece/file proof view

Shows:

- file-level equality proofs
- piece maps proven so far
- shifted-layout warnings
- restart-from-zero risk if applicable

### Pane C — Cost model

Shows:

- local reads
- local hashes
- local block copies
- network bytes remaining
- expected resource pressure class

### Pane D — Repair actions

Actions:

- continue proving and reuse
- prefer network fetch over local reuse
- quarantine suspect local witness
- require full-file verification before commit

### Pane E — Receipts

Shows prior reuse receipts and fallback events.

## CLI parity

Minimum commands:

- `anonsync reuse show <subject>`
- `anonsync reuse inspect <subject> --object <id>`
- `anonsync reuse require-full-proof <subject> --object <id>`
- `anonsync reuse receipt show <receipt-id>`

## Non-goals

This spec does **not** define:

- compression policy
- scheduler priority
- ordinary transfer finalization after proof is complete
- business or license packaging of advanced delta features
