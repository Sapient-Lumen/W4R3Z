# Worklog — 2026-03-07

## rev0170 - stage bundle handoff

- added `vhk bundle-stage <project_dir> <out.zip> --target-profile <profile>` so
  release-stage lanes can be zipped directly from
  `build/release-stage/<profile>/` instead of falling back to a full-project
  bundle
- stage bundles now embed `bundle_kind: release-stage` plus
  `release_stage_metadata` in `vhk_bundle_manifest.json`
- `vhk inspect-bundle` now surfaces that lane metadata, so reviewers can see
  which stage lane a zip came from before unpacking it
- updated README/spec/release-stage docs so the new handoff becomes part of the
  explicit product contract instead of living only as an issue-note follow-up

### Why this matters

`gen-release-stage-pack` already made lane-local ship trees real, but the last
step of actually handing one to someone still collapsed back into a generic
project zip. This pass keeps the packaging source aligned with the lane an
operator actually reviewed.

### Tests run for this slice

```bash
pytest -q \
  tests/test_bundle_manifest.py \
  tests/test_bundle_support_metadata_cli.py \
  tests/test_release_stage_pack_cli.py
```

### Next likely steps

- let publish/package commands consume a chosen stage lane directly too
- grow lane-native signing/notarization/distribution handoff on top of the same
  staged tree instead of inventing another parallel packaging surface

## What changed in this revision

- Extended `vhk gen-setup-pack` so setup guidance now includes a concrete
  **toolchain package bootstrap** lane derived from planner `toolchain_choices`.
- Added normalized package groups plus aggregate install-command hints for:
  - `apt`
  - `dnf`
  - `pacman`
  - `zypper`
- Added a dry-run-first helper script:
  - `scripts/vhk_install_toolchain_packages.sh`
- Kept the install helper conservative:
  - it defaults to printing commands
  - it only executes when `RUN_INSTALL=1` is set explicitly
  - it preserves per-capability grouping via `PACKAGE_FILTER=<group-id>`
- Updated setup-pack docs/spec text so package bootstrap is treated as part of
  the Linux-native install surface rather than buried in prose.
- Refreshed the issue shortlist with additional March 2026 ecosystem notes from
  current upstream docs/projects (AutoKey, xremap, GlobalShortcuts portal,
  libei, ydotool).

## Why this matters

The repo already had a strong planning layer (`toolchain_choices`,
`deployable_surfaces`, `setup_recipes`), but there was still a gap between:

1. knowing which Linux helper/toolchain was likely right, and
2. giving operators a reviewable bootstrap path for installing that lane.

This revision closes part of that gap without pretending Linux automation can be
reduced to a universal one-click installer.

## Tests run

Focused setup-pack tests:

```bash
pytest -q tests/test_setup_pack_cli.py
```

Broader pack/planning regression slice:

```bash
pytest -q \
  tests/test_setup_pack_cli.py \
  tests/test_publish_pack_cli.py \
  tests/test_support_pack_cli.py \
  tests/test_portability_pack_cli.py \
  tests/test_operator_pack_cli.py \
  tests/test_claim_pack_cli.py \
  tests/test_trigger_pack_cli.py \
  tests/test_bundle_manifest.py \
  tests/test_plan_project_cli.py \
  tests/test_validate_cli.py \
  tests/test_doctor_cli.py
```

## Next likely steps

- Make package bootstrap environment-aware enough to emit narrower package sets
  for GNOME/KDE/wlroots/Hyprland lanes instead of one conservative union.
- Let planner output distinguish between:
  - packages
  - services
  - permissions/groups
  - portal/backend routing
  so setup packs can stop collapsing those into one install section.
- Add a future `doctor` / `validate` flow that can compare missing helpers
  directly against the generated bootstrap groups.

---

## Later update: design/runtime architecture pack

This pass shifted the planner a bit closer to the actual product goal:
Linux-native automation should not only know **what to install** or **what to
verify**; it should also know **which layers belong where**.

### What changed

- Extended `plan-project` with explicit `stack_profiles` output (an architecture-facing alias/extension of `deployment_profiles`).
- Added `runtime_seams` so the planner can name the split between:
  - runner core
  - trigger/dispatch surface
  - text/export surface
  - selector/debug asset pack
  - watcher/service plane
  - helper/compositor boundary
- Added `ecosystem_lessons` so product-shape research stops living only in markdown notes and becomes machine-readable planner output.
- Added a new command:
  - `vhk gen-design-pack`
