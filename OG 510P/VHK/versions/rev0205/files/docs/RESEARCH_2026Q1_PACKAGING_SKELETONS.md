# Research notes: packaging skeletons (2026 Q1)

This note captures the upstream packaging lessons that shaped
`vhk gen-distribution-pack`.

## AppImage

The generated AppImage side follows the documented AppDir model instead of
inventing a VHK-only directory layout:

- AppDirs are the source of AppImages.
- `AppRun` is the required entry point.
- the root of the AppDir should also expose a desktop file and icon entry.
- modern AppDir layouts commonly keep desktop files, icons, and payloads under
  `usr/share/...`.

That is why the VHK handoff now emits:

- `AppDir/AppRun`
- `AppDir/<app-id>.desktop`
- `AppDir/.DirIcon`
- `AppDir/usr/share/applications/<app-id>.desktop`
- `AppDir/usr/share/metainfo/<app-id>.metainfo.xml`
- `AppDir/usr/share/icons/hicolor/256x256/apps/<app-id>.png`

The build script is intentionally shaped around refreshing a known AppDir and
only then invoking `linuxdeploy`/`appimagetool` if they exist, because
`linuxdeploy` is explicitly documented as an AppDir maintenance tool.

Sources:

- https://docs.appimage.org/reference/appdir.html
- https://docs.appimage.org/packaging-guide/from-source/linuxdeploy-user-guide.html

## Flatpak

The Flatpak side follows official expectations instead of treating the manifest
as a generic YAML bucket:

- use a reverse-DNS application id
- name desktop and metainfo files after that id
- install desktop files under `/app/share/applications/`
- install metainfo files under `/app/share/metainfo/`
- express host access via explicit `finish-args`

The docs are equally important here: Flatpak's sandbox is intentionally narrow
by default, and additional host access is granted through static finish args and
portal-mediated flows. That means a VHK Flatpak skeleton should stay explicit
about what it *isn't*: a proof that host-global remapper or helper-daemon lanes
fit inside the sandbox.

Sources:

- https://docs.flatpak.org/en/latest/conventions.html
- https://docs.flatpak.org/en/latest/manifests.html
- https://docs.flatpak.org/en/latest/sandbox-permissions.html
- https://docs.flatpak.org/en/latest/available-runtimes.html

## Product lesson for VHK

The point of the distribution pack is not "ship Flatpak/AppImage because Linux".

The point is:

- keep package metadata tied to the same reviewed bundle story
- preserve the chosen release-stage lane where relevant
- make package boundaries honest instead of implying that every delivery format
  has equal automation authority

That is the Linux-native lesson worth borrowing: package form and automation
authority are different axes, and VHK should model them separately.
