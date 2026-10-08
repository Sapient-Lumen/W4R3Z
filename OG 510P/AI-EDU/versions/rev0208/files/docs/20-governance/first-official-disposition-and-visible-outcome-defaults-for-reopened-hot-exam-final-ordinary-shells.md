# First official-disposition and visible-outcome defaults for reopened hot-exam final-ordinary shells

The archive already has a very small late-trigger grammar for the hottest exam-like child routes.

It can now say:

- which late named trigger has appeared;
- whether that trigger stays route-local, reopens the ordinary shell, or reopens only the affected artifact shell;
- whether score-risk is officially live yet; and
- who has to act now.

That is not yet enough.

The archive still lacked the next tighter answer: **once one of those later triggers actually resolves or partially resolves, what should the shell publish as the official disposition and the visible outcome?**

This document adds one thing only:

- a **tiny official-disposition / visible-outcome field set** for those already reopened-or-still-settled hot exam shells.

That means the archive now asks a different question than before. It no longer asks only **what later trigger is live and who acts now**. It now asks **what the official route has actually decided, what the ordinary or artifact shell should visibly look like afterward, whether the score-report effect is now official, and what state the shell has truthfully reached next**.

## Small field set for official-disposition / visible-outcome defaults

| Code | Meaning | Default archive action |
|---|---|---|
| `OD0-NO-UNIVERSAL-POST-REVIEW-MENU` | no one universal late-review resolution menu, cure packet, or disposition banner governs every reopened shell | keep the layer route-bounded and disposition-bounded rather than collapsing all late outcomes into one generic `resolved` state |
| `OD1-PUBLISH-OFFICIAL-DISPOSITION` | publish the official disposition reached by the route | name `route-local complete`, `cleared / no further action`, `partial cure`, `score delayed / pending`, or `score canceled / declined / invalid` rather than leaving only a vanished-or-open review banner |
| `OD2-PUBLISH-VISIBLE-OUTCOME` | publish what that disposition actually does to the visible shell | say whether the result returns to settled ordinary, stays route-local only, keeps the affected artifact shell open, keeps upstream review / score processing open, or ends in final adverse closure |
| `OD3-PUBLISH-SCORE-REPORT-EFFECT-ONLY-WHEN-OFFICIAL` | publish score-report effect only when the official route has actually made it real | keep nonadverse completion and cleared review free of fake delay/cancellation language, publish `delayed / pending` or `canceled / declined / invalid` only when official materials actually support it |
| `OD4-PUBLISH-NEXT-SHELL-STATE` | publish which named shell state truthfully follows the disposition | say `settled ordinary`, `route-local residue only`, `affected artifact shell still open`, `upstream review still open`, or `final adverse state` rather than pretending every disposition closes the shell in the same way |

## Field values that now travel together

When this layer is used, the shell should publish only four concrete fields:

1. `official_disposition` — `route-local complete`, `cleared / no further action`, `partial cure`, `score delayed / pending`, or `score canceled / declined / invalid`;
2. `visible_outcome` — `route-local only`, `settled ordinary restored`, `affected artifact shell still open`, `upstream review / score processing still open`, or `final adverse closure`;
3. `score_report_effect` — `none published`, `delayed / pending`, or `canceled / declined / invalid`;
4. `next_shell_state` — `settled ordinary`, `route-local residue only`, `affected artifact shell still open`, `upstream review still open`, or `final adverse state`.

That is deliberately small. It is enough to distinguish cleared review from delay, partial cure from route-local completion, and cancellation from ordinary settlement without inventing one universal post-review workflow.

## First official-disposition / visible-outcome assignments

