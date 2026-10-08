# Issues to track (2026 Q1)

This is a focused issue shortlist derived from the current VHK codebase plus the
current official Wayland/portal documentation landscape.

## Fixed in this revision

- Process-aware window context for `GetActiveWindow`, `GetWindowAtCursor`, and `GetWindowList`, including `window_pid` / `window_process` convenience vars and selector-side PID matching.
- Deterministic bundle mode with normalized timestamps and `SOURCE_DATE_EPOCH`.
- X11 recorder smoothing presets + distance-aware mouse move thinning.
- Recorder drag collapse now survives intermediate motion samples.
- `vhk doctor` now probes `Screenshot`, `ScreenCast`, `RemoteDesktop`, `InputCapture`, and `GlobalShortcuts` separately, inspects `portals.conf`, and emits a capability matrix.
- `vhk validate` now reuses that capability model to warn about likely session/project mismatches.
- `vhk lint-project` now reuses the same model, so bulk project advice combines macro hygiene with session-fit warnings.
- `PromptForm` adds a first-class multi-field prompt step with YAD-native forms plus a portable sequential fallback.
- `vhk palette` adds a launcher-friendly project-level macro picker with recent-run ordering and lightweight macro metadata (`description`, `group`, `icon`, `tags`, `hidden`).
- Macros can now define saved parameter presets, and the palette surfaces them as separate launcher actions (`macro@preset`).
- Presets can now attach prompt overlays so one launcher action can preload stable vars and still collect a few run-time fields before execution.
- Prompt forms and preset overlays now remember last-used answers in a project-local store, support named prompt profiles from the CLI, and can expose saved-profile actions directly in `vhk palette`.
- VHK can now export a `.desktop` launcher for the project palette, plus optional quick actions for macros, presets, and saved prompt-profile workflows so launcher integration is part of the runtime story.
- VHK now ships lightweight prompt-profile management commands (`list-prompt-profiles`, `delete-prompt-profile`).
- VHK now ships `vhk plan-project`, a project-shape / strategy analyzer that turns macro structure + trigger surfaces + session capability mismatches into Linux-native recommendations.
- `vhk gen-support-pack` now ships planner-backed triage artifacts plus a support capture script so bug reports can preserve doctor/validate/plan facts, recent logs, and privacy review notes.
- `vhk gen-capability-audit-pack` now turns the repo's long-promised capability/fallback surface into a real artifact: audit docs, fixup queue, machine-readable plan, refresh script, and a `build/capability-audit/...` capture handoff that can regenerate fresh doctor/validate/plan + host/readiness/activation evidence on a target host.
- `vhk gen-host-contract-pack` now turns planner host requirements plus live helper/uinput/portal probes into reviewable deployment artifacts, and `plan-project` now emits explicit `host_requirements` so service lifecycle, permissions, and portal routing stop being stranded in prose.
- `vhk gen-publish-pack` can now target one reviewed release-stage lane via `--bundle-target-profile <profile>`, so audience-facing release/install docs and refresh scripts can ship the same lane payload a maintainer actually reviewed instead of always re-zipping the whole project tree.
- `vhk gen-publish-pack` now also materializes a reviewable publish handoff tree under `build/publish/<bundle-name>/`, with copied support/install docs, machine-readable handoff metadata, and refresh/bundle scripts that keep whole-project and release-stage shipping flows explicit.
- `vhk gen-distribution-pack` now grows that handoff into `build/publish/<bundle-name>/distribution/`, emitting AppImage and Flatpak skeletons from the same reviewed bundle story instead of asking maintainers to invent package metadata later.
- `vhk gen-runtime-pack` now partially closes the next packaging gap too by materializing a reviewable runtime handoff under `build/publish/<bundle-name>/runtime/`, with dependency specs, wheelhouse/offline-install scripts, and a Flatpak bridge helper derived from the same reviewed bundle lane.
- `vhk gen-runtime-embed-pack` now partially closes the next runtime gap after that by generating exact-target bootstrap helpers under `build/publish/<bundle-name>/runtime/embed/`, so maintainers can build the runtime where it will actually live instead of copying virtual environments around.
- `vhk gen-native-install-pack` now partially closes the next productization gap by materializing a conservative XDG-local app/install handoff under `build/publish/<bundle-name>/native/`, so maintainers can test one reversible native lane before overselling AppImage/Flatpak or helper-daemon-heavy stories.
- the native lane now also defaults to a palette-first launcher that reuses a materialized reviewed bundle from XDG cache and exposes desktop quick actions, which makes the installed app story feel much closer to a real Linux product surface instead of a maintainer-only inspect-bundle shim.
- `vhk gen-service-compose-pack` now partially closes the next startup gap by materializing a session-service handoff under `build/publish/<bundle-name>/service/`, with first-party busd user units, environment.d exports, and an XDG autostart bridge so login-time composition becomes reviewable instead of tribal knowledge.
- VHK now ships a generic `WaitUntil` step for expression-observable state, so authors can replace a class of brittle fixed sleeps and hand-rolled polling `While` loops with one backoff-aware primitive.
- VHK now also ships `WaitForBusEvent`, giving macros a dedicated event-driven synchronization primitive for helper scripts / WM binds / service glue instead of forcing everything through polling waits.
- VHK now ships `GetIdleMs` and `WaitForIdle`, making idle-aware automation first-class while keeping the support language explicit instead of pretending every Wayland session exposes one generic idle probe.

