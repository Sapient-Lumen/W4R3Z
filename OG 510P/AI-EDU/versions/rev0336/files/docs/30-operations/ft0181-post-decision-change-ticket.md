# FT-0181 post-decision change ticket

Use this immediately after the first-packet decision board and before any service-record, public-summary,
lifecycle, schema, or closure change. The board says what the owner packet changed. This ticket says the
smallest reversible change the archive is allowed to make. The live-window stop and rollback card
then says how that change is kept small, paused, reversed, and read at the end of the first window.

The ticket exists to prevent a common failure: a first owner packet produces a useful review note, and
then the maintainer quietly turns that note into a broader claim, a lifecycle promotion, a schema field,
or a public summary update that the packet did not justify.

## Executable gates

The prose ticket below is backed by `tools/record_ft0181_post_decision_change_ticket.py`. After a valid `first-packet-decision.json` exists, do not hand-edit this surface as the next artifact. Rerun `make owner-field-next`; it first emits `make owner-post-decision-change-ticket-brief ...` so the human can choose a bounded ticket route from a one-screen command brief. After the brief exists, execute only the emitted `make owner-post-decision-change-ticket ... CONFIRM=human-recorded-bounded-post-decision-change-ticket` command. The generated `post-decision-change-ticket.json` remains local, `NOT_ACCEPTED`, and `not_evidence`. After a ready or active ticket exists, rerun `make owner-field-work` or `make owner-field-next`; rev0298 emits `make owner-activation-live-window-brief ...` before any activation receipt or live-window card command. A ready ticket cannot source live-window work; only an `active_change` ticket created from a valid activation receipt may source a live-window card.


## Change-ticket brief rule

`make owner-post-decision-change-ticket-brief DECISION=scratch/.../first-packet-decision.json` may prepare a minimized ticket handoff. The brief is not a ticket, activation receipt, evidence, custody, public-summary support, service-record mutation, live-window authority, or closure. Its active-change command template is only a boundary reminder and must not be used until `make owner-activation-receipt` has already created a valid activation receipt from the same first-packet decision and a real owner-reviewed SRC2+ source packet.



## Activation/live-window entry brief rule

`make owner-activation-live-window-brief TICKET=scratch/.../post-decision-change-ticket.json` may prepare the next minimized late-field handoff. For a `ready_for_real_packet` ticket it emits only the same-source `owner-activation-receipt` command template and no live-window card. For an `active_change` ticket it emits bounded `owner-live-window-card` command skeletons with no-expansion, human-pause, fallback-route, stop, and rollback controls. The brief is not an activation receipt, not an active-change ticket, not a live-window card, not evidence, not custody, not public-summary support, and not closure.

## Active-change receipt rule

A `ready_for_real_packet` ticket is not active authorization. To create an
`active_change` ticket, first record `make owner-activation-receipt ...` from a
real owner-reviewed SRC2+ source packet. The receipt stores only path, hash,
counts, and confirmations. It is not evidence, custody, closure, or public-summary
support, but the ticket recorder must verify it before writing `active_change`.

## Entry rule

Open a change ticket only when all of these are true:

| Required fact | Minimum evidence |
|---|---|
| packet disposition | owner packet workbench outcome recorded |
| five-slice decision | authority, evidence, construct, public, and lifecycle before/after rows filled |
| source truth | candidate class preserved before acceptance; `SRC2+` packet acceptance requires an activation receipt before `active_change` |
| field survival | kept, trimmed, local-only, quarantined, and re-requested fields named |
| reviewer posture | record owner and reviewer roles identified, or the missing role is an unresolved block |

If any fact is missing, the ticket state is `blocked_no_real_packet` or `blocked_incomplete_board`.
Do not update lifecycle, public-summary language, or schema requirements from an incomplete ticket.

## Ticket fields

Use this compact table. It is intentionally shorter than the decision board.

| Field | Required answer |
|---|---|
| ticket id | `PCT-...` identifier tied to packet or board note |
| service | one service only; default `AIEDU-SR-003`, fallback `AIEDU-SR-001`, reserved `AIEDU-SR-004` only with aggregate no-trace evidence |
| ticket state | `blocked_no_real_packet`, `blocked_incomplete_board`, `ready_for_real_packet`, `active_change`, `rolled_back`, or `quarantined` |
| source truth required | lowest source class needed for the proposed change |
| allowed changes | exact edits permitted now or after the named source class exists |
| prohibited changes | claims, lifecycle states, schema changes, or data transfers not permitted |
| rollback owner | person or role that can reverse the change |
| rollback triggers | concrete events that revert to prior state or fallback service |
| public claim ceiling | maximum public language allowed by the evidence |
| closure boundary | why this ticket alone does not close `FT-0181` |
| live-window control | whether a staged or active change needs a stop/rollback card before use |

