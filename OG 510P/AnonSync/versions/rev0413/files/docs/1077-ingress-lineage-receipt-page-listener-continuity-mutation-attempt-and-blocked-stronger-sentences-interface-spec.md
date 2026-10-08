# Ingress lineage receipt page, listener continuity, mutation attempt, and blocked stronger sentences interface spec

## Purpose

Ingress posture is continuity-bearing.
It changes local listener state, may request off-host mutation, and affects what the product may safely claim about reachability and audience.

AnonSync therefore needs one durable receipt for any meaningful ingress-widening action.

## Receipt questions

Every receipt in this family must answer:

1. **What local listener contract was chosen?**
2. **Was router-side mutation requested, and by which authority plane?**
3. **What audience widening was accepted, requested, or refused?**
4. **What proof ceiling existed at the moment of issuance?**
5. **What stronger sentence was blocked?**

## Receipt sections

### 1) Decision summary

Show:

- decision class (`accepted`, `accepted-with-warning`, `held`, `blocked`, `retracted`)
- operator intent
- runtime namespace
- reviewed timestamp

### 2) Listener continuity snapshot

Show:

- prior listener posture
- new listener posture
- continuity relevance for forwarding, known hosts, or support recipes
- whether this decision invalidated prior ingress assumptions

### 3) Mutation snapshot

Show:

- automatic mapping requested or not
- manual forwarding expected or not
- rollback boundary
- adjacent-device / router side-effect class

### 4) Proof snapshot

Show:

- proof class at issuance
- whether relay remained in the envelope
- whether any pairwise directness had been demonstrated
- invalidators that would weaken the receipt later

### 5) Strong language block

Preserve both:

- strongest safe sentence
- blocked stronger sentence

Examples of blocked stronger sentences:

- `the runtime is now safely reachable from the internet`
- `direct connectivity is guaranteed`
- `turning this off removes all router state immediately`
- `this was only a local preference change`

## Public object

### `ingress_lineage_receipt`

Fields:

- `ingress_lineage_receipt_id`
- `seat_ref`
- `runtime_namespace_ref`
- `decision_class`
- `operator_intent`
- `prior_listener_posture`
- `new_listener_posture`
- `mutation_mode`
- `requested_audience_class`
- `proof_class_at_issuance`
- `relay_envelope_class`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `invalidators[]`
- `issued_at`

## Main surface

A compact receipt row should read like one of these:

- `accepted with warning · fixed listener + automatic mapping request · directness still unproven`
- `held · random listener incompatible with manual forwarding claim`
- `blocked · audience widening not accepted`
- `retracted locally · external rollback boundary remains weaker than immediate certainty`

## Event language

Use phrases such as:

- `ingress receipt issued`
- `listener continuity changed`
- `router mutation request recorded`
- `stronger reachability sentence blocked`

Avoid phrases such as:

- `port opened`
- `outside access granted`
- `connectivity completed`

## Design tests

The receipt fails if any of these remain true:

- later operators cannot tell whether the action mutated only the host or also requested router change
- random-vs-fixed port continuity is absent from the durable record
- the product preserves only success/failure and loses the blocked stronger sentence