## Next issues worth tackling

### 1) Studio-side form editor + parameter surfacing

`PromptForm` now exists at the engine level, but it still needs the rest of the
product surface around it:

- scaffold/templates that generate parameterized macros
- studio-side field editors
- palette flows that can surface stored or prompted parameter sets
- better preset-prompt tooling (saved answers, optional validation, future Studio editors)
- preset editors and saved-parameter review inside future Studio surfaces
- richer prompt-profile management (rename/export/import, profile selection policies, future Studio editors) now that listing/deletion and palette surfacing exist

### 2) Capability-aware scaffold/help UX

`plan-project` now gives VHK a planning surface for this work, and `setup_recipes` now makes the operator handoff explicit. `vhk init` now partially consumes that language too by generating a starter guide + machine-readable starter plan for new projects, so authoring begins with deployable surfaces, setup recipes, toolchain choices, and reference patterns already visible.


The capability model now reaches doctor, validate, lint-project, and init. The next
step is to thread the same language into scaffold/help and into live session-aware authoring flows so the user
sees "text injection available, pointer injection missing" instead of a vague
"Wayland caveat" while they are authoring, not just reviewing.

### 3) libei helper spike

The official libei docs are mature enough to justify a small throwaway helper
spike. The Python runtime should not absorb all of that complexity directly; a
helper binary or isolated module is the safer first cut.

### 4) Recorder key-state fidelity

The recorder is now better at motion thinning, but richer modifier/key-state
reconstruction is still a separate problem. That likely needs either XI2 state
tracking improvements or a second conversion pass.

- Launcher export follow-up: richer picker bundles and multi-action launcher flows still remain, but WM-ready snippets now exist via `export-wm-bindings`, and transient launcher layers now exist via `export-wm-launcher-mode`, so users can wire rofi-mode / launcher-script / direct palette-command flows into i3/sway/Hyprland without hand-assembling the command syntax.
- Remaining launcher-workflow gap: mode/submap exports currently map one key to one launcher or palette entry. They do not yet export richer session bundles such as nested management submodes or which-key style hints. Higher-level install/export bundles now exist via `export-wm-bundle`, so the next launcher-install work should probably focus on richer session UX rather than basic artifact placement.
- Exported launcher scripts now auto-detect rofi script mode and emit stable `info` ids, invisible `meta` search terms, and optional row icons.


## Fresh issues from March 2026 research

These are not regressions in VHK itself; they are ecosystem realities that should continue to shape VHK's Linux-native roadmap.

### 5) wlroots portal support is still incomplete enough to block a "portal-only" strategy

As of early March 2026, `xdg-desktop-portal-wlr` still shows open work for both RemoteDesktop and InputCapture, even though active pull requests now exist for both areas. That is a strong signal that VHK should keep compositor-native and uinput-based fallbacks first-class instead of assuming a clean cross-DE portal path yet.

### 6) Hyprland portal backend still lacks RemoteDesktop coverage in practice

`xdg-desktop-portal-hyprland` continues to track missing `org.freedesktop.portal.RemoteDesktop` support, and follow-up reports from 2025 show user-visible remote-input failures collapsing back onto that same gap. For VHK, that means Hyprland automation should keep leaning on Hyprland-native events/dispatch plus optional helper tooling rather than betting on RemoteDesktop.

### 7) Portal routing remains a configuration problem, not just an API problem

The official `portals.conf` docs make it clear that backend routing is selected per interface and can vary by desktop-specific config file, system config, and user overrides. VHK's current doctor/config inspection is the right direction; future authoring/install flows should continue to surface routing details explicitly instead of assuming "portal installed" means "portal usable".

### 8) Performance guidance needs to stay tied to measured runs

VHK now has a much better post-run feedback loop (`vhk report` advice), but the next step is to connect that with recorder cleanup and future Studio workflows so authors can move directly from a slow/flaky log to a concrete fix.


### 9) App-scoped behavior on Wayland still depends on desktop-specific context bridges

Current remapper/text-expander ecosystems still rely on shell extensions,
window-context helpers, or compositor-native metadata to make per-app behavior
reliable on Wayland. VHK should keep treating app/window scoping as a capability
with backend-specific implementations, not a generic checkbox.

### 10) `plan-project` should eventually compare candidate export surfaces, not just recommend them

The new playbooks are a good first step, but the next leap is comparative
review: given a project and a target desktop, VHK should eventually say why
keyd vs kanata vs compositor binds vs portal hotkeys is the better fit.


### 11) Planning output should eventually diff target environments, not just project shape

`plan-project` now emits architecture maps and stack profiles, but the next leap
is environment comparison: given the same project, VHK should eventually show
how the preferred profile changes across X11, GNOME Wayland, KDE Wayland, or
wlroots/Hyprland-class sessions when the capability matrix changes.

