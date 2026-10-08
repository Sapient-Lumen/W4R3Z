# Candidate equivalence review page: property mismatch and stronger proof requirements interface spec

## Purpose

This page exists for the moment when an operator is not asking about policy in the abstract.
They are comparing two concrete candidate objects and need one answer:

> are these the same enough for the product's current contract, and if not, what exact mismatch or missing proof still matters?

## Core decision

Every serious sync product must own one first-class **Candidate equivalence review** page.
That page is the semantic home of:

- compared candidates
- active compare plane
- plane-by-plane mismatch list
- missing stronger proof
- allowed next actions
- post-decision receipt plan

## Fixed page order

The page always renders the same sections in the same order:

1. compared candidates strip
2. effective compare-plane card
3. property mismatch table
4. stronger-proof requirements
5. allowed decisions
6. receipt preview

### 1) Compared candidates strip

Show:

- candidate A and candidate B
- subject and seat
- current review verdict: `equivalent`, `equivalent-under-current-plane`, `content-equal-plane-divergent`, `different`, `insufficient-proof`, `unknown`
- one next honest action

### 2) Effective compare-plane card

Show the exact planes that matter for this comparison and whether each is:

- decisive now
- advisory only
- deferred to later apply
- intentionally excluded

The operator must be able to answer: **what rules are these two candidates being judged under?**

### 3) Property mismatch table

Rows should include:

- content/hash
- path/name identity
- size
- modification time
- creation time
- execute bit
- permissions
- xattrs/streams
- platform-specific decorations

For each row show:

- observed state on both candidates
- mismatch class: `equal`, `different`, `not-compared`, `not-representable-here`, `pending-proof`, `unknown`
- consequence class: `blocks-equivalence`, `narrows-claim-only`, `later-apply-gap`, `safe-to-ignore`, `needs-escalation`

### 4) Stronger-proof requirements

Show what extra evidence would upgrade the verdict, such as:

- full hash proof
- native permission-apply check
- xattr/stream witness
- target compatible landing
- manual inspect / compare

The operator must be able to answer: **what stronger proof is still missing?**

### 5) Allowed decisions

Allowed decisions may include:

- `treat as same under current plane`
- `wait for stronger proof`
- `branch candidates`
- `preserve both; apply later`
- `narrow claim and continue`
- `block and escalate`

Each decision preview must disclose:

- continuity impact
- claim ceiling after decision
- whether any plane remains deferred or narrowed

### 6) Receipt preview

Show what the equivalence receipt will preserve:

- compared candidates
- active compare plane
- mismatch rows that mattered
- chosen decision
- strongest safe sentence

## Public objects

### Candidate equivalence review page

Fields:

- `candidate_equivalence_review_page_id`
- `subject_ref`
- `seat_ref`
- `candidate_a_ref`
- `candidate_b_ref`
- `effective_compare_plane_ref`
- `property_rows[]`
- `review_verdict`
- `allowed_decision_rows[]`
- `receipt_plan`

### Property row

Fields:

- `plane_name`
- `candidate_a_state`
- `candidate_b_state`
- `mismatch_class`
- `consequence_class`
- `stronger_proof_needed`

## Guardrails

The page must never:

- let `same file` hide which property mismatch was ignored or deferred
- imply content equality means full parity when optional planes still diverge
- hide the difference between `not compared` and `equal`
- present `continue` without naming the post-decision claim ceiling

## Success criteria

The page is successful only when an operator can answer:

1. what exact candidates were compared
2. what compare plane governed the review
3. which mismatches mattered and why
4. what stronger proof would upgrade the verdict
5. what claim ceiling follows from the chosen decision
