# Dispute and remedy lifecycle

rev0185 promotes the appeal/correction/grievance cluster into a reusable lifecycle model. The archive should stop treating every redress noun as a new dossier. Most belong to one clocked state machine.

## Core move

The managed-legibility lane previously modeled how packets are created, relied upon, stayed, corrected, superseded, and archived. The missing companion model is how a person, supplier, buyer, platform user, downstream recipient, regulator, or representative **challenges** a state.

The remedy lifecycle is not simply “appeal filed → decision.” It is a sequence of state transitions with standing checks, clocks, interim-use rules, evidence requests, reviewer authority, outcome classes, propagation duties, and abuse controls.

## Lifecycle stages

| Stage | Question | Typical artifacts | Failure modes |
|---|---|---|---|
| `notice` | Did the affected party receive enough information to contest? | statement of reasons, adverse-action notice, explanation packet | empty notice, clock-start ambiguity |
| `intake` | Was a challenge received and recorded? | intake receipt, case ID, filing timestamp | lost filing, inaccessible channel |
| `standing-check` | Is the filer entitled to bring or view this matter? | subject proof, reliance proof, representative authority | false denial, privacy leak |
| `admissibility` | Is the filing timely, sufficiently specific, and in the right forum? | admissibility record, cure notice | wrong-forum trap, overstrict substantiation |
| `interim-state` | What may continue while the matter is pending? | stay label, restriction object, holdback reserve | overbroad suspension, no protection |
| `evidence-request` | Who must provide what by when? | source-witness request, vendor request, sealed access order | nonresponse, trade-secret overclaim |
| `review` | Who evaluates merits, and with what authority? | reviewer roster, human-review log, escalation path | rubber-stamp review, language gap |
| `decision` | What is the outcome class? | sustained, denied, partly sustained, unverifiable, corrected, abuse-limited | ambiguous outcome |
| `correction` | What changes in the source or packet? | correction notice, materiality class, restatement | invisible edit, over-notice |
| `propagation` | Who must receive the changed state? | recipient graph update, delivery attestation | stale downstream reliance |
| `closure` | Is the case final, appealable, archived, or reopened? | closure notice, reopen trigger, non-reliance state | premature closure |
| `telemetry` | What pattern should governance learn from? | complaint metric, error class, abuse metric | suppressed signal, metric gaming |

## State families

The remedy model uses separate state families. Do not collapse them.

- **Validity**: whether the underlying proof or decision is authorized.
- **Freshness**: whether the observation is current enough for reliance.
- **Dispute**: whether a challenge is pending or decided.
- **Interim reliance**: whether downstream use is allowed, restricted, stayed, or reserved.
- **Correction**: whether the object must be amended, restated, superseded, or withdrawn.
- **Abuse**: whether the filing is restricted because of duplicate, frivolous, bad-faith, or high-volume behavior.
- **Representation**: whether the actor is allowed to file, view, or receive the remedy record.

## Design rule

A dossier in this family should identify:

1. who can file;
2. what starts the clock;
3. who reviews;
4. what happens while pending;
5. what evidence is admissible;
6. how silence is treated;
7. what outcomes exist;
8. who receives the outcome;
9. whether abuse filters apply;
10. what metric exposes failure.

## Refactor implication

Most future ideas about appeal buttons, dispute labels, statements of reasons, human review, grievance channels, correction notices, and stay flags should begin as substates in this model. Promote them only if they add a new enforcement surface, a new actor class, a new abuse mode, or a new cross-domain mechanism.