- The new pack writes:
  - `docs/VHK_DESIGN_BRIEF.md`
  - `docs/VHK_RUNTIME_CONTRACT.md`
  - `docs/VHK_DESIGN_PLAN.json`

### Why this matters

The repo already had strong ops-facing packs (`operator`, `verification`,
`support`, `portability`, `setup`). The missing surface was the **design
handoff**:

- what should stay inside VHK because it needs state, retries, prompts, and diagnostics?
- what should stay thin/exported because Linux-native tools are better at owning that edge?
- what lessons from AHK / Pulover / Espanso / AutoKey / xremap / keyd / portals should turn into product rules instead of vague inspiration?

That is exactly the gap this revision tries to close.

### Tests run for this slice

Focused planner + design pack tests:

```bash
pytest -q tests/test_plan_project_cli.py tests/test_design_pack_cli.py
```

Broader regression slice:

```bash
pytest -q \
  tests/test_plan_project_cli.py \
  tests/test_design_pack_cli.py \
  tests/test_operator_pack_cli.py \
  tests/test_setup_pack_cli.py \
  tests/test_support_pack_cli.py \
  tests/test_portability_pack_cli.py \
  tests/test_publish_pack_cli.py \
  tests/test_claim_pack_cli.py \
  tests/test_trigger_pack_cli.py \
  tests/test_verification_pack_cli.py
```

### Next likely steps after this

- let scaffold/init consume `runtime_seams` directly so new projects start with the right layer split already visible
- add comparative scoring inside the design pack for “thin trigger export vs service vs helper seam” decisions
- let future Studio surfaces edit/support these contracts instead of treating them as write-only generated docs

---

## Later update: session-fit / host-review pack

This pass closed the gap between **project strategy** and **current-host
reality**. VHK already knew how to describe a project's Linux-native shape and
probe a session's capabilities, but it still lacked a first-class artifact that
joined those views into an operator decision.

### What changed

- Added a new command:
  - `vhk gen-session-fit-pack`
- The new pack writes:
  - `docs/VHK_SESSION_FIT.md`
  - `docs/VHK_SESSION_FIXUPS.md`
  - `docs/VHK_SESSION_PLAN.json`
  - `scripts/vhk_review_session_fit.sh`
- The generated plan now classifies required project capabilities against the
  current session as `ready`, `degraded`, `blocked`, or `unknown`.
- Blocked/degraded capabilities are linked back to planner `toolchain_choices`
  plus the normalized setup/bootstrap groups from the setup-pack work, so host
  fixes stop living only in issue comments or support chat.

### Why this matters

Linux automation work keeps falling into the same trap: one artifact says what
a project wants, another says what a desktop might provide, and the actual
operator decision still has to happen in someone's head.

This revision makes that join explicit. It does **not** pretend the result is a
universal installer; instead it gives VHK a reviewable host-fit surface.

### Tests run for this slice

Focused session-fit tests:

```bash
pytest -q tests/test_session_fit_pack_cli.py
```

Broader regression slice:

```bash
pytest -q \
  tests/test_session_fit_pack_cli.py \
  tests/test_design_pack_cli.py \
  tests/test_setup_pack_cli.py \
  tests/test_plan_project_cli.py \
  tests/test_operator_pack_cli.py \
  tests/test_support_pack_cli.py \
  tests/test_portability_pack_cli.py \
  tests/test_publish_pack_cli.py \
  tests/test_claim_pack_cli.py \
  tests/test_trigger_pack_cli.py \
  tests/test_verification_pack_cli.py \
  tests/test_bundle_manifest.py \
  tests/test_validate_cli.py \
  tests/test_doctor_cli.py
```

### Next likely steps after this

- split setup/bootstrap guidance more explicitly into packages, services,
  permissions/groups, and portal/backend routing
- add desktop-aware narrowing so session-fit packs can prefer GNOME/KDE/wlroots
  lanes instead of always showing a conservative helper union
- let future scaffold/init/Studio surfaces consume the same host-fit language so
  projects start with an explicit deployment target story

---

## Later update: host-contract / deployment-contract pack

This pass addressed the next Linux-native deployment gap after setup/bootstrap
and session-fit review: a project still needs an explicit contract for
**services, permissions, and portal routing**.

### What changed

- Extended `plan-project` with explicit `host_requirements` output.
- Added a new command:
  - `vhk gen-host-contract-pack`