- `plan-project` now compares concrete Linux integration surfaces (`surface_choices`) so issue 10 is partially addressed: remap/text/trigger/service options can now be scored and reviewed side-by-side instead of only being mentioned in prose.
- `plan-project` now emits hypothetical `environment_diffs`, so issues 11 and 12 are partially addressed too: the same project can be compared against X11/i3, GNOME/KDE Wayland, and conservative wlroots/Hyprland targets without depending on a live session switch.

### 12) Surface comparison should eventually become environment-specific

The new `surface_choices` layer still compares candidates against one project
plus an optional live session. The next step is to let the same project be
scored against hypothetical targets such as GNOME Wayland, KDE Wayland, X11/i3,
or wlroots/Hyprland conservative profiles without needing to boot each session
right away.

- `plan-project` now emits `portability_gaps`, so environment comparison can be
  turned into a migration plan instead of stopping at a score table.
- `plan-project` now also emits `portability_playbooks`, which partially addresses
  the next step too: each portability gap can now suggest concrete exports,
  install checks, and validation commands instead of only naming abstract target
  changes.


### 13) Research needs to become planner output, not just documentation

A recurring repo risk is that ecosystem research ends up stranded in markdown
without affecting commands, scaffolds, or deployment decisions.

Update:

- `plan-project` now emits `reference_patterns`, which partially addresses this
  by turning "learn from AHK / Pulover / Espanso / keyd / kanata / KMonad /
  xremap / portal helpers" into machine-readable output.

Update:

- `vhk gen-operator-pack` now partially addresses this too by turning planner output into portable guide/checklist/JSON handoff artifacts for real projects, not only new-project starter docs.

Remaining gap:

- future scaffold/studio flows should consume these patterns directly when
  suggesting project layouts, recorder defaults, and export bundles.

Update:

- `plan-project` now also emits `runtime_seams` and `ecosystem_lessons`, which partially address the architecture-handoff gap by turning “what stays inside VHK vs what stays thin/exported” plus adjacent-tool lessons into machine-readable design output.
- `vhk gen-design-pack` now partially addresses the same gap by generating `VHK_DESIGN_BRIEF.md`, `VHK_RUNTIME_CONTRACT.md`, and `VHK_DESIGN_PLAN.json` for real projects instead of leaving this analysis stranded in terminal tables.


### 14) Toolchain choice still needs to become scaffold/export behavior

`plan-project` now emits `toolchain_choices`, so the research is no longer stuck
in prose: VHK can recommend concrete paths like `xdotool`, `wtype`,
portal-first capture, helper/uinput seams, or compositor metadata bridges.

Remaining gap:

- init now partially consumes that data directly when generating starter guide/plan artifacts.
- `vhk gen-trigger-pack` now partially addresses the export-behavior gap by turning remapper/WM trigger advice into a self-contained bundle of generated configs/docs/JSON plus a refresh script.
- future scaffold/export flows should consume the same data when generating starter bundles, install notes, and deployment recipes for text, services, and support surfaces too
- future Studio UX should expose why a project is being pushed toward one input
  or capture path instead of another


### 15) Planning should eventually become release gating, not only recommendation

The planner is now much better at describing targets, surfaces, toolchains,
and portability gaps. The next requirement is release discipline: Linux-native
projects need a way to say what must be proven before a capability is treated
as shippable.

Update:

- `plan-project` now emits `verification_gates`, which partially addresses this
  by turning capability planning into explicit acceptance checks, commands,
  artifact hints, and fallback paths.

Update:

- `vhk gen-verification-pack` now partially addresses this by turning verification gates, setup recipes, and deployable surfaces into a release guide, release checklist, machine-readable verification plan, and a shell-oriented rehearsal script.
- `vhk gen-support-pack` now partially addresses the support handoff gap by turning planner + diagnostics output into triage docs/checklists/JSON plus a capture script for real projects.

Remaining gap:

- future CI and Studio flows should consume these artifacts directly instead of
  leaving them as review-time exports only.


- `plan-project` now also emits `artifact_blueprint`, which partially addresses the deployment/scaffold gap by naming the concrete exports/configs/services/assets a Linux-native project should generate.
- `plan-project` now also emits `deployable_surfaces`, which partially addresses the same gap from the operator side by grouping artifacts into install-facing Linux surfaces instead of leaving them as a flat file list.


### 16) Global shortcuts are still better for stable action catalogs than open-ended macro systems

The GlobalShortcuts portal is real and useful, but current upstream discussion makes the constraint explicit: applications generally need to pre-register the shortcuts they want, which is a poor fit for endlessly dynamic macro catalogs or recorder-generated ad-hoc bindings. VHK should keep WM/compositor binds and launcher surfaces first-class instead of treating portal shortcuts as the universal answer.

### 17) libei / InputCapture still needs operational caution, not just feature detection

Portal and libei progress matters, but recent field reports still show lifecycle hazards around input-capture stacks. A February 2026 lan-mouse issue reports a suspend/resume path that panics in the libei layer and can crash GNOME Shell. VHK should keep recovery notes, helper boundaries, and conservative release gates around input-capture-class features instead of treating portal presence as proof of production readiness.

### 18) Linux-native install stories are still product work, not packaging trivia

Current adjacent tools keep reinforcing the same lesson:

