# Headless launch review page, launchd user, storage home, WebUI audience, and delay interface spec

## Why this page exists

Once pre-login runtime is requested, the operator should get one high-friction but very clear review surface.
The review is not about whether automatic startup sounds handy.
It is about whether the operator actually wants:

- a sessionless launch path
- a possibly different runtime user
- a specific storage home
- browser-mediated control
- a widened control audience
- a delayed/keepalive launch posture

Current official Resilio docs still spread those facts across setup steps.
AnonSync should own them in one page.

## Operator questions this page must answer

1. **Which account will run this world?**
2. **Which storage home will open under that account?**
3. **Will control remain local-only, or be reachable from the LAN?**
4. **How soon after boot should I expect the runtime to exist?**
5. **What ordinary app/session affordances am I giving up?**

## Required panes

### A. Requested launch shape

Show:

- requested launch class
- requested start trigger
- keepalive on/off
- expected boot/login dependence

### B. Principal and storage preview

Show a side-by-side preview:

- current principal / storage home
- proposed principal / storage home
- continuity verdict (`same-world likely`, `new-world likely`, `manual adoption required`, `unclear`)

### C. Headless control audience

Show:

- listener posture (`loopback-only`, `LAN-exposed`, `custom bind`)
- transport posture (`HTTP`, `HTTPS self-signed`, `HTTPS operator cert`, `unknown`)
- credential posture (`required`, `optional-but-empty`, `missing`, `unknown`)
- audience delta

### D. Startup witness expectations

Show:

- expected delay before runtime should be visible
- whether a helper script or orchestrator delay exists
- whether keepalive means spontaneous restart is expected later

### E. Lost parity / new burden list

Show the exact burden list, for example:

- local app UI replaced by browser control
- local protocol/link click handoff may not work
- share intake may require manual entry
- ordinary session cues/tray presence absent
- additional mode caveats still require review

## Decision ladder

Allowed commit buttons should be exact and explicit:

- `Accept pre-login runtime under reviewed principal`
- `Keep session-bound app`
- `Review control exposure first`
- `Review mode caveats first`

Never use a bare button like `Enable`.

## Public object

### `headless_launch_review`

Fields:

- `headless_launch_review_id`
- `requested_launch_class`
- `requested_start_trigger`
- `requested_keepalive`
- `current_principal`
- `proposed_principal`
- `current_storage_home`
- `proposed_storage_home`
- `world_continuity_verdict`
- `listener_posture`
- `transport_posture`
- `credential_posture`
- `audience_delta_summary`
- `expected_start_delay_summary`
- `lost_affordances[]`
- `next_required_review[]`
- `decision`
- `reviewed_at`

## Main surface language

Use summaries like:

- `Pre-login headless runtime under dedicated user; LAN control exposure requested`
- `New storage home likely; continuity review required`
- `Boot-start expected after helper delay; browser-only control`

Avoid summaries like:

- `Start automatically`
- `Launch at boot`
- `Run headless`

Those are incomplete.

## Design tests

The page fails if:

- audience widening is not visible next to launch-class change
- storage-home change is hidden until after apply
- delay/keepalive semantics remain support-lore
- browser-only intake losses are absent from the burden list

## Non-clone reason

Current official Resilio docs still let the real meaning of `run before login` hide inside a setup recipe.
AnonSync should instead make the review about world lineage, control audience, and operator burden before commit.
