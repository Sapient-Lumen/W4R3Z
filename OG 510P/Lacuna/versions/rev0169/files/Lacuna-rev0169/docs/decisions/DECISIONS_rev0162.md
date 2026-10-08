# Decisions — rev0162

## D-162-01 — put replication above, not inside, the single-block runner

A bundle owns ordering, witnessing, sealing, and aggregate custody while every child remains an ordinary rev0161 scenario run. Reusing the child protocol avoids a second implementation of condition assignment, cell validation, ratings, and report reconstruction.

## D-162-02 — require the full block roster before publication

A bundle must contain two to 128 blocks at `begin`. Blocks cannot be appended after a result is observed. Every scheduled block is included in the report.

## D-162-03 — precreate every child and assignment atomically

Build all child runs, hidden assignments, and exact seed clones inside one owner-private staging tree and publish the whole tree only after complete preflight. Do not create the next replicate lazily after seeing earlier outcomes.

## D-162-04 — randomize one private block order

Use a retained master seed and canonical SHA-256 ordering to fix block order, child identities, and assignment seeds. Call this deterministic custody, not a trusted randomness oracle.

## D-162-05 — expose a public commitment without condition mappings

Commit the full plan/schedule digests and per-block seed/capsule/assignment boundaries while retaining opaque labels. This permits external retention without giving blind raters the hidden mapping.

## D-162-06 — make external witnessing optional but executable

A plan may require a fixed number of receipt records before block execution. Lacuna verifies binding to the commitment and uniqueness of witness/receipt IDs, but does not claim to verify the external service.

## D-162-07 — execute blocks serially in the private fixed order

One active block makes authority hyperlegible and reduces accidental preview. Parallel execution can be added only with an explicit contamination and lock model; it is not smuggled into v1.

## D-162-08 — seal all blocks before unblinding any

Sequential unblinding would expose earlier outcomes while later execution choices remain. A seal freezes each rated child and leaves its report unpublished. Only the all-sealed state permits the parent to enter unblinding.

## D-162-09 — treat direct early child unblind as contamination

Do not recover it as cache drift. Emit a typed premature-unblinding refusal because the information boundary has already been crossed.

## D-162-10 — require one comparable rating contract

Every capsule must use identical rating prompts, dimensions, scale, and fixed rater count. Story/model/script differences remain explicit strata rather than hidden incompatibilities.

## D-162-11 — preserve ordinal observations at rater level

Retain integer scores and ranks; emit only sums and counts as descriptive conveniences. Do not automatically calculate a winner, p-value, effect, interval utility, or exclusion-adjusted result.

## D-162-12 — include refusals and failures

Terminal `completed`, `refused`, and `failed` cell states all appear in aggregate counts and observations. Operational failure is part of method performance, not missing data to erase silently.

## D-162-13 — enforce cross-block declaration separation before mutation

Reject a candidate return that reuses a prior block's declared context or provider invocation ID before writing it into the active child. Repeat the global check during every full audit.

## D-162-14 — make unblinding resumable, not restartable

Durably enter one unblinding phase with one timestamp, publish child reports idempotently, and build one deterministic aggregate. Never sample replacement assignments after a crash.

## D-162-15 — distinguish canonical JSON from spreadsheet export

JSON retains exact authored text. CSV is a derived convenience surface and neutralizes common formula-leading text to avoid turning rater comments or strata into spreadsheet commands.

## D-162-16 — remove competing experiment vocabularies

Delete the unfinished `experiments` and `scenario_studies` modules and retain one `scenario_bundles` contract. A model-facing entrance is less reliable when several near-synonymous state machines appear authoritative.

## D-162-17 — keep the player entrance entirely separate

“Will you DM?” remains sufficient to begin play. Bundle operation belongs to an experiment owner, not the player or the ordinary DM chat.

## D-162-18 — compile subagent work but do not require native subagents

Every frontier host receives the same exact local role/input/schema/return contract. Native subagents, separate chats, API contexts, and a human paste bridge are implementations of that contract; none is silently treated as proof of independence.