- AutoKey still has to be honest that it is fundamentally X11-oriented
- Espanso exposes first-class service and app-specific config flows
- keyd / kanata / ydotool-class helpers still require explicit uinput/group/service setup

That means VHK should keep treating setup/install/rollback guidance as part of
the core product surface.

Update:

- `plan-project` now emits `setup_recipes`, which partially addresses this by
  turning deployable surfaces into explicit install/review/verification handoffs
  instead of leaving operators to infer the setup story from raw artifact lists.

Remaining gap:

- init now partially consumes these recipes directly by emitting starter onboarding artifacts for new projects.
- future scaffold/export flows should consume these recipes directly too.
- future Studio onboarding should render the same handoff language instead of
  re-describing install stories in ad-hoc prose


### 15) Remapper installs are still operator work, not just config generation
### 16) Planner-backed host requirements still need deeper live verification

`plan-project` can now name service lifecycle, permissions, and portal-routing
requirements, `gen-host-contract-pack` can turn them into review artifacts, and
`gen-readiness-pack` now partially closes the next gap by probing common
service-manager states, current group membership, and raw-input readability.

Remaining gap:

- service coverage is still intentionally conservative (`espanso`, `vhk-busd`,
  `ydotoold`, `keyd`, `kanata`, `kmonad`), not a universal service-manager
  abstraction
- dedicated service users, custom socket activation layouts, and non-systemd
  launch stories still need deeper review support
- espanso registration is still inferred through service state rather than a
  dedicated espanso-native probe

Current keyd and kanata guidance still makes permissions, service wiring,
config placement, and reload/start commands explicit. VHK already exports
configs, but deployment UX should keep those operator seams visible instead of
implying that generating a remap file is the whole job.

### 19) There is still no generic portal for active-window / open-window introspection

AHK-class tooling depends heavily on being able to inspect the active window,
enumerate candidates, and scope automation against app/title/class-like facts.
That remains straightforward on X11 and desktop-specific on Wayland, and the
upstream portal discussion around a generic “currently open windows” surface is
still unresolved. VHK should keep Window Spy / app-scoping features layered on
X11 and compositor-native bridges instead of assuming a portal-first answer is
arriving soon.

Reference:

- `flatpak/xdg-desktop-portal#304` (“Add a portal to see currently open windows”)

### 20) Support evidence still needs privacy-aware capture and better replay hooks

Linux automation failures are often only visible on one real desktop, so triage quality depends on whether a project can capture the right evidence without oversharing secrets.

Update:

- `vhk gen-support-pack` now partially addresses this by generating a support guide, support checklist, machine-readable support plan, and a capture script that gathers doctor/validate/plan reports, recent logs, traces, and optional bundles into `support/capture_*/`.
- `vhk gen-portability-pack` now partially addresses issues 11, 12, and 14 too by turning environment diffs, capability coverage, portability gaps, and playbooks into a portability guide, target rollout worksheet, machine-readable plan, and review script for real projects.

Remaining gap:

- future Studio and run-history flows should be able to launch this capture process directly, preview sensitive artifacts before export, and capture richer evidence such as curated traces, redacted screenshots, or short repro clips.



### 15) Wayland app-scoping and remapping still depend on desktop-specific bridges

Current xremap docs still advertise X11/Wayland app-specific remapping, but the
installation/troubleshooting story remains desktop-shaped: GNOME needs an
extension and DBus allowances, some Wayland paths rely on `sudo -E`, and the
troubleshooting guide still tells users to inspect which desktop integration is
actually active. That reinforces VHK's decision to treat app/window scoping as
a portability review surface instead of a generic checkbox.


### 21) Support claims need an auditable contract, not just rollout prose

Linux automation teams eventually need to say what they actually support:
reference lane, supported lane, caveated lane, experimental lane, and what is
still outside the matrix. Current tools keep forcing that honesty in practice:
Espanso still splits X11/Wayland install methods and capabilities, AutoKey's
official project is still Xorg-bound while forks narrow Wayland scope to GNOME,
and xremap/Toshy-style stacks keep shipping desktop-specific setup bridges.

Update:

- `vhk gen-claim-pack` now partially addresses this by turning planner output into a claim guide, editable target-claims manifest, machine-readable audit plan, and claim-audit script.
- `vhk audit-target-claims` now makes those claims enforceable by failing overclaims and checking for missing proof artifacts on stronger lanes.

Remaining gap:

- `vhk bundle` now partially addresses this by embedding planner-backed claim snapshots into `vhk_bundle_manifest.json`, and `vhk inspect-bundle` can now review that support/proof summary from a shared zip.

Update:

- `vhk gen-publish-pack` now partially addresses this by turning the audited target matrix into public support notes, install quickstarts, machine-readable publish metadata, and a refresh script that bundles + inspects the project again.

Remaining gap:

- exported launcher/menu/install surfaces still need to consume the same publish/support metadata automatically, so every outward-facing entrypoint inherits the same audited claim tiers by default.

## Issue: public support posture can still drift from install-facing entrypoints

Even after claim audits and publish packs, outward-facing launcher surfaces can still drift when the shared bundle, launcher helper, desktop entry, or WM snippet does not actually carry that support story with it.

Partial mitigation in this revision:

