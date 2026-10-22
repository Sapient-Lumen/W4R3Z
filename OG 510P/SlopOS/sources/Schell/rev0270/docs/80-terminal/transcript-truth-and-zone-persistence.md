# Transcript truth and zone persistence

This surface exists because the archive now has enough semantic-zone ambition that it needs a text-truth rule for logs, SSH, and plain terminals.

## Core question

When a rich terminal knows about prompts, review cards, receipts, denials, and shelves, what must survive into a plain text transcript so the session still tells the truth?

## Working answer

A transcript should preserve at least:

- boundary type (`prompt`, `input`, `review`, `output`, `receipt`, `denial`, `background-change`),
- stable local ids or handles when available,
- short human-readable summaries,
- ordering in time,
- and the references needed to reopen the richer local rendering later.

## Important split

### Shell truth

The shell owns:

- the meaning of the boundary,
- the ids and handles,
- the action/object references,
- and the receipt/denial lineage.

### Semantic transport

The transport only needs to preserve enough structure that a transcript or remote hop can say,
"a review happened here," "a denial happened here," or "this receipt belongs to that request."

### Local luxury UX

A richer terminal may restore cards, panes, shelves, previews, and block jumps from the same underlying references.

## Bootstrap rule

Do not require one canonical wire format yet.
Instead require that any early format can round-trip these truths:

- review boundary identity,
- receipt boundary identity,
- denial boundary identity,
- request↔receipt / request↔denial linkage,
- and enough text to remain understandable without the richer renderer.

## Why this matters now

Without this rule, Schell could accidentally make its best features disappear the moment the user goes remote, saves a transcript, or replays work outside the fancy terminal.
