# Action enactment contract sheet page — proposed, executed, noticed, and effective states

## Purpose

This page is the canonical declaration of how a typed act moves from idea to real consequence.
It exists so the product can stop pretending that `signed`, `clicked`, `notified`, and `effective` are the same truth.

The page must answer:

> for each action family in this case, what are the enactment states, when does the act become effective, who must be notified, what timers run, and what later events supersede or withdraw the effect?

## Mandatory state classes per action family

At minimum each action row must expose these states separately:

- drafted
- submitted for execution
- blocked before execution
- executed but not yet noticed
- partially noticed
- notice complete
- cooling running
- effective
- contest open
- superseded
- withdrawn
- reopened with surviving narrower truth

The implementation may add more states, but it may not collapse these into one generic `done` badge.

## Mandatory blocks per action family

### A. Definition block

- action family name
- plain-language description
- reversibility class
- whether the act is protective, revisable, or irreversible
- whether the act may ever skip notice or cooling

### B. Execution block

- preconditions required before execution
- who may trigger execution
- whether execution is single-step or staged
- whether execution can be auto-triggered after threshold satisfaction
- exact event that changes state from drafted to executed

### C. Notice block

- required notice cohort
- optional notice cohort
- allowed notice channels
- what counts as delivered
- what counts as acknowledged
- what happens if notice is partial, delayed, or impossible

### D. Effectivity block

- exact rule for becoming effective
- whether effect depends on execution alone, notice completion, cooling completion, adjudication, or some combination
- whether effect is local-slice, multi-slice, or case-wide
- strongest sentence earned at execution time
- stronger sentence earned only after full effectivity

### E. Aftermath block

- contest window length and opening trigger
- supersession rule
- withdrawal rule
- reopen rule
- narrower truths that survive supersession or withdrawal
- evidence horizon for all of the above

## Required comparisons

The page must keep these comparisons explicit:

- `drafted` vs `executed`
- `executed` vs `effective`
- `notice sent` vs `notice completed`
- `cooling running` vs `cooling satisfied`
- `superseded` vs `withdrawn`
- `reopened` vs `void in full`

## Required badges

- `draft-only`
- `executed-not-effective`
- `notice-required`
- `notice-partial`
- `notice-complete`
- `cooling-running`
- `effective-now`
- `contest-open`
- `superseded`
- `withdrawn`
- `narrower-truth-survives`

## Failure modes the page must prevent

- treating signature collection as if effectivity were already earned
- treating bell notifications or history entries as proof of full notice completion
- letting irreversible acts skip cooling merely because execution happened quickly
- forgetting that some acts become effective for a narrow protective purpose before broader closure effectivity is earned
- erasing narrower truths when a broader act is superseded or reopened

## Stronger-sentence guard

The page may say `final waiver may be executed by quorum, but does not become effective until required notice is complete and a 72-hour cooling window expires`.
It may not say `case closed on signature` unless the exact effectivity row says that signature alone is sufficient.
