# VHK revision 0259 — portal route contracts in host/readiness packs

This revision takes the manifest-aware portal work from revision 0258 and carries it into the project-level deployment packs.

## Problem

`vhk doctor` could already explain a lot more about portals than before, but host-contract/readiness artifacts still flattened that knowledge back into a thin “portal routing config present/missing” story.

That left a real Linux-native review gap:

- a backend could be installed yet excluded by `UseIn`
- a usable backend could exist on disk while the live frontend interface was still missing on D-Bus
- `portals.conf` could be absent or malformed while the host still had plausible fallback backends installed
- operator-facing docs had to jump back to raw doctor JSON to compare configured vs installed vs live

## What changed

### 1) New shared `portal_route_contract` surface

Host-contract and readiness plans now include a machine-readable `portal_route_contract` that summarizes:

- config status / config path / preferred backends from `portals.conf`
- installed backend manifests and whether they are usable on the current desktop
- per-interface live status for Screenshot, ScreenCast, RemoteDesktop, InputCapture, and GlobalShortcuts
- mismatches such as missing configured backend ids, desktop-ineligible configured backends, and “installed but not live” interfaces

### 2) Host-contract docs now expose route truth directly

`VHK_HOST_REQUIREMENTS.md` and `VHK_HOST_FIXUPS.md` now include explicit portal-route sections instead of leaving that information buried in raw snapshot JSON.

### 3) Readiness docs now keep portal proofs visible

`VHK_READINESS_REPORT.md` and `VHK_READINESS_FIXUPS.md` now carry the same configured/installed/live comparison forward, so operator review can stay in one pack.

## Why this matters

This is closer to how Linux automation actually fails in the field. Package presence is not enough. Configured routing, installed backend manifests, and live D-Bus availability are three different truths, and VHK now keeps them visible together in the deployment-review surfaces.

## Tests run

- `tests/test_host_contract_pack_cli.py`
- `tests/test_readiness_pack_cli.py`
- `tests/test_doctor_cli.py`
- `tests/test_portal.py`
- `tests/test_global_shortcuts_portal.py`
- `tests/test_capability_audit_pack_cli.py`
- `tests/test_activation_pack_cli.py`
- `tests/test_route_selection_pack_cli.py`
- `tests/test_plan_project_cli.py`
- `tests/test_validate_cli.py`
