# Creditor dispute timeline page — claim open, evidence age, challenge, ruling, and reopen events

## Purpose

This page is the chronology view for the full life of creditor attribution once restoration depends on who is actually owed and on what proof.
It must let operators answer:

> when was the creditor set asserted, when was evidence captured, when did that evidence age or get challenged, when was release frozen, and when was the case ruled or reopened?

## Mandatory event types

### A. Claim-formation events

- creditor set asserted
- reserve creditor auto-verified
- named harmed claimant added
- cohort formula applied
- evidence package captured

### B. Horizon events

- evidence freshness warning opened
- archive horizon changed
- history horizon nearly expired
- size-limit witness missing
- rereview deadline reached

### C. Dispute events

- challenge filed
- counterevidence attached
- claim split into verified core and contested residue
- release frozen
- provisional relief allowed
- claim denied as unverifiable

### D. Resolution and reopen events

- creditor verified
- absorber named
- waiver granted
- residue carried forward
- release freeze lifted
- case reopened
- prior release withdrawn
- final closure fixed

## Required timeline annotations

Each event must carry:

- actor
- authority quality
- evidence state before event
- evidence state after event
- creditor consequence
- strongest sentence gained or still blocked

## Required overlays

The page must support overlays for:

- verified creditor amount over time
- contested residue over time
- evidence-horizon countdown over time
- release-freeze posture over time
- future-burst posture over time

## Failure modes the page must prevent

- showing only the final ruling and hiding the aging or contest path that shaped it
- allowing evidence expiry to look identical to actual dispute resolution
- allowing provisional relief to look identical to full creditor verification
- allowing reopened cases to erase the fact that release had already been announced once

## Stronger-sentence guard

The page may say `release frozen on this date` or `verified core expanded on this date`.
It may not say `final closure fixed on this date` unless the timeline separately shows the last material dispute resolved or absorbed and any reopen window actually closed.
