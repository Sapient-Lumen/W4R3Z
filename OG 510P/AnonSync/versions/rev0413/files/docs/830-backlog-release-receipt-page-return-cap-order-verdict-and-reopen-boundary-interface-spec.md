# Backlog release receipt page — return cap, order verdict, and reopen boundary interface spec

## Purpose

After a quiet window ends or a backlog-release plan is accepted, the operator needs one durable object that records what reopened, what cap returned, what order was authoritative enough to trust, and what was still too provisional for stronger promises.
This is that receipt.

## Core decision

Every applied backlog-release decision emits a **backlog release receipt**.
The receipt is durable, auditable, and linkable from quiet windows, queue rows, maintenance notes, and later aftershock reviews.

## Receipt sections

1. **Release summary**
2. **Returned cap**
3. **Authoritative order verdict**
4. **Distortion and flood-risk factors**
5. **Safe sentence**
6. **Reopen boundary**

## 1) Release summary

Fields:

- scope
- release trigger
- prior quiet or cap posture
- actor or authority class
- applied time

## 2) Returned cap

Fields:

- returned send cap
- returned receive cap
- whether `full` means literal full bandwidth or simply no narrower active rule
- whether cap equality holds across relevant peers or only locally

## 3) Authoritative order verdict

Fields:

- order verdict
- order basis
- policy origin
- whether visible queue order was authoritative, cosmetic, or mixed
- active-window limit of that verdict

## 4) Distortion and flood-risk factors

List the currently strongest factors that can still distort a neat backlog story, for example:

- active queue cap exceeded
- non-splittable transfer exception
- queue rebuild in progress
- visible-vs-actual order mismatch
- priority inheritance frozen on selected subjects

Include one flood-risk verdict.

## 5) Safe sentence

Render the strongest sentence the receipt supports, for example:

`Quiet ended and full transfer caps returned, but the authoritative order only governs the active queue and remains subject to rebuild and transfer-class exceptions.`

Below it, show one forbidden stronger sentence, for example:

`Forbidden stronger claim: the backlog will now drain cleanly in visible queue order.`

## 6) Reopen boundary

Show exactly which later events would reopen this receipt, for example:

- release cap changes again
- queue rebuild begins or ends
- priority basis changes
- visible-vs-actual mismatch worsens
- a later aftershock creates a second release wave

## Example receipt

```text
Backlog release receipt blr_01K...

Release summary
  scope ..................... share media/raw
  release trigger ........... scheduled quiet-window expiry
  prior posture ............. scheduled-zero
  authority ................. schedule rule
  applied at ................ 2026-03-22T18:00:00-04:00

Returned cap
  send ...................... full
  receive ................... full
  meaning ................... no narrower active schedule rule

Authoritative order verdict
  verdict ................... priority-partial
  basis ..................... newer-first
  source .................... subject override
  visible queue ............. cosmetic only
  active-window limit ....... first 50,000 active files

Distortion and flood-risk factors
  exception ................. non-splittable current transfer may continue
  rebuild status ............ no rebuild at receipt time
  flood risk ................ moderate

Safe sentence
  Quiet ended and full transfer caps returned, but authoritative order is only partial and the visible queue is not the source of truth.
  Forbidden stronger claim .. The backlog will now clear cleanly in listed order.
```

## CLI projection

```text
anonsync backlog release receipt show <receipt_id>
anonsync backlog release receipt show latest --scope <scope>
```

## Success condition

A good backlog release receipt lets a future operator answer exactly what reopened, what cap returned, what order was authoritative enough to trust, what still distorted that order, and what later event would invalidate the receipt.
