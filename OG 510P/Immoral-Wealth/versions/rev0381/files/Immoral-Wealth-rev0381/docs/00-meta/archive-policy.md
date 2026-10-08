---
status: live_anchor
claim_kind: archive_governance
route_role: archive_governance_core
canonical_anchor: true
route_refs:
- archive_governance_core
- source_governance_core
supersedes: null
depends_on: []
source_refresh_due: '2026-12-31'
case_pressure: rev0304_portfolio_calibration
---

# Archive policy

## Inclusion rule

A document belongs in this archive if it does at least one of the following:

- sharpens the definition of immoral wealth inequality,
- improves the target distribution,
- identifies a real policy lever,
- improves measurement,
- clarifies sequencing or failure modes.

## Exclusion rule

Do not keep material that is mostly:

- raw download bulk,
- duplicate literature summary,
- long quotation,
- uncited opinion that could be replaced by a tighter claim,
- source artifact warehousing.

## Source discipline

- Keep **links, titles, short annotations, and relevance notes**.
- Do not retain PDFs in the long-run archive.
- Use source IDs (`[S01]`, `[S02]`, ...) so docs stay compact.
- Prefer high-quality public anchors: WID, OECD, IMF, ILO, Urban Institute, peer-reviewed work.
- For deciding whether a source earns a new retained byte, a refresh in place, or no long-run archive weight, use `docs/00-meta/source-refresh-and-citation-compression.md`.
- For deciding whether a proposed source fills a real coverage gap or merely thickens an already-covered support function, use `docs/00-meta/source-function-map-and-coverage-gaps.md` and the compact coverage map in `SOURCES.md` / `SOURCES.json`.
- For case-source precedence and disagreement handling, use `docs/20-program/source-order-and-conflict-resolution.md`.

## Refactor rule

When a later revision can merge, slim, or dedupe files without losing a live distinction, do it.
This archive should grow by **compression with clarity**, not by drift toward a junk drawer.


## Triage rule

Use [`research-triage-and-closure-rules.md`](research-triage-and-closure-rules.md) before adding a new research-facing note or expanding an open empirical branch.
Prioritize questions that would change verdict, package choice, rails, or pass / de-escalation confidence.
Prefer tightening, bridge notes, and demotion of parked questions over parallel branches.
Use [`archive-growth-budgets-and-refactor-triggers.md`](archive-growth-budgets-and-refactor-triggers.md) when deciding how much space a new note should get and when existing notes should be merged, split, trimmed, or compressed.
Use [`revision-chronology-and-bundle-naming-discipline.md`](revision-chronology-and-bundle-naming-discipline.md) when deciding how revisions should identify themselves over time, how bundle timestamps should behave, and how chronology anomalies should be repaired without rewriting released history.
Use [`release-readiness-and-bundle-integrity-checks.md`](release-readiness-and-bundle-integrity-checks.md) when deciding whether a revision is actually ready to ship, how the front door and machine-readable metadata should agree, and when a mismatch is a release-blocking failure rather than optional polish.
Use [`source-refresh-and-citation-compression.md`](source-refresh-and-citation-compression.md) when deciding whether source work deserves a new ledger entry, a refresh in place, or no retained archive bytes at all.
Use [`canonical-anchors-and-bridge-note-discipline.md`](canonical-anchors-and-bridge-note-discipline.md) when deciding which note in a cluster should count as the main anchor, when a bridge should stay separate, and when route cleanup should fold satellites back into a tighter canonical path.
Use [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md) when deciding whether an older note is still live doctrine, should remain only as support, or should shrink into an honest redirect rather than lingering as undead guidance.
Use [`doctrine-precedence-and-conflict-repair.md`](doctrine-precedence-and-conflict-repair.md) when two live notes appear to disagree and the archive needs an explicit rule for which path governs, how anchor-versus-bridge precedence should work, and how live tension should be repaired instead of normalized.
Use [`case-to-doctrine-promotion-and-quarantine.md`](case-to-doctrine-promotion-and-quarantine.md) when a case seems to teach a wider lesson and the archive needs to decide whether that lesson stays local, earns one narrow bridge, or properly belongs in live doctrine.
Use [`doctrine-revision-and-demotion-under-case-pressure.md`](doctrine-revision-and-demotion-under-case-pressure.md) when repeated case work or better evidence appears to press against an already-live rule and the archive needs to decide between boundary repair, bridge patch, anchor revision, or honest demotion of the old wording.
Use [`term-discipline-and-synonym-control.md`](term-discipline-and-synonym-control.md) when deciding whether a new phrase names a real new distinction or just renames a concept the archive already has. Use [`preferred-terms-and-alias-map.md`](preferred-terms-and-alias-map.md) when the archive needs the current short list of recurring terms it should keep fixed across revisions and case work.
Use [`claim-kinds-and-revision-burdens.md`](claim-kinds-and-revision-burdens.md) when deciding whether a challenge is really pressing doctrine, a program rule, archive governance, a source ledger, or only a route / integrity surface, and therefore what revision burden actually applies.

## Closure rule

A question does not need a perfect answer to stop attracting new archive weight.
Once the archive has a good-enough operational answer, demote, merge, or park the question unless later evidence genuinely reopens it.
