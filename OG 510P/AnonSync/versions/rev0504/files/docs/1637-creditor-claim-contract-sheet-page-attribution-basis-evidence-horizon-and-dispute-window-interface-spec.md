# Creditor claim contract sheet page — attribution basis, evidence horizon, and dispute window

## Purpose

This page is the canonical object for any creditor set that feeds a burst-debt or restoration-waterfall case.
It must answer:

> who is being treated as a creditor, why, what evidence supports that status, how long that evidence remains strong enough, and what dispute or reopen window still blocks clean release?

## Primary questions the page must answer

1. Which source debt or restoration case is this claim set attached to?
2. Which creditors are verified, partially verified, contested, or currently unverifiable?
3. What evidence packages support each creditor assertion?
4. When do those evidence packages expire, degrade, or require rereview?
5. What release or probation posture is frozen while any material dispute survives?

## Required fields

### A. Source-case block

- source burst-debt object
- source restoration waterfall if one exists
- claimant name
- claimed creditor universe summary
- current strongest blocked clean-release sentence
- current future-burst posture

### B. Creditor-roster block

For each creditor or creditor cohort the page must show:

- creditor name or cohort label
- creditor class (`protected-reserve`, `named-harmed-claimant`, `cohort-headroom`, `manual-residual-absorber`)
- claimed amount or harm slice
- attribution confidence (`verified`, `split-core`, `contested`, `unverifiable`, `waived`)
- whether this creditor currently participates in the waterfall
- strongest sentence currently allowed for that creditor

### C. Evidence-package block

For each creditor assertion the page must show:

- evidence sources used (`history`, `archive`, `runtime-witness`, `manual-attestation`, `diagnostic-capture`, `policy-formula`, `other`)
- evidence freshness horizon
- evidence capture time
- evidence expiry or rereview time
- actor-attribution strength (`direct`, `indirect`, `structural-only`, `missing`)
- counterevidence present (`no`, `yes-pending-review`, `yes-material`)

### D. Dispute-window block

- dispute status (`none-open`, `open`, `reopened`, `expired-with-residue`, `ruled`)
- dispute opener
- dispute open time
- dispute window end time
- reopen allowed (`no`, `new-material-evidence-only`, `manual-authority-only`)
- release freeze posture (`none`, `clean-release-frozen`, `probation-lift-frozen`, `future-burst-frozen`)

### E. Provisional-handling block

- undisputed core amount
- disputed residue amount
- provisional relief allowed (`none`, `reserve-only`, `undisputed-core-only`, `manual-only`)
- stronger harmed-neighbor sentence still blocked
- event required to unfreeze release

## Required states

The page must keep these states separate:

- `all-creditors-verified`
- `verified-core-with-contested-residue`
- `reserve-only-verified`
- `evidence-aging-risk`
- `material-dispute-open`
- `claim-unverifiable`
- `release-frozen`
- `reopened-after-provisional-close`
- `ruled-and-carried-forward`

## Required comparisons

The page must keep these comparisons explicit:

- `verified creditor` vs `plausible but unverified harmed party`
- `expired evidence` vs `debt retired`
- `undisputed core` vs `total asserted claim`
- `archive residue present` vs `actor attribution proven`
- `history fragment available` vs `durable creditor ledger`

## Failure modes the page must prevent

- silently dropping a creditor because evidence aged out before review
- treating Archive presence as automatic proof of which peer caused harm
- allowing a disputed creditor set to masquerade as cleanly settled
- forcing operators into all-or-nothing acceptance when only part of a claim is verified
- lifting probation because the dispute window expired without an actual ruling

## Stronger-sentence guard

The page may say `reserve creditor verified; named harmed claimant still contested under release freeze`.
It may not say `all creditors settled` or `clean restoration eligible` until every material creditor is either verified and resolved, explicitly waived by authority, or explicitly absorbed by a named residual bearer.
