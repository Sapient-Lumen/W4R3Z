# VHK revision 0262 — target-fit contracts for later-stage packs

This revision teaches VHK’s later-stage deployment/support artifacts to compare
the **current host** with the **declared flagship lane** instead of only
repeating local host truth.

## Problem

Recent revisions made VHK much more honest about Linux host truth: setup, native
install, service-compose, release deploy, release stage, rehearsal, and dossier
artifacts can all carry compact deployment truth and portal-route evidence
forward.

But one important comparison was still missing. The repo could say what the
current host can do, and it could say what its flagship release lanes were, but
it could not yet compare those two directly in the later-stage packs.

That left a real Linux-native gap:

- a host might be healthy for its own desktop/session
- the same host might still drift from the lane the project wants to ship as
  flagship

## What changed

### 1) Added a shared target-fit contract

New module: `src/vhk/project/target_fit_contract.py`

It builds one compact comparison between:

- the current observed host truth / requirement state / portal route contract
- one selected or flagship release lane

The contract keeps the result explainable rather than numeric. It compares:

- desktop family
- backend posture
- deploy style
- trigger-route identity
- requirement-state drift

### 2) Release deploy now surfaces flagship fit

`gen-release-deploy-pack` now emits:

- top-level `flagship_target_fit` in `docs/VHK_RELEASE_DEPLOY_PLAN.json`
- per-lane `target_fit_contract` rows
- a human section in `docs/VHK_RELEASE_DEPLOYMENT.md` showing how the current
  host matches or drifts from the flagship lane

### 3) Release stage now keeps lane fit attached

`gen-release-stage-pack` now carries:

- top-level `flagship_target_fit`
- per-lane `target_fit_contract`

into the stage plan and per-lane staged `README.md` files.

That means a staged ship tree can still say not just what the local host is
missing, but whether that host actually resembles the lane being staged.

### 4) Native install, rehearsal, and dossier now keep the same comparison

`gen-native-install-pack`, `gen-host-rehearsal-pack`, and
`gen-host-dossier-pack` now all preserve the same compact target-fit contract in
addition to current host truth and portal-route evidence.

That makes install/rehearsal/support artifacts better review surfaces for Linux
operators who need both answers in one place:

- what the current machine can do
- how that machine compares with the intended flagship lane

## Tests run

- `tests/test_release_deploy_pack_cli.py`
- `tests/test_release_stage_pack_cli.py`
- `tests/test_native_install_pack_cli.py`
- `tests/test_host_rehearsal_pack_cli.py`
- `tests/test_host_dossier_pack_cli.py`
- `tests/test_setup_pack_cli.py`
- `tests/test_release_lane_pack_cli.py`

## Follow-through

The next strong step is to let planners/audits and optional operator-selected
comparison lanes consume the same contract, so VHK can compare one host against
more than just the flagship profile without collapsing everything into a single
generic Linux support score.
