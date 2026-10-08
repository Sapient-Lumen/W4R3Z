## Fresh issue cluster: startup ownership was still too easy to duplicate

- revision 0303 made graphical-session lifetime explicit, but the service handoff could still install more than one startup owner for the same VHK-owned lane: a systemd target path plus an XDG autostart bridge
- Linux-native automation needs one more repo rule here: startup ownership should be explicit and singular by default, with alternate owners kept as reviewed fallbacks instead of silently enabled in parallel
- revision 0304 closes the next part of that gap by adding a startup-handoff policy, guide, and probe, and by changing generated install helpers so graphical-session-bound user units stay primary while the XDG autostart bridge becomes an explicit opt-in fallback
- next follow-up: carry the same startup-owner policy into bootstrap/runtime launcher lanes so packaged first-run behavior does not drift back into duplicated startup hooks

## Fresh issue cluster: activation sync alone was not enough

- revision 0302 made live session/user-bus variables explicit, but the service handoff still left one operational truth too fuzzy: should the VHK-owned unit die with the graphical session or behave like a generic user daemon?
- Linux-native automation needs that answer in shipped artifacts because user services, XDG autostart, and desktop-specific session targets are related but not identical
- revision 0303 closes the next part of that gap by adding a session-target policy, generated session-target guide/probe, and explicit `BindsTo=graphical-session.target` wiring in the generated user units
- next follow-up: carry the same session-lifetime expectations into bootstrap/runtime launcher lanes so first-run helpers and packaged launchers stop flattening session truth back into generic app startup language

## Fresh issue cluster: release handoffs still drifted away from Linux ownership truth

- planner/install/service work had already identified who owns Linux automation authority per surface, but setup/release artifacts still risked flattening those distinctions back into package/deploy prose
- VHK now needs a persistent repo rule: setup, release-lane, release-deploy, and release-stage outputs should all preserve the same authority story the planner learned
- revision 0301 closes the next part of that gap by carrying project-level authority policy and per-lane authority stories through those packs
- next follow-up: let bootstrap/release-stage assembly/runtime launchers consume those same authority signals when deciding default service/env/session wiring

## Fresh issue cluster: installs and services must respect Linux authority boundaries

- native-install packs were already good at shipping launcher/runtime/doc handoffs, but they still risked implying that one local install somehow owned portal sessions, remapper edges, or privileged helpers too
- session-service packs were already good at user units and autostart bridges, but they did not yet say which surfaces they truly owned versus which ones remained adjacent privileged or desktop-mediated lanes
- VHK now needs this as a persistent product rule: installs can own userland packaging and resident session orchestration, while portal/global-shortcut and evdev/uinput/helper lanes stay explicit boundary objects
- next follow-up: let more setup/release/bootstrap artifacts consume the same authority policy so service scope and helper adjacency stay consistent across the repo


## Fresh issue cluster: authority envelopes were still implicit

VHK had become much better at saying who should ship, start, control, recover,
verify, and stay warm for a promoted Linux-native surface. But one product truth
was still too easy to lose in prose: *which layer actually has authority to own
that surface on Linux?*

That gap matters because Linux surfaces that all appear to “work” often mean very
different things operationally:

- a text expander is usually a user-session service/config authority story
- a portal lane is a desktop-mediated session/consent authority story
- a remapper is an evdev/uinput or compositor-edge authority story
- a helper daemon is a socket + `/dev/uinput` + service policy authority story
- a launcher is often only a discoverability/launch authority story

`plan-project` now closes that gap with `promotion_authority_envelope_plan` and
`promotion_authority_envelope_summary`, and promotion/operator/capability packs
now render the same surface so release/install docs stop conflating warm paths
with real host authority. The next follow-up is to let setup/native-install/
runtime generation consume those authority envelopes directly when deciding which
service scope, permission story, or desktop integration lane to materialize by
default.

### 0) Portal audit history needed operator-facing review + retention

The portal ledger and diff work now live under `XDG_STATE_HOME`, and VHK now ships `vhk portal-assignment-history`, `vhk export-portal-assignment-history`, `vhk prune-portal-assignment-history`, and `vhk inspect-portal-assignment-preset` so that state root becomes reviewable, shareable, pruneable, and provenance-aware instead of a pile of YAML files. Recent gaps closed: time-window / changed-shortcut filters, age-based pruning, Markdown + HTML summary export, generated saved review presets, layered `--preset-file` merging for team-shared plus operator-local overrides, and machine-readable preset-resolution provenance in history/export/prune handoffs. Remaining gap: carry that same provenance model into broader machine-readable review packs outside the portal lane.

## Fresh issue cluster: media automation needed a concrete thin adapter handoff

- the planner already knew how to recognize MPRIS-shaped projects, but that lane still stopped at review prose and generic session-fit/design commands
- `vhk gen-playerctl-pack` now closes the first deployment gap for that route with a reviewable playerctl/MPRIS adapter pack: route catalog, machine-readable command ledger, and thin helper wrappers that either print `playerctl --follow` output or invoke the matching `vhk run ...` command
- this keeps the product boundary honest: playerctl owns latest-player/follow behavior while VHK still owns macro semantics and project review
- next follow-up: feed those generated playerctl artifacts into broader release/setup/deploy packs and eventually support richer route-specific follow templates instead of one generic helper shape

## Fresh issue cluster: notification feedback needed action/progress runtime semantics