- exported launcher scripts now expose `--about` / `--support-json`
- desktop entries now emit `X-VHK-Support-*` metadata
- self-contained WM bundles now ship bundle-local public support/install docs plus `docs/VHK_BUNDLE_SUPPORT.json`

Remaining gap:

- install-mode WM exports still rely on the project docs staying nearby; future package/install surfaces should ingest the same metadata more directly



## Issue: setup recipes were documented but not yet executable

`setup_recipes` already captured the missing Linux-native layer between
artifact generation and real deployment, but authors still had to translate
that plan into ad-hoc shell history.

That was especially visible in the current ecosystem:

- service-managed tools like Espanso expose explicit register/start/status
  surfaces
- remapper stacks like keyd/xremap still depend on reviewable config placement
  and desktop/session-aware verification
- Wayland/X11 differences keep forcing honest install/review loops instead of
  universal one-click stories

Partial mitigation now exists:

- `vhk gen-setup-pack` generates project-specific setup docs
- it also emits runnable apply/verify scripts derived from planner
  `setup_recipes`, filtered down to command-like steps instead of blindly
  executing prose
- it now also emits a dry-run-first `vhk_install_toolchain_packages.sh` helper
  plus normalized apt/dnf/pacman/zypper command hints derived from planner
  `toolchain_choices`, so package bootstrap stops living only in prose

Remaining gap:

- package names are still best-effort and distro-shaped, so install helpers
  must remain opt-in and reviewable instead of pretending to be a universal
  one-click installer
- these scripts are intentionally conservative and still stop short of claiming
  that every install or rollback path can be fully automated

## Issue: planner + doctor still needed a first-class host-fit handoff

By this point VHK could already answer two adjacent questions:

- what kind of Linux-native stack a project wants (`plan-project`)
- what the current session can likely do (`doctor` / session capability matrix)

But operators still lacked the missing join: a single artifact that says whether
a concrete project is *ready*, *degraded*, or *blocked* on the current host,
and which helper/bootstrap lanes are relevant when it is not.

Partial mitigation now exists:

- `vhk gen-session-fit-pack` generates project-specific host/session review docs
- it emits `VHK_SESSION_FIT.md`, `VHK_SESSION_FIXUPS.md`, and
  `VHK_SESSION_PLAN.json` so the project requirements and session capability
  story live together
- it also emits `scripts/vhk_review_session_fit.sh`, which refreshes
  `doctor`, `validate`, `plan-project`, and the generated session-fit artifacts
  into a small evidence folder
- the pack links blocked/degraded capabilities back to planner
  `toolchain_choices` and normalized setup/bootstrap groups so missing helper
  lanes stop being an implicit support conversation

Remaining gap:

- package groups still collapse services, permissions, and portal/backend
  routing into a mostly package-shaped view
- host-fit guidance is still intentionally conservative; desktop-specific app
  context, consent flows, and permission models remain real
- future desktop-aware scoring should narrow the union package story for
  GNOME/KDE/wlroots/Hyprland instead of showing one broad helper set

## Additional March 2026 ecosystem notes folded into this revision

- The official AutoKey project still describes itself as an X11 application and
  explicitly warns that it will not function correctly under Wayland. That keeps
  reinforcing VHK's decision to treat X11-era automation parity as a separate
  lane from Linux-native Wayland surfaces rather than pretending they are one
  portability story.
  - https://github.com/autokey/autokey
- xremap continues to advertise app-specific remapping on both X11 and Wayland,
  which is useful evidence that the Linux market wants per-app behavior, but it
  is still a remapper/helper product shape rather than a full AHK/PMC-class
  authoring surface. VHK should keep learning from that split instead of trying
  to flatten remapping, hotkeys, recording, and visual automation into one
  universal always-on daemon.
  - https://github.com/xremap/xremap
- The GlobalShortcuts portal is now documented as a session-oriented API where
  applications create a shortcut session and bind explicit shortcuts into it.
  That is a real capability, but it still fits stable action catalogs better
  than ad-hoc recorder output or endlessly dynamic macro inventories.
  - https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.GlobalShortcuts.html
- The InputCapture portal docs make two constraints unusually explicit: there is
  no immediate-capture mode, and the compositor decides when capture becomes
  active. That keeps reinforcing VHK's current plan to treat portal capture as a
  capability lane, not as a drop-in replacement for unrestricted AHK-style
  low-latency hooks.
  - https://flatpak.github.io/xdg-desktop-portal/docs/doc-org.freedesktop.portal.InputCapture.html
- xremap's own GNOME Wayland docs still rely on a GNOME Shell extension and
  extra DBus/root allowances for some flows, while its troubleshooting guide
  still points users back to desktop-specific context bridges for app-specific
  remappings. That is exactly the sort of desktop-shaped reality VHK should keep
  modeling explicitly instead of flattening into a generic "Wayland supported"
  checkbox.
  - https://github.com/xremap/xremap/blob/master/doc/running_with_sudo.md
  - https://github.com/xremap/xremap/blob/master/doc/troubleshooting.md
- Espanso's current docs still say app-specific configurations are not yet
  supported on Wayland. For VHK that is another data point that per-app Linux
  behavior on Wayland is still backend/tool/desktop-specific instead of a solved
  platform primitive.
  - https://espanso.org/docs/configuration/app-specific-configurations/
