# VHK (i3/sway) — engine + CLI scaffold

This repo is the **engine** and **headless runner** foundation for a future
"VisualHotKey + Pulover’s Macro Creator"-class studio on Linux (i3 on X11, sway on Wayland).

The long-form requirements/inventory live at:
- `docs/requirements.md`

The explicit engine + studio specs live at:
- `docs/SPECS.md`

A current Linux-native runtime plan lives at:
- `docs/PLAN_2026Q1_LINUX_NATIVE_RUNTIME.md`
- `docs/NATIVE_RUNTIME_SPEC_2026Q1.md`

A focused issue shortlist lives at:
- `docs/ISSUES_2026Q1.md`

Focused runtime/introspection notes:
- `docs/WINDOW_PROCESS_CONTEXT.md`
- `docs/WINDOW_EVENT_WAITS.md`
- `docs/DRAGONFLY_PACK.md`
- `docs/TALON_PACK.md`
- `docs/DBUS_SIGNAL_WAITS.md`

Project-shape / strategy analysis docs live at:
- `docs/PROJECT_STRATEGY.md`
- `docs/DEPLOYABLE_SURFACES.md`
- `docs/SETUP_RECIPES.md`
- `docs/STARTER_ARTIFACTS.md`
- `docs/OPERATOR_PACK.md`
- `docs/VERIFICATION_PACK.md`
- `docs/PORTABILITY_PACK.md`
- `docs/PUBLISH_PACK.md`
- `docs/READINESS_PACK.md`
- `docs/RESEARCH_2026Q1_DEPLOYMENT_LIFECYCLE.md`
- `docs/NOTE_2026.03.17_AUTHORITY_AWARE_INSTALLS_AND_SERVICE_SCOPE.md`
- `docs/RESEARCH_2026.03.17_AUTHORITY_AWARE_INSTALLS_AND_SERVICE_SCOPE.md`
- `docs/NOTE_2026.03.17_RELEASE_AUTHORITY_HANDOFFS.md`
- `docs/RESEARCH_2026.03.17_RELEASE_AUTHORITY_HANDOFFS.md`
- `docs/NOTE_2026.03.17_SESSION_TARGET_BINDING.md`
- `docs/RESEARCH_2026.03.17_GRAPHICAL_SESSION_TARGET_BINDING.md`
- `docs/NOTE_2026.03.17_SESSION_READINESS_EVIDENCE.md`
- `docs/RESEARCH_2026.03.17_SESSION_READINESS_EVIDENCE_AND_OPERATOR_DIAGNOSTICS.md`
- `docs/NOTE_2026.03.17_INSTALLED_LANE_READINESS_STATUS.md`
- `docs/RESEARCH_2026.03.17_INSTALLED_LANE_READINESS_STATUS.md`
- `docs/NOTE_2026.03.17_INSTALLED_INCIDENT_SIGNATURES.md`
- `docs/RESEARCH_2026.03.17_INSTALLED_INCIDENT_SIGNATURES.md`

## What exists today (v0.24)

- A small **project format** (folder-based) with macros in YAML.
- Voice adapter exports: `vhk gen-dragonfly-pack` generates a reviewable Dragonfly command module + command ledger, and `vhk gen-talon-pack` generates a reviewable Talon `.talon` + Python action pack + ledger, so spoken phrases can launch `vhk run ...` without turning VHK into its own speech recognizer. Macro/preset `voice_when` selectors can now scope those generated voice commands to honest app/title contexts when the target toolchain can express them, repeated spoken phrases can safely be reused across different exported voice contexts, and `vhk lint-project` now warns when phrases still collide inside the same effective Dragonfly/Talon scope.
- `vhk lint-project` now also gives voice-phrase quality guidance before export: it warns when an explicit `voice_phrases` entry normalizes to nothing, notes when punctuation/case/hyphen variants collapse to a different literal spoken form, flags redundant variants that normalize to the same export phrase, and nudges authors away from short single-word global commands unless they add `voice_when` scope.
- AutoKey/X11 adapter export: `vhk gen-autokey-pack` generates a reviewable AutoKey folder tree (`data/...` script + sidecar metadata pairs, README, manifest) from VHK hotstrings and bindings, keeps VHK as the execution engine, skips scoped selectors by default because AutoKey window filters match title OR class with one regex, and only allows that lossy scope export behind `--allow-window-filter-approximation`.
- `vhk lint-project` now also acts as an export-honesty pass for adapter lanes: it warns when `voice_when` uses selector fields Dragonfly/Talon cannot export, when AutoKey scope would require title-or-class approximation, when Espanso-scoped hotstrings are being designed for Wayland, when Espanso package-dir export will need synthetic composite configs to preserve overlapping scopes, when xremap-scoped bindings rely on selector fields that xremap cannot pre-filter itself, when keyd/Kanata/sxhkd/KMonad bindings still keep `when:` scope runtime-only inside VHK, when a Wayland project still targets sxhkd, and when KMonad export will change trigger shape into a leader/layer flow or selector sublayers.
- Structured control flow / error handling:
  - `While(condition, steps, max_iterations?)`
  - `WaitUntil(condition, timeout_ms?, poll_ms?, max_poll_ms?, jitter_ms?, max_attempts?)`
  - `WaitForBusEvent(event?, pattern?, condition?, timeout_ms?, socket_path?)`
  - `WaitForDbusSignal(bus?, sender?, path?, interface?, member?, match?, pattern?, condition?, timeout_ms?)` for event-driven service / desktop integration without custom bridge glue
  - `GetSystemdUnitState(unit, scope?)` / `WaitForSystemdUnitState(unit, active_state?, sub_state?, status?, ...)` for Linux-native service/user-unit synchronization without hand-parsed `systemctl show` shell glue
  - `GetIdleMs()` / `WaitForIdle(minimum_ms, ...)` / `WaitForUserActivity(maximum_ms, ...)` for honest idle-aware automation on X11 and GNOME Wayland, with explicit bus-bridge guidance for compositor-specific Wayland idle lanes
  - `Try(steps, catch_steps?, finally_steps?, catch_pattern?)`
  - `Break`, `Continue`, `Return`
  - `SetVar` now accepts plain expressions like `i + 1` in addition to literals/interpolation
- Data-oriented workflow helpers:
  - `ReadCsv`, `WriteCsv`, `ReadJson`, `WriteJson`
  - `ForEach(items_expr, item_var, steps)`
  - `RegexReplace`, `TrimText`, `SplitText`, `JoinText`
- Desktop/browser/network glue:
  - `OpenUrl`, `ComposeEmail`, `PasteClipboard`
  - `HttpRequest`, `DownloadFile`, `WaitForNewFile`, `WaitForFileEvent`, `WaitForDownload`
  - `Notify` now supports replace/update ids, progress hints, and optional action capture (`out_id`, `replace_id`, `progress`, `actions`, `out_action`)
  - `ShowMessage`, `AskYesNo`, `InputBox`, `PromptForm`, `ChooseFromList`
  - `StartProcess`, `WaitForProcessExit`, `KillProcess`
- A **runner** that executes a step list with variables + interpolation + safe-ish
  expression evaluation.
- A minimal **vision** backend:
  - template matching via OpenCV (`ImageSearchFile`, `WaitForImageFile`, `ImageSearchAllFile`)
  - openQA-style needle metadata support (`foo.png` + `foo.json`)
    - match areas + per-area `match` percent
    - exclude areas (masked matching)
    - click points (loaded for tooling)
    - OCR areas (used by `OcrNeedleText` / `WaitForNeedleText`)
  - pixel search (`PixelSearch`, `WaitForPixel`) and image-file equivalents (`PixelSearchFile`, `WaitForPixelFile`)
    - optional `step` stride for faster scanning; waits cycle sampling phases when `step>1`
  - pixel FindAll + click-all (`PixelSearchAll`, `WaitForPixelAll`, `ClickPixelAll`) and file equivalent (`PixelSearchAllFile`)
    - optional `group: connected` to collapse contiguous pixels into blobs
  - pixel sampling (`PixelGetColor`) and image-file equivalent (`PixelGetColorFile`)
  - OCR from image files via Tesseract (`OcrReadTextFile`)
    - plus OCR bounding boxes: `OcrFindTextFile` (word/line bbox)
  - Screen-capture convenience steps:
    - `ImageSearch`, `WaitForImage`, `ImageSearchAll`, `WaitForImageAll`, `ClickImageAll`
    - `OcrReadText`, `WaitForText`, `AssertText`
    - `OcrFindText`, `WaitForTextBox`, `ClickText` (find/click by OCR bbox)
    - `OcrFindTextAll` + `ClickTextAll` (multi-match OCR bbox search + click for lists/grids)
    - OCR fuzzy matching: `match: fuzzy` with `fuzzy_threshold`/`fuzzy_mode`
    - `ClickNeedle` (uses openQA click points when available)
    - `VisualAssert`, `VisualVerify`, `WaitForRegionChange`, `WaitForRegionStable`
  - AHK-style coordinate mode translation:
    - `CoordMode(target=pixel|mouse, mode=screen|window|client)`
    - affects how regions and mouse coordinates are interpreted (outputs remain screen-absolute)
  - `ReadFile`, `WriteFile`, `AppendFile`, `ListDirectory`, `WaitForFile`, `WaitForFileEvent`
  - `WaitForClipboardChange` / `WaitForClipboardEvent` with optional regex + condition filtering
  - `MouseDrag`, `MouseWheel`