- the planner already knew desktop notifications were a real Linux feedback lane, but the runtime `Notify` step was still too thin for repeated progress/status updates and daemon-owned action prompts
- `Notify` now carries richer daemon-facing metadata too: `app_name`, `icon`, `category`, `timeout_ms`, `replace_id`, `transient`, `out_id`, `progress`, `actions`, and `out_action`
- the runtime can now round-trip notification ids so one step can create a notification and a later step can atomically replace it instead of spraying duplicate toasts
- progress-style notification hints can now stay explicit in macros instead of hiding in ad hoc `notify-send -h INT:value:...` wrappers
- action selections can now flow back into macro vars when the backend supports blocking/action output, which makes passive “open / dismiss / retry” prompts more honest than turning them into fake modal dialogs
- planner evidence now also highlights `replaceable_notifications`, `timed_notifications`, `transient_notifications`, `actionable_notifications`, and `progress_notifications` when projects start using that richer lane
- next follow-up: model close reasons/capability probing more explicitly and add a reviewable notification adapter pack so daemon-owned actions/history stay as explicit as the playerctl/kitty/mpv/qutebrowser lanes

## Fresh issue cluster: portal backend inventory still matters even after `portals.conf` support

`vhk doctor` already knew how to probe the live portal frontend interfaces and summarize `portals.conf`, but there was still a blind spot that mattered on real Wayland hosts: the installed backend manifests themselves.

That gap made several failure modes hard to explain cleanly:

- `portals.conf` could name a backend id that is not actually installed
- a backend could exist on disk but be excluded by its `.portal` `UseIn` rules for the current `XDG_CURRENT_DESKTOP`
- alternative wlroots backends such as `luminous` could be present yet invisible to VHK unless the user had already routed them explicitly

This revision closed the next part of that gap too: host-contract and readiness packs now ship a dedicated portal route contract so operators can compare "configured", "installed", and "actually live on D-Bus" in one place.

The next follow-up is to carry the same route-contract surface into setup/native-install/release-facing artifacts, so deployment bundles do not regress back into package-only portal prose.

## Fresh issue cluster: route ownership still drifts unless each macro names its lane

VHK already had stack profiles, surface choices, activation routes, and target
route packs, but one gap remained: authors could still ask “should this macro
really stay in the runner?” and the answer lived only in review prose.

That makes Linux-native design drift more likely:

- remap-like key transforms stay trapped in YAML when they belong in keyd / xremap / kanata-class exports
- hotstring/text bodies get treated like generic replay instead of text-tier assets
- watcher-driven workflows hide inside “normal macros” instead of becoming service-owned routes
- Wayland capture/pointer flows overpromise portability because the macro never says it is helper-boundary owned

`plan-project` now closes more of that gap with both `macro_route_profiles` and `macro_export_candidates`, while the new `route_portfolio`, `export_promotion_plan`, `promotion_waves`, `promotion_readiness`, `promotion_backlog`, and `promotion_evidence` surfaces finally let reviewers see which lanes dominate the whole project, which Linux-native promotions should be staged next, what belongs in the first shipping wave versus later fixup waves, which export surfaces are actually ready versus still needing session/compositor review, what concrete queued work remains, and which checked-in proof artifacts are still missing before those surfaces/gates should count as release-proof. `lint-project` now surfaces advisory `ROUTE_DRIFT_*` findings for text-tier, remapper-tier, watcher-service, and helper-boundary macros plus `PROMOTION_EVIDENCE_*` gaps when promotion proof has not been materialized yet. `gen-promotion-pack` closes more of the execution gap by turning that promotion work into docs/JSON/refresh scripts plus backlog/evidence docs, and now carries the planner's shipping-lane map directly so each promotion surface shows which Linux-native input lane actually owns shipping. The next issue is to let scaffold/export generators consume that plan directly instead of stopping at review artifacts.

## Fresh issue cluster: dispatch budgets were still under-expressed

VHK had gotten much better at saying who should ship, start, operate, recover, and verify a promoted Linux-native surface. But one AHK-parity question was still too easy to hand-wave away: *what dispatch path is that surface actually supposed to protect?*

That omission matters because Linux-native surfaces do not all win the same way:

- a text package wants a service-resident warm path instead of paying startup or per-character orchestration costs on every expansion
- a remapper wants an edge-resident path that stays as close to the input edge as possible instead of detouring through launcher or runner startup
- a helper/portal route may honestly accept daemon-warm or session-resume first use, but it still needs that posture stated out loud
- a watcher service wants a resident event pipeline, while a launcher may remain intentionally launch-cold

`plan-project`, `gen-promotion-pack`, `gen-capability-audit-pack`, and `gen-operator-pack` now expose a `promotion_dispatch_budget_plan` plus summary data so those expectations become reviewable. The next follow-up is to let setup/export/runtime-pack generation consume those postures directly, so “service-resident” and “edge-resident” stop being only documentation labels and start shaping the default shipped lane.

## Fresh issue cluster: portal shortcut lane should close the bind/install loop

- the portal trigger lane got noticeably more honest too: `vhk lint-project` now flags GlobalShortcuts bindings that would be skipped from the freedesktop catalog and reminds authors that `when:` selectors stay runtime-only after activation, while the converter itself now handles more punctuation keys via shortcuts-spec/xkbcommon identifiers instead of treating them as impossible
- `plan-project` now also separates **stable portal-catalog bindings** from **dynamic/helper-sensitive Wayland hotkeys**, exposes that split in `portal-global-shortcuts` evidence, and uses it to stop defaulting every Wayland hotkey toward the portal session route

- extend the new portal assignment diff flow into a persistent history lane (likely under XDG state) so VHK can keep reviewed snapshots across multiple sessions without hand-managed report paths
- surface portal shortcut catalogs in more release/install packs so Wayland release lanes do not rely on maintainers describing portal actions by hand
- add backend-specific validation hints for portal shortcut ids/triggers when desktop support is partial or gated by backend policy

## Fresh issue cluster: WM grouped trigger layers were under-modeled

- VHK already had exporter support for WM launcher modes and `gen-wm-config`
  mode/submap snippets, but the planner still treated that capability like a
  hidden implementation detail
- that made Linux-native trigger planning too binary: authors were nudged toward
  either more flat global binds or launcher hubs, with no first-class middle
  lane for grouped desktop-native action families
