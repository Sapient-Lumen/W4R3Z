# Cleanup outcome receipt page: freed scope, surviving witness, and strongest safe claim interface spec

## Purpose

This receipt proves the result of one reviewed cleanup action.
It answers:

> what was actually cleaned up, what still survived, and what is the strongest honest sentence I am allowed to say now?

## Core rule

Every consequential cleanup apply must emit one durable **Cleanup outcome receipt**.
That receipt owns:

- requested cleanup family
- effective cleanup family
- freed scope
- surviving witness summary
- strongest approved claim
- stronger forbidden overclaim
- linked preservation receipts if any

## Primary receipt layout

The receipt always renders the same regions:

1. outcome summary
2. requested versus effective cleanup
3. freed-scope matrix
4. surviving-witness matrix
5. claim ceiling block
6. linked receipts and follow-up actions

### 1) Outcome summary

Show:

- subject / seat / app target
- cleanup family
- outcome class (`applied`, `applied-with-narrower-scope`, `preserved-first-then-applied`, `blocked`, `aborted`)
- one-line honest summary

### 2) Requested versus effective cleanup

Show where the effect differed from the request, for example:

- requested `erase all local residue`
- effective `app removed; shared folders remained; hidden archive retained`

### 3) Freed-scope matrix

Rows should cover:

- local materialized bytes
- placeholders / namespace view
- linked row / share visibility
- hidden archive bytes
- service/log/config roots
- ordinary shared folders
- platform-forced local file loss

For each row show `removed`, `preserved`, `moved`, `unknown`, or `not-in-scope`.

### 4) Surviving-witness matrix

Show which witness classes remain after the cleanup and where:

- rollback bytes
- event/history witness
- placeholder visibility
- hidden local residue
- external peer-only witness
- manual export witness

### 5) Claim ceiling block

Always render:

- strongest approved sentence
- stronger forbidden sentence
- residue or missing proof that blocks the stronger sentence

Examples:

- approved: `local copies cleared; recovery witness preserved only in exported bundle`
- forbidden: `all evidence erased`

### 6) Linked receipts and follow-up actions

Show:

- preservation receipt refs
- recovery-horizon receipt refs
- further cleanup still required
- next safe action

## Rules

### Rule 1 — receipts must preserve non-effects

What did *not* happen is part of the result.

### Rule 2 — stronger forbidden phrase is mandatory

The receipt is incomplete if it does not name at least one tempting overclaim the action still did not earn.

### Rule 3 — platform-caused loss must remain typed

If local files vanished because of seat architecture rather than because the product deleted them, the receipt must say so.

## CLI shape

```text
anonsync cleanup review --target <target>
anonsync cleanup apply <review>
anonsync cleanup receipt show <receipt>
```

## Honest outputs

This receipt may conclude:

- `Local payload evicted; placeholder view preserved; later fetch still depends on surviving full-copy witness.`
- `Linked-device presence removed; external remote retainers may still exist.`
- `App removed; hidden archive residue required separate cleanup and was preserved intentionally.`
- `Preserve-first export completed; cleanup then narrowed local evidence but retained manual rollback proof.`
