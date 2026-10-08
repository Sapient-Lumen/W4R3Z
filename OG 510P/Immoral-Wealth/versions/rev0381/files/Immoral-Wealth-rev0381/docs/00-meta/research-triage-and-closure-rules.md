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

# Research triage and closure rules

## What this note is for

This archive already has more open empirical questions than it should try to answer at once.
That is not a bug.
But it becomes a problem when every unresolved measurement problem, country nuance, or calibration curiosity tries to become a live branch in the archive.

This note gives the archive a **small priority rule** for deciding:

1. which open questions deserve active work now,
2. which ones should stay parked without guilt,
3. when a question is resolved enough to stop attracting new notes,
4. and when a new note does **not** earn its bytes because it only restates a live distinction somewhere else or should instead change the status of an older note.

Use this note with [`archive-policy.md`](archive-policy.md), [`archive-growth-budgets-and-refactor-triggers.md`](archive-growth-budgets-and-refactor-triggers.md), [`source-refresh-and-citation-compression.md`](source-refresh-and-citation-compression.md), [`canonical-anchors-and-bridge-note-discipline.md`](canonical-anchors-and-bridge-note-discipline.md), [`note-status-and-supersession-discipline.md`](note-status-and-supersession-discipline.md), [`research-questions.md`](research-questions.md), [`../90-open/open-questions.md`](../90-open/open-questions.md), and [`../20-program/case-portfolio-triage-and-memo-selection.md`](../20-program/case-portfolio-triage-and-memo-selection.md).

## The archive's research priority rule

An open question should move to the front of the queue only when answering it would likely change at least one of these four things:

1. the **verdict** on whether a wealth order is structurally failing, correction-required, near-passing, or near-ideal,
2. the **package choice** or the lead lane in a live case,
3. the **rail / gating judgment** on what can honestly begin now,
4. or the **confidence** the archive can claim about any softer pass, de-escalation, or durable-success story.

If a question would not likely move one of those, it usually does **not** belong near the front of active work.

That does not make it worthless.
It makes it a **later-calibration** question rather than a **program-steering** question.

A candidate real-world case should not automatically become a retained memo just because it is interesting or vivid. When the archive is choosing among possible country, city, sector, or cohort memos, route that queueing problem through [`../20-program/case-portfolio-triage-and-memo-selection.md`](../20-program/case-portfolio-triage-and-memo-selection.md). When the archive already has several case memos alive, route the follow-on byte-budget question through [`../20-program/case-portfolio-caps-and-retirement.md`](../20-program/case-portfolio-caps-and-retirement.md) rather than quietly letting case accumulation become a shadow archive. If a live case seems to teach a wider rule, route the promotion question through [`case-to-doctrine-promotion-and-quarantine.md`](case-to-doctrine-promotion-and-quarantine.md) rather than letting one memo quietly become archive-wide doctrine by drift. If repeated cases or better evidence instead seem to press against an already-live rule, route that repair question through [`doctrine-revision-and-demotion-under-case-pressure.md`](doctrine-revision-and-demotion-under-case-pressure.md) rather than normalizing strained doctrine by unwritten caveat.

## The four standing priority classes

### A. Spine-critical now

Treat a question as spine-critical when the answer would likely change one of the archive's main decision outputs in a wide range of cases.

Typical examples:
- what should count as enough proof to certify a softer verdict under opacity,
- which compact metric best captures top-tail rule conversion,
- which floor-pass trigger travels well enough to guide real-case verdicts,
- which washout indicators best predict fast reabsorption of gains.

Questions in this class can justify:
- a new compact note,
- a substantive rewrite of a core framework or program note,
- or a narrow source refresh if the archive's current support is materially too weak, using [`source-refresh-and-citation-compression.md`](source-refresh-and-citation-compression.md) to decide whether that means a true new source, a replacement, or only a citation refresh.


### B. Routing / scoreboard refinement

Treat a question as second priority when the answer would improve case routing, package comparison, monitoring, or scoreboard reading, but would not usually overturn the archive's whole moral target.

Typical examples:
- better compact indicators for timing failure,
- a cleaner bundled trigger for territorial closure,
- a better cross-case measure of claimant load,
- a better screen for person-level ownership failure.

Questions in this class often justify:
- a small bridge note,
- a compact operator note,
- or a modest sharpening of an existing measurement or program file.

### C. Later calibration

Treat a question as later calibration when it would mostly narrow a parameter, threshold, or cross-country adjustment after the archive already knows the case is failing and already knows the general package family.

Typical examples:
- whether one rate should sit slightly above or below another,
- which of two plausible sub-metrics is marginally cleaner for a narrow subclass of cases,
- or which warning threshold is most elegant once the main constitutional judgment is already obvious.

Questions in this class usually do **not** justify a fresh standalone note.
They belong in:
- `research-questions.md`,
- `open-questions.md`,
- or a one-line addition to a current note's open-questions tail when that is enough.

