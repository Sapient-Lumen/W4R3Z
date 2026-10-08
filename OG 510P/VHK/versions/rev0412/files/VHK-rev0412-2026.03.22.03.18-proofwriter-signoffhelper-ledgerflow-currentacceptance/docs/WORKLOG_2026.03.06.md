# Worklog (2026-03-06)

## Summary

This revision focuses on strengthening VHK's Linux-native **measure -> explain -> optimize** loop instead of adding another large backend surface.

## Code changes

- Added step-type aggregation to event-log summaries.
- Added heuristic `advice` output to event-log summaries and `vhk report`.
- Added report CLI rendering for optimization advice.

## Docs changes

- Added a Linux-native runtime plan.
- Expanded SPECS with an optimization-feedback contract.
- Expanded performance/reporting docs to describe the new loop.
- Extended the issue shortlist with March 2026 ecosystem notes.

## Test coverage run in this revision

Representative passing suites:

- `tests/test_report_cli.py`
- `tests/test_trace_cli.py`
- `tests/test_optimize_cli.py`
- `tests/test_optimize_project_cli.py`
- `tests/test_optimize_review_modes_cli.py`
- `tests/test_doctor_cli.py`
- `tests/test_validate_cli.py`
- `tests/test_expr.py`
- `tests/test_runner_features.py`


## Later update: project-shape / strategy planning

- Added `vhk plan-project` to summarize project shape, macro archetypes, trigger surfaces, recorder smells, and Linux-native recommendations.
- Added `docs/PROJECT_STRATEGY.md` to make the command and its product intent explicit.
- Reframed the next slice of work around product shape learned from AutoKey, Espanso, SikuliX, and the current portal/libei docs: text workflows, forms, selector assets, and capability-aware deployment need to stay first-class.

- Extended `vhk plan-project` with explicit **integration targets** (trigger plane, text tier, selector pack, event bridge, Wayland helper boundary, remap/export surfaces) plus a prioritized **next steps** roadmap so project-shape analysis turns directly into implementation guidance.


## Later update: architecture lanes + implementation playbooks

- Extended `vhk plan-project` again so it now emits scored **product lanes**.
  This makes the command answer not just "what tags are present?" but also
  "which subsystem should we invest in first?"
- Added explicit **implementation playbooks** with concrete VHK commands.
  The command now turns strategy into runnable loops such as deployment audit,
  text export, selector debug, remap export, and dispatch-daemon packaging.
- Reframed the research docs around a stronger Linux-native lesson: exported
  configs and helper/service boundaries are not second-class compromises. They
  are often the right architecture for performance, portability, and session
  awareness.


## Later update: architecture maps + stack profiles

- Extended `vhk plan-project` again so it now emits an explicit **architecture map** with component ownership boundaries (`vhk-core`, external/helper, adapter seam, user service, export surface).
- Added scored **deployment/stack profiles** so planning output can say not only which subsystem matters, but also which Linux-native product shape best fits the project.
- Added `docs/STACK_PROFILES.md` to capture the design lesson from current Linux tools: the right architecture is often thin dispatch + strong runtime + exported/helper surfaces, not one monolithic always-on macro daemon.


## Later update: desktop target matrix + ecosystem patterns

- Extended `vhk plan-project` again so it now emits a scored **desktop target matrix**.
- Added explicit targets for portable text/export, X11 tiling-native, portal-centric Wayland, helper-boundary Wayland, and wlroots/Hyprland-conservative landing zones.
- The planner now carries lightweight **learn_from** patterns so the repo can preserve lessons from current Linux tools and interfaces instead of burying them in prose only.
- Added `docs/DESKTOP_TARGETS.md` and expanded strategy/profile docs so this new planning surface is documented as a product-shaping tool, not just another JSON blob.


## rev0134 - surface choice matrix

Added a new `plan-project` output surface: `surface_choices`.

This scores concrete Linux integration candidates such as Espanso-style text
packages, VHK palette launches, WM-native dispatch, portal shortcut paths,
keyd/kanata/KMonad-class remap layers, and watcher services.

Why this mattered: the planner was good at naming abstract targets, but it
still did not help enough with the real implementation choice teams face on
Linux: which surface should own this workflow?

Also added CLI table rendering and focused tests for the new output.