## Default no-real-data ticket

Until a real `SRC2+` owner packet exists, the only allowed change ticket for the first-contact service is a
blocked preparation ticket:

```text
Ticket state: blocked_no_real_packet
Allowed changes: keep sandbox/example-only posture; prepare a reversible delta; trim future fields
that the board already proves decision-neutral.
Prohibited changes: no pilot promotion, no learning-effectiveness claim, no raw learner trace import,
no protected-route normalization, no raw security payload, no schema field merely because a local export
contains it.
Rollback owner: record owner plus teacher-of-record or equivalent educational reviewer.
Rollback triggers: final-answer behavior, unresolved reviewer disagreement, public overclaim, protected
or security payload leakage, missing non-AI fallback, or owner inability to verify field meaning.
Public claim ceiling: example-only, no outcome claim.
Closure boundary: does not close FT-0181.
Live-window control: blocked until a valid activation receipt sources an `active_change` ticket, then `make owner-activation-live-window-brief ...` prepares the live-window card handoff before any `make owner-live-window-card ...` command records scope counts, no-expansion rule, stop triggers, rollback steps, evidence readouts, and public claim freeze in scratch.
```

## Allowed change classes

| Class | When allowed | Examples |
|---|---|---|
| `PCT-A` trim | board shows a field is decision-neutral or burdensome | remove a future request field, do not add a schema field |
| `PCT-B` suppress | evidence does not support a claim or protected/security detail cannot transfer | remove public outcome language, keep detail local |
| `PCT-C` sandbox adjustment | real packet changes stop trigger, fallback, notice, or rollback without proving outcomes | keep `SLC1`, revise trigger, lower authority |
| `PCT-D` bounded pilot | real `SRC2+` packet plus reviewer agreement supports a limited pilot decision | move to `SLC2` only with expiry, rollback, and a live-window stop/rollback card; still no scale claim |
| `PCT-X` quarantine | source, protected-route, or security risk invalidates import | quarantine packet and suppress public summary |

## Overreach tests

A proposed change is overreach if any answer is yes:

1. Does the ticket promote a sandbox to pilot or scale without a real `SRC2+` packet and reviewer agreement?
2. Does it publish learning, safety, access, compliance, or workload claims that the decision board did not downgrade or approve by claim family?
3. Does it add a schema field because the local export had that field, rather than because the field changed authority, evidence, construct, public, protected/security, or lifecycle decisions?
4. Does it normalize protected-route facts, raw learner traces, small cells, or raw security payloads into public examples?
5. Does it lack a rollback owner or rollback trigger?
6. Does it leave `FT-0181` closure language ambiguous?
7. Does it start or continue a live window without a no-expansion rule, executable rollback steps, and public claim freeze?

If yes, return to the board, suppress the change, or quarantine the packet.

## Copyable ticket

```text
Ticket ID:
Service:
Owner packet or board reference:
Ticket state:
Source truth required:

Allowed changes:
Prohibited changes:
Public claim ceiling:
Schema/validator effect:
Lifecycle effect:
Rollback owner:
Rollback triggers:
Fields trimmed or kept local:
Next owner question:
Closure boundary:
```

## Exit rule

A change ticket exits in one of four ways:

- `blocked`: no service/public/schema/lifecycle change; name the missing fact;
- `trimmed`: future packet request shrinks because a field was decision-neutral;
- `staged`: a reversible change is ready but waits for `SRC2+`, an activation receipt, or reviewer agreement;
- `active`: a real packet supports the bounded change, with rollback and expiry named.

The ticket is not a new governance family. It is the last mile between a board decision and a concrete
service change. If it starts growing into another registry, stop and move the extra material back to
the owner packet workbench, first-packet decision board, decision-delta log, or lifecycle decision.

## Closure boundary

A post-decision ticket can authorize, block, trim, or reverse a narrow change. It cannot create source
truth, cannot make a synthetic example real, cannot replace reviewer calibration, cannot close
`FT-0181`, and cannot prove learning, safety, access, compliance, workload reduction, or service
effectiveness.