- The libei docs now expose a mature split between libei/libeis/liboeffis and
  explicitly position liboeffis as the portal connection layer. That makes a
  helper-boundary experiment more justified, but it still argues against shoving
  the whole input-capture/input-emulation stack directly into VHK's Python core.
  - https://libinput.pages.freedesktop.org/libei/api/index.html
- ydotool still presents itself as a generic command-line automation tool built
  around a lower-level input path rather than a high-level desktop workflow
  engine. That reinforces VHK's current architecture direction: keep helpers like
  ydotool behind adapters and let VHK own orchestration, project packaging,
  review surfaces, and eventually Studio UX.
  - https://github.com/ReimuNotMoe/ydotool


### 22) Host truth should become activation truth, not just readiness truth

`gen-readiness-pack` proved whether services, groups, sockets, and portal config
look alive on one host. The next problem is route ownership:

- which lane actually wakes the project?
- which lanes are only fallback/manual routes?
- which lanes are blocked because one dependency is still degraded?
- which lanes stay session-bound versus restartable?

Update:

- `plan-project` now emits `activation_routes`, `gen-activation-pack` turns
  those into route docs/fixups/refresh scripts, and `gen-route-selection-pack`
  now chooses explicit primary/fallback reference routes per activation lane
  instead of leaving all routes flat.

Remaining gap:

- future proofing should probe route-native state more deeply (for example
  explicit portal/session binding status, non-systemd launch managers, and
  process/socket ownership beyond conservative `systemd` unit checks)
- `vhk gen-target-route-pack` now partially closes the cross-target comparison
  gap by comparing reference-route decisions across conservative `x11-desktop`,
  `gnome-wayland`, `kde-wayland`, and `wlroots-wayland` planning profiles.
- `vhk gen-release-lane-pack` now partially closes this by turning target-route
  comparisons into `VHK_RELEASE_LANES.md`, `VHK_RELEASE_SNIPPETS.md`,
  `VHK_RELEASE_LANE_PLAN.json`, and `scripts/vhk_refresh_release_lanes.sh` so a
  project can ship per-desktop release/support language without hand-maintained
  prose.
- release lanes now flow into launcher/about metadata, desktop-entry `X-VHK-Release-*` fields, WM bundle support JSON, and bundle manifests so exported surfaces stop losing the desktop-lane story by default.
- `vhk gen-release-deploy-pack` now partially closes that remaining gap by emitting lane-native install/autostart snippets, generated artifact subsets, and deploy-style summaries for each release lane.
- remaining gap: route-native install output should eventually grow deeper live packaging helpers (portal/session verification, non-systemd managers, and per-lane release artifact assembly) instead of only generator commands + docs.

## Release-stage follow-through

- now that `gen-release-stage-pack` materializes per-lane ship trees, the next gap is
  lane-native signing/notarization/distribution handoff instead of only project-local
  staging
- `vhk bundle-stage` now partially closes the bundle side of that gap by zipping one
  materialized lane directly from `build/release-stage/<profile>/`, with embedded
  release-stage metadata so `inspect-bundle` can tell reviewers which lane they are
  looking at without unpacking it first.
- `vhk gen-publish-pack` now partially closes that gap too by materializing
  `build/publish/<bundle-name>/` with copied public docs, bundle scripts, and
  release-stage references, so a maintainer can review one publish handoff tree
  instead of only a repo-level script.
- remaining gap: package/signing/AppImage/Flatpak handoff should eventually grow
  from that same publish tree instead of stopping at deterministic zip output.


## Distribution-pack follow-on gaps

- The generated AppImage/Flatpak outputs are intentionally skeletons; `vhk gen-runtime-pack` now gives maintainers a reviewable Python runtime handoff and `vhk gen-runtime-embed-pack` now gives them exact-target bootstrap helpers, but final interpreter selection, store-ready packaging, and helper-daemon review are still future work before VHK should market those lanes as fully self-contained automation products.
- `vhk gen-native-install-pack` plus `vhk gen-service-compose-pack` now give the repo one conservative proving lane for local install + login-time composition, including a bundle-state long-lived runner, but the remaining gap is deeper verification of actual desktop-shell discoverability and full host rehearsal on real sessions.
- `vhk gen-host-rehearsal-pack` now partially closes that follow-through gap by materializing one reviewed-lane operability tree with install/status/log/uninstall scripts, desktop-file validation hooks, and integrated rehearsal smoke paths, but real compositor/session verification still needs live host runs rather than generated scripts alone.
- Native package/AppImage/Flatpak signing, repo publishing, and store policy
  checks are still future work.
- Flatpak permissions remain deliberately conservative and should stay tied to
  portal/app-scoped workflows rather than host-global remapper claims.

## Bundle-native session runner follow-through

The service pack now has a bundle-state runner, but the next hardening step is
proving one conservative lane end to end on a real host: install native app
root, embed runtime, materialize the reviewed bundle into user state, and start
a watcher unit without falling back to the mutable project checkout.

## Native doc-surface follow-through