## rev0135

- Added a new `plan-project` output surface: `environment_diffs`.
- The planner now compares one project against hypothetical target environments such as X11/i3, GNOME Wayland, KDE Wayland, wlroots/sway conservative, Hyprland conservative, and a portable text baseline.
- This turns the strategy layer from “what is this project?” into “how does this same project change across Linux targets?”
- Added CLI rendering for the environment comparison table, expanded tests, and documented the new contract in `ENVIRONMENT_DIFFS.md`.

## rev0137 - portability gaps and migration planning

- Added a new `plan-project` output surface: `portability_gaps`.
- The planner now compares the strongest hypothetical environment against the
  more conservative targets and summarizes what actually changes.
- Added explicit migration hints: newly blocked capabilities, degraded
  capabilities, surfaces to keep, surfaces to replace, new preferred surfaces,
  and a short migration response.
- Added CLI table rendering and documented the surface in
  `docs/PORTABILITY_GAPS.md`.

## rev0138

- Added a new `plan-project` output surface: `portability_playbooks`.
- These turn portability gaps into concrete export/install checklists with
  artifact suggestions (desktop entries, launcher scripts, WM snippets,
  remapper configs, user services, helper-boundary review) plus validation
  commands.
- Added CLI rendering for a new **Portability playbooks** section.
- Added `docs/PORTABILITY_PLAYBOOKS.md` and updated strategy/spec/issues docs.



## rev0139

- Added a new `plan-project` output surface: `reference_patterns`.
- This scores reusable product patterns such as AHK-style runner core,
  Pulover-style visual studio, Espanso-style text/forms export, WM bind
  dispatch, remap-daemon offload, and portal/helper-boundary integration.
- Added CLI rendering for a new **Reference patterns** section.
- Added `docs/REFERENCE_PATTERNS.md` and expanded strategy/spec/issues docs so
  ecosystem lessons can be reused by code instead of staying in prose only.


## Later on 2026-03-06: concrete toolchain choices

Added another `plan-project` layer: `toolchain_choices`.

This turns a lot of the repo's Linux ecosystem learning into a more actionable
planner output. Instead of stopping at “helper-boundary Wayland” or “text-first
export”, VHK can now say things like:

- prefer `xdotool`-class paths on X11 when text/pointer breadth matters
- prefer `wtype`/clipboard-first flows for Wayland text lanes
- keep Wayland pointer automation behind portal/helper/uinput seams
- keep capture portal-first on Wayland unless a compositor-native target is explicit
- treat `wmctrl`/`xprop` versus `hyprctl`/`swaymsg`/`kdotool` as target-shaped context bridges

That is a better fit for the project than yet another abstract scoring surface,
because it helps bridge planning into real installation/export choices.


## rev0141 - capability coverage matrix

- Added a new `plan-project` output surface: `capability_coverage`.
- This summarizes each major Linux automation capability across the hypothetical target environments instead of only comparing whole-project scores.
- Added explicit coverage classes such as `portable`, `conditional`, `desktop-boundary`, `helper-boundary`, `x11-first`, and `experimental`.
- Added CLI rendering for a new **Capability coverage matrix** section.
- Added `docs/CAPABILITY_COVERAGE.md` and updated strategy/spec docs so portability risk is modeled per capability, not only per desktop.


## rev0142 - verification gates

- Added a new `plan-project` output surface: `verification_gates`.
- This turns planner output into capability-shaped shipping gates instead of
  stopping at target/surface/toolchain advice.
- Each gate now carries priority, gate type, acceptance checks, commands,
  target environments, fallback paths, and artifact hints.
- Added CLI rendering for a new **Verification gates** section.
- Added `docs/VERIFICATION_GATES.md` and updated strategy/spec/issues docs so
  release validation can be modeled capability-by-capability.


## rev0143 - implementation waves

- Added a new `plan-project` output surface: `implementation_waves`.
- This sequences the existing planning surfaces into delivery waves instead of
  stopping at target, toolchain, or gate recommendations.
- Each wave now carries an objective, why-now rationale, commands,
  deliverables, validation checks, borrowed ecosystem patterns, and
  dependencies.
- Added CLI rendering for a new **Implementation waves** section.
- Added `docs/IMPLEMENTATION_WAVES.md` and updated strategy/spec docs so VHK can
  describe not just what to build, but what to build first.