- Installed launcher/support/rehearsal/dossier surfaces now also preserve one **incident-signature** verdict for the reviewed lane, so support can distinguish clean session skips, generic condition skips, start-limit churn, real service failures, missing units, and probe/runtime breakage without collapsing everything into generic user-unit state. Those same surfaces now also keep one short **incident-signature drift** history so support can tell whether those incidents are first-seen, stable, chronic, flapping, or recovered to a quiet lane.
- Native-install and session-service handoffs now carry an **authority-aware ownership policy**: packaged launcher/docs/runtime stay explicitly userland, portal/session lanes remain desktop-mediated, and remapper/helper lanes stay adjacent privileged surfaces instead of being silently absorbed into the install story. Generated native app trees now ship `VHK_AUTHORITY_OVERVIEW.md`, and service composition packs surface the same ownership boundary in docs/JSON.
- Setup, release-lane, release-deploy, and release-stage handoffs now carry the same authority model all the way through shipping. That means generated docs/JSON/README output say not only how a lane starts or deploys, but also whether it is session-userland, desktop-mediated, helper-daemon-adjacent, or input-edge-owned after release.
- Service composition handoffs now also carry an explicit **graphical-session lifetime binding policy**: generated docs/JSON/probe scripts say whether the VHK-owned unit should bind to `graphical-session.target`, the user units now declare that binding directly, and install/uninstall helpers keep that target wiring reviewable instead of leaving session lifetime semantics implicit.
- A tiny **i3/sway IPC** client (pure Python) + runner steps.
  - session auto-detection now treats `WAYLAND_DISPLAY` as authoritative, which helps avoid accidentally picking X11-only helpers inside XWayland-heavy sessions
  - socket discovery checks `SWAYSOCK`/`I3SOCK`, `sway --get-socketpath`, `i3 --get-socketpath`, and the X11 `I3_SOCKET_PATH` property.
- Cursor/reliability helpers inspired by xbanish / unclutter + xdotool caveats:
  - project setting `settings.hide_cursor_during_run: true`
  - explicit `CursorHide`, `CursorShow`, and `ResetModifiers` steps
  - `GetCursorPos` step (best-effort; uses compositor/tool helpers on Wayland)
  - `GetActiveWindow` step for watcher-style runtime introspection (`window` / `wm` plus convenience vars like `window_title`, `window_class`, `window_pid`, and `window_process`), so one-shot macros can reuse the same active-window vocabulary as window watchers and `window-spy`; active snapshots now also carry best-effort state fields such as `visible`, `fullscreen`, `floating`, `sticky`, or `minimized` when the backend exposes them cleanly
  - `GetWindowAtCursor` step for AHK-style “window under mouse” probing, returning the current pointer location plus a best-effort top-level window snapshot across i3/sway, Hyprland, X11, and KDE Wayland, with optional PID/process-name context and state fields when the backend exposes them cleanly
  - `GetWindowList` step for AHK-style open-window enumeration, returning a stable watcher-like list shape across i3/sway, Hyprland, X11, and best-effort KDE Wayland (`kdotool`), including PID/process-name context plus best-effort visibility/fullscreen/floating/minimized/sticky metadata where available
  - `WaitForWindowEvent` step for event-driven focus/workspace/title/urgent/new/close/custom synchronization, with optional selector/raw-name/expression filtering and best-effort watcher-style payloads for the matched WM event
  - window selectors now accept best-effort state fields such as `visible`, `fullscreen`, `fullscreen_mode`, `floating`, `sticky`, `minimized`, `hidden`, `mapped`, and `pinned`, so `WaitForWindow`, `WaitForWindowVanish`, `GetWindowList(selector=...)`, hotkey `when:` gates, and runtime-side selector checks can reason about state instead of only title/class/PID
  - `GetIdleMs`, `WaitForIdle`, and `WaitForUserActivity` steps for session-idle-aware macros; current first-party support is explicit rather than magical (`xprintidle` on X11, Mutter IdleMonitor on GNOME Wayland, or external idle daemons bridged into the VHK bus)
  - `vhk doctor` now reports cursor helpers, deeper screenshot fallbacks, AT-SPI bus health, X11/XKB diagnostics, i3 IPC reachability, X11 recovery commands, daemon-backed Wayland helper readiness (`ydotoold` socket reachability plus `dotoold`/`dotoolc` lifecycle), and a Wayland portal/backend capability matrix (Screenshot, ScreenCast, RemoteDesktop, InputCapture, GlobalShortcuts + `portals.conf` routing hints + installed `.portal` manifest inventory); `window_introspection` also includes a best-effort `window_contract_support` shape so planners/validators can distinguish generic title/class matching from richer state/geometry/pointer-window needs
  - Wayland runtime auto-selection now consumes that same truth too: it avoids auto-picking `dotoolc`, `ydotool`, or `wtype` when daemon/socket/protocol absence has already been explicitly proven, while still staying pragmatic when probe state is genuinely unknown
