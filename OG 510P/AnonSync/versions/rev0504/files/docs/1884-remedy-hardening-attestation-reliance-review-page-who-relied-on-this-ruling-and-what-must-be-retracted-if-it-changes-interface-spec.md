# Remedy-hardening-attestation-reliance review page — who relied on this ruling and what must be retracted if it changes?

## Review question

Can the product honestly present this ruling as merely allowed for some audience, partially consumed, fully dependency-governed for the named cohort, or actively under revocation or revalidation because downstream artifacts still depend on it?

## Review panels

### 1) Eligibility versus registration review

Ask who was ever allowed to rely on the sentence and whether they were actually registered.
The review must preserve:

- allowed audience in principle
- explicit registry entries
- eligible-but-unregistered consumer classes
- consumers intentionally excluded from reliance
- current freeze-new-reliance posture

False upgrades to reject include:

- treating eligible audience as if everyone in that audience actually consumed the ruling
- treating one known automation as proof that all automations were accounted for

### 2) Consumption evidence review

Ask what evidence proves that a consumer actually consumed the ruling.
The review must classify evidence at least as:

- merely eligible
- self-declared registration only
- observed read or fetch
- observed decision or state change
- derived artifact published
- durable acknowledgement from the consumer owner

The page must reject `consumed` when the evidence only proves visibility, not use.

### 3) Dependent artifact review

Force the operator to enumerate what was derived from the ruling:

- downstream receipts
- dashboards and status surfaces
- exports or handoff packets
- operational automations
- policy or template updates
- human approvals or denials made on the basis of the ruling

The review must separate `quoted the receipt`, `made a decision using the receipt`, and `published a derivative artifact from the receipt`.

### 4) Unknown-consumer risk review

Force review of every reason the registry may still be incomplete:

- short history or log horizon
- disconnected or pending participant that may later reconnect
- linked-device spread without per-consumer acknowledgement
- startup or config rollout without callback receipt
- new synchronization instance or clone ambiguity
- stale or rotated evidence about prior consumption

The review must reject any broad-coverage claim that outruns the evidence horizon.

### 5) Supersession and reopen impact review

Ask what happens if the source receipt changed now.
The review must make explicit:

- whether new reliance freezes immediately
- which consumers need only notification
- which dependents need revalidation
- which artifacts need retraction
- which downstream receipts require reseal or supersession
- whether the source remains dependency-owning or historical only

### 6) Revocation-wave review

The page must land on explicit branches such as:

- allowed but unused
- registered, not yet consumed
- partially consumed, wave planning required
- fully dependency-governed for the named cohort
- superseded with revocation wave active
- reopened with new reliance frozen
- downstream current again after revalidation or reseal

### 7) Speakability review

The review must decide which sentence is honestly speakable now:

- `allowed for named consumers only`
- `consumed by the registered named consumers only`
- `required cohort current on governing receipt`
- `superseded; do not rely on stale dependents`
- `historical only; revocation complete`

## Output states

The page must be able to land on at least these outputs:

- audience allowed, no observed consumption
- observed consumption, dependency coverage incomplete
- named cohort covered, external cohort unknown
- stale dependents detected, revocation wave open
- revalidation complete, downstream current restored
- permanently blocked from `all dependents are current` language

