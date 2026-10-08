# Packet shaping review page: raw, derived, redacted, and minimum-sufficient-share interface spec

## Purpose

The contract sheet names the source artifacts, audience, and packet options.
The **Packet shaping review** decides which packet form should actually leave the operator workspace.
It exists to stop raw oversharing, summary overclaiming, and silent weakening through careless redaction.

## Core decision

AnonSync must ship one review page that ranks packet-form options by **diagnostic power**, **audience fit**, **confidentiality cost**, **validation ease**, and **redaction loss**.

## Fixed page order

1. **Review header**
2. **Packet-option matrix**
3. **Minimum-sufficient-share card**
4. **Redaction-loss card**
5. **Audience-validation card**
6. **Review verdict**

### 1) Review header

Show:

- review id
- linked packet sheet id
- target audience
- current confidentiality posture
- current evidence sensitivity
- current strongest safe export sentence

Supported `confidentiality_posture` values:

- `raw-safe`
- `raw-restricted`
- `redaction-required`
- `summary-preferred`
- `export-frozen`

Hard rule:

The review must publish confidentiality posture before comparing packet forms.

### 2) Packet-option matrix

Columns:

- packet label
- packet form
- diagnostic power preserved
- appeal or challenge usability
- confidentiality cost
- audience comprehension cost
- validation ease
- recommended rank

Supported `recommended_rank` values:

- `export-first`
- `acceptable-second`
- `hold-in-reserve`
- `too-weak-for-purpose`
- `too-sensitive-for-envelope`

Hard rule:

A weaker packet cannot outrank a stronger packet merely because it is easier to read.
The matrix must weigh evidentiary strength and not just convenience.

### 3) Minimum-sufficient-share card

Required rows:

- least-sensitive packet that still serves the purpose
- stronger packet kept in reserve
- audience tasks that the minimal packet supports
- audience tasks that it cannot support
- condition that forces promotion to a stronger packet

Hard rule:

Minimum sufficient share must publish its boundary.
It may not pretend to support later challenge, appeal, or reproduction work if it does not.

### 4) Redaction-loss card

Required rows:

- redaction steps chosen
- strongest fact preserved
- strongest fact blurred or removed
- reproducibility cost
- doctrine-applicability cost
- dispute or appeal cost

Hard rule:

Redaction loss must be stated in operator language.
A later reviewer must not need the raw packet to learn that a time window, path, or identifier was removed.

### 5) Audience-validation card

Required rows:

- can audience open the packet
- can audience validate integrity
- can audience act on the packet alone
- additional context needed
- packet likely to bounce or fail transport

Hard rule:

Audience readability and audience validation are different truths.
A packet can arrive and still be unusable.

### 6) Review verdict

Supported `review_verdict` values:

- `raw-packet-approved`
- `hybrid-packet-approved`
- `redacted-packet-approved`
- `summary-only-too-weak`
- `export-deferred-for-reshaping`
- `retain-raw-send-summary-first`

Render one sentence only:

- `Review verdict: [review_verdict]. Export [packet] because it preserves [preserved power] within confidentiality posture [posture]; claims above [ceiling] remain blocked unless [stronger packet] is later released.`

## Required interactions

- **Re-rank packet options**
- **Toggle stronger reserve packet**
- **Add redaction-loss note**
- **Promote or demote minimal share**
- **Defer export**

## Failure state

If every acceptable packet is too weak for the current purpose, show:

- `All audience-safe packet forms are below the needed evidence ceiling. Export is deferred unless a stronger envelope or different audience is authorized.`
