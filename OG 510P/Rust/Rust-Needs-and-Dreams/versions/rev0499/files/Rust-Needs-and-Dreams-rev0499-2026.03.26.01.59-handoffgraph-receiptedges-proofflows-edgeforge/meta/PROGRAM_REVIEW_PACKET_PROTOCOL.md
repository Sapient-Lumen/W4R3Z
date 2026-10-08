# Program review packet protocol

## Goal
Force future broad portfolio revisions to pay the **comparison packet tax** before advancing, widening, merging, holding, folding, or killing a top Rust ecosystem program.

This protocol exists because the archive already has ranking, reference architectures, charters, and stage gates.
The next failure mode is not lack of ideas.
It is decision drift caused by comparing candidates with different hidden criteria.

Read with:
- `design/epic-contribution-review-packets-2026Q1.md`
- `design/epic-contribution-stage-gates-and-proof-budgets-2026Q1.md`
- `design/epic-contribution-program-charters-2026Q1.md`
- `design/epic-contribution-reference-architectures-2026Q1.md`
- `design/epic-contribution-scorecards-2026Q1.md`
- `meta/PILOT_SCORECARD_PROTOCOL.md`
- `meta/REVISION_OPERATING_PROTOCOL.md`
- `meta/AMNESIA_RESISTORS.md`

## Use this protocol when
Use this protocol when a revision is mainly about any of the following:
- comparing two or more top-band candidates,
- deciding whether a candidate advances or widens,
- deciding whether a candidate should merge into a stronger parent,
- deciding whether a candidate should be held, folded, or killed,
- or claiming that a proposal is now practical, review-ready, or worthy of a new launch phase.

Do not use this protocol for:
- seam-local execution-blueprint deepening that does not change portfolio comparison posture,
- routine citation refreshes,
- or archive-only hygiene that does not change candidate interpretation.

## Required packet questions
A revision governed by this protocol must leave behind one review packet or one review-packet-shaped note that answers all of the following:
1. What exact candidate is being reviewed?
2. What macro-program or seam is it in?
3. Why now?
4. What is the minimum kernel and artifact family?
5. What stage and proof budget has it earned?
6. What practical decision gets better?
7. What proving grounds and negative states are visible?
8. Who owns it and what upkeep is assumed?
9. What adjacent options were compared, merged, narrowed, or refused?
10. What verdict is being requested now?
11. What evidence expires and what triggers reissue?

## Required verdict vocabulary
A governed revision must use one of these verdicts explicitly for each reviewed candidate:
- `advance`
- `deepen`
- `merge`
- `hold`
- `fold`
- `kill`

Do not substitute vague prose such as “promising”, “practical”, “interesting”, or “important” for a verdict when the revision is making a comparison decision.

## Minimum packet spine
A compliant packet must visibly separate:
- identity and scope,
- why-now signals,
- kernel and artifact family,
- stage/proof status,
- decision improved,
- proving grounds and negative states,
- owner shape and maintenance envelope,
- adjacency/comparison/fold logic,
- bounded v0 and requested verdict,
- refresh/expiry and reissue triggers.

## Failure conditions
A packet-governed revision fails if any of the following happen:
- it compares candidates without naming the requested verdict;
- it says a proposal is practical or ready without stage and owner posture;
- it uses only broad prose and no artifact family;
- it hides unsupported, partial, or regressed states;
- it widens a candidate without stating what larger form is still refused;
- it carries forward stale comparison claims without renewal or reissue triggers;
- or it introduces a new broad portfolio note without saying why an existing packet could not be deepened instead.

## Default routing rule
If a future revision starts asking “what should we do with this candidate now?” it should route through `design/epic-contribution-review-packets-2026Q1.md` before creating another ranking note or another loose synthesis memo.
