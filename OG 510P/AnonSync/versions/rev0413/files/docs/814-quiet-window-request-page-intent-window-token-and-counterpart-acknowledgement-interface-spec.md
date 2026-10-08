# Quiet window request page — intent, window token, and counterpart acknowledgement interface spec

## Purpose

If a quiet agreement needs counterpart action, the product should not push that work into ad-hoc chat, memory, or ticket prose.
It should issue a structured quiet-window request.

## Core decision

Every unresolved quiet cohort may generate one or more **quiet window requests**.
A request is not itself proof of quiet.
It is the structured bridge from local intent to counterpart action.

## Required sections

1. **Requested window**
2. **Counterpart obligations**
3. **Return token**
4. **Acknowledgement states**
5. **Escalation paths**

## 1) Requested window

Show:

- subject
- operation intent
- requested start and end time
- requested stop class
- why the request exists
- initiating seat / actor

## 2) Counterpart obligations

List exactly what the counterpart is being asked to do.

Examples:

- pause payload send and receive
- enter maintenance isolation
- stop delete-capable participation
- confirm observer-only posture
- confirm non-participation for the window

Do not ask for vague `please pause` when the operation actually needs something stronger.

## 3) Return token

Every request must carry a return token that can bind later evidence.

Fields:

- request id
- cohort id
- window id
- target seat
- required proof type
- expiry time

The token lets later acknowledgements or receipts attach to the right quiet agreement review.

## 4) Acknowledgement states

Each target seat must show one state:

- `pending`
- `acknowledged`
- `matched-with-proof`
- `declined`
- `expired`
- `replaced`

Acknowledgement without proof may be useful socially, but it must never be treated as matched stillness.

## 5) Escalation paths

If a request is not matched, the page should propose:

- resend request
- narrow the cohort
- defer the operation
- accept weaker claim language
- escalate to different operation type

## Example projection

```text
Quiet window request qwin_01K...

Requested window
  subject ............... share hr/payroll
  intent ................ destructive repair
  window ................ 2026-03-22 03:00–03:30 UTC
  requested stop class .. maintenance isolation

Counterpart obligations
  nas-01 ................ hold send/receive/delete participation
  laptop-ops ............ hold local edits and delete-capable participation

Return token
  token ................. qtok_01K...
  proof required ........ quiet cohort receipt or matched quiet review
  expires ............... 2026-03-22T03:35:00Z

Acknowledgements
  nas-01 ................ matched-with-proof
  laptop-ops ............ pending
```

## Commands

```text
anonsync quiet-window request create --cohort <cohort_id>
anonsync quiet-window request show <request_id>
anonsync quiet-window request acknowledge <request_id>
```

## Success condition

A good quiet window request makes counterpart coordination explicit, typed, and bindable instead of leaving it in side-channel prose.