- `gen-native-install-pack` now ships a packaged app-home/support doc surface plus launcher actions to open those docs, which makes the installed lane more product-real and less maintainers-only.
- remaining gap: those surfaces are still static/generated docs, not a richer interactive GTK/QML front-end or tray/status surface.
- next hardening path: tie packaged home/status surfaces to live session/service state carefully, without making desktop-entry actions depend on a terminal or on desktop-specific notification daemons.

## Native launcher-state follow-through

- `gen-native-install-pack` now keeps launcher state under XDG state and can refresh installed desktop actions from pinned/recent entries, which is a better Linux-native posture than freezing every quick action at generation time.
- remaining gap: quick actions are still only as visible as the launcher/menu actually allows; they should stay additive rather than become the only way to reach important workflows.
- next hardening path: let the installed lane surface richer live status/home data without making the desktop file itself depend on a compositor-specific tray or a full GUI shell.

## Native live-status follow-through

- `gen-native-install-pack` now partially closes the “static docs only” gap by emitting a live installed-lane status report under XDG state, with machine-readable JSON + Markdown and best-effort `systemctl --user show` probing for expected VHK-owned user-service units.
- remaining gap: this is still a launcher/report surface, not a full GTK/QML status UI or tray app, and it should stay that way until one conservative lane has been exercised on real GNOME/KDE/wlroots hosts.
- `gen-host-rehearsal-pack` now partially closes that gap by emitting `report_reviewed_lane.sh`, which collects one host-rehearsal report from the installed launcher’s live status JSON plus best-effort desktop/systemd probes under XDG state.
- remaining gap: the report is still generated by scripts rather than by a richer in-app operator UI, and real compositor/session confidence still needs live host runs on representative desktops.

## Host dossier follow-through

- `gen-host-dossier-pack` now turns that rehearsed installed lane into one shareable XDG-state support packet with collection/archive/smoke scripts, so launcher status, rehearsal output, session facts, and best-effort `loginctl`/`systemctl`/`journalctl` probes stop living only in scattered terminals.
- remaining gap: the dossier is still a scripted support packet, not a live in-app support/export UI, and it still needs manual privacy review before external sharing.
- next hardening path: exercise dossier collection on representative GNOME/KDE/wlroots hosts and refine which session/service facts are most useful without over-collecting private data.

## Host dossier privacy follow-through

- `gen-host-dossier-pack` now partially closes its own privacy gap by generating a share-safe dossier copy plus a redaction report before external archive handoff.
- remaining gap: automatic redaction can only catch common path/email/secret patterns; real projects may still log tenant names, app titles, or domain-specific identifiers that need a final human review.
- next hardening path: exercise the share-safe dossier on representative GNOME/KDE/wlroots hosts and tune the suspicious-pattern report using real bug packets instead of synthetic examples.



### 12) Idle-aware automation needs explicit probe/event routing

Current Linux idle tooling still splits cleanly into two families:
- direct probes (`xprintidle`, Mutter IdleMonitor)
- event daemons (`xidlehook`, `swayidle`)

VHK should keep both lanes explicit. The new idle steps close the basic runtime
gap, but future route-selection/help/doctor surfaces should keep teaching when
an author should use a direct probe and when they should bridge compositor
activity into the local VHK bus instead.


### 20) There is still no generic cross-desktop idle-inhibitor model

Current idle daemons keep exposing their own inhibitor and lifecycle seams.
Recent `hypridle` docs still name `ignore_dbus_inhibit` and
`ignore_systemd_inhibit`, while `swayidle` continues to document `idlehint`,
lock/unlock, and before-sleep/after-resume behavior behind logind support. VHK
should keep idle-aware authoring first-class, but it should treat inhibitor
policy and sleep/lock orchestration as desktop/helper-specific deployment work
rather than pretending one generic Linux idle contract exists.

## Window introspection follow-through

- `GetActiveWindow` now closes an authoring gap by making active-window state a
  runtime primitive instead of a CLI-only debugging surface.
- remaining gap: there is still no generic cross-desktop window-enumeration /
  active-window portal that deserves broad “Wayland window introspection”
  marketing language.
- next hardening path: keep one stable runtime data shape (`window`, `wm`,
  `window_title`, `window_class`, `workspace`, `urgent`) while expanding the
  backend matrix carefully for KDE/wlroots/Hyprland-class sessions.
- additional follow-through: planning/doctor/report surfaces should eventually
  call out when a project depends on geometry-grade window introspection versus
  metadata-only focus detection.


## Window enumeration follow-through

- `GetWindowList` now closes the next obvious authoring gap after
  `GetActiveWindow`: macros can enumerate currently open windows directly
  instead of shelling out to one-off helper scripts.
- this is still a backend-shaped feature, not a generic Wayland right. On KDE,
  `kdotool search` helps, but it uses KWin internal ids and does not fully match
  `xdotool` flags; on Hyprland, `hyprctl clients` is powerful but not a high-rate
  polling API.
- remaining gap: there is still no generic cross-desktop portal for open-window
  enumeration, so VHK should keep its marketing language precise and continue
  routing through compositor-specific helpers where necessary.
- `GetActiveWindow`, `GetWindowAtCursor`, and `GetWindowList` now partially
  close that next hardening path by carrying best-effort state fields such as
  `visible`, `fullscreen`, `floating`, `sticky`, `minimized`, `mapped`, or
  `hidden` where the backend exposes them cleanly.