## rev0144 - artifact blueprint

- Added a new `plan-project` output surface: `artifact_blueprint`.
- This consolidates waves, gates, portability playbooks, and toolchain/context hints into a concrete deployment/file map.
- Each artifact now carries category, deployment surface, ownership, install hint, first-wave context, generator commands, validation commands, related capabilities, and source references.
- Added CLI rendering for a new **Artifact blueprint** section.
- Added `docs/ARTIFACT_BLUEPRINT.md` and updated strategy/spec/issues docs so VHK can describe not only what to build and in what order, but which Linux-facing artifacts the project should actually ship.

## rev0145 - deployable surfaces + issue refresh

- Added a new `plan-project` output surface: `deployable_surfaces`.
- This groups file-level artifacts back into the Linux-facing surfaces operators actually install and depend on: text packages, launcher entrypoints, WM trigger layers, remap/helper seams, watcher services, selector/debug packs, and capability-audit packs.
- Added CLI rendering for a new **Deployable surfaces** section.
- Added `docs/DEPLOYABLE_SURFACES.md` and expanded the specs/README so the new surface is part of the explicit product contract.
- Refreshed the issue shortlist with two additional March 2026 ecosystem notes: GlobalShortcuts still favors predeclared bindings, and recent libei/input-capture failure reports reinforce the need for helper boundaries and recovery guidance.
- Fixed README version drift (`v0.22` -> `v0.24`).



## rev0146 - setup recipes + install-story research

- Added a new `plan-project` output surface: `setup_recipes`.
- This turns deployable surfaces into explicit Linux-native install/review handoffs: text package install, launcher entrypoint install, WM trigger install, remap/helper install, watcher-service install, selector-debug review, and capability-audit review.
- Added CLI rendering for a new **Setup recipes** section.
- Added `docs/SETUP_RECIPES.md` and expanded the specs/README/issues docs so setup/install/rollback is part of the explicit planning contract.
- Refreshed the issue shortlist with a broader ecosystem lesson from current tools: AutoKey still frames itself as X11, Espanso still treats service/app-scoping as first-class, and keyd/kanata/ydotool-style helpers still require explicit Linux setup seams.


## rev0147 - init starter artifacts + onboarding bridge

- `vhk init` now consumes the planner instead of only creating a bare project skeleton.
- New projects can emit `docs/VHK_STARTER_GUIDE.md` and `docs/VHK_STARTER_PLAN.json`, derived from the same strategy model used by `vhk plan-project`.
- The starter guide surfaces likely product lanes, integration targets, deployable surfaces, setup recipes, toolchain choices, reference patterns, suggested commands, and early verification gates before desktop-specific checks run.
- Added `--starter-guide/--no-starter-guide` and `--starter-plan-json/--no-starter-plan-json` to let authors choose how much onboarding material they want in a new project.
- Added `docs/STARTER_ARTIFACTS.md` and updated init/spec/issues/README docs so init is explicitly part of the Linux-native planning story.
- Research takeaway carried into product shape: Espanso keeps app-specific configs, forms, and shareable packages as first-class surfaces; keyd and kanata keep reminding us that helper/remap installs are permissions-and-service work; AutoKey still has to be explicit about X11 scope.


## rev0148 - operator pack + deployment handoff

- Added `vhk gen-operator-pack`, which turns planner output into operator-facing deployment artifacts for existing projects.
- New generated artifacts: `docs/VHK_OPERATOR_GUIDE.md`, `docs/VHK_DEPLOYMENT_CHECKLIST.md`, and `docs/VHK_OPERATOR_PLAN.json`.
- This pushes the repo one step beyond starter onboarding: the same planner data can now travel as install/review/rollback docs instead of living only in CLI output or markdown research notes.
- Added `docs/OPERATOR_PACK.md` and updated README/spec/issues docs so deployment handoff is part of the explicit product contract.
- Research lesson reinforced in product shape: current Linux automation ecosystems still make service wiring, remapper permissions, app-scoping, and rollback paths explicit, so VHK should generate operator docs rather than pretending one universal installer can own every desktop/session path.


## rev0149 - verification pack + release rehearsal