- `vhk validate` can now compare a project against the current session capability matrix, so authors get early warnings when a project needs hotkeys, text injection, pointer injection, screen capture, or window introspection that the current desktop likely cannot provide cleanly; window-heavy projects also get a second-pass “window contract” warning when they depend on stateful selectors, geometry, pointer-window semantics, or WM event kinds that the current backend cannot honestly guarantee
- `vhk lint-project` now reuses that same capability language, so project advice covers both recorder hygiene and session fit in one place; it also surfaces route-drift advice when a macro obviously wants a text tier, remapper lane, watcher service, or explicit helper boundary instead of quietly staying runner-owned, and now emits project-level promotion-gate warnings/reviews when the repo is drifting toward Linux-native claims that its current staged surfaces do not yet support honestly; it also emits `PROMOTION_EVIDENCE_MISSING` / `PROMOTION_EVIDENCE_PARTIAL` when the proof artifacts those surfaces/gates depend on are not yet checked into the project
- `vhk plan-project` now summarizes project shape, macro archetypes, trigger surfaces, recorder smells, Linux-native strategy recommendations, explicit stack profiles/runtime seams/ecosystem lessons, per-macro `macro_route_profiles` that make route ownership explicit (text tier vs remapper vs watcher service vs launcher vs full runner), matching `macro_export_candidates` that point to concrete Linux-native shipping surfaces/tool families, an aggregated `route_portfolio` that shows where the project is actually accumulating macro ownership, an explicit `planner_target_claims` lane with recommended support levels, and a compact `planner_claim_witness` contract so wrong-host proof drift shows up directly in core planner JSON instead of waiting for later pack overlays; it now also emits an `input_lane_dossier` that turns text bursts, daemon-backed repeated playback, permissioned portal input, and X11-native replay into one workload-oriented Linux review surface instead of scattering those truths across helper names. It also carries current `host_truth` and `portal_route_contract` when live checks are available, alongside an `export_promotion_plan` that groups those macro-level candidates into concrete project-level Linux-native promotion work, a new `promotion_input_lane_plan` that says which workload-oriented input lane should actually own each promotion surface, plus a matching `promotion_activation_route_plan` that says which startup/service/session route actually owns wake-up and steady-state lifecycle for that surface, plus a new `promotion_operator_control_plan` that says which status/reload/log loop actually owns day-2 operation for that surface, plus a `promotion_recovery_plan` that says which first-response/rollback/re-entry lane owns failure recovery for that surface, plus a `promotion_verification_plan` that says which smoke/proof loop actually demonstrates that the shipped surface is alive on Linux, plus a `promotion_dispatch_budget_plan` that says which dispatch posture (edge-resident, service-resident, daemon-warm, session-resume, or launch-cold) should actually own first-use and steady-state latency for that surface, staged `promotion_waves` that sequence that work into explicit shipping waves, a new `promotion_readiness` surface that says which export lanes are actually ready versus needing compositor/session review, explicit `promotion_gates` that translate those surfaces into claim/release gates, a concrete `promotion_backlog` that turns those surfaces and gates into queued Linux-native tasks, a new `promotion_evidence` layer that names the proof artifacts each surface/gate should have checked into the repo before it is treated as release-proof, the concrete artifacts/services/configs a project should generate, the deployable Linux surfaces those artifacts roll up into, the concrete setup recipes operators should follow to install/review them, explicit host-side requirements for services, permissions, and portal routing, a dedicated `window_contract` summary for stateful selectors / geometry / pointer-window dependence, and a `performance_profile` that surfaces capture/OCR/polling budgets plus dispatch-sensitive macros before they turn into Linux latency folklore
- `vhk init` now consumes that planner language too: new projects can emit `docs/VHK_STARTER_GUIDE.md` and `docs/VHK_STARTER_PLAN.json` so authors start with deployable surfaces, setup recipes, toolchain choices, and reference patterns already visible
- `vhk gen-design-pack` now turns the planner's architecture output into project-level design/runtime handoff artifacts for real projects: `docs/VHK_DESIGN_BRIEF.md`, `docs/VHK_RUNTIME_CONTRACT.md`, and `docs/VHK_DESIGN_PLAN.json`
- `vhk gen-session-fit-pack` now turns the planner + doctor capability language into a host-review handoff for real projects: `docs/VHK_SESSION_FIT.md`, `docs/VHK_SESSION_FIXUPS.md`, `docs/VHK_SESSION_PLAN.json`, and `scripts/vhk_review_session_fit.sh`
- `vhk gen-host-contract-pack` now turns planner host requirements plus live helper/uinput/portal probes into a deployment-contract handoff for real projects: `docs/VHK_HOST_REQUIREMENTS.md`, `docs/VHK_HOST_FIXUPS.md`, `docs/VHK_HOST_PLAN.json`, and `scripts/vhk_review_host_contract.sh`; host packs now also carry a dedicated portal route contract that compares configured `portals.conf`, installed `.portal` backends, and live D-Bus interfaces in one review surface
- `vhk gen-readiness-pack` now layers live service-manager, group-membership, and raw-input checks on top of that host contract so projects can ship `docs/VHK_READINESS_REPORT.md`, `docs/VHK_READINESS_FIXUPS.md`, `docs/VHK_READINESS_PLAN.json`, and `scripts/vhk_refresh_readiness_report.sh`; readiness packs now keep portal route proofs visible too so an operator can compare configured routing, installed backends, and live portal availability during host review
- `vhk gen-activation-pack` now turns planner + readiness output into explicit Linux activation lanes for real projects: `docs/VHK_ACTIVATION_ROUTES.md`, `docs/VHK_ACTIVATION_FIXUPS.md`, `docs/VHK_ACTIVATION_PLAN.json`, and `scripts/vhk_review_activation_routes.sh`
- `vhk gen-capability-audit-pack` now closes a strategy-shaped gap in the repo by turning doctor + host-contract + readiness + activation output into one explicit Linux capability/fallback surface: `docs/VHK_CAPABILITY_AUDIT.md`, `docs/VHK_CAPABILITY_FIXUPS.md`, `docs/VHK_CAPABILITY_AUDIT_PLAN.json`, `scripts/vhk_refresh_capability_audit_pack.sh`, and a reviewable `build/capability-audit/<project>/` handoff with a fresh-snapshot capture script
- `vhk gen-claim-pack` and `vhk audit-target-claims` now keep one more Linux-native boundary visible: whether the current machine is actually a believable witness for the target lane being claimed. Claim guides/audits can now carry compact current-host review (`aligned`, `degraded`, `drifted`, `neutral`, `unknown`) so a sway/Hyprland box is not accidentally treated as verified proof for a GNOME/KDE portal-first release story. Capability-audit output now surfaces that same host-witness posture next to claim status.
- `vhk gen-route-selection-pack` now turns those activation lanes into an explicit shipping/reference-route decision for real projects: `docs/VHK_ROUTE_SELECTION.md`, `docs/VHK_ROUTE_FIXUPS.md`, `docs/VHK_ROUTE_PLAN.json`, and `scripts/vhk_review_route_selection.sh`
- `vhk gen-promotion-pack` now turns project-level promotion advice into reviewable artifacts for real projects: `docs/VHK_PROMOTION_PLAN.md`, `docs/VHK_PROMOTION_FIXUPS.md`, `docs/VHK_PROMOTION_BACKLOG.md`, `docs/VHK_PROMOTION_PLAN.json`, and `scripts/vhk_review_promotion_plan.sh`; promotion output now also carries a compact current-host claim witness review plus a `current-host-proof-gate` so wrong-host evidence drift shows up in promotion docs/backlog/evidence before anyone edits the claim manifest, and now renders the planner's `promotion_input_lane_plan`, `promotion_activation_route_plan`, `promotion_operator_control_plan`, `promotion_recovery_plan`, and `promotion_verification_plan` directly so each shipping surface shows its Linux-native lane ownership, startup/service/session ownership, day-2 operator-control ownership, first-response/rollback ownership, and surface-level smoke/proof ownership instead of leaving lifecycle reality implicit
- `vhk gen-target-route-pack` now compares those route decisions across hypothetical Linux target desktops so release planning does not depend only on the current host: `docs/VHK_TARGET_ROUTE_MATRIX.md`, `docs/VHK_TARGET_ROUTE_FIXUPS.md`, `docs/VHK_TARGET_ROUTE_PLAN.json`, and `scripts/vhk_compare_target_routes.sh`
- `vhk gen-release-lane-pack` now turns those cross-desktop route comparisons into ship-facing release lanes with copy-ready support language: `docs/VHK_RELEASE_LANES.md`, `docs/VHK_RELEASE_SNIPPETS.md`, `docs/VHK_RELEASE_LANE_PLAN.json`, and `scripts/vhk_refresh_release_lanes.sh`
- `vhk gen-operator-pack` now turns that same planner output into deploy/install handoff artifacts for real projects: `docs/VHK_OPERATOR_GUIDE.md`, `docs/VHK_DEPLOYMENT_CHECKLIST.md`, and `docs/VHK_OPERATOR_PLAN.json`
- `vhk gen-verification-pack` now turns the planner's release guidance into reviewable release artifacts for real projects: `docs/VHK_VERIFICATION_GUIDE.md`, `docs/VHK_RELEASE_CHECKLIST.md`, `docs/VHK_VERIFICATION_PLAN.json`, and `scripts/vhk_verify_release.sh`
- `vhk gen-support-pack` now turns those same planning/diagnostic surfaces into triage artifacts for real projects: `docs/VHK_SUPPORT_GUIDE.md`, `docs/VHK_SUPPORT_CHECKLIST.md`, `docs/VHK_SUPPORT_PLAN.json`, and `scripts/vhk_capture_support.sh`; it now also teaches/captures the installed lane's own readiness and runtime-health verdicts before escalating to heavier host packets
- `vhk gen-portability-pack` now turns the planner's cross-desktop comparison into target-review artifacts for real projects: `docs/VHK_PORTABILITY_GUIDE.md`, `docs/VHK_TARGET_ROLLOUT.md`, `docs/VHK_PORTABILITY_PLAN.json`, and `scripts/vhk_review_portability.sh`
- `vhk gen-claim-pack` now turns that portability/release story into explicit support-claim artifacts for real projects: `docs/VHK_CLAIM_GUIDE.md`, `docs/VHK_TARGET_CLAIMS.yaml`, `docs/VHK_CLAIM_AUDIT_PLAN.json`, and `scripts/vhk_audit_claims.sh`
- `vhk audit-target-claims` can now fail overclaims, so a project's desktop/session support matrix becomes reviewable instead of living only in marketing prose or issue comments
- `vhk bundle` now embeds a support snapshot into `vhk_bundle_manifest.json` when it can, and `vhk inspect-bundle` can read that target/claim/proof summary back out of a shared zip without unpacking the whole repo
- `vhk gen-publish-pack` now turns the audited support matrix into audience-facing release/install artifacts: `docs/VHK_PUBLIC_SUPPORT.md`, `docs/VHK_INSTALL_QUICKSTART.md`, `docs/VHK_PUBLISH_PLAN.json`, and `scripts/vhk_refresh_publish_pack.sh`; it also materializes a reviewable publish handoff tree under `build/publish/<bundle-name>/`, and with `--bundle-target-profile <profile>` it can point those publish commands/scripts at one reviewed release-stage lane instead of the whole project tree
- `vhk gen-distribution-pack` now turns that publish handoff into maintainer-facing AppImage/Flatpak skeletons under `build/publish/<bundle-name>/distribution/`, plus `docs/VHK_DISTRIBUTION.md` and `docs/VHK_DISTRIBUTION_PLAN.json`, so packaging metadata stays pinned to the same reviewed bundle story instead of being invented later
- `vhk gen-runtime-pack` now extends that distribution handoff into a reviewable Python runtime lane under `build/publish/<bundle-name>/runtime/`, plus `docs/VHK_RUNTIME.md` and `docs/VHK_RUNTIME_PLAN.json`, so wheelhouse/offline-install work stops being an implicit maintainer side quest
- `vhk gen-runtime-embed-pack` now adds exact-target embedding helpers under `build/publish/<bundle-name>/runtime/embed/`, plus `docs/VHK_RUNTIME_EMBED.md` and `docs/VHK_RUNTIME_EMBED_PLAN.json`, so native/AppImage/Flatpak lanes can bootstrap a venv where it will actually live instead of pretending venv directories are portable
- `vhk gen-native-install-pack` now turns that reviewed bundle/runtime story into a conservative XDG-local app handoff under `build/publish/<bundle-name>/native/`, plus `docs/VHK_NATIVE_INSTALL.md` and `docs/VHK_NATIVE_INSTALL_PLAN.json`, so maintainers can assemble/install one reversible native app tree before claiming package or helper-daemon polish; the installed launcher now resolves through the installed symlink correctly, materializes the reviewed bundle into XDG cache, tracks launcher state under XDG state, opens the project palette by default, can refresh desktop quick actions from pinned/recent entries instead of staying frozen at generation time, and now carries current host truth plus portal-route contract hints forward so install docs keep configured-vs-installed-vs-live Wayland reality visible; it now also computes a target-fit contract so the native lane can compare the current host against one declared flagship release lane instead of only describing the local machine, and its installed status bridge now preserves both session-readiness and runtime-health verdicts for the owned lane
- `vhk gen-service-compose-pack` now turns that native lane into an explicit session-service handoff under `build/publish/<bundle-name>/service/`, plus `docs/VHK_SERVICE_COMPOSE.md`, `docs/VHK_SESSION_ACTIVATION.md`, `docs/VHK_SESSION_TARGETS.md`, `docs/VHK_STARTUP_HANDOFF.md`, and `docs/VHK_SERVICE_COMPOSE_PLAN.json`, so user units, environment.d exports, activation-sync helpers, bundle-state runners, and XDG autostart bridges stop living only in shell history; service-compose output now also keeps current host truth and portal-route contract evidence visible where operators actually stage long-lived session services, and now ships explicit startup-handoff guidance/probes so one primary startup owner is chosen by default instead of silently installing duplicate startup hooks for the same lane
- `vhk gen-host-rehearsal-pack` now turns that reviewed native/service lane into one operable proving path under `build/publish/<bundle-name>/rehearsal/`, plus `docs/VHK_HOST_REHEARSAL.md` and `docs/VHK_HOST_REHEARSAL_PLAN.json`, so install/status/log/uninstall flows and desktop-entry checks stop living only in maintainer shell notes; rehearsal docs and JSON now also keep current host truth plus portal-route contract evidence visible where operators validate the actually installed lane, and now add a target-fit contract so rehearsal can say how the current host matches or drifts from the flagship release lane
- `vhk gen-host-dossier-pack` now turns that rehearsed installed lane into one shareable XDG-state support packet under `build/publish/<bundle-name>/dossier/`, plus `docs/VHK_HOST_DOSSIER.md` and `docs/VHK_HOST_DOSSIER_PLAN.json`, so launcher status, rehearsal output, session facts, and best-effort systemd visibility can be archived together instead of pasted from terminals; it now also emits a share-safe redaction lane (`redact_host_dossier.sh` + `archive_share_dossier.sh`) with a redaction report so external handoff does not start from raw paths/logs by default, and the dossier docs now keep the same compact host truth plus portal-route contract visible instead of flattening support packets back into raw collection prose; dossier output now also carries the flagship target-fit contract so support packets keep the intended Linux lane visible alongside the observed host state
- `vhk materialize-bundle <bundle.zip> <out_dir>` now safely extracts a verified VHK bundle into one target directory, which gives release, native-install, and session-service flows a shared reviewed-payload handoff instead of ad-hoc unzip folklore
- `vhk gen-trigger-pack` now turns the planner's scattered remapper/WM export advice into a self-contained trigger-layer bundle under `build/trigger_pack/`, with generated configs for i3/sway/Hyprland, sxhkd, keyd, Kanata, KMonad, xremap, and a reviewable GlobalShortcuts portal catalog plus `docs/VHK_TRIGGER_SURFACES.md`, `docs/VHK_TRIGGER_MATRIX.md`, `docs/VHK_TRIGGER_PACK.json`, and `scripts/vhk_refresh_trigger_pack.sh`
- `vhk gen-portal-shortcuts-spec` now emits a reviewable GlobalShortcuts action catalog (stable shortcut ids, preferred freedesktop triggers, and forwarded bus payloads), `vhk portal-hotkeys --catalog ...` can consume that file directly, `--assignment-report ...` can capture the portal's requested-vs-assigned trigger ledger, `--assignment-history` can persist those ledgers under XDG state as `latest/` plus timestamped history snapshots, `vhk portal-assignment-history` can browse and filter that audit lane by drift/time/changed shortcut, `vhk prune-portal-assignment-history` can trim older snapshots by count or age, `vhk export-portal-assignment-history` can now render either a shareable Markdown summary or a single-file HTML handoff from that same XDG-state history lane, `vhk gen-portal-assignment-presets` can generate reusable review/export/prune filter bundles for that audit lane (and optionally a local override template via `--local-out`), the history/export/prune commands can merge multiple `--preset-file` layers with later files overriding earlier ones, `vhk inspect-portal-assignment-preset` can show the merged filters plus winning-layer provenance for a named preset, and the history/export/prune JSON + HTML/Markdown handoffs now carry that preset-resolution provenance too; `vhk diff-portal-assignment-report <old> <new>` can diff those ledgers across sessions so requested/reviewed shortcuts can be audited against what the desktop actually assigned over time
- the portal lane now also accepts more common punctuation-oriented shortcut keys (`[`, `]`, `;`, etc.) by translating them to shortcuts-spec/xkbcommon identifiers, and `vhk lint-project` now warns before export when a binding would be skipped from the GlobalShortcuts catalog or when a binding's `when:` selector will remain runtime-only inside VHK after the portal fires
  - docs: `docs/PORTAL_SHORTCUTS.md`