- `plan-project` now surfaces that middle layer explicitly through
  `wm-modal-trigger-layer`, `wm-modal-submap-lane`, and the ecosystem lesson
  `wm-modes-submaps-grouped-triggers`
- next follow-up: keep future which-key / hinting work aligned with the same
  action ids so grouped trigger UX can deepen without creating a second macro
  runtime

## Fresh issue cluster: remapper lanes are real product boundaries

- finish a real `xremap` exporter or adapter manifest so the new `xremap-remap` surface stops being planning-only
- teach setup/bootstrap to separate **portal-first trigger installs** from **remapper-first trigger installs** instead of always carrying portal base packages alongside remapper lanes
- carry the same choose-one-lane math into docs/install recipes for app-context bridges and focused-window metadata, because xremap-like lanes often depend on desktop-specific context adapters


## Fresh issue cluster: text-first automation should stay first-class even when recordings start low-level

- keep pushing text reconstruction carefully past the easy cases: backspace is now covered, but dead keys, compose sequences, IME flows, and layout-specific printable keys still need a truth-preserving policy
- keep teaching the recorder/optimizer to distinguish semantic shortcuts from literal text entry, especially around dead keys, multi-stroke compose/IME flows, and layout-specific printable characters
- carry the same text-first bias into future Studio cleanup flows so recorded snippets graduate toward `TypeText`, prompts, hotstrings, or exported text-expander lanes instead of staying as unreadable raw key chatter
- keep adapter/export honesty first-class: `vhk lint-project` now flags voice-context loss, AutoKey scope widening, and Espanso scoped-hotstring gaps before pack generation, but future Studio/setup flows should surface the same warnings visually instead of hiding them in JSON or terminal tables
- keep app-aware text/export lanes explicit in support language, since Linux text insertion still varies by session, helper, and compositor
- keep the new typing-vs-pasting optimizer lane conservative: long literal single-line text can be promoted to clipboard-paste explicitly, `${...}` templates and typed-delay choreography should stay visible as typed text by default, and Tab/Enter-rich form snippets should only cross into the new hybrid segmentation lane when an author explicitly opts in


## Fixed in this revision

### App-native protocol lanes now show up in planning

VHK already had enough building blocks to notice when a project was clearly
aiming at protocol-rich apps, but it was still flattening those flows into
generic window/text/pointer language.

This revision adds:

- `app-native-control-adapter` to candidate surface choices
- `app-native-protocol-lane` to reference patterns
- `native-app-protocols-beat-input-replay` to ecosystem lessons

That keeps kitty/WezTerm/mpv/qutebrowser-shaped targets visible as explicit
adapter opportunities instead of letting them disappear into generic replay
prose.

### Fresh follow-up

- `vhk gen-kitty-pack` now makes the first concrete app-native lane real for terminal text routes
- `vhk gen-mpv-pack` now makes the first concrete app-native media lane real for reviewable pause/stop/next/previous/seek/volume/mute/fullscreen commands over local mpv JSON IPC
- `vhk gen-wezterm-pack` now makes the next concrete app-native terminal lane real for reviewable pane-text routes over `wezterm cli send-text`, `wezterm cli get-text`, and `wezterm cli list --format json`
- `vhk gen-qutebrowser-pack` now makes the first concrete app-native browser lane real for reviewable userscript entrypoints that preserve `QUTE_*` context and route execution back through `vhk run`
- future Studio/inspector flows should help authors capture app-specific target evidence (window class/app_id/title, socket path hints, pane/window ids, userscript entrypoints, hint-mode assumptions) instead of expecting them to infer it from terminal/browser docs

### Fresh issue cluster: qutebrowser hint/userscript shaping is still intentionally thin

The first concrete qutebrowser adapter pack is now real, but it also stays intentionally conservative:

- it exports one reviewable userscript wrapper per qutebrowser-targeted macro instead of inventing a browser-specific macro DSL
- it preserves browser-side `QUTE_*` context and optional `QUTE_FIFO` status feedback, but it does not yet synthesize dedicated hint-mode variants or richer qutebrowser command templates from macro intent
- future Studio/inspector flows should help authors capture userscript entrypoints, hint-mode assumptions, and browser-side command affordances directly instead of reconstructing them from qutebrowser docs

### Fresh issue cluster: mpv socket capture is still mostly operator-supplied

The first concrete mpv adapter pack is now real, but it also stays intentionally conservative:

- it infers only a small reviewable command set from macro names/descriptions/binding keys
- it does not claim to discover a live `--input-ipc-server` path from running mpv instances, so helpers default to `${XDG_RUNTIME_DIR:-/tmp}/mpv.socket` unless the operator overrides `MPV_SOCKET`
- future Studio/inspector flows should help authors capture real mpv socket paths and richer per-route IPC commands instead of asking them to reconstruct those from player docs

### Fresh issue cluster: WezTerm pane identity capture is still partly operator-supplied

The first concrete WezTerm adapter pack is now real, but it also stays intentionally conservative:

- helpers prefer explicit `WEZTERM_PANE_ID` or `WEZTERM_PANE` and only fall back to title/title-regex lookup through `wezterm cli list --format json` when there is enough reviewable selector evidence
- ambiguous pane-title matches fail instead of guessing, because the exporter does not yet capture richer pane identity such as cwd, workspace, or semantic pane roles
- future Studio/inspector flows should help authors capture stable pane ids and richer pane-match hints directly instead of reconstructing them from the running terminal

### Fresh issue cluster: kitty match capture is still narrower than the runtime

The first concrete kitty adapter pack is now real, but it stays intentionally conservative:

- title/title-regex selectors can become honest exported `kitten @ send-text --match ...` routes
- class/app_id-only kitty selectors are still skipped because the exporter does not yet capture live kitty window metadata or synthesize safer cmdline/cwd match rules
- future Studio/inspector flows should help authors capture kitty match hints (title, cwd, cmdline, socket target) directly instead of asking them to infer those from terminal docs

