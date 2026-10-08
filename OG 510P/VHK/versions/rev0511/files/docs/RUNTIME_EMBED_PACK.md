# Runtime embed pack

`vhk gen-runtime-embed-pack <project_dir>` extends the runtime handoff into
exact-target embedding helpers.

Artifacts:

- `docs/VHK_RUNTIME_EMBED.md`
- `docs/VHK_RUNTIME_EMBED_PLAN.json`
- `scripts/vhk_refresh_runtime_embed_pack.sh`
- `build/publish/<bundle-name>/runtime/embed/README.md`
- `build/publish/<bundle-name>/runtime/embed/vhk_runtime_embed_handoff.json`
- `build/publish/<bundle-name>/runtime/embed/refresh_runtime_embed_inputs.sh`
- `build/publish/<bundle-name>/runtime/embed/bootstrap_runtime_at_target.sh`
- `build/publish/<bundle-name>/runtime/embed/embed_native_runtime.sh`
- `build/publish/<bundle-name>/runtime/embed/embed_appimage_runtime.sh`
- `build/publish/<bundle-name>/runtime/embed/embed_flatpak_runtime.sh`
- `build/publish/<bundle-name>/runtime/embed/smoke_test_embedded_runtime.sh`

## Why this exists

The runtime pack made wheelhouses and offline installs reviewable, but it still
left a portability trap: Python virtual environments are not the sort of thing
VHK should encourage people to copy between arbitrary paths or hosts.

This pack turns the next honest step into code:

- build the runtime at the target path where it will really run
- keep native/package runtime targets explicit
- let package scripts opt into embedding instead of hiding it

## Design constraints

This is still not a promise of universal self-contained parity.

The generated handoff is explicit that:

- the wheelhouse still has to be built on a matching OS/architecture class
- the bootstrap helpers solve the Python/app layer, not remapper/helper-daemon
  review
- AppImage/Flatpak consumption is opt-in and builder-facing (`VHK_EMBED_RUNTIME=1`)
- exact-target bootstraps are safer than copying a venv, but they still do not
  erase Linux session/compositor/package boundaries
