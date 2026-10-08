# Promise reservation proof page: reserved scope, expiry window, and ghost-hold guard interface spec

## Purpose

After a reservation decision, the operator needs one proof page that preserves:

- what room is truly spoken for
- why the hold remains valid now
- when it expires or must renew
- what stronger promise is blocked by the hold
- what event would turn the hold into ghost debt

## Core decision

AnonSync must expose one **Promise reservation proof** page for every active or recently expired hold that meaningfully shapes future admissions.

## Fixed page order

1. **Reservation claim**
2. **Current support basis**
3. **Expiry confidence**
4. **Blocked-stronger-sentence ledger**
5. **Ghost-hold guard**
6. **Surviving sentence**

### 1) Reservation claim

The page must state:

- hold owner
- hold class
- protected promise class or scope
- linked capacity lane
- current status
- next review or expiry point

### 2) Current support basis

Required basis rows:

- named future work still exists
- dependency still unresolved or scheduled
- capacity lane still appropriate
- hold has not already been superseded by a real promise
- no release event already fired
- strongest basis fact and strongest weakening fact

Supported `support_basis_grade` values:

- `well-supported`
- `supported-but-fragile`
- `aging`
- `weak`
- `unsupported`

Hard rule:

A reservation cannot remain `well-supported` once its named dependency or issuance path has disappeared.

### 3) Expiry confidence

Required rows:

- expiry type
- remaining time or unresolved condition
- renewal path
- next mandatory review
- confidence that expiry will actually be enforced
- reclaim owner readiness

Supported `expiry_confidence_grade` values:

- `tight`
- `credible`
- `fragile`
- `already-breached`

Hard rule:

A hold with `already-breached` expiry confidence must also show whether it is awaiting reclaim or has become active ghost debt.

### 4) Blocked-stronger-sentence ledger

Required rows:

- strongest blocked promise class
- strongest blocked scope
- who is blocked
- whether weaker promise classes remain open
- whether co-sign or override could bypass the hold
- what exact event would unblock the stronger sentence

Hard rule:

The page may not say only `capacity reduced`.
It must show which stronger claim is actually blocked.

### 5) Ghost-hold guard

Required checks:

- expiry crossed without release
- named future work cancelled or forgotten
- hold duplicated by another reservation
- owner no longer accountable
- reserve still consumed despite no live need
- automatic reclaim armed or not

Supported `ghost_hold_guard_status` values:

- `clean`
- `aging-watch`
- `duplicate-risk`
- `ownerless-risk`
- `expired-ghost-risk`
- `active-ghost-hold`

Hard rule:

A reservation with `active-ghost-hold` status must weaken future admission claims immediately.

### 6) Surviving sentence

The proof page must end with one strongest surviving sentence, for example:

- `This hard reservation still validly protects one narrowed recovery commitment slot until the dependency review at 14:00 tomorrow; broader delivery promises remain blocked until release or co-signed override.`
- `This hold has crossed its expiry and is now active ghost debt; no one may cite it as a valid reservation without reclaim or re-approval.`