### D. Parked unless needed

Treat a question as parked when:
- it is interesting but not decision-moving,
- it is mostly a literature-tour temptation,
- it would require a bulky casebook the archive does not want,
- or it mainly asks for a perfect metric where a rough compact trigger already does the job well enough.

A parked question should stay visible, but it should not keep pulling bytes into the archive.
Parked is not abandoned.
It just means **not worth active expansion right now**.

## The three main tests before adding a new note

A new note should usually exist only if it passes **all three** tests.

### 1. Repeated-use test

Will this note likely be used across many future cases or many future revisions?
If it only resolves one local confusion in one file, prefer editing that file directly.

### 2. Non-duplication test

Does the note add a distinct judgment rule, routing bridge, or compression gain that the archive does not already contain?
If the answer is already implicit across two or three current notes and can be made explicit by tightening one of them, prefer the tightening.

### 3. Compression-after-addition test

After adding the note, can the archive become **easier to read or shorter to route through** rather than harder?
A new note earns its bytes only when it reduces future repetition, case drift, or re-synthesis.

### 4. Term-discipline test

Would the proposed note still look new if its vocabulary were forced back into the archive's current preferred terms?
If the answer is no, it probably wants tightening or routing cleanup rather than a new file; use [`term-discipline-and-synonym-control.md`](term-discipline-and-synonym-control.md).

If a proposed note fails any one of those tests, the default answer should usually be:
**do not add it**.

## The closure rule for open questions

An open question does **not** need a perfect answer to be treated as closed enough for archive purposes.

Close or downgrade the question when one of these conditions is met:

### 1. Good-enough operational answer

The archive now has a compact rule that is good enough to guide verdicts, package choice, rails, or confidence, even if some empirical refinement remains possible.

### 2. Stable provisional answer

The archive now has a provisional answer strong enough to carry action-grade use, and the remaining uncertainty mainly affects calibration rather than posture.

### 3. Merge into a wider question

The question turned out not to be truly separate.
It was one surface of a larger unresolved bundle and should stop attracting its own line item.

### 4. Park without harm

The question remains genuinely open, but leaving it open no longer materially harms the archive's ability to answer its main question or route real cases responsibly.

In all four situations, the archive should stop feeding the question extra standalone notes unless later evidence reopens it.

## The default no-bloat move

When a live gap is found, the archive should try these moves **in order**:

1. **tighten an existing note,**
2. **add one compact bridge note,**
3. **compress or dedupe the routes around it,**
4. **and only then consider a broader new branch.**

This ordering matters.
The archive's main danger is not just being wrong.
It is becoming correct in too many overlapping places at once.

## What a new research addition must say

Any new research-facing note or major open-question expansion should say, explicitly and briefly:

- **what decision it helps with** — verdict, package, rails, confidence, or watch / reopen,
- **what existing note it changes or unblocks,**
- **what would count as enough closure** for now,
- and **what further work does *not* need to be done yet**.

That last line matters.
Without it, the archive quietly turns every improvement into a demand for another layer of polish.

## The archive's asymmetry in research spending

The archive should spend its scarce bytes and scarce attention asymmetrically.

It should spend **more** on questions that prevent false passes, false de-escalations, fake broadening, or misrouted packages.

It should spend **less** on questions that only perfect already-obvious judgments, decorate settled doctrine, or offer finer calibration inside a package family the archive already knows it would choose.

This mirrors the archive's substantive asymmetry:
it usually needs more proof to certify comfort than to justify continued vigilance and lower-regret correction.
Research attention should follow the same discipline.

## Minimal maintenance rule for the open-question lists

`research-questions.md` and `open-questions.md` should stay as **question ledgers**, not mini-essays.
When a question is active, mark it by routing to the note that is currently carrying the work.
When a question is parked, leave it visible but do not keep elaborating it.
When a question is effectively resolved for archive purposes, either remove it or fold it into one wider surviving item.

The lists should remain useful for priority-setting, not become shadow archives.

## Fast use rule

Use this note in six steps:

1. **Ask whether the question would move verdict, package, rails, or confidence.**
2. **Classify it** as spine-critical, routing / scoreboard refinement, later calibration, or parked.
3. **Prefer editing or tightening** before adding a fresh file.
4. **Add a new note only if it passes repeated-use, non-duplication, compression-after-addition, and term-discipline tests.**
5. **State what would count as closure** so the question does not become immortal by default.
6. **Demote or park the question once the archive has a good-enough operational answer.**

## Bottom line

The archive now has a compact answer to its own growth problem:
**which unanswered questions deserve new bytes, and when can we stop?**

Prioritize questions that move verdicts, package choice, rails, or confidence.
Demote questions that only fine-tune later calibration.
Prefer tightening and bridge notes over parallel branches.
And once the archive has a good-enough operational answer, treat the question as closed enough until something real reopens it.
