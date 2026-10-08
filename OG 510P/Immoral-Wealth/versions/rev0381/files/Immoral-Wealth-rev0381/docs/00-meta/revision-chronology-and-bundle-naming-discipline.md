---
status: active_bridge
claim_kind: archive_governance
route_role: archive_governance_core
canonical_anchor: false
route_refs:
- archive_governance_core
supersedes: null
depends_on: []
source_refresh_due: '2026-12-31'
case_pressure: rev0304_portfolio_calibration
---

# Revision chronology and bundle-naming discipline

## What this note is for

This archive already has strong rules for **what earns bytes**, **which note governs**, and **when older notes stop being live**.
What it still needs is a compact rule for **how revisions identify themselves over time** so bundle names, receipts, indexes, and changelog entries remain trustworthy instead of forcing later readers to guess which build came first.

Use this note with [`archive-policy.md`](archive-policy.md), [`archive-growth-budgets-and-refactor-triggers.md`](archive-growth-budgets-and-refactor-triggers.md), [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md), and [`doctrine-precedence-and-conflict-repair.md`](doctrine-precedence-and-conflict-repair.md).

## Canonical order rule

The archive's **canonical revision order** is the revision number.
`rev0165` comes after `rev0164` even if a prior timestamp or bundle clock string is wrong, reconstructed, or locally inconsistent.

Use timestamps to aid orientation, not to override the revision sequence.
If revision number and wall-clock label ever conflict, the archive should treat the higher revision number as canonical and explicitly repair the chronology in the next receipt.

## Timestamp basis rule

Bundle timestamps should use the archive's stated working local time.
For this archive that means the local New York wall clock in the form:

`YYYY.MM.DD.HH.MM`

A bundle timestamp should describe **when that revision bundle was produced**, not when an older source was read, when a prior draft started, or when a later route cleanup was imagined.

## Bundle-entry timestamp rule

The bundle should not tell two different time stories at once.
If the zip name and receipt use the current build timestamp, the file entries inside the released zip should normally carry that same build-time basis rather than stale working-copy mtimes from older revisions.

The archive does not need per-file historical editing times inside the released bundle.
For release trust, one declared build clock is usually better than a mix of old local mtimes that make the bundle look older than the revision it claims to be.

## Monotonic naming rule

Under ordinary conditions, both of these should move forward together:

1. revision number,
2. bundle timestamp.

A later revision should not normally carry an earlier timestamp string than the bundle it supersedes.
If that happens because of a clock error, timezone slip, or packaging mistake, the next revision should:

- keep the new revision number,
- use the correct current local timestamp,
- and acknowledge the anomaly in `REVISION-RECEIPT.json` and `CHANGELOG.md` instead of silently pretending the sequence is clean.

## Bundle-name rule

The retained zip name should stay compact and predictable:

`Immoral-Wealth-rev####-YYYY.MM.DD.HH.MM-summary-codename.zip`

Where:

- `rev####` is the canonical sequence label,
- the timestamp is the local archive build time,
- `summary-codename` is short, descriptive, and stable enough to identify the revision's main move.

Do not rename older released bundles merely to make the past look cleaner.
Repair the record prospectively in the next revision note.

## Receipt rule

`REVISION-RECEIPT.json` should always state:

- the revision number,
- the bundle name,
- the timestamp used in the bundle name,
- the latest bundle actually read,
- and, when needed, a plain-language chronology note explaining any anomaly.

The receipt exists so future readers do not have to infer sequence from filenames alone.

## Index and changelog rule

`README.md`, `ARCHIVE_INDEX.md`, `ARCHIVE_INDEX.json`, and `CHANGELOG.md` should agree on the current revision identity.
If a revision introduces a chronology repair, the human-readable surfaces should say so plainly rather than letting the fix hide only in machine-readable metadata. `CHANGELOG.md` should remain a thin accumulating revision ledger distinct from the full current-revision receipt in `REVISION-RECEIPT.json`; a changelog that merely duplicates the current receipt is archive-memory waste, not chronology discipline. When same-minute revisions, future-stamped anomalies, or repaired clock slips exist in the live record, `ARCHIVE_INDEX.json` should also expose a compact top-level chronology-order surface so later tools do not have to reconstruct ordering rules from prose alone. If the archive also surfaces retained changelog coverage as a top-level revision-memory scope, prefer explicit span bounds rather than a start-only marker when the retained ledger is intended to run through the current revision. When that bounded scope is meant to describe a continuous retained recent ledger, the scope should also say whether the span is contiguous and, where practical, how many retained revision entries are intentionally present so later readers do not have to infer whether the named range contains gaps. If the bounded retained scope is also meant to reach the live bundle, the scope should say that explicitly rather than making later readers infer current-revision inclusion from the end marker alone. Once bounded span, contiguity, entry count, and current-revision inclusion are already explicit, the scope should also say whether the retained thin ledger is read latest-first or oldest-first so readers do not have to reverse-engineer direction from the current text order of `CHANGELOG.md`. And if `CHANGELOG.md` carries its own ledger-scope preface, that preface should either state the same bounded span, continuity, current-revision inclusion, and sort order locally or point readers directly to the authoritative `revision_memory_scope` object instead of naming only one edge of the retained range. When the top-level scope is already present and trustworthy, prefer the shorter pointer rather than a second long prose recap of the same retained-ledger facts.

## Historical-anomaly rule

Past chronology mistakes are archive facts once released.
Do not rewrite old receipts or old bundle names after release unless the archive is intentionally producing a marked historical reconstruction.
Instead:

- preserve the old bundle as part of the record,
- state the anomaly in the next revision,
- and restore monotonic discipline going forward.

## Fast use rule

Use this note whenever a revision changes bundle naming, timestamp handling, receipt structure, or top-level identity files.
A compact archive should not make readers solve a forensics problem just to know which revision is current.
