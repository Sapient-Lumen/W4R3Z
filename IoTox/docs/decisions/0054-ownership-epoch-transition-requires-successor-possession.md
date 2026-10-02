# ADR 0054 — ownership-epoch transition requires successor possession

Status: accepted and implemented
Date: 2026-08-14

## Context

The v1 authority ledger supports explicit owner succession inside one ownership epoch: an active
owner grants another full-capability owner, and one of the remaining owners may then revoke the old
owner. That does not retire every delegated key or distinguish a planned transfer from continued
administration under the same constitutional generation.

Phrase compromise needs a stronger cut. After a successful cut, the old RecallRoot owner and every
controller delegated in the old epoch must be unable to authenticate or authorize new work. A
single record signed only by the old owner cannot prove that the intended successor controls the
new key, while a vendor or manufacturer reassignment signature would violate IoTox sovereignty.

## Decision

An ownership-epoch transition is an adjacent two-record ceremony:

1. An active owner signs an ordinary full-capability `owner` grant naming the successor in the
   current epoch. This record nominates the successor only when the subject was not already an
   active owner.
2. Before any intervening authority mutation, that nominated successor signs an
   `epoch-transition` record proving possession of the successor key.

The transition record is canonical authority-ledger format v1 with action value 4. It must:

- target the same stable device and name the nominated successor as both issuer and subject;
- use role `owner`, the complete v1 capability set, zero time fields, and a valid successor
  signature;
- advance the ownership epoch exactly once, reset the in-epoch sequence to 1, and name the prior
  epoch's exact tail digest;
- immediately follow the nominating grant, with no mutation permitted between nomination and
  transition.

Applying the transition replaces the live principal set with exactly the successor owner. Prior
owners and delegates remain visible in the immutable signed record history but have no live state
in the new epoch. The ledger record count remains global and bounded. Authority sessions invalidate
on the changed head and must prove again against epoch 2 or later. Exact replay of the current
transition tail is idempotent and cannot increment the epoch twice.

## Remote ceremony

Remote nomination and transition remain separately named operator actions even though they use the
existing signed-record request/result transport:

```text
current owner proves against the target's exact current head
current owner signs and sends the successor nomination
authority head changes and all proofs invalidate
successor proves against the new current-epoch head
successor signs and sends the epoch-transition record
target enters the next epoch with only the successor active
successor proves again against the new epoch before further administration
```

The generic remote self-delegation ceremony continues to reject owner role. Nomination accepts only
a full owner grant to a subject other than the proven current owner. Transition accepts only the
currently nominated successor as proven remote owner, issuer, subject, and signer.

## Recovery and compromise boundary

For planned transfer, the old owner authorizes the successor and the successor demonstrates key
possession. For suspected phrase compromise, the same ceremony cuts off future use of the old
phrase and all old-epoch delegates once the transition is durably applied.

It cannot undo actions taken before the cut or prevent a holder of the compromised current phrase
from racing a conflicting valid mutation. IoTox has no consensus service to order concurrent
owners and no monotonic hardware witness to detect restoration of an older complete valid ledger.
Operators must perform compromise response while they still control a currently authorized owner
and can observe the target's exact result.

If no current owner secret remains available, there is no nondestructive ownership transition.
Destructive physical reclaim must create a visibly new ownership domain (and potentially a new
device identity) under a separately specified local-presence ceremony. It is not implemented by
this transition, and there is still no vendor reassignment key.

## Evidence gates

- deterministic rejection of skipped nomination, stale/intervening nomination, same-owner
  nomination, wrong signer, epoch skip, non-reset sequence, and altered prior tail;
- one successful transition that removes every old principal from live authority;
- exact duplicate handling and restart replay at the new epoch and sequence 1;
- pre-transition commands/proofs fail under the new epoch while successor proof succeeds;
- genuine two-peer nomination, transition, old-owner denial, successor re-entry, and fresh
  delegation in normal native and TCP-only modes.