- `vhk gen-setup-pack` now makes planner `setup_recipes` executable: it generates `docs/VHK_SETUP_GUIDE.md`, `docs/VHK_SETUP_MATRIX.md`, `docs/VHK_SETUP_PLAN.json`, runnable `scripts/vhk_apply_setup_recipes.sh` / `scripts/vhk_verify_setup_recipes.sh`, and a distro-oriented `scripts/vhk_install_toolchain_packages.sh` bootstrap helper so Linux setup guidance stops living only in JSON and prose; setup docs now also surface observed deployment truth from live host checks so maintainers see portal/helper reality before they run the recipes
- exported launcher scripts now expose `--about` / `--support-json`, desktop entries now carry `X-VHK-Support-*` metadata, and self-contained WM bundles now embed public support/install docs plus `docs/VHK_BUNDLE_SUPPORT.json`
- those outward-facing surfaces now also ingest release-lane posture directly, so launcher/about output, desktop-entry metadata, WM bundle support JSON, and `vhk_bundle_manifest.json` can name a flagship desktop lane instead of flattening everything back into generic Linux support prose
- `vhk gen-release-deploy-pack` now turns release lanes into lane-native deployment output: `docs/VHK_RELEASE_DEPLOYMENT.md`, `docs/VHK_RELEASE_INSTALL_SNIPPETS.md`, `docs/VHK_RELEASE_DEPLOY_PLAN.json`, and `scripts/vhk_refresh_release_deploy.sh`; release deployment output now also carries host truth and portal-route contract evidence forward so per-lane install claims stay tied to the current Linux host reality, and now computes a flagship target-fit contract so the deploy docs can compare the current machine against the intended release lane
- support/about JSON, desktop-entry metadata, and bundle manifests now also carry flagship deploy style so the exported artifact remembers whether it expects desktop autostart, WM bundles, or remapper/helper services
- `vhk gen-release-stage-pack` now turns those lane-native deploy plans into project-local staged payload trees under `build/release-stage/`, plus `docs/VHK_RELEASE_STAGE.md`, `docs/VHK_RELEASE_STAGE_MATRIX.md`, `docs/VHK_RELEASE_STAGE_PLAN.json`, and `scripts/vhk_refresh_release_stage.sh` so maintainers can hand someone a lane-specific ship folder instead of only prose; staged lane docs/JSON now also keep current host truth, host requirements, and portal-route contract evidence attached so shipping review does not regress to static packaging copy, and they now surface a lane target-fit contract so every staged lane can say how the current host aligns or drifts from that intended desktop profile
- `vhk bundle-stage` can now zip one staged release lane directly, so the reviewed stage tree (`README.md` + install/verify/assemble scripts + `payload/`) becomes a shareable artifact instead of staying trapped in `build/release-stage/`
- Playback profiles + more robust text injection:
  - `settings.runner_profile: normal|turbo`
  - turbo mode reduces incidental playback delays and can prefer clipboard-paste for larger printable text
  - `TypeText` now supports `backend=auto|native|clipboard|xvkbd`, optional clipboard preservation, terminal-friendly paste shortcuts like `ctrl+shift+v`, and an authoring-time optimizer lane that can split structured form text into typed `Tab`/`Enter` boundaries plus clipboard-paste field chunks
