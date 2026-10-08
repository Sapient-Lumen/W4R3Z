# Support / triage pack

`vhk gen-support-pack <project_dir>` turns the existing planner + diagnostics
surfaces into a maintainer-facing support handoff.

Generated artifacts:

- `docs/VHK_SUPPORT_GUIDE.md`
- `docs/VHK_SUPPORT_CHECKLIST.md`
- `docs/VHK_SUPPORT_PLAN.json`
- `scripts/vhk_capture_support.sh`

This is intentionally **not** a magic "send everything" button.
Linux automation failures often involve a mix of:

- session capability facts (`doctor`)
- project structure facts (`validate`, `plan-project`)
- run evidence (event logs, report summaries, traces, failure screenshots)
- deployment expectations (operator + verification packs)
- privacy review (screenshots, clipboard text, prompt answers, bundles)

The support pack closes that gap by generating:

- a human guide for what to capture and why
- a checkbox-style checklist for maintainer handoff
- a machine-readable plan other tools can reuse
- a shell-oriented capture script that can gather the most useful artifacts into
  `support/capture_*/`

## Example

```bash
vhk gen-support-pack . --force
sh scripts/vhk_capture_support.sh
```

The capture script gathers:

- `vhk doctor --json`
- `vhk validate . --json`
- `vhk plan-project . --json`
- regenerated operator / verification / support docs under the support folder
- latest run summary + trace when event logs exist
- recent event logs, watcher logs, failure JSON, screenshots, and diff images
- an optional deterministic project bundle when
  `SUPPORT_INCLUDE_PROJECT_BUNDLE=1`

## Why this exists

The rest of the repo already did a good job answering:

- what kind of Linux-native product lane a project fits
- which surfaces/install recipes/operators/release gates it should use

But there was still a practical gap once something broke on a real machine.
`gen-support-pack` turns that gap into a first-class project surface instead of
leaving triage quality up to ad-hoc shell history and incomplete bug reports.

## Installed-host dossier guidance

When the failure is in launcher discovery, native install layout, or user-session services, prefer the dossier's share-safe lane before attaching anything outside the team:

- `vhk gen-host-dossier-pack . --force`
- `sh build/publish/<bundle>/dossier/redact_host_dossier.sh`
- `sh build/publish/<bundle>/dossier/archive_share_dossier.sh`

The raw dossier zip is still useful for trusted internal debugging, but the support posture now treats the share-safe dossier archive plus its redaction report as the default external handoff.

