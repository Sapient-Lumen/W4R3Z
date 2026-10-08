# Flagship runtime spec — i3/X11 warm service and LLM author loop

## Product identity

VHK is an **i3/X11-first desktop automation runtime** and the runtime core for a future
Pulover-style Linux macro studio.

## Explicit primary contract

### Desktop target

- window manager: `i3`
- display server: `X11`
- support tier: primary / default / actively optimized

### Runtime target

- a **session-bound long-lived user service** while the user is logged in
- socket activation for cheap entry into the resident daemon
- thin emitters from i3 and wrapper scripts
- startup ownership should converge on one primary owner, not multiple overlapping launch paths

### Authoring target

- preferred loop: **record -> cleanup -> replay -> inspect -> refine**
- the recorder is not just a bootstrap utility; it is part of the canonical authoring path for UI-heavy macros
- cleanup and replay proof are mandatory parts of the core experience, not optional polish

### Advanced use case

A **private LLM** should be able to:

- discover the next macro to work on
- find the editable source path for that macro
- inspect recorder context and drift
- review render/lint/validate surfaces
- execute through checked warm dispatch or direct run
- inspect latest run and dispatch receipts
- revise the macro again without scraping prose docs or reverse-engineering wrapper behavior

## Fast path

The preferred dispatch path is:

`i3 binding -> vhk-emit -> vhk busd -> macro execution`

Implications:

- i3 binds should stay cheap
- hotkey emission should not pay cold-start costs for the entire runtime when avoidable
- checked dispatch should be the default warm actuation route when the gate allows it

## Runtime guardrails

### Session attachment

The warm runtime is only healthy when it is attached to the real graphical session.
For the X11 lane that means the runtime contract should keep `DISPLAY`, `XAUTHORITY`,
`DBUS_SESSION_BUS_ADDRESS`, `XDG_RUNTIME_DIR`, and the live i3 socket binding honest.
Socket-activated restarts are not trustworthy when the systemd/D-Bus activation
environment drifted away from the current X11/i3 shell. The runtime contract
should also be able to prove whether the currently running `vhk busd` process
was started with those same bridge variables, because fixing activation state
after the fact does not repair an already-misattached resident daemon. It
should also prove that the daemon that answered the socket probe is actually
running the expected watcher contract for the generated stack's hotkey/dispatch
lane. Finally, because the resident daemon survives source edits, the runtime
contract should also prove whether the daemon's loaded project state still
matches the current project on disk before warm dispatch is trusted after LLM or
operator edits.

### Replay discipline

Prefer waits, guards, and event-aware boundaries over long blind sleeps.

### Control-plane clarity

Anything a private LLM must routinely do should have a machine-readable control-plane surface.
That now includes a first-class session-attachment witness, a dispatch-watcher contract witness, a resident-project-contract digest witness, and an observable runtime-reload receipt, not just generic unit state and shell env presence.

## Demoted directions

These are allowed only when they clearly strengthen the flagship lane:

- broad Wayland-native ambitions
- portal-first activation stories
- compositor-specific shaping outside i3/X11
- app-native adapters as roadmap centerpieces

## Required artifacts for the flagship lane

At minimum, the repo should keep improving:

- the generated i3/X11 warm stack
- control-plane JSON and wrapper surfaces
- recorder sidecars and cleanup tooling
- replay/runtime/dispatch/acceptance boards
- startup ownership and readiness diagnostics
- X11 window/focus/workspace control quality


## Replay proof now binds to a macro proof contract

A healthy past run is only resident-runtime proof if it still matches the **current** editable macro source and its recorder sidecar freshness state. VHK now records a `macro_proof_contract` on `run_start` and downgrades replay posture to `stale_contract` when a later source edit, recorder-sidecar change, or legacy log without that contract breaks the binding.

Revision 0407 makes that replay truth more X11/i3-honest by binding it to the desktop session too. When a run captures `desktop_session_contract` at `run_start`, later replay inspection compares the current shell's `DISPLAY`, `XAUTHORITY`, `I3SOCK`, and desktop/session identity against that witness. If those drift, replay posture becomes stale and the bounded answer is to rerun on the current desktop session rather than trust an old healthy log from a different i3/X11 binding.


## Resident dispatch receipts

Warm-dispatch receipts now carry two different honesty contracts:

- the **dispatch receipt contract** says whether the receipt still matches the
  current macro source, recorder sidecar, bus event, and dispatch selector
- the **dispatch runtime witness** says whether the receipt was emitted against
  the same resident `vhk busd` epoch that is currently advertised by the
  daemon's runtime-state cache

The runtime-state cache is written by the resident daemon on startup and reload.
That keeps the hot emit path thin: receipts can capture daemon identity cheaply
from disk, while `check_runtime_json.sh` still owns the stronger bounded live
probe for current dispatch-path truth.

## Durable runtime acceptance now binds to a proof contract

Stored runtime signoff is only current if it still matches the selected macro's current runtime posture, preferred execution mode, replay posture, macro proof contract, dispatch receipt contract, and the current resident-runtime witness cached by busd. Legacy posture-only signoff remains visible, but it is now treated as stale until the ledger stores a `proof_contract` that matches current runtime truth.


## Dispatch receipt session truth

Warm dispatch receipts are now session-bound in the same X11/i3-specific sense as replay proof. Each receipt captures the emitting shell's desktop session contract, and receipt health compares that witness against the current shell before treating the receipt as current warm-path evidence. Legacy receipts without that witness remain inspectable, but a captured session witness now goes stale when `DISPLAY`, `XAUTHORITY`, `I3SOCK`, `XDG_SESSION_TYPE`, or `XDG_CURRENT_DESKTOP` drift.


Revision 0409 extends durable runtime signoff into the resident dispatch lane. `runtime_acceptance_contract` now carries `dispatch_history_posture_id` and `dispatch_history_attention_id`, so an old accepted runtime posture goes stale when the warm bus lane has since changed underneath it even if the macro source itself did not. Revision 0410 tightens that one step further with `resident_runtime_epoch_id` and `resident_runtime_contract_digest`, so a busd reload/restart also stales durable signoff before the next emit. That keeps durable signoff aligned with the actual always-on X11/i3 service state rather than just replay posture. Revision 0411 binds the same durable signoff to the current desktop session too with `desktop_session_contract_digest`, so operator acceptance from one `DISPLAY`/`I3SOCK` binding does not silently remain current after the shell moves to another X11/i3 session.
