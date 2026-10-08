# Runtime pack

`vhk gen-runtime-pack <project_dir>` extends the publish/distribution chain into
an explicit Python runtime handoff.

Artifacts:

- `docs/VHK_RUNTIME.md`
- `docs/VHK_RUNTIME_PLAN.json`
- `scripts/vhk_refresh_runtime_pack.sh`
- `build/publish/<bundle-name>/runtime/README.md`
- `build/publish/<bundle-name>/runtime/vhk_runtime_handoff.json`
- `build/publish/<bundle-name>/runtime/refresh_runtime_inputs.sh`
- `build/publish/<bundle-name>/runtime/requirements.runtime.txt`
- `build/publish/<bundle-name>/runtime/build-requirements.txt`
- `build/publish/<bundle-name>/runtime/wheelhouse/README.md`
- `build/publish/<bundle-name>/runtime/build_wheelhouse.sh`
- `build/publish/<bundle-name>/runtime/smoke_test_offline_install.sh`
- `build/publish/<bundle-name>/runtime/run_bundle_with_runtime.sh`
- `build/publish/<bundle-name>/runtime/emit_flatpak_python_modules.sh`

## Why this exists

The distribution pack made package metadata honest, but it still left one major
maintainer chore outside the repo: how to rebuild the VHK Python runtime in a
repeatable, reviewable way.

This pack makes that runtime story explicit.

## Design constraints

This is not a promise that VHK packages are already self-contained.

The generated handoff is explicit that:

- wheelhouses are build-host / ABI / architecture sensitive
- virtual environments are the safest reversible smoke/native-install surface
- Flatpak builders should start from one requirements file instead of a
  hand-typed dependency list
- helper daemons, remappers, uinput/device permissions, and portal/compositor
  seams still sit outside the Python wheelhouse contract

## Current handoff shape

The runtime side emits:

- dependency specs derived from the VHK package metadata
- build-system requirements for wheel creation
- a wheelhouse build script that builds third-party wheels plus the local VHK
  wheel
- an offline-install smoke test that creates a local venv and installs VHK from
  the wheelhouse with `--no-index --find-links`
- a bundle runner script that reuses that smoke venv
- a Flatpak helper script that feeds the same requirements file into
  `flatpak-pip-generator`

## Relation to distribution pack

The distribution pack keeps AppImage/Flatpak launchers pinned to the reviewed
bundle story. The runtime pack adds the missing Python runtime handoff that
those package lanes can eventually consume.

It still does **not** collapse sandboxed/package delivery into a claim of
host-global AHK-style automation parity.

## Relation to runtime embed pack

`vhk gen-runtime-pack` stops at the truthful dependency/runtime handoff.
`vhk gen-runtime-embed-pack` builds on top of it by creating exact-target
bootstrap helpers for native/AppImage/Flatpak paths so the runtime is created
where it will actually live.