## Fresh issue cluster: typed-text throughput needs first-class planning

- keep making long literal `TypeText` visible in lint/planner output so snippet-heavy projects do not hide latency behind otherwise clean-looking YAML
- keep the policy conservative: interpolation-heavy text, IME/dead-key flows, and choreographed per-character typing should stay explicit until VHK can prove a faster lane preserves semantics
- future Studio cleanup / palette / export surfaces should surface the same throughput advice instead of treating text optimization as a recorder-only trick

# Issues to track (2026 Q1)

This is a focused issue shortlist derived from the current VHK codebase plus the
current official Wayland/portal documentation landscape.

## Fixed in this revision

- planner/lint now flag long literal typed-text throughput and structured Tab/Enter-rich `TypeText` bodies so clipboard/hybrid text lanes become an explicit design-time choice instead of a buried optimizer feature.
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
- `vhk gen-service-compose-pack` now partially closes the next startup gap by materializing a session-service handoff under `build/publish/<bundle-name>/service/`, with first-party busd user units, environment.d exports, an explicit session-activation sync lane, and an XDG autostart bridge so login-time composition becomes reviewable instead of tribal knowledge.
- `vhk optimize --compress-text` (and recorder-side optimize) now recognizes shifted printable text too, so recorded runs like `Hello!` can collapse into one `TypeText` step instead of staying trapped as `shift+...` chords.
- that same text compaction lane now reconstructs small in-run corrections too, so recorder cleanup can turn sequences like `hex` + `Backspace` + `llo` into the final intended `TypeText("hello")` form instead of preserving typo noise as if it were author intent.
- recorder cleanup now also tolerates short cursor-local edits (`Left`/`Right`/`Home`/`End`/`Delete`), whole-word cleanup via `Ctrl+Backspace` / `Ctrl+Delete`, and tiny local selection replacements (`Shift+Left` / `Shift+Right` / `Shift+Home` / `Shift+End` followed by replacement text) when it can still prove the final caret returns to the logical end of the text with no live selection left behind; remaining gaps are richer editor semantics, dead keys, IME composition, and layout-aware printable inference.
- VHK now ships a generic `WaitUntil` step for expression-observable state, so authors can replace a class of brittle fixed sleeps and hand-rolled polling `While` loops with one backoff-aware primitive.
- VHK now also ships `WaitForBusEvent`, giving macros a dedicated event-driven synchronization primitive for helper scripts / WM binds / service glue instead of forcing everything through polling waits.
- VHK now ships `GetIdleMs` and `WaitForIdle`, making idle-aware automation first-class while keeping the support language explicit instead of pretending every Wayland session exposes one generic idle probe.
- `vhk plan-project` now emits a `performance_profile`, so unscoped capture/OCR pressure, aggressive polling waits, fixed-delay budgets, and heavy hotkey-bound macros are surfaced during design review instead of only after runtime profiling.
- planner and host-contract output now name daemon-backed Wayland uinput lanes more explicitly: `dotoold`/`dotoolc` becomes a first-class repeated-playback requirement alongside `ydotoold` instead of being buried under a generic helper seam.
- `plan-project` now also names a launcher/menu-hub surface and related reference pattern so larger macro catalogs can stay discoverable via rofi/WM launcher exports instead of defaulting to more memorized hotkeys.
- `gen-setup-pack` now stops flattening `dotool` and `ydotool` into one additive bootstrap list when the planner already knows they are alternative Wayland helper lanes; setup docs/scripts now surface one default lane plus explicit alternative package filters.
- host-contract and readiness packs now treat `dotoold` / `ydotoold` as a choose-one requirement group where appropriate, so one healthy helper lane no longer looks blocked just because a sibling fallback is absent.

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

### 2.5) broader alternative-lane modeling

The helper-daemon case is now modeled more honestly, but the same pattern still
needs to spread further:

- portal shortcut lanes vs compositor/WM bind lanes
- portal capture lanes vs compositor-native capture helpers
- remapper families (`keyd`, `kanata`, `kmonad`, `xremap`) when only one is
  meant to own the trigger surface on a given host

The key follow-up is not just setup packaging. It is effective readiness math:
VHK should keep distinguishing "missing optional sibling" from "actual
blocked deployment path" anywhere multiple Linux-native routes satisfy the
same capability.

### 2.75) accessibility inspector/editor gap

The planner now models an explicit AT-SPI / structured-UI lane more honestly,
but the product still lacks the authoring surface that would make that lane feel
first-class:

- an Accerciser-class inspector/browser inside future Studio flows
- event-monitor style visibility for focus/object/window signals
- selector capture/copy workflows that can turn inspected nodes into VHK-ready
  structured targets

Until that exists, the planner can say the right thing about accessibility lanes
but the authoring UX still relies too heavily on outside tools and manual
translation.

### 2.9) chooser preview / manifest gap

The planner now models a picker-native chooser lane more honestly, but the
product still lacks the authoring/install surface that would make it feel
first-class:

- a preview harness that can render the same palette/action catalog through
  rofi-script, stdin/stdout picker, and desktop-entry launch paths
- explicit per-picker manifests/argv notes so operators can review how a
  project should be wired into rofi, fuzzel, wofi, or similar shells
- future Studio affordances for testing hidden search terms, icons, and chooser
  action ids without manually launching external picker tools

Until that exists, VHK can plan the chooser lane correctly, but picker-native
flows still feel more external than the rest of the product.

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

### 11.5) Helper families still need alternative-lane modeling, not additive wishlists

Update:

- `gen-host-contract-pack`, `gen-readiness-pack`, and `gen-session-fit-pack` now partially close the operator-action gap too by carrying one preferred helper member and a bootstrap filter id through alternative-lane docs/JSON, so a healthy `dotoold` lane can point directly at `pointer-injection__dotool-daemon` instead of only saying “some helper is ready”.