- Thin wrappers over common desktop CLI tools (best-effort):
  - screenshots: X11 (`maim`, `scrot`, ImageMagick `import`, or `xwd`+ImageMagick), Wayland (`grim`)
    - Wayland fallback: `spectacle` (KDE) or `gnome-screenshot` (GNOME) for full-screen capture when `grim` isn't available
  - region selection: X11 (`slop`), Wayland (`slurp`)
  - input: X11 (`xdotool`, `xvkbd`), Wayland keyboard (`wtype` / `dotool` / `ydotool`), Wayland pointer (`ydotool` / `dotool`)
  - clipboard: X11 (`xclip`/`xsel`), Wayland (`wl-copy`/`wl-paste`)
  - notifications (`notify-send`/`dunstify`)
  - prompts/dialogs (`zenity`, `yad`, `kdialog`, with console fallback)
    - `PromptForm` prefers YAD's native multi-field form dialog when available, then falls back to sequential prompts on other desktops
    - `ChooseFromList` now prefers launcher-style pickers on the active session (`rofi` / `dmenu` on X11, `fuzzel` / `tofi` / `wofi` on Wayland) before dropping to dialog or console fallbacks
    - `vhk palette` builds on the same chooser stack to expose a real project-level macro palette, with recent-run ordering plus macro metadata, saved parameter presets (`macro@preset`), optional preset-attached prompt forms, and saved prompt-profile actions
    - `vhk export-desktop-entry` can turn that project/preset/profile surface into a `.desktop` launcher plus optional quick actions for Linux menus, taskbars, and drun-style launchers
  - optional event helpers: `clipnotify` (clipboard on X11), `inotifywait` (filesystem waits)
  - KDE Wayland helper: `kdotool` (improves `vhk window-spy` + `vhk cursorpos` on KWin)
- Project-level **clipboard watchers** inspired by CopyQ/clipmenu-style clipboard rules
- Project-level **file watchers** for filesystem-triggered macros (export/drop-folder/download flows), using `inotifywait` when available with a polling fallback plus optional `quiet_ms` burst coalescing for noisy producers
- Event-driven synchronization via `WaitForBusEvent`, so one-shot macros can pause on a local IPC signal from helper scripts, WM binds, or service glue instead of adding more sleeps/poll loops.
- Honest idle-aware automation via `GetIdleMs` / `WaitForIdle` / `WaitForUserActivity`, with a deliberate split between direct probes (`xprintidle`, Mutter IdleMonitor) and compositor-specific idle daemons such as `swayidle`/`xidlehook` that can emit into VHK's bus.
- Linux-native service/runtime glue via `GetSystemdUnitState` / `WaitForSystemdUnitState`, keeping macro authoring close to `systemctl show` and `ActiveState` / `SubState` instead of forcing raw D-Bus or brittle shell parsing into every workflow.
- Project-level **hotstrings** (text expansion triggers) exportable to Espanso
  - define `hotstrings:` in `project.yaml`
  - generate a match file with `vhk gen-espanso`
  - generate a package dir with `vhk gen-espanso --package-dir` for scoped app/title configs, composite precedence configs, and a local `pack.json`/README handoff
  - use `vhk run --print-return` to output expansions on stdout

  - regex-filter clipboard changes and trigger macros
  - metadata-only watcher JSONL logs for explainability/debugging
  - `list-watchers` + `watch-clipboard` / `watch-file` CLI commands
- A JSONL **timeline event log** for runs + a simple panic switch.
- `vhk report` now turns those logs into a practical optimization loop: slowest-step summaries, wait timing, failing-step review, and heuristic advice for common Linux automation bottlenecks (delay-heavy runs, vision-heavy waits, backend/capability mismatches, and costly text injection).
- `vhk plan-project`, `vhk gen-promotion-pack`, `vhk gen-capability-audit-pack`, and `vhk gen-operator-pack` now also emit **promotion performance envelopes**, so every promoted surface names its latency class, hot path, batching strategy, related planner hotspots, and the Linux-native lane that should own throughput or low-latency behavior instead of leaving performance intent implicit.
- those same planner and pack surfaces now also emit **promotion dispatch budgets**, so cold-start versus warm-path ownership is explicit per promoted surface instead of being buried inside a general “startup route” story.
- Cross-step **retry / continue-on-error** controls (Robot-Framework-ish).
- Shareable bundles with integrity manifests plus an opt-in **deterministic bundle** mode (`--deterministic`, `SOURCE_DATE_EPOCH`) for reproducible packaging. Bundles now also carry best-effort support metadata (target claims, recommended levels, audit status, and proof-artifact presence) when the project can be planned.
- Better **failure diagnostics**:
  - `wait_attempt` events during polling waits
  - reuses the *last actual capture* for screenshot-on-error
  - writes an `error_<macro>_<step>.json` context file
  - writes visual diff images for failed visual compares/timeouts