- Added `vhk gen-verification-pack`, which turns planner output into release-facing verification artifacts for existing projects.
- New generated artifacts: `docs/VHK_VERIFICATION_GUIDE.md`, `docs/VHK_RELEASE_CHECKLIST.md`, `docs/VHK_VERIFICATION_PLAN.json`, and `scripts/vhk_verify_release.sh`.
- This consumes the same deployable surfaces, setup recipes, verification gates, toolchain choices, and implementation waves already emitted by `vhk plan-project`, but packages them for shipping review instead of only operator handoff.
- Added `docs/VERIFICATION_PACK.md` and updated README/spec/issues docs so release rehearsal becomes part of the explicit Linux-native product contract.
- Product lesson carried forward: Linux automation installs are only half the story; a believable release needs an explicit rehearsal path for services, remappers, launchers, and desktop-specific fallbacks too.

## rev0150 - support pack + triage handoff

- Added `vhk gen-support-pack`, which turns planner + diagnostics output into support-facing triage artifacts for existing projects.
- New generated artifacts: `docs/VHK_SUPPORT_GUIDE.md`, `docs/VHK_SUPPORT_CHECKLIST.md`, `docs/VHK_SUPPORT_PLAN.json`, and `scripts/vhk_capture_support.sh`.
- The support plan now adds explicit support paths, likely evidence artifacts, privacy review notes, and suggested capture commands on top of the existing planner output.
- The capture script gathers doctor/validate/plan JSON, regenerates operator/verification/support packs into a support folder, copies recent event/error artifacts, exports the latest report/trace when logs exist, and can optionally create a deterministic project bundle.
- Added `docs/SUPPORT_PACK.md` plus README/spec/issues updates so support/triage becomes part of the explicit Linux-native product surface instead of remaining an ad-hoc debugging chore.


## rev0151 - portability pack + target rollout

- Added `vhk gen-portability-pack`, which turns planner-backed environment comparison into cross-desktop review artifacts for existing projects.
- New generated artifacts: `docs/VHK_PORTABILITY_GUIDE.md`, `docs/VHK_TARGET_ROLLOUT.md`, `docs/VHK_PORTABILITY_PLAN.json`, and `scripts/vhk_review_portability.sh`.
- The portability plan now adds an explicit `target_rollout` ordering, stable portability review commands, and review-path metadata on top of the existing planner output.
- Added `docs/PORTABILITY_PACK.md` and updated README/spec/issues docs so cross-desktop rollout review becomes part of the explicit Linux-native product contract.
- Research lesson carried forward: current xremap docs still show that app-specific remapping on Wayland depends on desktop-specific bridges, session wiring, and troubleshooting paths, so VHK should keep portability review explicit instead of pretending one backend can claim every desktop honestly.


## rev0152 - claim pack + auditable support matrix

- Added `vhk gen-claim-pack`, which turns planner-backed portability/release knowledge into explicit support-claim artifacts for existing projects.
- New generated artifacts: `docs/VHK_CLAIM_GUIDE.md`, `docs/VHK_TARGET_CLAIMS.yaml`, `docs/VHK_CLAIM_AUDIT_PLAN.json`, and `scripts/vhk_audit_claims.sh`.
- Added `vhk audit-target-claims`, which compares the editable claim manifest against the current planner output and fails stronger-than-recommended claims.
- The new claim manifest seeds each desktop lane with a recommended claim tier, blockers/caveats, proof artifacts, review commands, and maintainer/evidence fields so release/support language becomes reviewable.
- Added `docs/CLAIM_PACK.md` plus README/spec/issues updates so VHK can move from portability worksheets to an auditable support matrix.
- Research lesson carried forward: current Linux automation stacks still force explicit target-specific support tiers, whether through X11/Wayland package splits, GNOME-only Wayland scope, or desktop-shaped remapper bridges.


## rev0153 - bundle support metadata + bundle inspection

