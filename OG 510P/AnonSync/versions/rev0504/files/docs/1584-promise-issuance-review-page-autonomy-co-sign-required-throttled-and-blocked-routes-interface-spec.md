# Promise issuance review page: autonomy, co-sign-required, throttled, and blocked routes interface spec

## Purpose

Once authority is modeled, the operator needs one review page that decides:

> may this actor publish the next promise autonomously, only with co-sign, only for narrower scope, only as a target/checkpoint, or not at all?

## Entry conditions

Open this page whenever:

- a new promise is being drafted after a miss or breach
- a recovery object claims `re-promise eligible`
- repeated misses suggest authority degradation
- a wider promise class is requested during probation
- a reviewer needs to overrule or restore authority

## Fixed page order

1. **Request summary**
2. **Credibility-budget review**
3. **Promise-class route review**
4. **Scope and signer route review**
5. **Outcome banner**

### 1) Request summary

Show:

- requested promise sentence
- requested promise class
- requested scope
- requested audience
- requested publisher
- linked authority object
- linked breaches and recoveries considered
- current strongest allowed sentence before review

Hard rule:

The requested sentence must stay visible even if denied.
The page may not rewrite the ask before evaluating it.

### 2) Credibility-budget review

Required checks:

- count and recency of relevant misses
- whether any same-class failure repeated
- whether recent recovery has been accepted
- whether current evidence grade supports wider authority
- whether any active dispute or reopen still exists
- whether version/world instability still applies

Supported `credibility_budget_status` values:

- `healthy`
- `reduced`
- `thin`
- `exhausted`
- `unknown`

Hard rule:

A recent successful make-good may improve budget, but may not erase repeat-failure history.

### 3) Promise-class route review

Supported route outcomes:

- `allow-autonomous-hard-commitment`
- `allow-autonomous-conditional-commitment`
- `allow-target-only`
- `allow-checkpoint-only`
- `require-co-sign-for-requested-class`
- `deny-requested-class-offer-weaker-class`
- `block-new-promise`

Hard rules:

- `allow-autonomous-hard-commitment` requires both adequate credibility budget and no active authority blocker.
- `allow-target-only` must keep target language weaker than commitment language.
- `block-new-promise` must name the next fact that could reopen review.

### 4) Scope and signer route review

Required decisions:

- whether the requested scope is allowed unchanged
- whether scope must narrow
- whether the audience must narrow
- whether signer class must strengthen
- whether the promise must be converted into a checkpoint or diagnostic milestone
- whether the promise may be issued only as internal planning and not external reliance

Supported `scope_signer_route` values:

- `same-scope-autonomous`
- `same-scope-with-co-sign`
- `narrowed-scope-autonomous`
- `narrowed-scope-with-co-sign`
- `audience-limited-only`
- `checkpoint-conversion-required`
- `diagnostic-only`
- `fully-blocked`

Hard rule:

The page must separate narrowing scope from strengthening the signer requirement.
Those are not the same concession.

### 5) Outcome banner

Supported `issuance_review_outcome` values:

- `autonomous-allowed`
- `co-sign-required`
- `scope-throttled`
- `promise-class-throttled`
- `audience-throttled`
- `blocked-pending-restoration`

The banner must publish:

- strongest allowed next sentence
- who may publish it
- whether co-sign is required
- what narrower scope or audience applies
- what stronger sentence remains blocked
- next fact that would reopen a wider route
