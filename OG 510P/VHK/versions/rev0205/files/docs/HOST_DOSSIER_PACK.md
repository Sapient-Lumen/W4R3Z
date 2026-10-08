# Host dossier pack

`vhk gen-host-dossier-pack <project_dir>` generates a shareable installed-host
support packet on top of the reviewed native + service + rehearsal lane.

It writes:

- `docs/VHK_HOST_DOSSIER.md`
- `docs/VHK_HOST_DOSSIER_PLAN.json`
- `scripts/vhk_refresh_host_dossier_pack.sh`
- `build/publish/<bundle-name>/dossier/README.md`
- `build/publish/<bundle-name>/dossier/vhk_host_dossier_handoff.json`
- `build/publish/<bundle-name>/dossier/collect_host_dossier.sh`
- `build/publish/<bundle-name>/dossier/archive_host_dossier.sh`
- `build/publish/<bundle-name>/dossier/smoke_test_host_dossier.sh`

## Why this exists

The reviewed lane already had:

- an installed launcher/home/status surface
- a bundle-native user-service lane
- a rehearsal report that proves desktop and service visibility

What it still lacked was one operator-facing packet that could be shared after a
host run. The host dossier pack closes that gap by collecting launcher state,
rehearsal output, session facts, and best-effort systemd visibility under one
XDG-state root.

## What gets captured

- installed launcher `--home-json` output
- installed launcher `--status-json` output
- packaged doc inventory from `--list-docs`
- host rehearsal report JSON/Markdown when available
- current session facts (`XDG_SESSION_TYPE`, `XDG_CURRENT_DESKTOP`, etc.)
- `loginctl show-session` output when logind is available
- `systemctl --user show` unit-path and expected-unit state when systemd user
  services are part of the lane
- `journalctl --user` excerpts for VHK-owned units when per-user journal access
  is available
- a zipped dossier archive after privacy review

## Important constraints

- This is a best-effort operator/support surface. Missing `loginctl`, skipped
  `systemctl`, or unavailable per-user journals should be recorded as gaps, not
  silently treated as success.
- The dossier may contain recent launcher usage, session names, unit paths, or
  journal excerpts. Review it before sharing outside your team.
- For Wayland-first projects, a green dossier still proves only one conservative
  reviewed lane. It does not erase portal consent, compositor policy, or helper
  daemon requirements.

## Share-safe handoff

The pack now emits two archive lanes instead of one:

- `archive_host_dossier.sh` keeps the raw XDG-state dossier for trusted internal debugging.
- `redact_host_dossier.sh` builds `share-safe/` plus `VHK_HOST_DOSSIER_REDACTION.json`.
- `archive_share_dossier.sh` zips only the redacted share-safe tree for external handoff.

That makes the privacy step more reproducible: paths under `$HOME`/XDG roots, email addresses, bearer/provider-token patterns, and secret-like assignments get redacted automatically, while the redaction report still warns when suspicious leftovers need a human review.

