# Attainment review page — did the effect land for the required cohort, and what residue remains?

## Purpose

This page is the operator review surface for deciding whether a typed effect merely ran, partially landed, or truly attained its required outcome.
It exists so the product can stop forcing operators to infer completion from status icons, quiet dashboards, or the absence of loud warnings.

## Questions this review must answer

- did the effect commit locally
- did the effect reach only connected participants or the full required cohort
- is any recipient still offline, disconnected, placeholder-only, paused, or no-source
- is the system still relying on rescans, delayed merges, or hidden internal tasks
- is there any residue that blocks a stronger completion sentence
- what exact next event would honestly strengthen or weaken the verdict

## Mandatory review sections

### A. Outcome snapshot

- highest honest attainment sentence currently earned
- strongest blocked stronger sentence
- exact reason the stronger sentence is blocked
- one-sentence operator summary in plain language

### B. Cohort coverage review

- required cohort list or cohort rule
- covered cohort list or coverage count
- uncovered cohort list or uncovered rule
- whether missing members are offline, disconnected, placeholder-only, paused, or otherwise unavailable
- whether connected-cohort calm is currently impersonating broader completion

### C. Residue review

- ghost or no-source items
- temp-file or partial-download residue
- hidden-task backlog relevant to this effect
- watcher-loss / rescan dependency posture
- file-system or merge failures relevant to this effect
- whether the residue is cosmetic, operational, or completion-blocking

### D. Verification review

- verification method already used
- verification method still missing
- whether later reconnect or rescan can change the answer
- whether an adjudicator or reviewer must sign off before stronger closure language is allowed
- whether the current state is safe for reversible use only or for stronger irreversible sentences

### E. Next-step review

- smallest event that would strengthen the sentence
- smallest event that would weaken the sentence
- whether compensation, retry, reopen, or narrower publication is required right now
- what receipt must be carried forward if the case pauses here

## Failure modes the review must prevent

- mistaking `green check with connected peers` for `required cohort attained`
- mistaking `paused` for `nothing else can still change`
- mistaking lack of visible transfer for durable completion while hidden tasks still run
- mistaking a ghost file or no-source warning for trivial noise when the intended effect never truly landed
- forgetting that later rescans, touches, reconnects, or source loss can legitimately change the verdict

## Stronger-sentence guard

The review may say `execution was valid, the effect landed locally, all connected recipients look caught up, one required recipient is offline, and one announced artifact is now ghost/no-source, so the strongest honest sentence is partial attainment with residue`.
It may not say `final completion proven` unless that stronger sentence is actually earned.
