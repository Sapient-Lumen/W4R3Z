# Decision — flagship stack day-2 verify/repair stays local and bounded (2026.03.23)

## Decision

The generated i3/X11 flagship stack now treats **post-install verification and bounded repair** as first-class top-level surfaces:

- `verify_user_session_json.sh`
- `verify_user_session.sh`
- `repair_user_session.sh`

These stay **stack-local** beside `install_user_session.sh`, `uninstall_user_session.sh`, and `smoke_install.sh`.

## Why

The previous revision solved initial install, but it still left one real operator/LLM gap:

> after the stack is copied into XDG-local paths, what is the smallest authoritative surface that says whether the installed lane is still intact, still bound to the expected X11/i3 session contract, and repairable without reopening the whole runtime story?

That gap matters for the active product direction:

- the warm resident lane is the primary product runtime
- recorder/cleanup/replay loops depend on the installed lane being believable
- a private LLM needs one **bounded install verdict** instead of scraping systemd units, XDG paths, and helper probes by hand

## Rule

Use the stack-local day-2 surfaces in this order:

1. `smoke_install.sh` before touching the live desktop
2. `install_user_session.sh` to land the stack
3. `verify_user_session_json.sh` to read the installed-lane verdict
4. `repair_user_session.sh` only when the installed lane drifted and the bounded reinstall + startup bridge is the right response
5. `reload_runtime_json.sh` / `restart_runtime_json.sh` only after the installed-lane contract itself is already present

## Non-goals

This does **not** widen the product to a generic Linux installer framework.

It does **not** replace the runtime ticket, stack-state snapshot, or per-macro dispatch/replay/acceptance control plane.

It does **not** make autostart a co-equal owner; graphical-session-bound user units remain primary, and XDG autostart remains fallback-only.

## Product effect

This keeps the X11/i3-first story tighter:

- install is explicit
- installed-lane truth is explicit
- repair stays bounded
- ad hoc CLI runs still exist, but the resident runtime is easier to trust and recover