- A CLI:
  - `vhk run <project_dir> <macro_name>` (supports `--preset`, `--preset-prompts/--no-preset-prompts`, `--prompt-profile`, `--save-prompt-profile`, `--step`, and `--dry-run`)
  - `vhk gen-i3-config <project_dir>`
  - `vhk gen-hyprland-config <project_dir>`
  - `vhk gen-wm-config <project_dir> --wm auto|i3|sway|hyprland`
    - optional: `--mode-enter Mod4+R` to generate an i3/sway **mode** or Hyprland **submap** (leader-key keymap)
  - `vhk gen-kanata-config <project_dir>` (Kanata hotkeys export)
  - `vhk gen-keyd-config <project_dir>` (keyd hotkeys export)
  - `vhk gen-kmonad-config <project_dir>` (KMonad macro-layer export)
  - `vhk gen-xremap-config <project_dir>` (xremap app-aware remap export; now preserves `title_regex` / `app_id_regex` as xremap-native `/regex/` filters when possible)
  - `vhk gen-sxhkd-config <project_dir>` (sxhkd hotkeys export; X11)
  - `vhk gen-udev-uinput` (starter udev rules for /dev/uinput; see docs/UINPUT.md)
  - `vhk gen-ydotoold-service` (systemd user unit for ydotoold; see docs/INPUT_BACKENDS.md)
  - `vhk gen-dotoold-service` (systemd user unit for dotoold; see docs/INPUT_BACKENDS.md)
  - `vhk gen-espanso <project_dir>` (hotstrings export)
  - `vhk gen-dragonfly-pack <project_dir>` (Dragonfly voice adapter export)
  - `vhk gen-talon-pack <project_dir>` (Talon voice adapter export)
  - `vhk gen-autokey-pack <project_dir>` (AutoKey/X11 trigger adapter export)
  - `vhk bundle <project_dir> <out.zip>`
  - `vhk inspect-bundle <bundle.zip>` (review embedded bundle metadata, including target-claim/proof snapshots when present)
  - exported launcher/desktop/WM entrypoints now inherit the same publish/support posture so recipients can review support claims from the entrypoint itself
  - optional: `--deterministic` and `--source-date-epoch` for best-effort reproducible zip metadata
  - `vhk list-macros <project_dir>`
  - `vhk palette <project_dir>` (launcher-friendly macro/preset picker; recent-first by default, `--json` for external tools, `--no-run` to emit the selected `macro`, `macro@preset`, or `macro@preset#profile`, `--entry-id` to resolve one stable palette action directly, palette JSON now includes `icon` + `search_terms`, preset prompt overlays when applicable, and saved prompt profiles surfaced as palette actions plus `--prompt-profile` / `--save-prompt-profile`)
  - `vhk list-prompt-profiles <project_dir>` / `vhk edit-prompt-profile <project_dir> <profile_key> <name>` / `vhk copy-prompt-profile <project_dir> <profile_key> <source> <target>` / `vhk rename-prompt-profile <project_dir> <profile_key> <old> <new>` / `vhk delete-prompt-profile <project_dir> <profile_key> <name>`
  - `vhk export-desktop-entry <project_dir> [output.desktop]` (`--install` writes to XDG application menus; exported quick actions can point at macros, presets, and saved prompt-profile workflows)
  - `vhk export-launcher-script <project_dir> [output]` (writes a picker-native launcher wrapper; supports `--install`, `--launcher-backend`, `--profile-management-actions`, and now doubles as a rofi script-mode provider with icon/meta/info rows)
  - `vhk export-rofi-mode <project_dir> [output]` (writes a rofi custom-mode helper and prints the exact `rofi -show ... -modes ...` command needed to expose the project palette)
  - `vhk export-wm-bindings <project_dir> [output.conf] --wm i3|sway|hyprland` (prints or writes ready-to-paste keybinding snippets for rofi-mode, launcher-script, or direct palette-command flows; now auto-quotes i3/sway launcher commands when they contain WM command separators)
  - `vhk export-wm-launcher-mode <project_dir> [output.conf] --wm i3|sway|hyprland --mode-enter ...` (exports an i3/sway mode or Hyprland submap that can open the project launcher and directly run the most relevant palette entries)
  - `vhk export-wm-include <project_dir> [output.conf] --wm i3|sway|hyprland --kind binding|launcher-mode` (writes WM snippets into a conventional XDG config include/source tree and prints the exact parent config line to add once)
  - `vhk export-wm-bundle <project_dir> [bundle_dir] --wm i3|sway|hyprland --kind binding|launcher-mode` (exports the launcher helper, WM snippet, bootstrap note, and reload hint together; `--install` writes into XDG bin/config targets instead)