Remaining gap:

- the same preference/filter language still needs to spread beyond helper daemons into remapper families and other route-choice surfaces.

The new `dotool-daemon` host/readiness requirement is more honest than the old
generic helper seam, but the planner can still make Wayland fallback toolchains
look additive when they are really *alternative* families. The next refinement
should express that a target lane might be satisfied by `wtype`, or a reviewed
`dotoold`/`dotoolc` lane, or a reviewed `ydotoold` lane, rather than quietly
implying an ideal host should run every helper stack at once.

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

### 18) daemon-backed uinput helper lifecycle should stay explicit

Current helper-backed Wayland injection keeps reinforcing the same operational
truth: repeated playback quality depends on long-lived helper lifecycle, not
just on whether a binary exists on PATH. `ydotoold` and `dotoold` should remain
visible in VHK planning, host contracts, and install docs so authors do not
confuse one-shot demos with real hotkey/session behavior.

### 19) Wayland text injection is still compositor-specific in practice

Current text-injection tools keep reinforcing the same lesson:

- `wtype` depends on compositor support for the virtual keyboard protocol
- KDE/Plasma now has KDE-specific lanes such as `KWtype`/`kdotool`
- `ydotool` still depends on `/dev/uinput` access and a helper-daemon lifecycle

That means VHK should keep text injection as a route-selection problem with
explicit toolchain choices, not a single generic “Wayland typing” checkbox.

### 20) Portal/input-capture persistence is still an operational edge, not solved product ground

Recent Input Leap Wayland discussions keep pointing at missing clipboard support
and repeated permission prompts, with upstream references to portal work around
clipboard transport and restore-token/persist-mode behavior. VHK should treat
portal/input-capture flows as recoverable session lanes with explicit re-arming,
not as fire-and-forget infrastructure.

### 21) AutoKey still validates the need for an honest X11-first lane

Current AutoKey issue templates still present the project as an Xorg/X11
application and continue to surface Wayland incompatibility up front. For VHK,
that reinforces the product stance: keep the X11/i3 lane strong and fast, and
make Wayland support route-based and capability-scoped rather than slogan-based.

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

- `gen-native-install-pack` now also carries an installed-lane readiness verdict directly inside `--status-json`/status Markdown, and `gen-support-pack` now asks for that lighter-weight status bridge before escalating to a full host packet.
- remaining gap: the installed status lane is still a report/document surface, not a live GTK/QML operator dashboard, and its usefulness still needs validation on real GNOME/KDE/wlroots hosts with service/session drift.

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

## Route-health follow-through

- helper and remapper alternative lanes should propagate all the way into activation, route selection, and target-profile comparison
- every route that depends on a choose-one lane should surface the exact reviewed bootstrap filter or preferred lane member, not only a generic readiness verdict
- remapper families (`keyd`, `kanata`, `kmonad`, `xremap`) still deserve the same alternative-lane treatment now implemented for helper daemons

- The xremap lane now has a first exporter, and it is a little less lossy than before: launch-style bindings plus app/window scoping are covered, `title_regex` / `app_id_regex` can now survive into native xremap filters, and `vhk lint-project` now warns when selector fields like `workspace`, `pid`, or window-state flags would remain runtime-only in VHK. Richer xremap features (device filters, more advanced sequence/mode stories, and broader compositor-specific testing) still need dedicated follow-through.


## 2026-03-08 portal history export follow-up

- `export-portal-assignment-history` now covers Markdown and single-file HTML, and `gen-portal-assignment-presets` now ships named review/export/prune bundles. The next useful operator surface is preset governance: distinguish team-shared review presets from local/operator overrides without forking the whole file.


### 15) Clipboard-trigger semantics need backend-aware review tooling

VHK now has a better runtime contract for clipboard change-vs-event waits, but
project/studio/planner surfaces still need to explain when `event_mode: event`
is genuinely available versus when a host has fallen back to pure polling.
That distinction matters for AHK-style repeated-copy workflows.

### 16) Linux-native app context should stay desktop-specific, not flattened

Recent ecosystem review keeps reinforcing that app-aware behavior on Wayland is
still mediated by desktop-specific context bridges and helper lanes. VHK should
keep modeling GNOME, KDE, wlroots/sway, Hyprland, and similar targets as
separate implementation lanes for app/window-sensitive automation instead of
pretending one generic "Wayland app detection" checkbox exists.

### 17) Portal-first hotkey stories still need drift/error budgeting

GlobalShortcuts is strategically important, but backend consent flow, app-id
association, and session-start timing issues still make it a soft boundary
rather than a deterministic always-on trigger lane. Planner/readiness/install
surfaces should keep budgeting for verification and fallback routes.


### 18) Voice adapter follow-through

`plan-project` now makes the voice lane visible too via `voice-command-adapter`, `voice-context-command-lane`, and `voice-tools-own-recognition-context`, so Dragonfly/Talon export stops hiding behind pack-generation trivia. `vhk gen-dragonfly-pack` and `vhk gen-talon-pack` still close the deployment side by exporting reviewable adapters instead of hand-waving toward speech support. The remaining gaps are now more concrete:
- doctor/readiness should surface Dragonfly/X11 and Talon/X11 prerequisites explicitly when operators choose these lanes
- prompt-heavy macros still need better spoken-workflow guidance than a raw `--include-prompt-entries` escape hatch
- future Studio surfaces should help authors assign/test `voice_phrases` instead of leaving them as hidden YAML-only metadata
- cross-export validation is better now: `vhk lint-project` catches duplicate spoken phrases within the same effective Dragonfly/Talon scope, warns when explicit phrases normalize to nothing, points out punctuation/case variants that export as a different literal phrase, flags redundant variants that collapse together, and nudges authors away from short one-word global voice commands. The remaining gap is richer pronunciation/homophone guidance rather than raw duplicate detection.
- `voice_when` now gives voice packs honest app/title scoping, but richer selector coverage still needs a deliberate design instead of backend-specific wishful thinking
- Wayland-native voice-trigger stories remain an open research area; VHK should keep these exports framed as X11-leaning adapters, not universal Linux voice layers


