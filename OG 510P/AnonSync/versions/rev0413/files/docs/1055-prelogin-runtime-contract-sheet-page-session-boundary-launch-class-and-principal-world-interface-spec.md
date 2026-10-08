# Pre-login runtime contract sheet page, session boundary, launch class, and principal world interface spec

## Purpose

The archive already had invocation-profile and service-world pages.
What it still lacked was one explicit contract for the narrower workstation question:

> is this runtime merely hidden until I open the UI, or is it a pre-session world with a different execution principal, storage home, and operator contract?

Current official Resilio docs make the missing contract unusually obvious.
On macOS they still separate:

- ordinary app start at user login under the current user
- pre-login launch through `launchd`
- a dedicated helper user
- `use_gui: false`
- WebUI-bound control
- explicit file-mode expectations created by `Umask 2`

That is not just startup trivia.
It is runtime-world truth.

AnonSync should therefore render one first-class **pre-login runtime contract sheet** before the operator is allowed to accept or normalize such a mode.

## Core decision

Every seat capable of running before interactive login must expose one explicit **launch-class contract**.
It must say:

- whether the runtime depends on an interactive session
- which principal owns the runtime
- where the runtime's storage world lives
- whether local UI is present or replaced by headless control
- what stronger sentence the product must refuse

The product must never let `starts automatically`, `runs in background`, or `launch at boot` stand in for this truth.

## Fixed review order

Every pre-login runtime contract sheet should render the same sections in the same order:

1. **Launch class**
2. **Execution principal**
3. **Storage-world home**
4. **Control-surface form**
5. **Strongest safe sentence**

### 1) Launch class

This section should show:

- launch class (`interactive-session-app`, `prelogin-headless-runtime`, `policy-daemon`, `unknown`)
- whether user login is required
- start trigger (`user-login`, `system-boot`, `launchd`, `service-manager`, `manual`)
- keepalive posture
- start delay or jitter if known

The operator must be able to answer: **does this runtime require an interactive session?**

### 2) Execution principal

This section should show:

- principal account name
- principal class (`current-user`, `dedicated-runtime-user`, `local-service`, `local-system`, `unknown`)
- principal source (`manual selection`, `system default`, `migrated carry-forward`, `policy`)
- whether the principal differs from the reviewing user

The operator must be able to answer: **who really owns this runtime?**

### 3) Storage-world home

This section should show:

- storage root path
- world lineage (`same-world`, `new-world`, `adopted-world`, `unknown`)
- whether current roster/shares came from the prior world or from a clean/prepared world
- whether the chosen principal implies a new home path by default

The operator must be able to answer: **what state world will open under this launch class?**

### 4) Control-surface form

This section should show:

- local GUI presence (`present`, `suppressed`, `not-applicable`)
- headless control surface (`none`, `loopback-webui`, `lan-webui`, `api-only`, `unknown`)
- control exposure grade
- whether browser-only handling changes ordinary intake flows

The operator must be able to answer: **how will this runtime be controlled, and by whom?**

### 5) Strongest safe sentence

The page must end with one sentence such as:

- `same user-session app; login required`
- `pre-login headless runtime under dedicated principal`
- `sessionless runtime opens a different storage world`
- `launch class unclear; continuity not yet proven`

And it must also show the stronger blocked sentence it refuses, such as:

- `this is the same as backgrounding the app`
- `your existing world will definitely be reused`
- `control exposure is unchanged`

## Public objects

### `prelogin_runtime_contract`

Fields:

- `prelogin_runtime_contract_id`
- `seat_ref`
- `launch_class`
- `login_requirement`
- `start_trigger`
- `keepalive_posture`
- `start_delay_summary` nullable
- `principal_class`
- `principal_name`
- `principal_basis`
- `storage_root`
- `world_lineage_class`
- `control_surface_form`
- `control_exposure_grade`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Main surface

A compact row should read like one of these, not just `runs at startup`:

- `interactive-session app · current user · GUI present`
- `pre-login headless runtime · dedicated principal`
- `pre-login runtime · new storage world likely`
- `headless runtime · control audience widened`
- `launch class ambiguous · continuity unproven`

## Event language

Use phrases such as:

- `promoted to pre-login runtime`
- `launch class changed from interactive-session to pre-login`
- `runtime principal moved to dedicated account`
- `headless control surface replaced local GUI entry`

Avoid phrases such as:

- `enabled auto-start`
- `runs in background now`
- `made persistent`

Those lines are too weak and too flattening.

## CLI shape

```text
anonsync runtime launch-class show --seat self
anonsync runtime principal explain --seat self
anonsync runtime world preview --seat self --launch-class prelogin
```

## Design tests

The model is not explicit enough if any of these remain true:

- the operator can choose pre-login launch without seeing principal and world-lineage consequences
- `background` and `pre-login` still read as near-synonyms
- storage-home changes can happen without the contract sheet surfacing them
- control-surface replacement is learned only after the switch

## Non-clone reason

Current official Resilio docs still make pre-login runtime truth feel like launchd know-how rather than one ordinary product contract.
AnonSync should instead render launch class, principal world, and control form as a stable reviewed object.
