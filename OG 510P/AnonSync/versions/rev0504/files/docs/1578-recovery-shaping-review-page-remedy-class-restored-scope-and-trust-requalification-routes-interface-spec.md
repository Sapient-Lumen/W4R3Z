# Recovery shaping review page: remedy class, restored scope, and trust requalification routes interface spec

## Purpose

This review page decides what recovery sentence is actually justified once a miss or breach has opened.
It must answer, in order:

1. What obligation truly survives after the failed promise?
2. Is full make-good still realistic, or only partial/substitute recovery?
3. What is the cheapest truthful recovery promise?
4. What facts are still missing before trust can be repaired?
5. What exact event allows a new promise instead of continued recovery-only language?

## Fixed page order

1. **Review header**
2. **Obligation-continuity panel**
3. **Make-good ladder**
4. **Trust-requalification panel**
5. **Re-promise route panel**
6. **Outcome panel**

### 1) Review header

Show:

- review id
- linked recovery id
- linked commitment id
- current review posture
- candidate recovery class
- strongest blocked stronger recovery sentence
- reviewer
- audience at risk

Supported `review_posture` values:

- `surviving-obligation-open`
- `make-good-shaping-open`
- `scope-reduction-review`
- `trust-requalification-open`
- `re-promise-gate-review`
- `ready-to-publish`
- `not-ready-to-publish`
- `closed`

### 2) Obligation-continuity panel

Required rows:

- did the full original obligation survive
- if not, what exact scope dropped
- why that scope dropped
- whether the audience must re-accept the reduced duty
- whether closure without make-good is allowed

Hard rule:

A reduced recovery scope may not be published without naming the abandoned original scope explicitly.

### 3) Make-good ladder

The page must show one rung per class:

- `diagnostic-checkpoint-only`
- `partial-make-good`
- `substitute-make-good`
- `full-make-good`

Each rung must state:

- minimum evidence required
- required restored scope at that rung
- trust status tolerated at that rung
- strongest stronger rung still blocked
- sentence that survives if that rung fails

Hard rules:

- The ladder must default to the weakest truthful rung.
- `full-make-good` is disallowed while any named abandoned scope remains.

### 4) Trust-requalification panel

Required rows:

- top fact blocking requalification
- whether the system has only resumed motion or actually restored scope
- whether breach cause is understood enough to re-promise
- whether audience acknowledgement is missing
- whether a second miss would be materially worse
- whether trust remains permanently downgraded

Supported `requalification_blocker_class` values:

- `scope-not-restored`
- `cause-not-understood`
- `only-motion-restored`
- `audience-has-not-accepted-remedy`
- `new-route-not-proven`
- `same-risk-still-open`
- `operator-capacity-not-requalified`
- `unknown-fragility`

Hard rule:

A new promise may not be published while the live route is still only `motion-restored` or `partially restored`.

### 5) Re-promise route panel

Required rows:

- earliest event that would allow a new promise
- whether that promise must start as conditional
- whether the old commitment id can be reused
- whether a new commitment id is mandatory
- whether trust repair must be published before any new target
- best weaker sentence if re-promise never becomes allowed

Supported `re_promise_route` values:

- `not-allowed-yet`
- `allowed-after-diagnostic-checkpoint`
- `allowed-after-partial-scope-acceptance`
- `allowed-after-full-scope-restoration`
- `allowed-only-with-new-commitment-id`
- `re-promise-disallowed`

### 6) Outcome panel

Supported `review_outcome` values:

- `publish-diagnostic-checkpoint-only`
- `publish-partial-make-good`
- `publish-substitute-make-good`
- `publish-full-make-good`
- `publish-trust-repair-only`
- `keep-breach-open-without-new-promise`
- `authorize-new-conditional-commitment`
- `close-recovery-with-permanent-downgrade`

Hard rule:

The page must state both the chosen remedy class and the next stronger class that remains blocked.