### AutoKey adapter lane should stay reviewable because the upstream trigger/editor surface is still noisy

Now that `vhk gen-autokey-pack` exists, the remaining product lesson is not “pretend AutoKey is a universal Linux backend,” but “keep the X11 adapter explicit and diffable.” AutoKey still documents itself as Linux/X11, its configs still live as body files plus sidecar metadata pairs, and recent issue traffic still includes both core X11/Wayland honesty and day-to-day trigger/editor rough edges such as abbreviation editing failures. That argues for shipping a reviewable adapter pack instead of burying AutoKey-specific behavior inside VHK internals.

Implications for VHK:
- keep AutoKey export strictly X11-positioned
- prefer generated script + sidecar pairs plus a manifest/README over hidden importer magic
- keep selector translation conservative because AutoKey's window filter is coarser than VHK's selector model
- keep skip reasons visible so operators can manually review what still needs a different trigger lane

Refs:
- https://autokey.github.io/intro.html
- https://autokey.github.io/api/system.html
- https://github.com/autokey/autokey/issues/1013
- https://github.com/autokey/autokey/issues/1061

### AutoKey window-filter export should stay opt-in approximate

Current AutoKey behavior and issue discussion still point to one important limitation: the window filter is effectively one regex matched against window title **or** class, not a true multi-field selector model. That means even a simple VHK `when: {class: Firefox}` export is broader than it looks once it crosses into AutoKey.

Product rule carried into VHK:
- skip scoped AutoKey exports by default
- only allow simple scoped export behind an explicit `--allow-window-filter-approximation` flag
- keep rejecting broader selectors (`class` + `title`, `workspace`, `app_id`, etc.)
- validate `title_regex` patterns before emitting AutoKey sidecar metadata

- Espanso package-dir export needed a more honest/applicable precedence model: current Espanso docs say only one app-specific config is active at a time, so VHK should not emit multiple overlapping scoped config files without also modeling precedence and composite includes.


## Trigger-lane honesty follow-through (2026-03-09)

- `vhk lint-project` now covers keyd, Kanata, KMonad, and sxhkd trigger honesty
  in addition to voice/AutoKey/Espanso/xremap.
- keyd-fork's current experimental `keyd-application-mapper` suggests a future
  app-aware export lane, but VHK should not claim it yet until it can emit and
  validate that extra sidecar/config surface honestly.
- KMonad's current leader/layer export is now called out before generation; the
  remaining gap is richer preview tooling so operators can see the selector-key
  layout without opening the generated `.kbd` file by hand.


### 19) Promotion gates should become release-audit inputs

VHK now has planner-facing promotion gates, but the next follow-through is to
connect them to the release and claim packs instead of leaving them only in
strategy/lint/promotion output. That would let a reviewed bundle or staged lane
carry explicit claim-discipline evidence instead of relying on maintainers to
copy the planner summary by hand.

### 20) Session proof should become target-aware, not only host-aware

This is now moving in the right direction: release-deploy, release-stage,
native-install, host-rehearsal, and host-dossier output can all carry a compact
`target_fit_contract`, so later-stage artifacts can compare current host truth
against one declared flagship release lane instead of only repeating local
status.

What remains open:
- planner/audit surfaces should learn to consume the same target-fit contract so
  claim discipline and promotion gates become target-aware too
- target-fit should eventually accept explicit operator-selected comparison
  lanes when a repo wants to review more than the flagship profile

### 21) Deployment truth should stay attached to install/release surfaces

`gen-setup-pack`, `gen-native-install-pack`, `gen-service-compose-pack`,
`gen-release-deploy-pack`, `gen-release-stage-pack`, `gen-host-rehearsal-pack`,
and `gen-host-dossier-pack` now carry the same compact host/deployment truth
forward instead of dropping back to static packaging or support prose.

What remains open:
- the deployment truth model should keep distinguishing configured routing,
  installed backend manifests, and live portal interfaces as separate review
  layers
- claim/audit-facing packs should eventually ingest that same deployment truth
  snapshot instead of expecting operators to correlate review docs by hand


### 22) Claim witness review is now host-aware, and promotion surfaces now consume it too

`gen-claim-pack`, `audit-target-claims`, and `gen-capability-audit-pack` can now
carry a compact current-host witness review so strong claims fail when the local
machine clearly drifts from the lane it is being used to prove.
`gen-promotion-pack` now consumes that same witness posture and adds a compact
`current-host-proof-gate` plus backlog/evidence pressure before maintainers ever
edit claim YAML.

What remains open:
- core planner/strategy JSON should eventually expose the same witness posture
  directly instead of waiting for the promotion/claim overlays
- claim witness review should eventually support explicit operator-selected
  evidence hosts/lanes instead of only the current machine
- release/publish output should be able to quote this witness status directly in
  support/release snippets when a repo wants a stricter proof chain

### 23) Core planner output still hides wrong-host proof until pack overlays run

Closed in REV0265: `plan-project` / core strategy JSON now exposes
`planner_target_claims`, `planner_claim_witness`, plus current `host_truth` and
`portal_route_contract` when live checks are available. That means wrong-host
proof drift no longer waits for claim/promotion overlays before it becomes
visible in core planner output.

What remains open:
- let maintainers compare more than one reviewed evidence lane instead of only
  the current host
- keep the planner-level contract small enough that it remains explainable in
  docs and CI output
- thread the same compact witness summary into any future CI/status surfaces
  that consume planner JSON directly

### 24) Evidence-lane review existed implicitly, but operators could not pin one lane across planner/claim/promotion flows