- The new pack writes:
  - `docs/VHK_HOST_REQUIREMENTS.md`
  - `docs/VHK_HOST_FIXUPS.md`
  - `docs/VHK_HOST_PLAN.json`
  - `scripts/vhk_review_host_contract.sh`
- Added a new reference doc:
  - `docs/HOST_CONTRACT_PACK.md`

### Why this matters

Linux-native automation install stories are not just package lists. Current
adjacent tools keep reinforcing the same operator reality:

- helper-backed input paths need daemon lifecycle and `/dev/uinput` review
- remapper exports need service placement/restart policy, not just config files
- portal-backed features need interface routing and consent/session review

This revision makes that contract explicit instead of burying it in comments or
issue threads.

### Tests run for this slice

Focused host-contract tests:

```bash
pytest -q tests/test_host_contract_pack_cli.py
```

Broader regression slice:

```bash
pytest -q \
  tests/test_host_contract_pack_cli.py \
  tests/test_plan_project_cli.py \
  tests/test_design_pack_cli.py \
  tests/test_session_fit_pack_cli.py \
  tests/test_setup_pack_cli.py \
  tests/test_operator_pack_cli.py \
  tests/test_support_pack_cli.py \
  tests/test_portability_pack_cli.py \
  tests/test_publish_pack_cli.py \
  tests/test_claim_pack_cli.py \
  tests/test_trigger_pack_cli.py \
  tests/test_verification_pack_cli.py \
  tests/test_bundle_manifest.py \
  tests/test_validate_cli.py \
  tests/test_doctor_cli.py
```

### Next likely steps after this

- deepen live verification for service state instead of only helper presence
- thread host-contract language into init/scaffold/studio onboarding
- compare host contracts across target desktops, not only on the current host

---

## Later update: readiness-pack / live deployment-proof layer

This pass tackled the next gap after host contracts: VHK could describe what a
Linux host should provide, but it still needed a first-class artifact for what
is **actually live right now**.

### What changed

- Added a new command:
  - `vhk gen-readiness-pack`
- The new pack writes:
  - `docs/VHK_READINESS_REPORT.md`
  - `docs/VHK_READINESS_FIXUPS.md`
  - `docs/VHK_READINESS_PLAN.json`
  - `scripts/vhk_refresh_readiness_report.sh`
- Added a new reference doc:
  - `docs/READINESS_PACK.md`
- Added a new research note:
  - `docs/RESEARCH_2026Q1_DEPLOYMENT_LIFECYCLE.md`
- Added new host probes used by the readiness layer:
  - current supplemental groups
  - raw `/dev/input/event*` readability
  - best-effort `systemd` unit state for planner-backed service lanes

### Why this matters

Current Linux automation tools keep teaching the same product lesson:
installation is not the same thing as readiness.

- Espanso still has a service-registration/start story and Wayland capability
  work, so “binary present” is not enough.
- xremap still branches into sudo vs non-sudo, `input`/`uinput` policy, and
  GNOME-specific app-context setup.
- keyd / kanata / KMonad still make service wiring and permission policy part of
  the real install surface.
- ydotool still depends on a daemon/socket split plus `/dev/uinput`.
- portals still add a backend-routing/session constraint on top of interface
  presence.

The new readiness pack is VHK learning the right lesson from that ecosystem:
keep planner language, host contracts, and live proofs separate but connected.

### Tests run for this slice

Focused readiness/contract/planning tests:

```bash
pytest -q \
  tests/test_readiness_pack_cli.py \
  tests/test_host_contract_pack_cli.py \
  tests/test_plan_project_cli.py
```

Broader regression slice:

```bash
pytest -q \
  tests/test_readiness_pack_cli.py \
  tests/test_host_contract_pack_cli.py \
  tests/test_design_pack_cli.py \
  tests/test_session_fit_pack_cli.py \
  tests/test_setup_pack_cli.py \
  tests/test_operator_pack_cli.py \
  tests/test_support_pack_cli.py \
  tests/test_portability_pack_cli.py \
  tests/test_publish_pack_cli.py \
  tests/test_claim_pack_cli.py \
  tests/test_trigger_pack_cli.py \
  tests/test_verification_pack_cli.py \
  tests/test_bundle_manifest.py \
  tests/test_validate_cli.py \
  tests/test_doctor_cli.py
```

### Next likely steps after this

- add narrower probes for espanso registration state instead of only service
  state inference
- support custom socket-activation / dedicated-service-user stories in the
  readiness contract
