# Quiescence review page — phase stop, residual activity, and safe alternative interface spec

## Purpose

Operators often say `pause` when they really mean one of several stronger intents:

- stop byte ingress for a while
- stop byte egress for a while
- keep this share visually stable during maintenance
- hold churn while I inspect evidence
- prevent accidental propagation
- make this seat truly quiet before surgery

Current sync products, including current Resilio, still make that intent too easy to overread.
The product owes one review surface that says exactly what kind of stillness is and is not being purchased.

## Core decision

AnonSync should never present `Pause` as a self-explanatory verb.
Every such request becomes a **quiescence review** with an explicit phase vector.

The operator chooses desired stillness in ordinary language.
The product answers with:

- effective stop class
- phases definitely stopped
- phases definitely still live
- phases unknown / not guaranteed
- better alternative if the request needs a stronger boundary

## Fixed review order

Every quiescence review renders the same sections in the same order:

1. **Requested stillness**
2. **Effective stop class**
3. **Phase stop vector**
4. **Residual activity**
5. **Safer stronger alternatives**
6. **Commit or back out**

## 1) Requested stillness

Capture:

- object under review
- requested phrase in plain language
- duration intent (`until resumed`, `until window ends`, `until maintenance done`)
- operator goal (`reduce bandwidth`, `freeze evidence`, `avoid outgoing changes`, `avoid incoming changes`, `maintenance isolation`)

The page should preserve the user's own wording instead of silently normalizing it.

## 2) Effective stop class

Show one of a small number of product-owned classes:

- `traffic-throttle only`
- `receive stopped; detect still live`
- `send stopped; detect still live`
- `partial transfer pause`
- `seat-local disconnect`
- `maintenance isolation`
- `global participation stop`

Each class must say whether it was achieved directly or approximated from a weaker request.

## 3) Phase stop vector

Render a fixed table with one row per phase and one verdict per row.
At minimum, the page must show:

- payload send
- payload receive
- delete propagation
- zero-byte / control-shaped propagation
- local detect / rescan
- local indexing / readiness change
- retained presence in lists / queues

Each row gets exactly one verdict:

- `stopped`
- `still live`
- `deferred but not stopped`
- `unknown / not guaranteed`

Never compress this to one icon.

### Example phase vector

```text
Requested stillness ........ maintenance freeze
Effective stop class ....... partial transfer pause

Phase stop vector
  payload send ............. stopped
  payload receive .......... stopped
  delete propagation ....... still live
  zero-byte/control events . still live
  detect/rescan ............ still live
  indexing/readiness ....... still live
  row visibility ........... still participating
```

## 4) Residual activity

Below the phase vector, show the concrete consequences of the still-live phases.
Examples:

- `Deletes from peers may still change this subject.`
- `New local files may still be indexed and enlarge visible share size.`
- `This row may still look active to other maintenance tools.`
- `This state is not suitable for byte-stable evidence capture.`

Residual activity must be expressed as outcomes, not only mechanism names.

## 5) Safer stronger alternatives

If the requested stillness needs a stronger boundary, the page should not merely warn.
It should propose the next stronger reviewed option, such as:

- `Stop transfers only`
- `Stop send and receive, keep detection live`
- `Disconnect this seat from the subject`
- `Enter maintenance isolation`
- `Use a snapshot/evidence capture flow instead`

Each alternative must preview what stronger claim it earns.

## 6) Commit or back out

The final barrier must restate:

- what class will actually be applied
- the strongest safe sentence after apply
- the stronger forbidden sentence
- whether resume is one click or needs rebind/rejoin

## Page objects

### A. Requested stillness card

Fields:

- target object
- operator phrase
- desired duration
- maintenance reason
- requested audience sentence

### B. Effective stop card

Fields:

- stop class
- certainty
- why this class won
- why stronger class did not

### C. Phase stop vector table

Columns:

- phase
- verdict
- proof basis
- visible consequence
- stronger action needed

### D. Stronger alternative ladder

Each rung shows:

- stronger action name
- what new phases it stops
- new side effects
- reversibility

## Commands

```text
anonsync quiesce review <object>
anonsync quiesce review <object> --goal maintenance-isolation
anonsync quiesce review <object> --goal bandwidth-relief
anonsync quiesce apply <review_id>
```

## Refusal rules

The page must refuse to label a state `paused` without phase detail.
It must also refuse dangerous substitutions like:

- `frozen`
- `fully stopped`
- `no changes can happen`
- `safe for evidence capture`

unless the phase vector really earns those phrases.

## Success condition

A good quiescence review lets an operator answer, before commit:

- what exact phases will stop
- what exact phases continue
- whether pause is enough for the real job
- what stronger action is needed if it is not