Closed in REV0266: `plan-project`, `gen-claim-pack`, `audit-target-claims`,
`gen-promotion-pack`, and `gen-capability-audit-pack` now accept
`--evidence-lane <profile-id>` and carry that explicit lane through JSON/docs and
refresh scripts. That means maintainers can ask one focused question: is this
particular machine believable proof for *this* chosen lane?

What remains open:
- allow comparing more than one explicit evidence lane in the same review run
- give operators a clearer distinction between flagship shipping lane, reviewed
  evidence lane, and fallback/reference lanes
- thread explicit evidence lanes into any future CI/status surfaces that consume
  planner or claim audit JSON directly

### 25) Several host-aware commands collected live proof but dropped it before pack/audit generation

Closed in REV0268: `plan-project`, `gen-host-contract-pack`, `gen-claim-pack`,
`audit-target-claims`, `gen-capability-audit-pack`, and `gen-promotion-pack`
now forward the live host snapshot and explicit evidence-lane context into the
pack/audit builders that consume it. That keeps wrong-host proof drift visible
across planner, claim, promotion, host-contract, session-fit, and
capability-audit workflows instead of silently degrading into hostless review.

What remains open:
- centralize this host-proof plumbing so future pack commands do not each have
  to hand-thread `host_snapshot` / `evidence_lane_profile` arguments
- add regression coverage for every host-aware CLI command that probes live
  readiness before calling a writer
- consider a shared proof-context object so refresh scripts, JSON, and markdown
  stay aligned by construction rather than by repeated parameter plumbing



### Planner output should keep explicit X11 adapter lanes visible

Closed in REV0269:

- `plan-project` now scores an explicit `autokey-x11-adapter` candidate surface
- planner patterns now include `autokey-reviewable-adapter`
- X11 text-tier route guidance now includes `vhk gen-autokey-pack ...` so AutoKey export is no longer just a hidden side feature

Why it matters:

- AutoKey remains an X11-first automation shell, which still makes it useful as a reviewable adapter lane
- but that usefulness only helps VHK if the planner shows *when* it is the right lane and *why* it is not a generic Wayland answer


### Generic Wayland text planning was too eager to treat `wtype` as the default answer

Closed in REV0270:

- `plan-project` now exposes `wtype-wayland-text` as an explicit narrow surface
  instead of hiding `wtype` behind a generic text-toolchain story
- planner patterns now include `wtype-narrow-wayland-text-lane`
- ecosystem lessons now include `wtype-virtual-keyboard-boundary`
- the generic Wayland text-toolchain default is now clipboard-first, with
  `wtype` remaining the explicit fast path when the session actually supports it

Why it matters:

- `wtype` is valuable precisely because it is a thin typed-text edge, not a full
  Linux automation contract
- virtual-keyboard support is compositor/protocol-shaped, so VHK should not
  present `wtype` as the broad Wayland default in host-agnostic planning
- keeping package/clipboard text export visible prevents text-heavy projects
  from drifting into unnecessary helper/uinput complexity


### Planner should expose daemon-backed helper lanes directly, not only through setup docs

VHK already knew a lot about helper lifecycle:

- `gen-dotoold-service` and `gen-ydotoold-service` existed
- setup packs already knew about `wayland-uinput-helper-daemon`
- host/readiness packs already reasoned about `/dev/uinput`, helper sockets, and
  choose-one daemon groups

But `plan-project` still under-expressed that lesson at the top level. That left
Wayland-heavy projects in an awkward place where the planner could say “helper
boundary” while the concrete daemon/service route stayed hidden until later
packs.

This revision closes that gap by adding:

- `uinput-helper-daemon` to candidate surface choices
- `daemonized-uinput-helper-lane` to reference patterns
- `daemonized-helper-lifecycle` to ecosystem lessons

That makes repeated helper-backed playback feel more like a real Linux-native
deployment lane and less like a buried implementation detail.

### Planner and audit output should expose workload-shaped input lanes directly

Closed in REV0290:

- `plan-project` now emits `input_lane_dossier`, a workload-oriented summary of
  clipboard-first text, Wayland virtual-keyboard fast paths, daemon-backed
  uinput playback, portal-permissioned input, and X11-native replay
- promotion surfaces can now also be tied back to concrete lanes through
  `promotion_input_lane_plan`, so project-level shipping work no longer floats
  free of the runtime/input model
- the next missing truth was lifecycle ownership, not just input ownership: the
  repo still needed a `promotion_activation_route_plan` so each shipping surface
  could say which service/session/launcher route actually wakes it and keeps it
  alive on Linux
- the dossier carries fit, commands, cautions, host requirement ids, and
  session-capability posture so Linux input review stops being a helper-inventory
  decoding exercise
- `gen-capability-audit-pack` now renders that same dossier as a human-readable
  section, so operator docs and planner JSON talk about the same real lanes

Why it matters:

- upstream Linux automation keeps splitting by lane and lifecycle rather than by
  one universal injection contract
- maintainers need to review workloads like "text bursts" or "repeated pointer
  playback," not just memorize helper names
- making those lanes first-class keeps VHK closer to a Linux-native AHK product
  strategy instead of a pile of adapters


## Fresh issue cluster: Linux-native prior art still splits by lane

- AutoKey mainline still presents itself as X11-first, while current Wayland work is active but not yet a clean general-purpose parity story
- Espanso continues to show why text expansion is its own lane: Wayland support exists, but it is explicitly experimental and still lacks app-specific configuration on that path
- xremap and keyd remain strong evidence that low-latency remap ownership belongs near evdev/uinput or desktop-specific context bridges, not in a generic replay runner
- libei/EIS remains the important longer-horizon input-emulation direction for Wayland-native automation, but shipping Linux desktops and compositors still vary widely in what they expose today
- implication: VHK should keep one authoring surface, but keep text-expander, remapper, notification, accessibility, and helper/service lanes explicit instead of claiming one universal backend can honestly cover them all


