# Readiness pack

`vhk gen-readiness-pack <project_dir>` turns the planner-backed host contract
into a live operator review.

The host-contract pack answers:

- what packages, services, permissions, and portal/session seams matter?

The readiness pack answers the next question:

- which of those seams look live on *this* host right now?

## Generated artifacts

By default the command writes:

- `docs/VHK_READINESS_REPORT.md`
- `docs/VHK_READINESS_FIXUPS.md`
- `docs/VHK_READINESS_PLAN.json`
- `scripts/vhk_refresh_readiness_report.sh`

## What it probes today

The pack currently layers these live checks on top of planner
`host_requirements`:

- current `systemd` user/system unit state for planner-backed service lanes
  such as `espanso.service`, `vhk-busd.service`, `ydotoold.service`, and common
  remapper units
- current supplemental groups for the invoking user
- `/dev/uinput` writeability (already surfaced by `vhk doctor`)
- best-effort raw-input readability for `/dev/input/event*`
- current portal backend config snapshot and existing session capability status

## Why this exists

Linux-native automation often fails in the space between:

- “the helper package is installed” and
- “the host is actually ready to run the workflow reliably”

That gap is especially visible for:

- text expanders that need user-service registration
- ydotool/remapper paths that need `/dev/uinput` and raw input access
- portal-backed features whose backend routing may still be desktop-specific
- watcher/bus lanes that should survive shell exits rather than living in an
  ad-hoc terminal

The readiness pack keeps those operator seams visible instead of burying them in
support comments or tribal knowledge.
