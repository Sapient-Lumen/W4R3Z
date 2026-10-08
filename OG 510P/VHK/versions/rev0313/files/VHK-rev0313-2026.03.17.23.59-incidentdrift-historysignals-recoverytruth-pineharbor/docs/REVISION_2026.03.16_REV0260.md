# VHK revision 0260 — deployment truth across setup/native/service/release packs

This revision takes the portal-route/host-truth work from revisions 0258–0259
and carries it into the deployment-facing packs where operators actually install
and stage VHK.

## Problem

Host-contract/readiness output could already explain configured vs installed vs
live portal reality, but setup/native/service/release docs still tended to fall
back to package hints and static install prose.

That left an avoidable Linux-native review gap:

- setup docs could tell you what to install without showing the current host
  truth they were trying to fix
- native/service packs could look deployment-ready while hiding a degraded input
  or portal state
- release deploy docs could read like lane claims detached from the current host
  evidence

## What changed

### 1) Setup packs now surface observed deployment truth

`gen-setup-pack` now accepts host-check context and carries compact observed
deployment truth into `VHK_SETUP_GUIDE.md`, `VHK_SETUP_MATRIX.md`, and
`VHK_SETUP_PLAN.json`.

The setup docs now keep visible:
- current host truth summary (`ok` / `review` / `blocked`)
- blocking/review issue counts
- the shared `portal_route_contract`

### 2) Native-install and service-compose packs now keep host truth attached

`gen-native-install-pack` and `gen-service-compose-pack` now thread the same
host/session evidence into their plans/docs instead of reducing everything to
filesystem layout plus shell commands.

That means install/service handoffs now surface:
- current host truth summary
- portal-route contract evidence
- reviewed host requirements already known from planner/readiness work

### 3) Release-deploy packs now keep lane claims tied to host truth

`gen-release-deploy-pack` now carries host truth and portal-route evidence into
release deployment docs and JSON. Per-lane install/autostart guidance can now be
reviewed next to the observed Linux host truth instead of floating as static
copy.

## Why this matters

This is a better Linux-native posture. Package hints are necessary, but they are
not enough. Deployment review should keep configured routing, installed backend
manifests, live helper state, and live portal interfaces visible in the same
operator-facing packs that ask people to install and stage the system.

## Tests run

- `tests/test_setup_pack_cli.py`
- `tests/test_release_deploy_pack_cli.py`
- `tests/test_native_install_pack_cli.py`
- `tests/test_service_compose_pack_cli.py`
- `tests/test_host_contract_pack_cli.py`
- `tests/test_readiness_pack_cli.py`

## Additional notes

The main follow-through left after this revision is to carry the same compact
deployment-truth contract into release-stage and host-rehearsal surfaces so
staged artifacts and installed-lane rehearsals do not regress to static prose.
