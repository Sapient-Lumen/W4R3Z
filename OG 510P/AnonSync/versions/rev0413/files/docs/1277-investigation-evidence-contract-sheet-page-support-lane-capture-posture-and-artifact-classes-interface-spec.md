# Investigation-evidence contract sheet page: support lane, capture posture, and artifact classes interface spec

## Purpose

The archive already has pages for reachability, activity posture, attestation, and chronology.
What it still lacked was one ordinary page for the narrower question:

> if something is wrong, what evidence lane actually exists here, what posture is required to capture it, what artifact classes are available, and what stronger diagnosis remains blocked?

Current official Resilio docs make this seam concrete.
They separately describe manual log capture, automatic feedback capture, mobile export, crash dumps, core dumps, NAS storage locations, log-size rotation, and iperf benchmarking while Sync is shut down.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Investigation-evidence contract sheet** whenever an operator is asked to capture evidence, decide whether a support lane exists, or judge which artifact class can actually justify a diagnostic sentence.

The sheet exists to answer seven things in one place:

1. what support lane currently exists
2. what capture posture is actually active
3. what artifact classes are currently collectible
4. what evidence window is required
5. what survival / rotation / cleanup risks exist
6. what privacy or redaction posture applies
7. what stronger diagnostic sentence remains blocked

## Fixed page order

1. **Investigation header**
2. **Support-lane card**
3. **Capture-posture card**
4. **Artifact-class matrix**
5. **Survival and redaction rail**
6. **Blocked stronger sentence**

### 1) Investigation header

Show at minimum:

- `investigation_contract_id`
- subject ref or incident ref
- actor / seat ref
- last evidence posture witness time
- strongest safe sentence
- blocked stronger sentence
- current support lane
- current capture posture

Supported headline states must include:

- `business-direct-support-lane`
- `self-serve-feedback-lane`
- `community-only-help-lane`
- `capture-ready-live-runtime`
- `capture-requested-restart-still-needed`
- `postmortem-only`
- `unknown`

Example safe sentence:

- `This seat can capture live rolling logs, but the current lane only guarantees self-serve evidence export rather than direct engineer review.`

### 2) Support-lane card

Separate these truths explicitly:

- entitlement lane
- intake path
- who may receive the artifact
- expected human review class
- escalation ceiling
- blocked stronger sentence

Supported values must include at least:

- `business-direct-ticket-lane`
- `self-serve-feedback-form`
- `community-forum-plus-help-center`
- `payment-or-licensing-web-form-only`
- `local-export-only`
- `unknown`

Hard rule:

- `contact support` must never be shown as a flat promise unless the lane and receiver class are witnessed.

Each row must show:

- current value
- witness source
- freshness
- why it matters

### 3) Capture-posture card

Separate these capture truths explicitly:

- `logging-disabled`
- `logging-requested-restart-pending`
- `logging-live-window-open`
- `live-repro-window-insufficient`
- `post-crash-residue-available`
- `offline-benchmark-mode`
- `cleanup-risk-open`
- `capture-posture-unknown`

Each row must show:

- whether the runtime is live or stopped
- whether reproduction is still required
- minimum suggested window
- rotation risk
- cleanup risk
- blocked stronger sentence

The operator must be able to answer:

> can this incident still be observed live, or am I already down to residue and offline comparison artifacts?

### 4) Artifact-class matrix

Separate these artifact classes explicitly:

- rolling debug log
- rotated log archive
- automatically attached feedback bundle
- manually exported log bundle
- crash report
- mini dump
- core dump
- mobile-exported log set
- NAS-path log set
- external transport benchmark
- operator narrative only

Each row must show:

- collection path
- capture preconditions
- runtime requirement (`live`, `postmortem`, `runtime-stopped`, `either`)
- survivorship ceiling
- privacy / redaction posture
- strongest safe claim supported by that artifact class

### 5) Survival and redaction rail

This rail must answer:

- what can rotate away?
- what can cleanup delete?
- what lives under service-account or vendor-specific paths?
- what evidence is likely to contain peer names, paths, addresses, or identifiers?
- what was redacted, what was not, and what remains unknown?

Supported states:

- `rotation-risk-low`
- `rotation-risk-open`
- `cleanup-will-discard-current-logs`
- `service-account-path-variant`
- `vendor-path-variant`
- `redaction-not-yet-reviewed`
- `redaction-reviewed`
- `unknown`

### 6) Blocked stronger sentence

Examples:

- `Support will definitely review this` blocked because only a self-serve or community lane was proven
- `Debug logging is active now` blocked because restart or sufficient runtime window was not yet witnessed
- `This benchmark proves the live runtime is healthy` blocked because iperf evidence was collected with Sync shut down
- `The necessary evidence is preserved` blocked because rotation or cleanup risk remained open

## Hard rules

- support lane, intake path, and human review class must never be collapsed into one promise
- live runtime evidence and runtime-stopped benchmark evidence must never be merged
- artifact survivorship must stay visible whenever rotation or cleanup exists
- redaction posture must be explicit; absence of redaction review may not be silently treated as safe export
