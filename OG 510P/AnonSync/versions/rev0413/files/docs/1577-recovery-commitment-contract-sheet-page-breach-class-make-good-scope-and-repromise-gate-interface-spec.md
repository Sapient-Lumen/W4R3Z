# Recovery commitment contract sheet page: breach class, make-good scope, and re-promise gate interface spec

## Purpose

Once a commitment is missed or breached, the operator still needs one page that answers:

> what is now owed, what part of the original scope still governs, what narrower or substitute recovery scope is allowed, and when is a new promise actually allowed again?

## Core decision

AnonSync must expose one first-class **Recovery commitment contract sheet** whenever a commitment is missed, a breach opens, any public recovery statement is requested, or any operator needs to distinguish apology language from a real make-good duty.

## Fixed page order

1. **Recovery header**
2. **Breach basis card**
3. **Surviving-obligation card**
4. **Make-good scope card**
5. **Trust-repair and re-promise card**
6. **Recovery sentence**

### 1) Recovery header

Show:

- recovery id
- linked commitment id
- linked breach event id
- named deliverable
- current recovery posture
- current breach class
- current make-good class
- current trust-repair status
- current owner
- current audience
- latest surviving sentence

Supported `recovery_posture` values:

- `not-opened`
- `breach-open-unshaped`
- `surviving-obligation-shaped`
- `make-good-proposed`
- `make-good-published`
- `scope-reduced-under-review`
- `substitute-scope-under-review`
- `trust-repair-blocked`
- `re-promise-gate-open`
- `closed`

Hard rule:

The header may not imply that a new promise exists merely because the original one failed.
Breach and recovery are separate objects.

### 2) Breach basis card

Required rows:

- linked commitment class
- breach class
- breach trigger fact
- original promise window
- public sentence that failed
- whether the miss was declared on time
- strongest fact still keeping the breach open
- strongest fact making recovery possible

Supported `breach_class` values:

- `target-missed`
- `conditional-commitment-failed`
- `hard-commitment-breached`
- `renegotiation-defaulted`
- `withdrawal-after-commitment`

Hard rule:

The card must preserve the exact sentence that failed.
Recovery may not erase the breached statement.

### 3) Surviving-obligation card

Required rows:

- surviving obligation after breach
- whether the original full scope still governs
- whether only a reduced scope survives
- whether recovery is diagnostic-only first
- whether external acknowledgement is owed
- whether trust downgrade must be published
- deadline class for the surviving obligation

Supported `surviving_obligation_class` values:

- `none-breach-only`
- `full-original-scope-still-owed`
- `partial-original-scope-still-owed`
- `substitute-outcome-owed`
- `diagnostic-clarity-owed-before-delivery`
- `closure-note-only`

Hard rule:

`we are still working on it` is invalid unless it maps to one supported obligation class.

### 4) Make-good scope card

Required rows:

- make-good class
- promised recovery scope
- what original scope is no longer promised
- whether substitute deliverable is allowed
- whether partial completion counts as recovery success
- whether audience re-acceptance is required
- strongest blocked stronger make-good

Supported `make_good_class` values:

- `none-yet`
- `full-make-good`
- `partial-make-good`
- `substitute-make-good`
- `diagnostic-checkpoint-only`
- `trust-repair-only`

Hard rules:

- `full-make-good` requires the original scope to remain live.
- `substitute-make-good` requires naming what original scope is abandoned.
- `diagnostic-checkpoint-only` may not impersonate a delivery promise.

### 5) Trust-repair and re-promise card

Required rows:

- current trust-repair status
- exact facts required before any new promise
- whether resumed motion is sufficient
- whether restored scope is sufficient
- whether audience acknowledgement is required before re-promise
- who may reopen commitment authority
- next event that would permit a new promise

Supported `trust_repair_status` values:

- `not-started`
- `motion-restored-only`
- `partial-scope-restored`
- `full-scope-restored-not-yet-retrusted`
- `re-promise-eligible`
- `trust-repaired`
- `permanently-degraded`

Hard rule:

`motion-restored-only` may not authorize a new promise.

### 6) Recovery sentence

The page must end with one strongest allowed sentence in this form:

- what failed
- what is still owed now
- what scope is promised or not promised in recovery
- whether trust is repaired enough for a new promise

Examples of supported sentence shapes:

- `The original commitment breached; full original scope is still owed, but only a diagnostic checkpoint is promised next and no new delivery promise is authorized yet.`
- `The original commitment breached; a partial make-good for the narrowed scope is now promised, and trust remains degraded until that scope is accepted.`