- compare readiness across hypothetical targets, not only the current host


---

## Later update: activation-route / Linux wake-up pack

This pass closed the next deployment/runtime gap after host contracts and
readiness proofs: VHK still needed a first-class answer to **how a project
actually wakes up and stays alive on Linux**.

### What changed

- Extended `plan-project` with explicit `activation_routes` output.
- Added a new command:
  - `vhk gen-activation-pack`
- The new pack writes:
  - `docs/VHK_ACTIVATION_ROUTES.md`
  - `docs/VHK_ACTIVATION_FIXUPS.md`
  - `docs/VHK_ACTIVATION_PLAN.json`
  - `scripts/vhk_review_activation_routes.sh`
- Added new reference docs:
  - `docs/ACTIVATION_PACK.md`
  - `docs/RESEARCH_2026Q1_ACTIVATION_LANES.md`

### Why this matters

Linux-native automation does not only vary by capability. It also varies by
activation ownership:

- launchers wake work on demand
- compositor/WM configs own one class of always-on bindings
- text expanders own service-managed snippet entry
- watcher/bus surfaces own background event planes
- remappers own low-latency key interception
- portals own session-bound bind/configure flows
- helper daemons own sockets and input-edge lifecycle

This revision makes those lanes explicit instead of leaving them spread across
strategy docs, host requirements, and support folklore.

### Tests run for this slice

Focused activation tests:

```bash
pytest -q tests/test_activation_pack_cli.py tests/test_plan_project_cli.py
```

### Next likely steps after this

- deeper per-route proofs (for example route-native portal/session status instead
  of only capability + backend-config inference)
- explicit reference-route selection so one lane can be marked “primary” and
  others can stay as fallback/experimental
- broader non-systemd launch stories (runit/s6/etc.) so activation packs stay
  honest outside systemd-heavy desktops

---

## Later update: reference-route selection pack

This pass closed the next product/deployment gap after activation lanes: VHK
needed to say not only **which Linux routes exist**, but **which route should be
treated as the shipping/reference lane on this host** and which routes should
stay fallback or promotion candidates.

### What changed

- Added a new command:
  - `vhk gen-route-selection-pack`
- The new pack writes:
  - `docs/VHK_ROUTE_SELECTION.md`
  - `docs/VHK_ROUTE_FIXUPS.md`
  - `docs/VHK_ROUTE_PLAN.json`
  - `scripts/vhk_review_route_selection.sh`
- Added new reference docs:
  - `docs/ROUTE_SELECTION_PACK.md`
  - `docs/RESEARCH_2026Q1_ROUTE_SELECTION.md`

### Why this matters

Linux-native automation projects do not only need routes. They need a route
*decision*: one honest operator fallback, one preferred trigger story, one text
surface story, one event-plane story, and one input-edge story when those lanes
exist.

This revision keeps two truths visible at once:

- the design-preferred route is not always the one that is currently the most
  ready on the host
- a healthier fallback route should sometimes be promoted until the preferred
  route is repaired

That is the missing bridge between architecture notes and a real deployment
playbook.

### Tests run for this slice

Focused route-selection tests:

```bash
pytest -q tests/test_route_selection_pack_cli.py
```

### Next likely steps after this

- add route-native portal/session proofs so portal-based decisions rely on more
  than backend-config/capability inference
- model non-systemd launch stories explicitly inside route selection instead of
  treating them as notes
- compare reference-route decisions across target desktops or claim tiers, not
  only the current host



## Later update: target-route matrix / hypothetical desktop comparison

This pass tackled the gap after route selection: VHK could choose a reference
route for the **current** host, but release planning still had to guess how that
decision would change across likely Linux targets.

What changed:

- add `vhk gen-target-route-pack`
- add `src/vhk/project/target_route_pack.py`
- add `tests/test_target_route_pack_cli.py`
- add `docs/TARGET_ROUTE_PACK.md`
- generated artifacts now include:
  - `docs/VHK_TARGET_ROUTE_MATRIX.md`
  - `docs/VHK_TARGET_ROUTE_FIXUPS.md`
  - `docs/VHK_TARGET_ROUTE_PLAN.json`
  - `scripts/vhk_compare_target_routes.sh`

Why this matters:

- route selection on one real host is still not the same as a release story for
  GNOME Wayland, KDE Wayland, wlroots-class compositors, and generic X11
- Linux automation stacks keep teaching that activation shape is desktop-family
  specific even when macro semantics stay stable