| Route or family | Official disposition now admitted | Visible outcome now admitted | Score-report effect now admitted | Next shell state now admitted | Why |
|---|---|---|---|---|---|
| `SR-WRITE-RHET-01B2 + AC4-PORTFOLIO-LOCAL-RECORD + TG1-NONADVERSE-QUALITY-SAMPLE-STAYS-ROUTE-LOCAL` once the sample request is satisfied | `route-local complete` | `route-local only` | `none published` | `settled ordinary` | current AP Capstone policy says retained presentation/oral-defense videos may be requested for scoring quality or scoring training, while performance tasks are not rescored, so the truthful default is route-local completion rather than a standing learner-facing late banner |
| `SR-WRITE-RHET-01B2 + TG2-INTEGRITY-OR-SECURITY-TRIGGER-REOPENS-ORDINARY-SHELL` or `SR-WRITE-RHET-01B1 + TG2-INTEGRITY-OR-SECURITY-TRIGGER-REOPENS-ORDINARY-SHELL` when the official review closes without an adverse finding | `cleared / no further action` | `settled ordinary restored` | `none published` | `settled ordinary` | current AP Terms and Conditions make adverse outcomes explicit only when invalid scores, misconduct, or testing irregularities are actually found, so the archive now admits the matching nonadverse closure state when that official adverse route is not taken |
| same-device post-end digital submission problems when answer submission or related processing remains unresolved after the ordinary route and official follow-up continue | `score delayed / pending` | `upstream review / score processing still open` | `delayed / pending` | `upstream review still open` | current Bluebook guidance says unresolved answer-submission problems may still require follow-up after 24 hours and acting promptly can reduce the chance of score delays, while current AP score pages say some AP scores take longer to process, delayed scores are added later, and students are emailed when the score is available |
| hybrid digital comparator families carrying `AC3-PAPER-BOOKLET-CUSTODY + TG3-CUSTODY-EXCEPTION-REOPENS-THE-AFFECTED-ARTIFACT-SHELL` when some paper-material facts are repaired but the artifact chain is not yet fully reclosed | `partial cure` | `affected artifact shell still open` | `none published` unless an official delay state is separately opened | `affected artifact shell still open` | current coordinator materials keep defective or missing paper materials and misplaced answers as named paper-related incidents, so the archive now admits a truthful middle state between `everything still broken` and `fully reclosed` |
| integrity/security or testing-irregularity routes after an official adverse finding | `score canceled / declined / invalid` | `final adverse closure` | `canceled / declined / invalid` | `final adverse state` | current AP Terms and Conditions and exam-security materials say College Board may decline to score all or part of the exam, cancel scores, or treat scores as invalid after misconduct, invalid-score review, or testing irregularities |
| `SR-READ-FOUND-01A2A` / `SR-READ-FOUND-01A2B` hot reading families | none beyond `OD0-NO-UNIVERSAL-POST-REVIEW-MENU` | none inherited | none inherited | none inherited | current reading-access and validity regimes still vary too much by state, content area, accommodation route, and validity consequences for one shared late-disposition menu to travel honestly |

## `OD1` and `OD2` — disposition and visible outcome are not the same thing

The archive now separates **what the official route decided** from **what the shell should look like afterward**.

That matters because two routes can both be `resolved` while telling very different truths:

- a quality-sample request can end in route-local completion while ordinary status stays settled;
- an integrity review can end in cleared ordinary restoration;
- a custody problem can be partially cured while the affected artifact shell still stays open; and
- a security or testing-irregularity process can end in final adverse closure.

So the archive now requires both `official_disposition` and `visible_outcome`. A single `resolved` label is not enough.

## `OD3` — score-report effect must be official, not guessed from trouble

`OD3-PUBLISH-SCORE-REPORT-EFFECT-ONLY-WHEN-OFFICIAL` is the archive's smallest anti-rumor rule for late outcomes.

It blocks three opposite mistakes at once:

- treating nonadverse route-local completion as if it implied delayed or threatened scoring;
- treating unresolved or late-processed scoring as if nothing learner-facing had changed; and
- treating an official cancellation / decline-to-score outcome as if it were only an internal review residue.

Current Bluebook guidance explicitly warns that prompt follow-up reduces the chance of score delays, and current AP score pages explicitly say some scores are delayed and later appear on score reports. Current AP Terms and Conditions and exam-security materials then make the opposite side visible by naming invalid-score, misconduct, testing-irregularity, decline-to-score, and cancellation outcomes. That is enough for one small score-report field. It is not enough for one universal remedy menu.

## `OD4` — every late disposition reaches a different next truthful shell state

`OD4-PUBLISH-NEXT-SHELL-STATE` is the archive's smallest anti-false-closure rule.

It stops the archive from pretending that every official outcome either fully closes everything or leaves everything equally open.

Current official materials make at least five different post-disposition truths visible:

- route-local scoring-quality requests can complete without changing the ordinary shell;
- cleared reviews can restore settled ordinary status;
- delayed or pending score-processing problems can leave upstream review visibly open;
- partial paper/custody cures can leave only the affected artifact shell open; and
- official adverse findings can end in final adverse closure.

That is enough for a tiny next-state field. It is not enough for a universal post-review lifecycle.

## What the archive now publishes when using this layer

When an institution or assessment family publishes one of these reopened hot final-ordinary shells, it should now add only the following where truthful:

1. the official disposition;
2. the visible outcome;
3. the score-report effect, if officially live; and
4. the next truthful shell state.

That is enough to make late outcome handling legible without inventing one universal post-review resolution menu.

## What counted as a real archive gain

The archive already knew which named late trigger had opened, what shell it reopened, whether score-risk was live, and who had to act now. It still lacked the next tighter answer: **what to publish once that later trigger actually ended, partially ended, or turned into a lasting scoring consequence**.

This document answers yes, but only barely.

It now allows the archive to publish one thin field set that distinguishes:

- route-local completion from cleared review;
- partial cure from full ordinary restoration;
- delayed / pending scoring from final adverse cancellation or decline-to-score; and
- visible shell outcome from the next truthful shell state.

That is a real operating gain because it blocks four opposite mistakes at once:

- treating every late outcome as either `still under review` or `fully resolved`;
- hiding the difference between route-local completion and ordinary-shell restoration;
- publishing learner-facing score-report effects before they are official; and
- pretending that every official disposition reaches the same closure state.
