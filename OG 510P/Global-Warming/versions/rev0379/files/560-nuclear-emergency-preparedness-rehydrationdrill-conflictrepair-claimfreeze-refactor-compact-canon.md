# 560 — Nuclear emergency preparedness: rehydration drill, conflict repair, claim-freeze and fork-clean refactor

## Purpose

Rev0353 closes the highest-risk seam left after rev0352: evidence can be captured offline, rehydrated later, passed through release-egress/DLP controls, and still become misleading if hash, custody, redaction, clock, fork lineage, or public-claim states disagree.

This revision therefore adds a **rehydration conflict-repair and claim-freeze layer**. The layer is operational rather than doctrinal: it gives packet owners a board for deciding what happens when the live packet, offline receipt, redacted surrogate, release manifest, synthetic-retirement record, and source clock do not match.

## Hard rule

A folder, README, placeholder, label, paper receipt, offline form, delayed hash, rehydrated packet, redacted surrogate, release manifest row, DLP pass, forked package, public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, claim-freeze row, conflict-repair row, or complete-looking packet can demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## New route

```text
offline/live/release packet state
  -> rehydration drill scenario
  -> hash/clock/custody/surrogate conflict ledger
  -> conflict-repair board
  -> claim-freeze board
  -> candidate-for-adjudication only
  -> CAP/retest/verifier if applicable
  -> integrated claim-kernel release gate
```

## What is repaired

Rev0352 created a public-release and sensitive-annex gate. That gate was necessary, but it introduced a new failure mode: an operator might mistake a DLP pass, release manifest row, redacted surrogate, or rehydrated packet for readiness evidence.

Rev0353 forces those states to remain claim-blocking until the packet is reconciled. The most important repair states are:

1. **hash conflict** — original hash, delayed hash, surrogate hash, or manifest hash disagree;
2. **clock conflict** — capture time, offline receipt time, hash time, rehydration time, and release-review time do not align;
3. **custody conflict** — missing witness, missing transfer, broken chain, wrong owner, or missing verifier;
4. **surrogate conflict** — redacted/public-safe surrogate does not map to the original or overclaims beyond the original;
5. **fork conflict** — same-revision packages in the cloudtainer disagree about which branch is canonical;
6. **synthetic contamination** — dry-run or red-team payload enters a live or release lane;
7. **public context conflict** — public meeting, AAR, PI, schedule, MSEL, or dashboard text is offered as closure;
8. **counterevidence** — a late packet contradicts an earlier public-safe statement, claim row, or release-ready assumption.

## No readiness claim

All 60 BVPS must-capture packets remain under active loss cap. Rev0353 does not import real or anonymized exercise evidence. It only makes the post-capture conflict-repair path explicit and testable.
