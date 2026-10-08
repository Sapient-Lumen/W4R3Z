# Pre-login mode caveat page, placeholders, link handoff, and session losses interface spec

## Why this page exists

A pre-login/headless runtime is not just a different start time.
It often carries feature-parity losses and workflow detours.
Current official Resilio docs still leave several of those costs spread across setup and WebUI articles:

- placeholder/selective-sync caveat in the Mac pre-login recipe
- browser/WebUI-only control when `use_gui` is false
- link-click share intake not working in WebUI
- ordinary session UI/tray habits no longer applying

AnonSync should collect those costs into one explicit mode-caveat page before the operator commits.

## Operator questions this page must answer

1. **Which ordinary desktop behaviors disappear or degrade in this mode?**
2. **Which features now require caveat flags or lose parity?**
3. **Which tasks now become manual browser work?**
4. **Which caveats are proven, inferred, or still unknown?**

## Required caveat families

### A. Placeholder / selective-sync compatibility

Show:

- placeholder compatibility state (`supported`, `requires caveat`, `not supported`, `unknown`)
- required config caveat if any
- whether the caveat changes the operator-visible semantics of selective fetch

### B. Intake and handler parity

Show:

- protocol/link-click intake parity
- whether browser-open or protocol-handler add is supported
- whether manual `enter key or link` flow is required

### C. Session UX losses

Show:

- local GUI availability
- tray/menu-bar availability
- local notifications class
- whether browser login/session now mediates ordinary control

### D. Transport and trust caveats

Show:

- HTTP/HTTPS posture
- self-signed warning expectation
- whether the control endpoint now requires manual trust/bootstrap on first use

### E. Operational patience costs

Show:

- boot/start delay expectation
- possible confusion windows (`configured`, `booting`, `not-yet-witnessed`, `restarting-under-keepalive`)

## Caveat posture labels

Each caveat row should carry one of:

- `reviewed and accepted`
- `review required`
- `proved live`
- `proved absent`
- `unknown`

## Public object

### `prelogin_mode_caveat_page`

Fields:

- `prelogin_mode_caveat_page_id`
- `seat_ref`
- `placeholder_compatibility_state`
- `placeholder_required_caveat` nullable
- `link_handoff_parity_state`
- `manual_intake_required` boolean
- `local_gui_state`
- `local_notification_state`
- `transport_posture`
- `bootstrap_warning_expectation`
- `start_delay_summary` nullable
- `accepted_caveats[]`
- `open_caveats[]`
- `generated_at`

## Main surface language

Use summaries like:

- `Pre-login mode requires browser/manual intake for shared links`
- `Placeholder behavior carries a reviewed caveat in this launch class`
- `Headless mode removes session UI cues; control remains via WebUI`

Avoid summaries like:

- `minor limitations`
- `advanced setup only`
- `works mostly the same`

Those are not tight enough.

## Design tests

The page fails if:

- placeholder/selective-sync caveats remain buried in setup steps
- protocol/link-intake loss is not called out before commit
- session UX losses are learned only after switching modes
- browser trust/transport caveats remain implicit

## Non-clone reason

Current official Resilio docs still disclose the right caveats, but only as scattered notes.
AnonSync should instead give the operator one durable page of accepted and still-open mode losses.
