# Re-promise authority contract sheet page: trust state, authority class, and approval requirements interface spec

## Purpose

After a breach, recovery, or trust downgrade, the operator still needs one page that answers:

> who may publish a new promise now, how strong may that promise be, what scope cap applies, whether co-sign is required, and what facts must land before broader promise authority returns?

## Core decision

AnonSync must expose one first-class **Re-promise authority contract sheet** whenever any prior miss, breach, degraded completion, disputed recovery, or trust-repair event might affect the right to publish new promises.

## Fixed page order

1. **Authority header**
2. **Authority-basis card**
3. **Allowed-promise-class card**
4. **Scope-cap and co-sign card**
5. **Probation and restoration card**
6. **Authority sentence**

### 1) Authority header

Show:

- authority id
- linked actor, system, or service id
- linked trust-repair object ids
- current authority posture
- current authority class
- current promise-class cap
- current scope cap
- current co-sign rule
- current probation status
- current owner of authority policy
- latest strongest allowed sentence

Supported `authority_posture` values:

- `not-reviewed`
- `fully-authorized`
- `authorized-under-probation`
- `scope-capped`
- `promise-class-capped`
- `co-sign-required`
- `target-only`
- `blocked`
- `suspended-pending-review`

Hard rule:

The header may not treat repaired motion or partial make-good as restored promise authority.
Authority is its own object.

### 2) Authority-basis card

Required rows:

- latest breach and recovery events considered
- credibility-budget basis
- trust-repair status considered
- version or world constraints considered
- approval or reviewer basis
- support or evidence posture considered
- strongest fact expanding authority
- strongest fact constraining authority

Supported `credibility_basis_class` values:

- `clean-history`
- `single-repaired-breach`
- `multiple-recent-breaches`
- `repeat-same-class-failure`
- `version-or-world-uncertainty`
- `support-gap-or-evidence-gap`

Hard rule:

The card must show why the current authority exists.
`we trust them again` is invalid unless mapped to explicit basis facts.

### 3) Allowed-promise-class card

Required rows:

- strongest promise class currently allowed
- weaker promise classes still allowed
- promise classes currently blocked
- whether only internal targets are allowed
- whether public commitments are blocked
- whether deadlines or only checkpoints are allowed
- strongest blocked stronger promise

Supported `promise_class_cap` values:

- `observation-only`
- `checkpoint-only`
- `target-only`
- `conditional-commitment-max`
- `hard-commitment-allowed`
- `no-new-promise`

Hard rules:

- `target-only` may not be rendered as a commitment.
- `hard-commitment-allowed` requires an explicit basis rather than default optimism.

### 4) Scope-cap and co-sign card

Required rows:

- maximum scope allowed for a new promise
- whether prior original scope remains blocked
- whether high-risk scopes require narrowing
- whether co-sign is required
- who may co-sign
- whether dual acknowledgement is required before publication
- whether audience-specific charters remain narrower than internal authority

Supported `scope_cap_class` values:

- `same-scope-allowed`
- `narrower-scope-only`
- `diagnostic-scope-only`
- `one-step-checkpoint-only`
- `audience-limited-only`
- `no-scope-authorized`

Supported `co_sign_rule` values:

- `none`
- `peer-review-required`
- `manager-co-sign-required`
- `operator-and-reviewer-required`
- `external-ack-required`

Hard rule:

`same team as before` is not enough.
The page must say whether scope or signature requirements narrowed.

### 5) Probation and restoration card

Required rows:

- current probation status
- probation start and expiry conditions
- events that would tighten authority again
- events that would restore broader authority
- whether repeated misses compound the downgrade
- next required review
- who may restore full authority

Supported `probation_status` values:

- `none`
- `active-clock-based`
- `active-event-based`
- `active-until-clean-delivery-count`
- `active-until-external-acceptance`
- `indefinite-until-manual-review`

Hard rule:

Probation may not clear merely because time passed with no new observation unless the page explicitly says that is sufficient.

### 6) Authority sentence

The page must end with one strongest allowed sentence in this form:

- who may promise
- what strongest promise class they may publish
- what scope cap or co-sign rule applies
- what still blocks broader authority

Examples of supported sentence shapes:

- `This service may publish only checkpoint targets for narrowed scope, and any new conditional commitment requires reviewer co-sign until one clean accepted recovery lands.`
- `Promise authority remains blocked; observation and diagnostic checkpoints are allowed, but no delivery commitment may be published until trust repair and scope parity are both restored.`
