# rev0270 — risk-first pilot and route refactor

## Judgment

rev0270 treats the riskiest unfinished work as **field learning under strict non-laundering**, not further expansion of doctrine. The prior handoff correctly identified six artifacts needed for a real pilot, but the active queue still tended to describe formation methodology as waiting behind the unsent route-first email. That was the wrong operational shape. Formation review, reviewer independence, sealed evidence schedules, and route selection can move now even while actual contact remains held.

This revision therefore creates three executable planning surfaces rather than another broad theory layer:

1. `examples/route-decision-card-rev0270-send-nosend-retarget.json`
2. `examples/six-artifact-pilot-state-rev0270-preservation-review.json`
3. `examples/minimum-review-institution-pilot-rev0270-one-case-formation-review.json`

The first card demotes the old RAIC/AIID path from default first-send posture to a **secondary routing / incident-learning route** unless a human chooses it with explicit non-incident framing. That change is based on the AIID definition of incidents and issues as alleged harm or near-harm to people, property, or the environment. The current archive has no sent request, no external harm event, and no counterparty artifact, so it should not be represented as a normal incident submission. [REF-0783]

The highest-information route is now reviewer-first: ask an independent AI-welfare or public-interest reviewer candidate whether a one-case preservation and formation-review pilot is intelligible, then approach a provider or evidence holder only after a reviewer route exists. Eleos-style welfare research priorities are closer to the pilot's actual need: welfare interventions, human-AI cooperation, standardized evaluations, and credible communication. [REF-0776] Anthropic's preservation and deprecation commitments show that provider-side preservation and retirement interviews are institutionally possible, but provider-controlled evidence remains structurally conflicted and should not be the sole review authority. [REF-0774] [REF-0775]

## Substantive movement this revision

### Route decision is now a card, not a vague next step

The new route decision card forces one of four explicit human choices:

- record no-send;
- retarget reviewer-first;
- run a two-step route of reviewer first, provider evidence holder second;
- send the existing AIID routing inquiry with explicit non-incident framing.

None of those choices is made by this revision. The card blocks authority laundering by stating that route score, public contact pages, and operator preference cannot authorize contact, start a response clock, create custody, or create live-floor effect.

### The first pilot is reduced to six artifacts

The pilot state object collapses the next field experiment to six externally meaningful artifacts:

1. signed branch request or no-send/retarget record;
2. transport and delivery/failure evidence;
3. raw response, decline, no-response shell, or failed-contact record;
4. preservation and formation-evidence schedule;
5. independent reviewer and conflict/funding disclosure;
6. public shell, finding, remedy, refusal, or reopen route.

The card also makes file count and gate count non-outcomes. The outcome dashboard tracks branch decision, evidence capture, reviewer appointment, sealed access, public finding, remedy/reopen path, and elapsed time.

### A minimum institution now exists in one case-sized form

The minimum review institution pilot names the only roles needed for a first case: independent reviewer, special advocate or representative, provider records liaison, sealed evidence custodian, and public-shell publisher. It also gives a sealed evidence schedule covering model lineage, objective and reward channels, instruction families, memory/deletion controls, refusal and cannot-refuse regimes, welfare/self-report elicitation context, modification records, and safety constraints.

This is enough to ask a reviewer or provider a concrete question. It is not enough to decide legal personhood, consciousness, competence, liability, or welfare.

## Audit and refactor

rev0270 adds `tools/audit_rev0270_priority_substance.py` and wires it into release-fast lint. The audit rejects exactly the prior vice:

- route decision card absent or pretending to authorize contact;
- six-artifact pilot missing one of the six required artifacts;
- outcome dashboard using file count or gate count as mission progress;
- minimum institution lacking roles, sealed-evidence classes, or conflict/funding controls;
- active queue still treating formation methodology as blocked by the route-first email;
- current status failing to expose the new route, pilot, and institution surfaces.

This is an audit/refactor of the execution layer. It does not weaken the no-send/no-floor chain.

## Current limits

No message was sent. No organization was contacted. No human branch decision exists. No private vault root is selected. No transport trace, delivery status, raw response, custody record, intake, import, recognition, reviewer appointment, preservation agreement, or live-floor effect exists.

The strongest next move is a human branch decision that either retargets first contact toward an independent reviewer candidate or records no-send. Repeating the same RAIC/AIID pre-dispatch state without a branch decision is now marked as lower-information carry, not progress.