- the new pack keeps launcher fallback, portal/session routes, and remapper-first
  targets visible at the same time instead of flattening them into one claim

Tests run for this slice:

```bash
pytest -q tests/test_target_route_pack_cli.py
```

Next likely steps after this:

- compare the same target-route matrix against explicit claim tiers or support
  tiers, not just target desktops
- let publish/operator/support flows ingest the chosen target profiles directly
- add deeper route-native proof for portal/session lanes so target assumptions
  can be checked against real desktops more mechanically

## rev0166 — release-lane ship guidance

- added `gen-release-lane-pack` so cross-desktop target-route comparisons now become ship-facing Linux release lanes
- new generated artifacts: `VHK_RELEASE_LANES.md`, `VHK_RELEASE_SNIPPETS.md`, `VHK_RELEASE_LANE_PLAN.json`, `vhk_refresh_release_lanes.sh`
- the new pack classifies hypothetical targets as `reference`, `supported`, `caveated`, or `experimental` and emits copy-ready public/support language per lane
- this closes part of the gap between route planning and release/publish/support docs: maintainers can now compare `x11-desktop`, `gnome-wayland`, `kde-wayland`, and `wlroots-wayland` as ship lanes instead of just abstract target profiles


## rev0167 — release-lane carry-through for export surfaces

This pass tackled the next gap after release-lane planning: VHK could model
reference/supported/caveated desktop lanes, but exported surfaces still mostly
collapsed back to the older publish/claim summary.

What changed:

- support posture now loads/merges release-lane posture by default
- launcher `--about` / `--support-json` now carry flagship-lane details and
  release-lane docs
- desktop entries now emit `X-VHK-Release-*` metadata alongside the existing
  support metadata
- WM bundle support JSON now includes the same release-lane posture
- `vhk bundle` now embeds a release-lane snapshot in `vhk_bundle_manifest.json`
  when it can

Why this matters:

- a Linux export surface should not lose the desktop-family support story the
  planner already derived
- this keeps the shareable artifact closer to the actual ship lane instead of
  forcing operators to rediscover the intended flagship desktop from repo docs
- it closes part of the remaining gap between release-lane planning and real
  outward-facing packaging/install surfaces

Tests run for this slice:

```bash
pytest -q tests/test_launcher_script_cli.py tests/test_desktop_entry_cli.py \
  tests/test_wm_bundle_cli.py tests/test_bundle_support_metadata_cli.py

pytest -q tests/test_release_lane_pack_cli.py tests/test_target_route_pack_cli.py \
  tests/test_route_selection_pack_cli.py tests/test_activation_pack_cli.py \
  tests/test_readiness_pack_cli.py tests/test_host_contract_pack_cli.py \
  tests/test_plan_project_cli.py tests/test_publish_pack_cli.py \
  tests/test_claim_pack_cli.py tests/test_support_pack_cli.py \
  tests/test_operator_pack_cli.py tests/test_portability_pack_cli.py \
  tests/test_trigger_pack_cli.py tests/test_verification_pack_cli.py \
  tests/test_bundle_manifest.py tests/test_validate_cli.py \
  tests/test_doctor_cli.py tests/test_launcher_script_cli.py \
  tests/test_desktop_entry_cli.py tests/test_wm_bundle_cli.py \
  tests/test_bundle_support_metadata_cli.py

python -m compileall -q src
```


## rev0168 — release-deploy pack and lane-native install output

This pass tackled the next gap after release-lane carry-through: exported
surfaces could now remember *which* desktop lane was flagship, but maintainers
still had to improvise the actual install/autostart story from several packs.

What changed:
- added `gen-release-deploy-pack`
- new artifacts:
  - `docs/VHK_RELEASE_DEPLOYMENT.md`
  - `docs/VHK_RELEASE_INSTALL_SNIPPETS.md`
  - `docs/VHK_RELEASE_DEPLOY_PLAN.json`
  - `scripts/vhk_refresh_release_deploy.sh`
- release lanes now expand into concrete `deploy_style` values such as
  `desktop-autostart`, `wm-bundle`, and `remapper-service`
- each lane now carries a generated artifact subset plus copy-ready generator
  commands and install/activation snippets
- hotstring/text lanes now also carry an Espanso package/service snippet so the
  text-surface route stops being hand-waved in deployment docs
- support posture, launcher/about JSON, desktop-entry metadata, and bundle
  manifests now also carry flagship deploy-style summaries

