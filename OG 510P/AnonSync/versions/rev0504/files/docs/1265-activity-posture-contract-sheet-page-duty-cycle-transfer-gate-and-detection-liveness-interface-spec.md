# Activity-posture contract sheet page: duty cycle, transfer gate, and detection liveness interface spec

## Purpose

The archive already has pages for reachability provenance, cohort census, redundancy floor, effective seat posture, presence, and capability floor.
What it still lacked was one ordinary page for the narrower question:

> what is this node or share willing to do **right now**: discover peers, stay visible, notice changes, announce changes, upload bytes, download bytes, propagate deletes, or sleep until the next wake window?

Current official Resilio docs make this seam concrete.
They separately describe global pause, folder pause, scheduler-based pause / bandwidth rules, LAN-exempt rate limits, Android Auto Sleep, Battery Saver stops, and per-share network restrictions.
That is useful truth.
It should not remain scattered.

## Core decision

AnonSync must expose one first-class **Activity-posture contract sheet** whenever a subject's truthful current behavior depends on operator pause, scheduler rule, rate limit, battery policy, sleep cadence, or network allowlist.

The sheet exists to answer seven things in one place:

1. whether the subject is currently visible to peers
2. whether change detection is currently live, periodic, degraded, or stopped
3. whether upload is allowed right now
4. whether download is allowed right now
5. whether delete propagation is still allowed right now
6. what current bandwidth ceiling actually applies, including LAN exceptions
7. what stronger activity sentence remains blocked

## Fixed page order

1. **Activity header**
2. **Duty-cycle card**
3. **Directionality and residual-work card**
4. **Rate / budget card**
5. **Gate stack card**
6. **Blocked stronger sentence**

### 1) Activity header

Show at minimum:

- `activity_posture_id`
- subject ref
- last posture witness time
- strongest safe sentence
- blocked stronger sentence
- current visibility grade
- current work-willingness grade

Supported headline states must include:

- `fully-active`
- `rate-limited`
- `download-blocked-upload-possible`
- `transfer-paused-observation-live`
- `sleeping-periodic-wake`
- `battery-stopped`
- `network-forbidden`
- `unknown`

Example safe sentence:

- `This share is not fully inert: byte download is currently blocked, but discovery and metadata observation remain live and deletes may still propagate.`

### 2) Duty-cycle card

Show explicit rows for at least:

- current visibility to peers
- detection mode (`live`, `periodic-wake`, `rescan-only`, `stopped`, `unknown`)
- wake cadence if any
- operator pause basis
- scheduler basis
- power/battery basis
- network-allowance basis

Every row must show:

- `current value`
- `governing gate`
- `freshness`
- `why this matters`

The operator must be able to answer:

> is this node continuously participating, intermittently waking, or truly stopped?

### 3) Directionality and residual-work card

Separate these truths explicitly:

- upload allowance
- download allowance
- discovery / announcement allowance
- delete-propagation allowance
- indexing / rescan allowance
- zero-byte / metadata-only allowance

Every row must show:

- `allowed now`
- `blocked now`
- `uncertain`
- `governing evidence`

The operator must be able to answer:

> what can still move even though the UI looks paused or limited?

### 4) Rate / budget card

Separate these truths explicitly:

- internet upload cap
- internet download cap
- LAN upload cap
- LAN download cap
- scheduler-imposed zero-rate windows
- implicit unlimited lanes

Each row must show:

- numeric ceiling or `unbounded`
- scope (`internet`, `lan`, `all`, `unknown`)
- whether the ceiling is currently active
- origin (`manual`, `scheduler`, `policy`, `license`, `unknown`)

The operator must be able to answer:

> what traffic budget is actually binding, and on which paths?

### 5) Gate stack card

Supported gate classes:

- `manual-pause-gate`
- `scheduler-gate`
- `bandwidth-cap-gate`
- `lan-exception-gate`
- `sleep-gate`
- `battery-threshold-gate`
- `network-allowlist-gate`
- `unknown-gate`

Rules:

- multiple gates may coexist and must be shown in precedence order
- every gate must specify whether it affects visibility, detection, upload, download, or all
- gates may never be collapsed into one generic `paused` explanation

### 6) Blocked stronger sentence

Examples:

- `This node is completely inactive` blocked because indexing and delete propagation still continue
- `This node is reachable and continuously watching for changes` blocked because it is asleep and only wakes on interval
- `This share is speed-limited to 2 MB/s everywhere` blocked because LAN peers remain exempt
- `This share is offline because of operator pause` blocked because the effective cause is forbidden-network policy

## Hard rules

- one badge may never hide directionality, detection liveness, and visibility at once
- `paused` must never silently imply `undetecting` or `offline`
- numeric bandwidth limits must publish whether LAN is included or excluded
- sleep and battery gates must stay distinct from operator intent
- every stronger sentence must be blocked by a named gate, not by vague status language