- `I3WindowSelector` now partially closes that gap by accepting best-effort
  state fields (`visible`, `fullscreen`, `fullscreen_mode`, `floating`,
  `sticky`, `minimized`, `hidden`, `mapped`, `pinned`) across runtime selector
  surfaces.
- planner/doctor/validate now summarize those stateful window dependencies as a first-class **window contract** instead of flattening them into generic `window_introspection` usage.
- remaining gap: release/readiness surfaces still do not rank those contracts by backend confidence (for example: direct pointer-window query vs best-effort geometry matching), and KDE/Hyprland state semantics still need more live-host hardening than sway/X11.


### 19) Pointer-window mapping is still backend-shaped and sometimes heuristic

AHK-style “window under mouse” workflows are important enough to support, but
Linux does not offer one generic, compositor-neutral answer. X11 and KDE
Wayland can often provide a direct pointer window id, while sway/i3 and
Hyprland more often force geometry-based matching. VHK should keep this feature
first-class, but it should also keep the support language explicit and avoid
turning pointer-window introspection into a high-rate polling dependency.


### 21) Process-aware window matching is still backend-shaped

AHK-style PID/process scoping is important enough to support directly, but Linux
does not expose it through one universal contract. X11 often relies on
`_NET_WM_PID`, which may be absent or incomplete; sway documents numeric `pid`
criteria; Hyprland exposes process-bearing client metadata but warns against
spamming synchronous `hyprctl` info calls; KDE Wayland still routes through a
KWin-specific bridge (`kdotool`). VHK should therefore keep `pid` /
`process_name` first-class in runtime snapshots and selectors while keeping
exported config snippets conservative per WM/backend.


## Window event support should stay explicit in planner/doctor surfaces

VHK now has a first-class `WaitForWindowEvent` lane, but the broader issue to
keep watching is **which event kinds are honestly available per backend**.

- i3/sway can support focus/workspace/title/urgent/new/close through IPC
- Hyprland can support focus/workspace/title/urgent/new/close/custom through
  socket2
- generic X11/other desktops should not be oversold as having a universal rich
  event stream

That means future work should keep event-kind support explicit in generated
artifacts and operator docs, not flatten it into generic `window_introspection`.

## Filesystem watcher truthfulness gap

- `file_watchers` now exist, but the Linux-native caveats are still real: `inotify` queue overflow, mount/filesystem quirks, and helper availability all affect reliability.
- next hardening path: expose watcher-health / overflow / fallback mode more clearly in doctor/readiness surfaces instead of leaving it implicit in implementation details.


## One-shot file-event waits are now first-class

- `file_watchers:` gave VHK a long-running daemon lane for filesystem-triggered
  macros, but one-shot macros still had to approximate "wait for the next file
  event" with `WaitForFile`, `WaitForNewFile`, or shell glue.
- `WaitForFileEvent` now closes that authoring gap with the same high-level
  event vocabulary as project watchers (`new`, `changed`, `deleted`, `any`),
  plus the same producer-friendly settling knobs (`exclude`, `min_size`,
  `stable_ms`, `recursive`).
- remaining gap: the file lane still does not summarize burst/coalescing needs
  as a first-class project contract, so "one event means done" can still be too
  optimistic for chatty producers without explicit settling or watcher-level
  dedupe/cooldown.


## New issue: noisy producer bursts still need first-class authoring knobs

VHK now has `quiet_ms` on `file_watchers:` and `WaitForFileEvent`, but the broader project story still lacks a cross-surface policy for burst coalescing, restart/reload semantics, and queue ownership. That matters because Linux-native file/event tools keep teaching the same lesson: the first low-level event is often not the right time to run the real automation.


- systemd's D-Bus API docs still say clients need to call `Subscribe()` before
  most manager signals are sent. That means VHK's new `WaitForDbusSignal` lane
  is useful immediately, but a future systemd-specialized helper should be able
  to auto-manage Subscribe/Unsubscribe when authors target manager/unit-state
  signals rather than leaving that contract implicit.
  - https://www.freedesktop.org/software/systemd/man/org.freedesktop.systemd1.html
- `gdbus monitor` remains a useful fallback, but its own command shape is
  narrower than `dbus-monitor`: it monitors one owner's objects (`--dest` and
  optional `--object-path`) instead of arbitrary match rules. VHK should keep
  preferring `dbus-monitor` for broad signal waits and stay explicit that
  `gdbus` fallback flows need a sender/bus-name scope.
  - https://manpages.ubuntu.com/manpages/focal/en/man1/gdbus.1.html

## systemd unit lifecycle should be first-class for Linux-native automation

VHK now has `GetSystemdUnitState` and `WaitForSystemdUnitState`, which closes
the most common service-orchestration gap for macros that depend on user units,
socket-activated helpers, timers, or other local manager-owned components.

What remains open is the *event-stream* side: long-lived service monitoring,
auto-managed `Subscribe()` / `Unsubscribe()` lifecycles for systemd
D-Bus-heavy flows, and richer unit-family helpers beyond the current
`systemctl show`-shaped state contract.
