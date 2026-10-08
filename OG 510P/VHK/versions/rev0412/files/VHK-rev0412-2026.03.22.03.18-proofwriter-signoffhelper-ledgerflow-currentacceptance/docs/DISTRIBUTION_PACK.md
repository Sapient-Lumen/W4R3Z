# Distribution pack

`vhk gen-distribution-pack <project_dir>` extends the publish handoff into a
maintainer-facing packaging handoff.

Artifacts:

- `docs/VHK_DISTRIBUTION.md`
- `docs/VHK_DISTRIBUTION_PLAN.json`
- `scripts/vhk_refresh_distribution_pack.sh`
- `build/publish/<bundle-name>/distribution/README.md`
- `build/publish/<bundle-name>/distribution/vhk_distribution_handoff.json`
- `build/publish/<bundle-name>/distribution/refresh_distribution_inputs.sh`
- `build/publish/<bundle-name>/distribution/appimage/AppDir/...`
- `build/publish/<bundle-name>/distribution/appimage/build_appimage.sh`
- `build/publish/<bundle-name>/distribution/flatpak/<app-id>.yaml`
- `build/publish/<bundle-name>/distribution/flatpak/build_flatpak.sh`

## Why this exists

The publish pack got VHK to a truthful bundle/release handoff, but packaging
metadata was still an after-the-fact maintainer chore. This pack keeps AppImage
and Flatpak skeletons tied to the same reviewed bundle story, copied support
docs, and release-stage target profile.

## Design constraints

This is not a claim that every VHK lane belongs in a sandboxed app format.

The generated handoff is explicit that:

- AppImage/Flatpak packaging is best suited to launcher/palette/portal-friendly
  flows unless the project later embeds a fuller runtime story.
- Host-global remappers, raw-input helpers, and privileged daemons still belong
  in native install lanes.
- The package metadata should travel with the same support docs and bundle name
  the maintainer already reviewed under `build/publish/<bundle-name>/`.

## Current handoff shape

The AppImage side emits an AppDir skeleton with:

- `AppRun`
- a root desktop file
- `.DirIcon`
- a launcher wrapper under `usr/bin/`
- desktop/metainfo/icon payload under `usr/share/`

The Flatpak side emits:

- a reverse-DNS app id
- a manifest pinned to a runtime/sdk pair
- conservative finish args derived from the project's desktop backend
- a local `files/` tree for launcher + desktop/metainfo/icon + bundled zip

Both build scripts refresh the publish bundle first so package skeletons stay
anchored to the reviewed bundle or reviewed release-stage lane.

When a project also runs `vhk gen-runtime-pack`, the package launchers are prewired
to prefer an embedded `usr/lib/vhk-runtime/bin/vhk` (AppImage) or
`/app/lib/vhk-runtime/bin/vhk` (Flatpak) before falling back to a host `vhk`.

When a project also runs `vhk gen-runtime-embed-pack`, those same build scripts
can optionally consume the exact-target embed helpers by setting
`VHK_EMBED_RUNTIME=1` before running `build_appimage.sh` or `build_flatpak.sh`.