## Newly surfaced gap after REV0293

- Promotion review also needed a `promotion_operator_control_plan` so each shipping surface names its day-2 status/reload/log ownership instead of stopping at startup-route truth alone.


### 25) Promotion review knew how to ship and operate a surface, but not how to recover it

`promotion_input_lane_plan`, `promotion_activation_route_plan`, and `promotion_operator_control_plan` made shipping/startup/day-2 ownership explicit, but review docs still left one Linux-native question implicit: what is the first safe response when a promoted surface drifts, seizes input, loses consent, or stops delivering events?

This revision partially closes that gap by adding `promotion_recovery_plan` to planner output and threading it into promotion, operator, and capability-audit docs. Each promoted surface now names a first-response / rollback / re-entry lane instead of leaving recovery as scattered prose. Remaining gap: the runtime still does not collect enough live watcher overflow/backpressure telemetry to prove those recovery loops empirically on host-aware runs.

### Promotion verification proof loops

`promotion_input_lane_plan`, `promotion_activation_route_plan`, `promotion_operator_control_plan`, and `promotion_recovery_plan` made shipping/startup/day-2/recovery ownership explicit, but one Linux-native question was still only implied: what exact smoke/proof loop demonstrates that a promoted surface is alive on the target desktop right now?

This revision closes part of that gap by adding `promotion_verification_plan` to planner output and threading it into promotion, capability-audit, and operator docs. Each promoted surface now names a verification posture, primary verification lane, related capability gates, smoke loop, live probe, and proof surfaces. Remaining gap: the runtime still lacks enough built-in live probes to automatically collect those proof loops from real sessions instead of only planning them.

- Add more direct performance-envelope review commands and examples for flagship surfaces, especially clipboard/text throughput smoke, remapper edge-path smoke, and daemon warm-path validation for repeated playback.


## Fresh issue cluster: service startup still needed live session proof

VHK had become much more explicit about startup ownership and session lifetime,
but one Linux-native failure mode remained too easy to misread: a service could
be *properly installed* yet still be started before its live graphical/session
prerequisites existed.

That gap is now narrower because service-compose output ships an explicit
session-readiness guide and probe, and the generated VHK-owned unit uses an
`ExecCondition=` guard. The next follow-up is to let broader rehearsal/dossier
surfaces ingest readiness outcomes directly instead of treating them as a pure
service-pack concern.


## Fresh issue cluster: readiness needed to become operator evidence

That gap is now narrower because host rehearsal and host dossier output ingest
installed `verify_session_readiness.sh` results directly. The next follow-up is
to feed those same readiness verdicts into higher-level support/public-status
lanes so session truth can travel beyond one machine-local rehearsal or dossier
archive.


## Fresh issue cluster: installed status still flattened runtime health

The installed lane could already say whether the session looked ready, but that
still left an important Linux-native question under-modeled: was the owned lane
actually healthy, quietly stopped, missing, or churning through restart
pressure?

That gap is now narrower because the installed status bridge carries an explicit
runtime-health verdict derived from readiness plus nearby user-unit facts,
including restart churn signals. The next follow-up is to let public/support
surfaces aggregate those verdicts over time instead of only reporting one live
snapshot.

## Fresh issue cluster: installed status still flattened startup ownership

The installed lane could already say whether the session looked ready and
whether the owned service looked healthy, but that still left one Linux-native
question under-modeled: did the lane actually have one valid startup owner, a
fallback autostart owner, both, or neither?

That gap is now narrower because the installed status bridge carries an explicit
startup-handoff verdict derived from both user-unit enablement and effective
autostart state, including `Hidden=true` and missing `TryExec` cases. The next
follow-up is to let rehearsal/dossier lanes preserve longer-term startup-owner
drift, not just one live snapshot.



## Fresh issue cluster: installed status still flattened startup-owner drift

The installed lane could already say who owned startup in one snapshot, but it
still could not say whether that ownership was stable, recently changed, or
chronically degraded. That made duplicate-start risk and missing-owner states
feel more transient than they really were.

That gap is now narrower because the installed status bridge keeps a short local
startup-owner history and surfaces a drift verdict. The next follow-up is to let
release/public-status lanes aggregate those drift verdicts across hosts instead
of only within one installed lane.


## Fresh issue cluster: installed status still flattened runtime-health drift

The installed lane could already say whether it looked healthy in one snapshot,
but it still could not say whether that health was stable, newly recovered, or
repeatedly degrading. That made restart churn and failed-state evidence feel
more transient than they really were, especially because systemd counters can be
reset during normal operator recovery work.

That gap is now narrower because the installed status bridge keeps a short local
runtime-health history and surfaces a drift verdict. The next follow-up is to
let release/public-status lanes aggregate those runtime-health drift verdicts
across hosts instead of only within one installed lane.


## Fresh issue cluster: installed status still flattened recent incidents

The installed lane could already say whether the session looked ready, whether
the owned service looked healthy, and whether that health/startup ownership was
drifting, but it still could not say what kind of recent incident had actually
happened. That made clean skips, start-limit churn, and genuine service
failures feel too similar in day-to-day support.

That gap is now narrower because the installed status bridge carries an
incident-signature verdict with a short user-journal sample when available. The
next follow-up is to let release/public-status lanes aggregate those incident
classes across hosts instead of only within one installed lane.

## Fresh issue cluster: incident snapshots still hid incident history

The installed lane could already classify the current incident, but one compact
incident snapshot still left operators guessing whether a clean skip or service
failure was a one-off, chronic, or flapping condition.

That gap is now narrower because the installed status bridge also carries one
incident-signature drift verdict with a short bounded local history. The next
follow-up is to let release/public-status lanes aggregate those drift stories
across hosts instead of only within one installed lane.