- Prompt answers can now be remembered safely per project: `PromptForm` steps and preset overlays reuse last-used values by default, support named prompt profiles from the CLI and palette, can be inspected/edited/copied/renamed/deleted with the prompt-profile commands, and never persist password fields unless the project shells out and handles that itself.
- Launcher integration is now a first-class product surface too: `vhk export-desktop-entry` can emit a `.desktop` launcher for the project palette and optionally include quick actions for the most relevant macros/presets/saved-profile workflows. Macro and preset `icon:` metadata now flows into palette rows and desktop quick-action icons too.
- VHK can also export a picker-native launcher wrapper with `vhk export-launcher-script`, so the same project palette can plug into script-driven Linux launchers as well as XDG app menus. The exported script auto-detects rofi script mode and emits icon/meta/info row metadata instead of forcing every launcher path through a generic chooser.
- VHK can now export a first-class rofi integration with `vhk export-rofi-mode`, which writes the launcher script and prints the exact `rofi -show ... -modes ...` command needed to expose the project as a rofi custom mode.
- VHK can now also export WM-ready binding snippets with `vhk export-wm-bindings`, so i3, sway, and Hyprland users can wire project launchers into real session keybindings instead of hand-assembling launcher commands. i3/sway exports now quote launcher commands automatically when they contain `,` or `;`, which matters for rofi `-modes ...` command lines.
- VHK can now export a transient WM launcher layer with `vhk export-wm-launcher-mode`, turning the project palette into an i3/sway mode or Hyprland submap instead of forcing users to choose between one global bind and a full launcher UI.
- VHK can now also export include-ready WM snippets with `vhk export-wm-include`, so i3/sway/Hyprland users can install VHK launcher fragments into an XDG config subtree and get the exact `include` / `source =` line to add once to the parent config.
- VHK can now export a complete WM integration bundle with `vhk export-wm-bundle`, so users can generate or install the launcher helper and the WM snippet together instead of manually stitching together `export-rofi-mode` / `export-launcher-script` and `export-wm-include`.
  - `vhk list-watchers <project_dir>`
  - `vhk watch-clipboard <project_dir> <watcher_name>`
  - `vhk watch-file <project_dir> <watcher_name>`
  - `vhk watch-window <project_dir> <watcher_name>`
  - `vhk select-region` (slop on X11, slurp on Wayland)
  - `vhk portal-screenshot` (XDG Desktop Portal screenshot; best-effort, usually interactive)
  - `vhk portal-pick-color` (XDG Desktop Portal color picker; best-effort)
  - `vhk pick-color` (samples under cursor or at --x/--y; Wayland falls back to portal picker)
  - `vhk capture-needle <project_dir> <name>`
  - `vhk capture-baseline <project_dir> <name>`
  - `vhk needle-info <needle.png>`
  - `vhk preview-needle <needle.png>` (debug: best match + optional annotated overlay; see docs/PREVIEW_NEEDLE.md)
  - `vhk doctor` / `vhk doctor --json`
    - reports optional event helpers like `clipnotify` and `inotifywait`
    - reports dialog helpers like `zenity`, `yad`, `kdialog`, and `dialog`
    - reports chooser helpers like `rofi`, `dmenu`, `wofi`, `fuzzel`, and `tofi`
    - now probes AT-SPI bus health via `busctl` when available, surfaces `NO_AT_BRIDGE` / `GTK_MODULES`, checks X11 `XTEST`/`RECORD` availability via `xdpyinfo`, reports active XKB layout/options via `setxkbmap`, verifies i3/sway IPC reachability, runs a real screenshot self-test, discovers installed Tesseract language packs, estimates monitor DPI/scale from `xrandr`, decodes Wayland portal interfaces (`Screenshot`, `ScreenCast`, `RemoteDesktop`, `InputCapture`, `GlobalShortcuts`), inspects `portals.conf` routing, emits a capability matrix, inventories installed `.portal` backend manifests (`DBusName` / `Interfaces` / `UseIn`) so `portals.conf` routing can be cross-checked against what is actually installed, and shows an emergency X11 `x11vnc -clear_keys` recovery command when possible
  - `vhk report <run.jsonl>` (summarize a run log; use `--project . --latest` to pick newest)
  - `vhk history <project_dir>` (recent run table; filter with `--status ok|fail`; export with `--csv`)
  - `vhk trace <run.jsonl>` (export a run log to Chrome/Perfetto trace JSON; see docs/TRACE_EXPORT.md)
  - `vhk render <project_dir> <macro>` (script view)
  - `vhk init <project_dir>` (create a new project skeleton: `project.yaml` + `macros/` + `assets/` + optional starter guide/plan artifacts under `docs/`)
  - `vhk gen-design-pack <project_dir>` (generate design/runtime architecture docs + machine-readable plan under `docs/`)
  - `vhk gen-session-fit-pack <project_dir>` (generate host/session fit docs + fixup plan plus `scripts/vhk_review_session_fit.sh`)
  - `vhk gen-host-contract-pack <project_dir>` (generate host-side requirements/fixups docs + plan plus `scripts/vhk_review_host_contract.sh`)
  - `vhk gen-readiness-pack <project_dir>` (generate live readiness docs/plan plus `scripts/vhk_refresh_readiness_report.sh`)
  - `vhk gen-activation-pack <project_dir>` (generate Linux activation-route docs/plan plus `scripts/vhk_review_activation_routes.sh`)
  - `vhk gen-capability-audit-pack <project_dir>` (generate capability/fallback audit docs/plan plus `scripts/vhk_refresh_capability_audit_pack.sh` and a `build/capability-audit/...` handoff)
  - `vhk gen-route-selection-pack <project_dir>` (generate reference-route selection docs/plan plus `scripts/vhk_review_route_selection.sh`)
  - `vhk gen-promotion-pack <project_dir>` (generate staged export-promotion docs/plan, including `docs/VHK_PROMOTION_BACKLOG.md`, plus `scripts/vhk_review_promotion_plan.sh`; now also surfaces current-host claim witness posture, a wrong-host-proof gate, and a shipping-lane map showing which Linux-native input lane should actually own each promotion surface when live checks are available)
  - `vhk gen-target-route-pack <project_dir>` (compare route choices across hypothetical target desktops plus `scripts/vhk_compare_target_routes.sh`)
  - `vhk gen-release-lane-pack <project_dir>` (turn target-route comparisons into ship-facing release lanes/snippets plus `scripts/vhk_refresh_release_lanes.sh`)
  - `vhk gen-release-deploy-pack <project_dir>` (turn release lanes into lane-native install/autostart docs, generated artifact subsets, current deployment-truth summaries, flagship target-fit analysis, and `scripts/vhk_refresh_release_deploy.sh`)
  - `vhk gen-release-stage-pack <project_dir>` (materialize per-lane release-stage trees under `build/release-stage/` plus `docs/VHK_RELEASE_STAGE*.md`, per-lane target-fit analysis, and `scripts/vhk_refresh_release_stage.sh`)
  - `vhk bundle-stage <project_dir> <out.zip> --target-profile <profile>` (zip one materialized release-stage lane directly from `build/release-stage/<profile>/`)
  - `vhk gen-operator-pack <project_dir>` (generate operator-facing deployment docs/checklists + machine-readable plan under `docs/`)
  - `vhk gen-verification-pack <project_dir>` (generate release verification docs/checklists/plan plus `scripts/vhk_verify_release.sh`)
  - `vhk gen-support-pack <project_dir>` (generate support/triage docs/checklists/plan plus `scripts/vhk_capture_support.sh`)
  - `vhk gen-portability-pack <project_dir>` (generate cross-desktop portability docs/rollout plan plus `scripts/vhk_review_portability.sh`)
  - `vhk gen-claim-pack <project_dir>` (generate support-claim docs/manifest/plan plus `scripts/vhk_audit_claims.sh`)
  - `vhk gen-publish-pack <project_dir>` (generate public support/install docs/plan plus `scripts/vhk_refresh_publish_pack.sh`, and materialize `build/publish/<bundle-name>/`; add `--bundle-target-profile <profile>` to ship one reviewed stage lane via `bundle-stage`)
  - `vhk gen-distribution-pack <project_dir>` (generate `docs/VHK_DISTRIBUTION.md`, `docs/VHK_DISTRIBUTION_PLAN.json`, `scripts/vhk_refresh_distribution_pack.sh`, and AppImage/Flatpak skeletons under `build/publish/<bundle-name>/distribution/`)
  - `vhk gen-runtime-pack <project_dir>` (generate `docs/VHK_RUNTIME.md`, `docs/VHK_RUNTIME_PLAN.json`, `scripts/vhk_refresh_runtime_pack.sh`, and a reviewable wheelhouse/offline-install handoff under `build/publish/<bundle-name>/runtime/`)
  - `vhk gen-runtime-embed-pack <project_dir>` (generate `docs/VHK_RUNTIME_EMBED.md`, `docs/VHK_RUNTIME_EMBED_PLAN.json`, `scripts/vhk_refresh_runtime_embed_pack.sh`, and exact-target native/AppImage/Flatpak embed helpers under `build/publish/<bundle-name>/runtime/embed/`)
  - `vhk gen-native-install-pack <project_dir>` (generate `docs/VHK_NATIVE_INSTALL.md`, `docs/VHK_NATIVE_INSTALL_PLAN.json`, `scripts/vhk_refresh_native_install_pack.sh`, and a conservative XDG-local native app/install handoff under `build/publish/<bundle-name>/native/`; the shipped launcher now resolves its installed symlink correctly, caches a materialized reviewed bundle, tracks launcher state under XDG state, can refresh desktop quick actions from pinned/recent entries, can emit/open a live installed-lane status report with service/session hints, and now carries current host/portal-route truth plus a target-fit contract into the install handoff)
  - `vhk gen-service-compose-pack <project_dir>` (generate `docs/VHK_SERVICE_COMPOSE.md`, `docs/VHK_SESSION_ACTIVATION.md`, `docs/VHK_SERVICE_COMPOSE_PLAN.json`, `scripts/vhk_refresh_service_compose_pack.sh`, and a session-service handoff under `build/publish/<bundle-name>/service/` that now includes activation-sync helpers, bundle-state runner helpers, and current host/portal-route truth)
  - `vhk gen-host-rehearsal-pack <project_dir>` (generate `docs/VHK_HOST_REHEARSAL.md`, `docs/VHK_HOST_REHEARSAL_PLAN.json`, `scripts/vhk_refresh_host_rehearsal_pack.sh`, and an end-to-end reviewed-lane rehearsal handoff under `build/publish/<bundle-name>/rehearsal/`, now including `report_reviewed_lane.sh` so the installed launcher’s live status JSON/Markdown gets bridged into one host-rehearsal report and accompanied by target-fit analysis against the flagship release lane)
  - `vhk gen-host-dossier-pack <project_dir>` (generate `docs/VHK_HOST_DOSSIER.md`, `docs/VHK_HOST_DOSSIER_PLAN.json`, `scripts/vhk_refresh_host_dossier_pack.sh`, and a shareable installed-host dossier handoff under `build/publish/<bundle-name>/dossier/`, including collection/redaction/archive/smoke scripts plus a share-safe dossier report for launcher state, rehearsal output, session facts, best-effort systemd visibility, and the flagship target-fit contract)
  - `vhk materialize-bundle <bundle.zip> <out_dir>` (verify and safely extract one reviewed VHK bundle into a target directory; machine-readable metadata available with `--json`)
  - `vhk gen-trigger-pack <project_dir>` (generate a self-contained trigger/remapper export pack under `build/trigger_pack/` by default)
  - `vhk gen-setup-pack <project_dir>` (generate setup/install docs + planner-backed apply/verify scripts plus a distro-oriented package bootstrap helper from `setup_recipes` and `toolchain_choices`, now with observed deployment-truth summaries from live host checks)
  - `vhk audit-target-claims <project_dir>` (audit `docs/VHK_TARGET_CLAIMS.yaml` against the current planner output)
  - `vhk new-macro <project_dir> <name>` (add a new macro file under `macros/`, optionally registering it)
  - `vhk schema --kind project|macro|...` (print JSON schema for editor validation/autocomplete)
  - `vhk schemas <project_dir>` (write `schemas/*.schema.json` + optional `.vscode/settings.json`)
  - `vhk validate <project_dir>` (static project checker: references + expressions + required visual assets; by default also warns about current-session capability mismatches, disable with `--no-session-check`)
  - `vhk lint <macro.yaml>` (advisor: flags hard sleeps + coordinate clicks; suggests waits/selectors)
  - `vhk lint-project <project_dir>` (bulk lint every macro under macros/; by default also reports current-session capability mismatches plus voice-export phrase collisions, disable session checks with `--no-session-check`)
  - `vhk scaffold <macro.yaml>` (non-breaking TODO scaffolds: inserts disabled WaitForImage/ClickNeedle stubs + comments)
    - review mode: `--check`, `--diff`
  - `vhk scaffold-project <project_dir>` (bulk scaffold every macro under macros/)
    - review mode: `--check`, `--diff`
  - `vhk pick-window` (prints i3 criteria for clicked window)
    - now captures `WM_WINDOW_ROLE`, suggests both a stable class/instance(/role) selector and an exact selector with title, and previews how many current i3 windows match each suggestion when IPC is reachable
  - `vhk window-spy` (active-window inspector for i3/sway/Hyprland/X11; Wayland-friendly)
  - `vhk window-at-cursor` (best-effort pointer-window inspector for i3/sway/Hyprland/X11/KDE Wayland)
  - `vhk window-list` (best-effort open-window enumerator for i3/sway/Hyprland/X11/KDE Wayland; now shows PID/process context in text mode too)
  - `vhk record-selectors` (records focus/title changes and suggests a `when:` selector)
  - `vhk record-x11` (baseline lexical recorder on X11 via `xinput test-xi2 --root`; supports `--smoothing precise|normal|compact`, distance-aware move thinning, and can write into a project with `--project`)
  - `vhk optimize <macro.yaml>` (post-process recordings: merge delays, squash mouse moves, compress key chords; optional TypeText collapsing, including shifted uppercase/punctuation runs such as `Hello!`, edited text runs with Backspace/Delete plus simple Left/Right/Home/End cursor corrections, whole-word cleanup via `Ctrl+Backspace` / `Ctrl+Delete`, selection-to-boundary replacements such as `Shift+End`, short shift-selection replacement patterns such as `hellp` + `Shift+Left` + `o`, Enter/Tab-rich snippets, an opt-in long-text promotion lane that rewrites paste-friendly literal `TypeText` blocks to `backend=clipboard`, and an opt-in hybrid structured-text lane that splits Tab/Enter-separated text into explicit `Key(tab|enter)` boundaries plus clipboard-paste chunks for the large literal fields)
    - review mode: `--check` (CI-friendly), `--diff` (unified diff)
  - `vhk optimize-project <project_dir>` (bulk optimize every macro under macros/)
    - review mode: `--check`, `--diff`
  - `vhk retime <macro.yaml>` (scale Delay/RandomWait and other delay-like knobs to speed up / slow down recordings)
  - `vhk retime-project <project_dir>` (bulk retime every macro under macros/)
  - `vhk cursorpos` (best-effort global cursor position; Wayland-friendly helpers)
  - `vhk cursor-step` (prints a macro step snippet at the current cursor position)
  - `vhk build-rule`
    - generates i3 `for_window` / `assign` snippets, devilspie2 Lua fallbacks, and wmctrl apply-once commands from selector fields or a clicked window
    - recommends `assign` for pure workspace placement, because i3 treats mapping-time assignment and runtime `for_window` rules differently
  - `vhk gen-systemd <project_dir> <macro>` (service+timer generator)
  - `vhk panic` / `vhk unpanic`

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# Run the example project
vhk run examples/hello_project hello