Why it matters:
- Linux release planning is not complete when the desktop lane is named; the
  shipping artifact still needs a specific install/autostart story
- this makes VHK more honest about the difference between portal-session lanes,
  WM-native binding lanes, and remapper/helper-service lanes

## rev0169 - release staging + recursion fix

- added `vhk gen-release-stage-pack` to materialize per-lane stage trees under `build/release-stage/` with lane-specific `README.md`, `install.sh`, `verify.sh`, `assemble_payload.sh`, and `vhk_release_stage.json`
- added top-level stage artifacts: `docs/VHK_RELEASE_STAGE.md`, `docs/VHK_RELEASE_STAGE_MATRIX.md`, `docs/VHK_RELEASE_STAGE_PLAN.json`, and `scripts/vhk_refresh_release_stage.sh`
- fixed the release-lane/support-posture recursion path so fresh projects can build release-deploy posture without silently dropping it


## Later update: stage-aware publish bundles + borrowed-product lessons

This pass tackled the gap between release-stage materialization and outward-
facing publish output. VHK could already stage one lane and zip it manually via
`bundle-stage`, but the publish pack still regenerated commands/scripts around a
whole-project bundle.

What changed:

- `vhk gen-publish-pack` now accepts `--bundle-target-profile <profile>`
- publish plans can now declare `bundle_release_story.bundle_kind = release-stage`
- publish commands can now pivot from `vhk bundle` to `vhk bundle-stage`
- the generated refresh script now regenerates the chosen stage lane first via
  `vhk gen-release-stage-pack --target-profile <profile>`
- public support/install docs now name the chosen bundle kind and target profile
- added `docs/RESEARCH_2026Q1_LEARNING_FROM_OTHERS.md` to keep a few current
  upstream lessons visible (AutoKey, Espanso, keyd, kanata, xremap, portals)

Why this matters:

- a maintainer can now keep README/release-note style guidance tied to the same
  reviewed stage payload they are actually shipping
- VHK stops re-deriving a release artifact from the full repo after already
  doing the work to choose and materialize a lane
- the project keeps learning from adjacent tools without pretending VHK must
  absorb every remapper/text-expander/runtime concern into one binary

Focused tests:

```sh
pytest -q tests/test_publish_pack_cli.py tests/test_release_stage_pack_cli.py \
  tests/test_bundle_manifest.py tests/test_bundle_support_metadata_cli.py
pytest -q tests/test_release_deploy_pack_cli.py tests/test_release_lane_pack_cli.py \
  tests/test_target_route_pack_cli.py tests/test_claim_pack_cli.py
```


## Later update: publish handoff trees + helper-daemon distribution lessons

This pass tackled the next gap after stage-aware publish bundles: the publish
pack could *describe* what to ship, but it still did not materialize a
maintainer-facing release handoff tree.

What changed:

- `vhk gen-publish-pack` now materializes `build/publish/<bundle-name>/`
- each publish handoff now includes:
  - `README.md`
  - `vhk_publish_handoff.json`
  - `refresh_publish_inputs.sh`
  - `bundle_release.sh`
  - `payload/docs/` with copied public support/install docs + publish plan
- release-stage publish handoffs also copy the chosen lane's staged `README.md`
  and `vhk_release_stage.json` into `payload/release-stage/`
- publish docs/specs now explicitly describe that review tree instead of
  treating publish as doc-only
- added `docs/RESEARCH_2026Q1_DISTRIBUTION_HANDOFF.md` to capture a few current
  adjacent-tool lessons around daemons, services, and package/distribution
  handoff

Why this matters:

- VHK now has a concrete bridge between “we picked a lane” and “here is the
  reviewable thing a maintainer actually ships”
- it keeps release-stage shipping honest by preserving the selected lane's
  story inside the publish handoff, not just in CLI flags
- it matches how adjacent Linux tools actually deploy: long-lived daemons,
  service registration, and explicit host/session boundaries are part of the
  distribution story, not an afterthought

Focused tests:

```sh
pytest -q tests/test_publish_pack_cli.py tests/test_release_stage_pack_cli.py \
  tests/test_bundle_manifest.py tests/test_bundle_support_metadata_cli.py
pytest -q tests/test_release_deploy_pack_cli.py tests/test_release_lane_pack_cli.py \
  tests/test_target_route_pack_cli.py tests/test_claim_pack_cli.py
python -m compileall -q src
```
