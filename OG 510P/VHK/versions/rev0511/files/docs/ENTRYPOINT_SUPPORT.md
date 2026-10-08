# Entrypoint support posture

VHK's exported entrypoints should no longer behave like anonymous launch helpers.

This repo now treats these outward-facing surfaces as part of the support story:

- `export-launcher-script`
- `export-desktop-entry`
- `export-wm-bundle`

## Why this matters

Linux automation still ships through desktop-specific seams:

- launchers / menus / taskbars
- WM include snippets and submaps
- helper scripts
- services / remappers / portals

That means a bundle recipient often sees the exported helper **before** they see
internal project docs. If the helper does not carry any support posture, the
recipient is forced to infer support from file names and hope the project's
README is current.

## Current behavior

### Launcher scripts

Generated launcher scripts now embed a support snapshot and expose:

```bash
./vhk-my-project-palette --about
./vhk-my-project-palette --support-json
```

That makes the helper itself reviewable when it gets copied into `~/.local/bin`,
a rofi mode, or a WM integration bundle.

### Desktop entries

Generated `.desktop` files now carry custom `X-VHK-Support-*` keys such as:

- `X-VHK-Support-Headline`
- `X-VHK-Support-ClaimSource`
- `X-VHK-Support-Reference`
- `X-VHK-Support-Supported`
- `X-VHK-Support-Caveated`
- `X-VHK-Support-Experimental`
- `X-VHK-Support-Docs`

These keys are intentionally descriptive metadata. They let launchers,
maintainers, or future VHK tooling inspect what the entry is supposed to support
without parsing internal planner JSON.

### WM bundles

Self-contained WM bundles now include:

- `docs/VHK_PUBLIC_SUPPORT.md`
- `docs/VHK_INSTALL_QUICKSTART.md`
- `docs/VHK_BUNDLE_SUPPORT.json`

And `vhk-wm-bundle.json` now records the support headline and those paths.

That keeps the support story attached to the exported i3/sway/Hyprland bundle
instead of requiring the recipient to unpack a separate project bundle first.

## Design rule

Outward-facing Linux surfaces should consume the same audited support posture as
bundle metadata and publish-pack docs. Public-facing entrypoints must not invent
stronger claims than the audited matrix can support.
