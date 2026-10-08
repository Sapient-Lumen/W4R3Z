# Project strategy analysis (`vhk plan-project`)

`vhk plan-project` is a planning/brainstorming command for VHK projects.

It does **not** replace `vhk validate`, `vhk lint-project`, or `vhk doctor`.
Instead, it answers a different question:

> What kind of Linux-native automation surface is this project becoming, and
> which integrations should we lean into?

## What it reports

- project-level shape:
  - macros
  - bindings
  - hotstrings
  - clipboard / bus / window watchers
  - presets
- per-macro profiles:
  - triggers (`hotkey`, `hotstring`, `bus-watcher`, `window-watcher`, `palette`)
  - tags such as `vision-heavy`, `text-expander`, `wm-native`,
    `parameterized`, `event-driven`, `data-glue`
  - recorder-ish smells such as long fixed delays, coordinate clicks, or raw
    key down/up noise
- strategy recommendations:
  - split low-latency trigger planes from the heavier runtime
  - keep text expansion as its own tier
  - invest in selector assets for vision-heavy macros
  - lean on presets/prompt profiles instead of cloning similar macros
  - surface session mismatches when capture/injection/hotkey capabilities do
    not match the project shape
- product lanes:
  - trigger plane / dispatch
  - text tier
  - visual lane
  - event bridge
  - remap surface
  - orchestration
- explicit integration targets:
  - trigger plane
  - text tier
  - selector asset pack
  - event bridge / watcher plane
  - Wayland helper boundary for injection when needed
  - remapper/export surfaces such as keyd/kanata/kmonad/xremap-class tools
- implementation playbooks:
  - deployment audit loop (`doctor` + `validate` + `plan-project`)
  - text export loop (`gen-espanso`)
  - selector debug loop (`optimize-project` + `report` + `preview-needle`)
  - remap export loop (`gen-keyd-config` / `gen-kanata-config` / `gen-kmonad-config`)
  - dispatch daemon loop (`gen-vhk-busd-service` / socket units)
- architecture maps:
  - capability-aware runner core
  - dispatch plane
  - text tier
  - selector asset pack
  - event bridge
  - Wayland helper boundary
  - remap/export surface
- suggested stack profiles:
  - text-first export
  - selector-driven runner
  - watcher-daemon
  - remap-integrated
  - Wayland helper-boundary
- desktop target matrix:
  - portable text/export
  - X11 tiling-native
  - portal-centric Wayland
  - helper-boundary Wayland
  - wlroots / Hyprland conservative
- hypothetical environment comparison:
  - portable text baseline
  - X11/i3 reference
  - GNOME Wayland conservative
  - KDE Wayland portal-first
  - wlroots/sway conservative
  - Hyprland conservative
- implementation waves:
  - capability contract / exported entry points
  - text/forms tier
  - visual debug loop
  - dispatch + daemon seams
  - release gates
- a prioritized roadmap:
  - cleanup recorder-heavy drafts first
  - organize selector assets as a subsystem
  - promote repeated variants into presets/prompt profiles
  - author target-desktop deployment profiles for Wayland
  - strengthen app-scoped activation and tiny external emitters

## Why this exists

VHK is trying to become Linux-native in the same way AHK felt native on
Windows: fast where it needs to be fast, explicit about capability boundaries,
and strong at turning rough recordings into maintainable automation.

That means we should not only ask "does the macro run?" We should also ask:

- should this be a hotstring-backed text macro?
- should this be triggered by a WM binding or bus watcher instead of a heavy
  process launch?
- is this project vision-heavy enough that image assets and named regions need
  to be treated as first-class project structure?
- are presets/forms doing enough work that the product should surface them more
  aggressively in palettes and future Studio views?

## Example workflow

```bash
vhk plan-project ./myproj
vhk plan-project ./myproj --json
vhk lint-project ./myproj --json
vhk validate ./myproj --json
vhk doctor
```

A useful rhythm is:

1. `plan-project` for product/architecture shape, integration targets, and roadmap
2. `lint-project` for macro hygiene
3. `validate` for project correctness + likely session mismatches
4. `doctor` for raw desktop capability facts

## Product lessons reflected in the heuristics

The command is intentionally shaped by what the current Linux automation
landscape already teaches:

- AutoKey shows that hotkeys, phrases, scripts, and app scoping belong in one
  product family.
- Espanso shows that forms/variables are a real product surface, not just a
  thin prompt helper.
- SikuliX shows that visual automation wants organized image assets and bounded
  search regions, not a pile of ad-hoc screenshots.
- XDG portals + libei/EIS show that modern Wayland support is a matrix of
  independently varying capabilities rather than one boolean feature flag.

Some current public references that shaped this direction:

- AutoKey docs: https://autokey.github.io/intro.html
- Espanso forms docs: https://espanso.org/docs/matches/forms/
- SikuliX docs: https://sikulix.github.io/docs/
- libei / EI docs: https://libinput.pages.freedesktop.org/libei/
- XDG portal docs: https://flatpak.github.io/xdg-desktop-portal/docs/


## Why the new surfaces matter

The useful planning output is no longer just "this project is vision-heavy".
`plan-project` now tries to answer two more operational questions:

- which **product lanes** deserve first-class investment?
- which **command playbooks** should a team actually run next?

That is the bridge from research to implementation. The Linux automation
landscape is fragmented enough that architecture advice needs to end in
concrete loops, not only prose.

Examples:

- a snippet-heavy project should quickly become a text-tier export experiment
  instead of staying trapped inside the macro runner