# Generate i3 keybindings from project.yaml
vhk gen-i3-config examples/hello_project

# Capture a needle (interactive selection)
# Tip: use --delay-ms if you want time to switch focus / hover before selecting.
vhk capture-needle examples/hello_project ok_button --out-dir assets/needles --delay-ms 3000

# Create a shareable bundle
vhk bundle examples/hello_project /tmp/hello_project.zip
```

## Project layout

```
project/
  project.yaml
  macros/
    <macro>.yaml
  assets/
    ... (images / metadata)
  data/
  logs/
```

See `docs/PROJECT_FORMAT.md`, `docs/CONTROL_FLOW.md`, and `docs/TEXT_INPUT_AND_TURBO.md`.

Named regions of interest (ROI): `docs/NAMED_REGIONS.md`.

Expression language reference: `docs/EXPRESSIONS.md`.

Platform caveats / known issues: `docs/KNOWN_ISSUES.md`.

Performance notes (polling waits, caching): `docs/PERFORMANCE.md`.

New in this revision: planner/claim/promotion/capability-audit flows now support an explicit `--evidence-lane <profile-id>` so maintainers can judge the current machine against one chosen Linux target lane instead of relying only on the default flagship lane or vague local proof.

## License

MIT.


## Recent planner surface

`vhk plan-project` now also emits **promotion authority envelopes**, making user-session, portal-mediated, evdev/uinput, helper-daemon, and launcher ownership explicit per promoted surface.


## New in rev0305: session readiness guards

`vhk gen-service-compose-pack` now treats **live session readiness** as a first-class operational boundary.
Generated session-service handoffs now include `docs/VHK_SESSION_READINESS.md` plus a
`verify_session_readiness.sh` probe, and VHK-owned user units now use an
`ExecCondition=` guard so they can skip startup cleanly when the graphical
session/runtime prerequisites are missing instead of turning wrong-session
launches into restart noise.


## New in rev0306: session readiness evidence in rehearsal and dossier

`vhk gen-host-rehearsal-pack` and `vhk gen-host-dossier-pack` now treat
**session readiness evidence** as first-class operator output. Generated
rehearsal reports and support dossiers now capture the installed
`verify_session_readiness.sh` verdict, its probe output, and a matching
`systemctl --user show` property slice so maintainers can distinguish
wrong-session skips from ordinary user-service failures without digging through
ad-hoc journal history.


## New in rev0307: installed-lane readiness status bridge

`vhk gen-native-install-pack` and `vhk gen-support-pack` now carry **installed-lane
readiness status** into the everyday operator surfaces. The installed launcher’s
`--status-json`/status Markdown now records one readiness verdict (`ready`,
`not_ready`, `unavailable`, or `error`) plus the nearby user-unit state, and the
support pack now teaches/captures that status before asking for a full rehearsal
or dossier packet.


## New in rev0308: installed-lane runtime health verdicts

`vhk gen-native-install-pack` and `vhk gen-support-pack` now also preserve one
**installed-lane runtime-health verdict** alongside session readiness. The
installed launcher’s `--status-json`/status Markdown can now distinguish a
healthy owned lane from `skipped_not_ready`, `degraded_restart_churn`,
`degraded_failed`, `degraded_probe_error`, `degraded_unit_missing`, `stopped`,
`no_owned_service`, or `unavailable`, and the support pack now teaches
maintainers to capture that lighter-weight runtime verdict before escalating to
full host packets.


## New in rev0309: installed-lane startup handoff verdicts

`vhk gen-native-install-pack` and `vhk gen-support-pack` now also preserve one
**installed-lane startup-handoff verdict** so operators can see whether the
reviewed lane currently has one primary startup owner, depends on the XDG
autostart fallback, risks duplicate starts, or lacks a valid startup owner
entirely. The installed launcher’s `--status-json`/status Markdown now carries
`primary_user_unit_owner`, `fallback_autostart_owner`,
`duplicate_start_risk`, `autostart_hidden_no_owner`,
`autostart_tryexec_missing`, `masked_no_owner`, `no_startup_owner`,
`manual_or_external_owner`, or `unavailable`, and the support pack now teaches
maintainers to capture that startup-ownership truth before escalating to a
heavier host packet.


## New in rev0310: installed-lane startup handoff drift

`vhk gen-native-install-pack`, `vhk gen-support-pack`, `vhk gen-host-rehearsal-pack`,
and `vhk gen-host-dossier-pack` now also preserve one **startup-handoff drift**
story for the installed lane. The launcher status bridge now keeps a short local
history of startup-owner snapshots and can say whether ownership is a first
snapshot, stable, changed recently, recovered to a primary user-unit owner,
drifted away from primary ownership, chronically duplicate, chronically missing,
flapping, or unavailable. The support/rehearsal/dossier surfaces now show that
drift summary instead of forcing maintainers to infer owner history from one
live snapshot.


## New in rev0311: installed-lane runtime health drift

`vhk gen-native-install-pack`, `vhk gen-support-pack`, `vhk gen-host-rehearsal-pack`,
and `vhk gen-host-dossier-pack` now also preserve one **runtime-health drift**
story for the installed lane. The launcher status bridge now keeps a short local
history of runtime-health snapshots and can say whether health is a first
snapshot, stable, changed recently, recovered to healthy, drifted away from
healthy, chronically restart-churning, chronically failed, chronically
inactive/missing, flapping, or unavailable. The support/rehearsal/dossier
surfaces now show that drift summary instead of forcing maintainers to infer
longer-term health from one live snapshot or from resettable systemd counters.

## New in rev0312: installed-lane incident signatures

`vhk gen-native-install-pack`, `vhk gen-support-pack`, `vhk gen-host-rehearsal-pack`,
and `vhk gen-host-dossier-pack` now also preserve one **incident-signature**
verdict for the installed lane. The launcher status bridge can classify clean
session skips, generic condition skips, start-limit churn, real service
failures, missing units, and probe/runtime breakage, and it keeps a short user
journal sample when `journalctl --user` is available.


## New in rev0313: installed-lane incident-signature drift

`vhk gen-native-install-pack`, `vhk gen-support-pack`, `vhk gen-host-rehearsal-pack`,
and `vhk gen-host-dossier-pack` now also preserve one **incident-signature drift**
story for the installed lane. The launcher status bridge now keeps a short local
history of incident-signature snapshots and can say whether incidents are a
first snapshot, stable, changed recently, recovered to a quiet lane, drifted
away from a quiet lane, changed skip mode, changed hard-incident mode,
chronically start-limited, chronically failing, chronically missing units,
chronically probe-broken, flapping, or unavailable.

