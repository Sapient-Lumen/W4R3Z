# 485 — Effective-state resolution, correction graphs, and no authority by feed order

## One-line thesis

When consequential public-AI notices, status updates, corrections, withdrawals, and superseding records accumulate over time, the institution should compute and publish one deterministic effective current state from explicit lineage links, and should treat forks or unresolved ambiguity as incidents rather than letting feed order, CMS recency, or whichever copy looks newest decide authority.

## Why this matters

The archive already requires canonical disclosure heads, correction chains, durable status surfaces, case lineage, and history-preserving navigation. What it still lacked was one sharper rule for the question people actually ask first: **what is the current official state right now?**

That question becomes fragile once several notices coexist. A service banner is narrowed by a later post but not formally withdrawn. An incident page is corrected while an API feed still exposes the older text. A public rights notice is superseded for one route but not another. A correction exists, but only in one channel. Several records are all individually preserved, yet the archive still leaves the public and reviewers to guess which combination of them is the present governing state.

Without an effective-state rule, the archive can preserve lineage perfectly while failing the operational accountability question. The public then learns the current state from feed order, page freshness, informal staff memory, or screenshot folklore instead of from a deterministic authority model.

## Pattern pack

### 1. Preserve typed lineage links between notices

Each consequential notice or status-bearing record should preserve whether it:

- supersedes an earlier record,
- corrects an earlier record,
- narrows or partially withdraws an earlier record,
- fully withdraws an earlier record,
- or stands parallel because it covers a different scope.

A stream of records without typed edges is only a chronology, not a resolution model.

### 2. Compute heads by lineage, not by recency alone

The current authority-bearing state should be derived from the records that remain active heads after typed supersession and withdrawal links are applied. A record should not become the head merely because it was most recently rendered, uploaded, or cached.

Where several heads intentionally coexist, each should carry explicit scope labels so the public can tell why plurality is legitimate.

### 3. Attach corrections to the effective state instead of hiding them in history

A correction should remain visible alongside the active state it affects. The institution should not require a reviewer to separately discover that the active notice is only understandable in light of a correction chain.

Correction visibility is part of effective state, not only archival history.

### 4. Detect forks and unresolved ambiguity as live governance defects

If two records both claim to supersede the same predecessor, or if two current candidates exist for the same scope with no admissible reason, the archive should surface that as a live defect or incident. The right answer is not to let users infer authority from whichever copy ranked first in a feed.

### 5. Keep scope explicit when several current states legitimately coexist

Plural current states can be real when they differ by:

- jurisdiction,
- audience lane,
- route or service phase,
- accessibility mode,
- emergency override window,
- or incident family.

The archive should make that scope machine-readable and human-legible so plurality does not look like contradiction.

### 6. Separate current effective state from historical record order

The archive should preserve at least three distinct truths:

- the historical sequence of records,
- the lineage graph between them,
- and the current effective state after resolution.

Chronological order alone should not have to do all three jobs.

### 7. Refuse silent fallback to last-write-wins editing

CMS edits, page refreshes, mirrored copies, and feed-window trimming should not silently redefine authority. If the effective state changed, the archive should preserve a new typed record or an explicit lineage update that makes the change reviewable.

### 8. Export effective-state reasoning into public and review surfaces

Public status boards, appeal packets, operator views, and regulator exports may display different detail levels, but each should be able to answer:

- which records formed the current effective state,
- what corrections remain attached,
- whether any ambiguity is unresolved,
- and which scope makes this state the relevant one.

## Guardrails

- Do not let feed order or page freshness decide authority by accident.
- Do not hide corrections in a separate history surface if they affect the current meaning.
- Do not pretend plurality is acceptable when it is really unresolved fork.
- Do not let one channel silently drift into a different effective state from another.
- Do not reduce typed lineage to one vague “updated” badge.

## Failure modes

- **feed-order authority**: the record that appears last is mistaken for the governing one.
- **forked current state**: several records claim the same live scope with no explicit resolution.
- **correction exile**: the correction exists historically but not on the current-state surface.
- **scope blur**: two legitimate heads look contradictory because their boundaries are hidden.
- **silent last-write-wins**: a consequential change appears only as a page edit, not as a typed lineage event.

## Practical tests

An effective-state discipline passes when it can answer yes to all of the following:

1. Do consequential notices preserve typed supersession, correction, withdrawal, or scope-parallel relations?
2. Can the institution compute a deterministic current effective state without relying on editorial recency?
3. Are corrections visibly attached to the active state they affect?
4. Do conflicting current candidates surface as incidents or defects rather than as silent ambiguity?
5. Can public and review surfaces explain why a particular state is the current relevant one?

## Compression rule for the archive

If an institution can preserve every notice but cannot also say **which typed chain yields the current effective state, which corrections still attach, and whether any fork remains unresolved**, then it is still letting **record order impersonate authority**.