- Extended `vhk bundle` so `vhk_bundle_manifest.json` can now embed a planner-backed support snapshot when the project has a readable `project.yaml`.
- Added `vhk inspect-bundle`, which exposes that embedded support snapshot (claim source, claim tiers, audit statuses, proof-artifact presence, and review commands) without requiring the recipient to unpack the bundle.
- The embedded snapshot prefers `docs/VHK_TARGET_CLAIMS.yaml` plus `vhk audit-target-claims` when available, but falls back to planner recommendations when no editable claims file exists yet.
- Added focused bundle/claim tests and updated README/spec/issues docs so VHK bundles become reviewable Linux-support artifacts rather than anonymous zip files.
- Research lesson carried forward: neighboring Linux automation tools keep shipping explicit package/service/config surfaces, so VHK bundles should carry support context and evidence status instead of pretending a zip alone explains what a project truly supports.


## rev0154 - publish pack + public release/install posture

- Added `vhk gen-publish-pack`, which turns planner-backed claim/audit data into audience-facing release/install artifacts for existing projects.
- New generated artifacts: `docs/VHK_PUBLIC_SUPPORT.md`, `docs/VHK_INSTALL_QUICKSTART.md`, `docs/VHK_PUBLISH_PLAN.json`, and `scripts/vhk_refresh_publish_pack.sh`.
- The publish plan now carries a `public_support_matrix`, rollout ordering, language guardrails, bundle release story, and publish commands so README/release prose can be generated from the same support evidence that the bundle manifest already uses.
- Extended embedded bundle support metadata so `vhk inspect-bundle` can now tell whether the bundle includes the public support/install docs as well as the audited claim snapshot.
- Added `docs/PUBLISH_PACK.md` and updated README/spec/issues docs so VHK can move from auditable internal support claims to auditable public release posture.
- Research lesson carried forward: neighboring Linux automation tools still expose explicit service/package/config boundaries and lane-specific support scope, so VHK should keep public docs tied to audited proof instead of marketing Linux support as a single flat checkbox.

## 2026-03-07 — Entrypoint support posture

- Added a shared support-posture helper that can load or rebuild the project's publish/support snapshot on demand.
- Exported launcher scripts now embed that snapshot and expose `--about` plus `--support-json`.
- Exported desktop entries now include `X-VHK-Support-*` metadata and incorporate the publish headline into the default `Comment=` line.
- Self-contained WM bundles now include `docs/VHK_PUBLIC_SUPPORT.md`, `docs/VHK_INSTALL_QUICKSTART.md`, and `docs/VHK_BUNDLE_SUPPORT.json`.
- `vhk-wm-bundle.json` now records the support headline plus those support-artifact paths.
- Added `docs/ENTRYPOINT_SUPPORT.md`.


## 2026-03-07 — Trigger pack export bundle

- Added `vhk gen-trigger-pack`, which turns planner-backed trigger/remapper advice into a self-contained export root under `build/trigger_pack/` by default.
- The new pack generates WM snippets for i3/sway/Hyprland plus external trigger/remapper configs for sxhkd, keyd, Kanata, and KMonad.
- Each generated config now carries a small support-posture header so recipients can see the audited support headline and the exact refresh command that produced the file.
- Added `docs/VHK_TRIGGER_SURFACES.md`, `docs/VHK_TRIGGER_MATRIX.md`, `docs/VHK_TRIGGER_PACK.json`, and `scripts/vhk_refresh_trigger_pack.sh` inside the pack root so trigger-layer review is no longer trapped in scattered CLI output.
- Added `docs/TRIGGER_PACK.md` and updated README/spec/issues docs so grouped trigger/export behavior becomes part of the Linux-native product contract.
- Research lesson carried forward: current Linux automation tools still split trigger ownership across compositor binds, X11 hotkey daemons, remapper layers, and portal/session paths, so VHK should export those layers as an explicit bundle instead of pretending one universal trigger backend exists.


## rev0157 - setup pack + executable planner recipes

- Added `vhk gen-setup-pack`, which turns planner `setup_recipes` into generated docs plus runnable apply/verify scripts.
- New generated artifacts: `docs/VHK_SETUP_GUIDE.md`, `docs/VHK_SETUP_MATRIX.md`, `docs/VHK_SETUP_PLAN.json`, `scripts/vhk_apply_setup_recipes.sh`, and `scripts/vhk_verify_setup_recipes.sh`.
- Portable-command normalization now rewrites maintainer-local absolute project paths to `.` inside the generated scripts/docs when appropriate.
- The scripts only auto-run command-like entries and keep prose validation/install notes in docs, which makes the feature useful without pretending Linux setup is a one-click problem.