- a visual project should immediately enter a selector-debug loop
- a watcher-heavy project should get packaged as user services early
- a Wayland-facing project should start by capturing a real deployment profile
  rather than claiming generic support


## New planning surfaces

`plan-project` now also tries to answer two more practical questions:

- what should the **architecture map** of this project look like?
- which **stack profiles** are the best fit for the current project shape?
- which **desktop targets** should we actively optimize for rather than vaguely claiming “Linux support”?

This is meant to encode a core Linux-native lesson from the current ecosystem:
exports, helpers, and dedicated service layers are often the right architecture,
not an embarrassing workaround.


## Candidate surface comparisons

`plan-project` now also emits `surface_choices` so the strategy layer can compare
real Linux integration options instead of only naming abstract targets.

This is the bridge between “build a text tier” and “should this become an
Espanso-style package or stay a palette/prompt workflow?” It does the same for
WM binds, portal shortcuts, remapper exports, and watcher services.


## Environment comparison

`plan-project` now also emits `environment_diffs` so the same project can be
compared against hypothetical desktop targets without requiring a live session
switch first.

This is important because Linux-native product design is not only about choosing
keyd vs portal shortcuts vs WM binds. It is also about seeing how those choices
shift across X11, GNOME/KDE Wayland, and conservative wlroots/Hyprland targets.

The output is deliberately heuristic. It does not claim live capability truth for
those desktops. Instead it gives authors a reusable planning lens:

- where the project looks closest to the classic AHK breadth target
- where helper boundaries become necessary
- where text/watcher/export surfaces become the safer product lane

## Capability coverage

`plan-project` now also emits `capability_coverage`.

This is the planner surface that asks the most Linux-native question of all:
not merely “which desktop is best?” but “which capabilities in this project are
portable, which are desktop-shaped, and which must stay behind helper/export
boundaries?”

That matters because projects rarely fail as a whole. They usually fail one
capability at a time:

- text survives but pointer playback does not
- launchers and binds survive but generic global shortcuts do not
- capture survives but raw input capture stays experimental

The planner now makes those differences explicit so teams can keep VHK core
strong while relocating portability risk into the right Linux-native seam.

## Portability planning

`plan-project` now also emits `portability_gaps`.

This takes the strongest environment plan and compares it against the more
conservative ones so the output can say:

- which capabilities become newly blocked or degraded
- which integration surfaces can stay the same
- which surfaces should be replaced
- what the migration response should be

That matters because Linux-native product design is not only about finding the
best environment for a project. It is also about understanding what must change
when support expands to stricter or less complete desktop targets.


## Portability playbooks

`plan-project` now also emits `portability_playbooks`.

This is the next step after `portability_gaps`: once the strategy layer knows
which capabilities degrade and which surfaces should change, it should also say
which artifacts to export, which install checks to perform, and which validation
loop to run on the destination desktop.


## Reference patterns

`plan-project` now also emits `reference_patterns`.

This is meant to preserve a deeper kind of research result: not just *which*
Linux surface looks plausible, but *which existing tool shape* VHK should learn
from for the current project.

Examples:

- AHK-style runner core when flow/data/process glue dominates
- Pulover-style visual studio when recording, selector assets, and presets are central
- Espanso-style text/forms export when hotstrings and prompted snippets dominate
- WM bind / launcher shells when dispatch should stay thin
- remapper offload when low-latency key semantics belong in generated configs
- portal/helper boundaries when Wayland capabilities vary by interface or desktop

That keeps online research from remaining a pile of notes. It becomes part of
`plan-project` output that downstream scaffold/help/workflow features can reuse.


## Concrete toolchain choices

`plan-project` now also emits `toolchain_choices`.

This is the next step after target and surface selection: it does not only say
"prefer a text tier" or "keep pointer injection behind a helper boundary". It
tries to name the concrete Linux toolchains that fit the project shape best
right now, together with fallback paths.

Examples:

- X11 text/pointer heavy projects should usually land on `xdotool`-class paths
- Wayland text-heavy projects should prefer `wtype`/clipboard-first flows
- Wayland pointer-heavy projects should stay behind helper/uinput/portal seams
- capture should stay portal-first on Wayland unless a compositor-native path is
  explicitly part of the target
- window-aware automation should treat `hyprctl`, `swaymsg`, `kdotool`, and
  `wmctrl`/`xprop` as desktop-shaped context bridges, not one universal API


## Verification gates

`plan-project` now also emits `verification_gates`.

This makes the planning output more operational. After targets, surfaces,
toolchains, and per-capability coverage are known, VHK should also say what the
team needs to prove before shipping a capability.

Examples:

- text paths should stay text-first and preserve a portable export or clipboard fallback
- pointer automation should prove its selector assets and conservative-desktop fallback story
- hotkeys should prove at least one exported bind or launcher path per user-facing trigger
- raw input capture should stay explicitly opt-in instead of becoming a hidden baseline dependency

This is a better Linux-native fit than a single “supported/not supported” label,
because real portability breaks at the capability seam.


## Artifact blueprint

`plan-project` now also emits `artifact_blueprint`.

This is the planner surface that ties all the other planning layers back to the
actual files and install surfaces a Linux project needs.

It does not stop at:

- which target fits
- which toolchain fits
- which wave comes first
- which capability gate must pass

It also asks:

- which files/configs/services should be generated
- where those artifacts likely belong in a Linux deployment
- which wave first needs them
- which commands and validation loops should stay attached to them

That makes the planning output reusable by future scaffold/setup/release flows,
instead of leaving deployment knowledge scattered across docs and shell history.
