# VHK revision 0261 — stage and rehearsal truth surfaces

This revision extends the deployment-truth work from revision 0260 into the last
operator-facing gaps: staged release trees, installed-lane rehearsal packs, and
host dossier/support packets.

## Problem

VHK could already keep configured-vs-installed-vs-live portal truth visible in
`doctor`, host-contract/readiness output, and the deployment-facing setup/native
/service/release packs. But `gen-release-stage-pack`, `gen-host-rehearsal-pack`,
and `gen-host-dossier-pack` could still fall back to static prose.

That was a real Linux-native review gap. The more shareable the artifact became,
the easier it was to lose the host truth that made the artifact believable.

## What changed

### 1) Release-stage lanes now keep host truth attached

`gen-release-stage-pack` now carries:

- `host_truth`
- `host_requirements`
- `portal_route_contract`

into `docs/VHK_RELEASE_STAGE.md`, `docs/VHK_RELEASE_STAGE_MATRIX.md`,
`docs/VHK_RELEASE_STAGE_PLAN.json`, and the per-lane staged `README.md` files.

That means a staged ship tree can still say what the current host is missing or
reviewing instead of reading like generic package assembly text.

### 2) Host rehearsal now proves the installed lane with the same truth model

`gen-host-rehearsal-pack` now keeps current host truth and portal-route evidence
visible in both its project docs and the staged rehearsal handoff.

That matters because rehearsal is exactly where a maintainer sees the mismatch
between:

- installed helpers
- configured portal routing
- live portal interfaces
- the actually installed launcher/service lane

### 3) Host dossier packets now keep support evidence honest

`gen-host-dossier-pack` now carries the same compact host truth and
portal-route contract into the dossier docs/JSON instead of reducing support
packets to raw collection scripts plus archives.

That keeps support export closer to a reviewable claim and farther away from an
unstructured pile of logs and paths.

### 4) CLI host/session checks now reach those later surfaces

The release-stage, host-rehearsal, and host-dossier generators now accept the
same host/session check flow used by earlier deployment-facing packs, so the
truth model is not just a doc convention — it is driven by the same observed
inputs.

## Tests run

- `tests/test_release_stage_pack_cli.py`
- `tests/test_host_rehearsal_pack_cli.py`
- `tests/test_host_dossier_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
- `tests/test_native_install_pack_cli.py`
- `tests/test_service_compose_pack_cli.py`

## Follow-through

The next strong step is target-aware comparison: let staged/rehearsal/support
packs compare the current host truth against one declared flagship target lane
so VHK can say "good on this host, review on that target" without flattening
Linux support into one generic answer.
