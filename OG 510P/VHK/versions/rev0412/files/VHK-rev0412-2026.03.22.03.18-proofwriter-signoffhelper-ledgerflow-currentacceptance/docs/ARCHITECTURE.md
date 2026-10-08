# Architecture — current i3/X11 flagship shape

VHK is no longer best understood as a generic Linux automation grab-bag.
The active architecture is a **narrow, opinionated desktop automation stack**:

**i3 binds -> `vhk-emit` -> socket-activated/session-bound `vhk busd` -> macro execution -> receipts/logs/artifacts**

The repo still keeps secondary seams, but they now exist to support or protect the
flagship lane instead of competing with it.

## Product boundary

### Tier 1

- i3 on X11
- session-bound long-lived user service
- thin emit/dispatch path
- recorder -> cleanup -> replay -> inspect -> refine loop
- readable YAML/project artifacts that a human or private LLM can safely edit

### Supporting but not primary

- ad hoc `vhk ...` CLI runs for debugging and one-shots
- packaging/install/readiness/report surfaces that help the X11/i3 lane ship well
- architecture seams that keep future backends possible without polluting the main story

### Demoted or vaulted

- broad Wayland parity as a near-term product promise
- portal-first activation as the default runtime story
- compositor-specific product shaping outside i3/X11
- app-native adapters that do not directly strengthen the X11/i3 core

## Runtime model

### 1. Warm resident lane

This is the operational center of the repo.

- i3 binds call `vhk-emit`, not the full macro runner
- `vhk busd` stays warm inside the user session
- the socket/service pair is intended to follow `graphical-session.target`
- warm dispatch is preferred when runtime readiness, replay proof, and gate checks agree
- warm-dispatch receipts are treated as current proof only when three things still match: the macro/dispatch contract, the resident daemon epoch, and the current X11/i3 desktop session
- runtime reloads should be observable as first-class receipts, not just shell sequences, because a long-lived daemon can answer probes while still serving stale project state

### 2. Direct CLI lane

This remains explicitly supported.

- `vhk run ...` for direct execution
- useful for debug, CI-style validation, focused replay checks, and fallback when warm dispatch is blocked
- should not replace the resident-runtime story in product language

## Code map

### `src/vhk/core/`

Execution model, event/watch logic, control-flow, selector helpers, and run logging.

### `src/vhk/system/`

Thin OS/X11 wrappers and runtime plumbing:

- input dispatch
- active window / cursor / screenshot helpers
- X11 recording support
- session and systemd probes
- event bus and runtime glue

### `src/vhk/i3/`

Authoritative i3 IPC integration for workspace/window/runtime truth.

### `src/vhk/project/`

Project schema, macro file handling, generated stacks, packs, readiness/support exports,
and machine-readable control-plane surfaces.

### `src/vhk/vision/`

Image match, OCR, pixels, and other visual primitives used when structural desktop control is not enough.

## Control-plane contract

The generated i3/X11 stack is the architecture's public shell/LLM contract.

The key artifact is `control-plane.json`, plus generated `bin/` wrappers such as:

- `stack_state_json.sh`
- `next_action_json.sh`
- `macro_author_queue_json.sh`
- `macro_author_loop_json.sh <macro>`
- `macro_source_json.sh <macro>`
- `macro_recording_json.sh <macro>`
- `dispatch_macro_checked.sh <macro>`

That contract now needs to answer, in one read:

- what the flagship product lane is
- which surfaces are editable truth vs generated review vs live runtime state
- how a private LLM should enter triage, per-macro review, source editing, execution, and inspection
- what session activation/environment sync is required for the warm X11 lane
- whether systemd/D-Bus activation still matches the live X11/i3 shell before trusting socket-activated restarts
- whether the *running* `vhk busd` service itself was started under the same X11/i3 session variables as the live shell
- whether the live daemon is actually running the watcher contract that the generated i3/X11 stack expects for thin dispatch

## Recorder and replay architecture

VHK's authoring posture is not “write everything from scratch.”
It is:

1. record on the real X11 desktop
2. capture window context and segment boundaries
3. clean up noisy output into readable source
4. replay with explicit waits/guards
5. treat replay proof as contract-bound: a healthy run only counts if it still matches current source + recorder evidence
6. treat replay proof as session-bound too once available: a healthy run proven on one `DISPLAY`/`I3SOCK` should not silently count as current proof for a different X11/i3 desktop session
5. inspect artifacts and receipts
6. iterate source until the macro is stable enough to sign off

That means recorder sidecars, cleanup tools, replay boards, acceptance ledgers,
and dispatch receipts are part of the real architecture, not optional garnish.

Durable acceptance is contract-bound too: a signoff is only current if it still matches the macro proof contract, replay posture, preferred execution mode, current dispatch proof contract, the current resident-runtime witness from the warm busd cache, and the current X11/i3 desktop-session digest. Because replay posture now goes stale on desktop-session drift too, and the resident-runtime witness now goes stale on daemon epoch/runtime-contract drift, durable signoff follows both the X11/i3 session truth and the actual long-lived daemon instance instead of preserving old acceptance across a rebinding, reload, or session switch.
The control plane now also carries an explicit proof-bound signoff writer (`macro-runtime-accept` / `record_runtime_acceptance.sh`), so the private-LLM/operator loop can refresh durable acceptance from current runtime proof without scraping YAML structure back out of docs or helper payloads.

## Design rules

### Prefer thin edges

Keep i3 binds, wrappers, and shell callers cheap. Put stateful ownership in the warm user service.

### Prefer explicit truth surfaces

Use machine-readable helpers instead of forcing humans or private LLMs to infer policy from scattered docs.

### Prefer X11/i3 honesty over generic Linux slogans

A correct i3/X11 contract is worth more than a vague cross-desktop promise.

### Keep seams that help the flagship lane

Retain abstractions when they protect the X11/i3 core or make future narrowing/reuse easier.
Demote abstractions that mostly serve abandoned directions.

- durable runtime signoff is now bound to the current warm-dispatch lane too, not just replay posture and macro contract truth; when dispatch history turns session-stale, runtime-stale, contract-stale, or newly blocked, the acceptance ledger reports the signoff as stale instead of silently leaving it accepted
- durable runtime signoff now also carries the resident daemon witness (`runtime_epoch_id` plus current runtime-contract digest), so a busd reload/restart can stale signoff even before new dispatch history exists
- durable runtime signoff now also carries the current desktop-session digest, so acceptance cannot silently survive a `DISPLAY`/`I3SOCK` session change when the resident service is still reachable but the desktop binding changed
