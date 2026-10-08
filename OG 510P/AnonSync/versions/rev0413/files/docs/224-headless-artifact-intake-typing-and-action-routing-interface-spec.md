# Headless artifact intake, typing, and action-routing interface spec

## Purpose

The archive already has offer artifacts, redemption lineage, and bringup contracts.
What it still lacked was one explicit contract for a narrower but very real headless seam:

> when a user pastes or imports something on a headless/Linux seat, what page proves whether it is a subject offer, a member grant, a capability seat, a license file, or another artifact class **before** the product takes action?

Current official Resilio docs make this seam vivid.
They still say Linux routes shared-folder links, license-seat links, and license activation through the same `Enter a key or link` entry path in WebUI.
A separate license-application guide still says headless use first creates identity, then applies the license file, while other docs route share offers and seat links through ordinary manual-connection style intake.

That is not just a cosmetic shortcut.
It means materially different artifact classes still converge on one generic intake verb.

AnonSync should therefore type imported artifacts before action and route each kind through a named reviewed lane.

## Core decision

Every imported string/file/QR/protocol artifact must pass through a two-step contract:

1. **artifact typing** — what kind of thing is this?
2. **action routing** — which reviewed lane does that kind belong to?

The product must never let one generic `enter key or link` control become the semantic home for unrelated actions.

## Fixed review order

Every headless artifact-intake surface should render the same sections in the same order:

1. **Artifact classification**
2. **Required prerequisites**
3. **Routed action lane**
4. **Receipt and audit trail**

### 1) Artifact classification

This section should show:

- source form (`text`, `file`, `qr`, `protocol-url`, `clipboard`, `other`)
- detected artifact class (`subject-offer`, `member-introduction`, `capability-seat`, `capability-file`, `identity-bootstrap`, `unknown`)
- confidence level
- any ambiguous interpretations

The operator must be able to answer: **what did I paste or import?**

### 2) Required prerequisites

This section should show:

- whether local identity already exists
- whether a capability envelope or control session is needed
- whether this artifact can be inspected without mutating anything
- which missing prerequisites block apply

The operator must be able to answer: **what must already exist before this artifact can honestly do anything?**

### 3) Routed action lane

This section should show:

- target lane (`inspect offer`, `claim subject`, `approve seat`, `apply capability`, `bootstrap identity`, `reject/hold`)
- whether the next step is local-only or remote-approval-based
- whether the artifact widens authority, consumes a seat budget, or merely reveals an offer
- what receipt type will be emitted if applied

The operator must be able to answer: **which workflow am I actually entering?**

### 4) Receipt and audit trail

This section should show:

- artifact fingerprint
- classification decision
- action lane chosen
- whether the operator inspected only or applied
- successor receipt, if any

The operator must be able to answer: **what later proves what this imported artifact really was and what I did with it?**

## Public objects

### `artifact_intake_review`

Fields:

- `artifact_intake_review_id`
- `seat_ref`
- `source_form`
- `artifact_fingerprint`
- `classification_candidates[]`
- `chosen_class`
- `prerequisite_findings[]`
- `routed_action_lane`
- `apply_blockers[]`
- `generated_at`

### `artifact_intake_receipt`

Fields:

- `artifact_intake_receipt_id`
- `review_ref`
- `seat_ref`
- `artifact_fingerprint`
- `chosen_class`
- `action_taken` (`inspect-only`, `hold`, `apply`, `reject`)
- `successor_ref` nullable
- `created_at`

## Main surface

A compact row should read like one of these:

- `subject offer detected · inspect before claim`
- `capability file detected · identity required before apply`
- `seat grant detected · remote approval lane`
- `ambiguous artifact · hold for typed review`

## CLI shape

```text
anonsync artifact intake inspect --from clipboard
anonsync artifact intake inspect --file ~/Downloads/token.asf
anonsync artifact intake route <review>
anonsync artifact intake receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- share offers, seat grants, and capability files still enter through one generic verb with no typed preview
- headless intake requires the operator to remember product lore about which artifact needs identity first
- import history cannot later prove whether the user inspected or actually applied the artifact
- a single pasted string can widen authority or consume seat budget without a typed action lane

## Non-clone reason

Current Resilio docs still route multiple materially different artifact classes through one generic `Enter a key or link` path on Linux/headless seats.
AnonSync should instead type imported artifacts first and route each one into a named reviewed workflow.
