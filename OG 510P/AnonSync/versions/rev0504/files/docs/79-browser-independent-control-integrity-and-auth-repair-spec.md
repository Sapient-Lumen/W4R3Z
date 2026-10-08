# Browser-independent control integrity and auth-repair spec

The archive already has a control-access model and a bring-up review model.
What it still lacked was a durable public contract for a more operational question:

> what happens when browser-mediated control becomes unreliable, unavailable, distrusted, or half-visible, and how does the operator recover control without mutating unrelated daemon state?

This document answers that question.
It exists so AnonSync does not recreate the same failure mode visible in existing sync products, where Linux/headless administration is nominally supported, yet practical control truth still leaks into browser quirks, ad-block exceptions, trust-warning ritual, hidden fallback menus, and credential-reset folklore.

## Resilio-derived motivation

Current Resilio docs still distribute control-surface integrity across several separate support notes:

- WebUI is the default and only interface on Linux-based machines and the default for Windows service installs
- opening links directly in browser is not supported with WebUI; the operator must paste the key or link through a specific menu path instead
- some browsers or ad blockers can hide the `Share` button in WebUI
- HTTPS commonly uses a self-signed certificate, with a separate article recommending click-through, HSTS clearing, or browser override strings as practical recovery
- one WebUI-password reset path deletes `settings.dat`, which resets global preferences and duplicates the device in `My devices`, while another path uses config mode to avoid that collateral state change
- browser cookies are session-scoped, while workstation password posture, NAS password posture, and config-enforced credentials are expressed in different places

Those are useful support notes.
They are not one durable operator-facing control-integrity model.

## Core rule

Browser-rendered control is a projection of public server state.
It is never the only place where action availability, trust posture, or auth-repair meaning exists.
Every high-signal control action must have:

- a server-declared capability record
- an explicit denial or degradation reason when not currently available
- at least one browser-independent path for inspection or recovery
- a repair workflow that does not silently mutate unrelated durable state

## Public objects

### Control capability manifest

A first-class record describing what one control action is, which channels may render it, and why it may currently be unavailable.

Fields:

- `control_capability_id`
- `action` (`share-create`, `share-grant`, `claim-intake`, `expose-control`, `rotate-credential`, `retire-device`, `other`)
- `subject_scope`
- `required_scope` (`observe`, `mutate`, `admin`)
- `supported_channels[]` (`workbench-browser`, `cli`, `tui`, `api-client`, `automation`)
- `currently_available_channels[]`
- `degraded_channels[]`
- `denial_or_degradation_reason_refs[]`
- `fallback_channel_order[]`
- `last_evaluated_at`

### Control integrity report

A first-class report describing why browser-mediated control is degraded, distrusted, or incomplete.

Fields:

- `control_integrity_report_id`
- `class` (`browser-incompatible`, `content-blocked`, `tls-untrusted`, `hostcheck-failed`, `session-expired`, `capability-render-failed`, `other`)
- `subject_ref`
- `affected_channel_refs[]`
- `affected_capability_refs[]`
- `operator_visible_effect`
- `safe_fallback_refs[]`
- `requires_repair_case`
- `severity`
- `freshness_state`
- `created_at`
- `updated_at`

### Auth repair case

A first-class case describing how control credentials, trust bootstrap, or browser/session authority will be repaired.

Fields:

- `auth_repair_case_id`
- `kind` (`session-rotate`, `password-reset`, `token-reissue`, `tls-bootstrap`, `hostcheck-repair`)
- `target_endpoint_ref`
- `target_session_or_token_ref` nullable
- `state_root_ref`
- `requested_effect`
- `collateral_delta_expected` (`none`, `separate-reviewed-state-change-required`)
- `blocking_report_refs[]`
- `available_apply_channels[]`
- `receipt_promise`
- `created_at`
- `updated_at`

## Rules

1. **Server truth beats client luck.**  
   Buttons, menus, browser prompts, and popovers may render capability state. They do not define it.

2. **A missing control must degrade into an explanation, not disappearance.**  
   If an action cannot be rendered or used in one channel, the operator should see why and what safe fallback exists.

3. **Browser trust warnings are symptoms, not the security model.**  
   A product should never rely on `Proceed anyway`, HSTS clearing, or unsafe override strings as its ordinary administration story.

4. **Auth repair must be side-effect bounded.**  
   Regaining control authority must not silently reset unrelated preferences, duplicate devices, move state roots, or reopen a different durable control universe.

5. **Every high-signal control action needs one browser-independent path.**  
   Linux-first deployments cannot treat browser health as the sole condition for safe administration.

6. **Link/key/intake paths must not depend on browser handoff magic.**  
   If a browser cannot hand off a link directly, the product must still expose one first-class intake path whose semantics are identical across channels.

7. **Trust posture must be inspectable before repair is applied.**  
   The operator should be able to inspect certificate posture, hostcheck posture, and endpoint identity without resorting to raw storage or browser internals.

## Capability availability

Capability availability should compile from server-side facts such as:

- current endpoint exposure class
- current session/token scope
- current trust/bootstrap posture
- channel health and compatibility findings
- subject-local blockers such as policy, state-root verification, or degraded control access

A capability may be denied because the action is truly not allowed.
It may also be degraded because one client cannot render it honestly.
Those are different states and should not collapse into the same “button missing” outcome.

## Auth-repair boundaries

Auth-repair work should be allowed to do things such as:

- issue a new interactive token
- revoke a stale browser session
- rotate a Web/workbench password equivalent
- re-establish reviewed TLS trust
- repair hostcheck or trusted-proxy posture

Auth-repair work should **not** silently do things such as:

- reset unrelated global preferences
- duplicate device identity rows
- switch to a different state root
- re-run bring-up as though it were the same workflow
- revive broader exposure than the operator reviewed

If any of those broader effects are actually required, the repair case must stop and hand off to bring-up, state-root transition, or access-exposure review instead of pretending they are credential maintenance.

## CLI contract

Minimal commands:

```text
anonsync access capability list
anonsync access capability show ccp_01J...
anonsync access integrity list
anonsync access integrity show cir_01J...
anonsync access repair open --kind session-rotate --endpoint cep_01J...
anonsync access repair show arc_01J...
anonsync access repair apply arc_01J...
```

These commands should answer:

- which control actions are actually available right now and through which channels
- whether a missing workbench/browser action is policy denial or client degradation
- what safe fallback exists when browser trust or rendering is degraded
- whether a repair action changes only control authority or would require a separate reviewed state transition

## Workbench contract

The existing `Access` page should grow a `Control integrity` lane rather than forcing operators into troubleshooting folklore.
That lane should show:

- action availability by capability, not just by visible buttons
- active integrity findings for browser compatibility, content blocking, trust posture, and session expiry
- safe fallback channel for each degraded capability
- auth-repair cases in progress and their expected collateral delta
- recent receipts proving that repair changed only control authority

Primary actions should include:

- inspect capability availability
- inspect trust/bootstrap posture
- open a bounded repair case
- pivot to CLI/TUI/API fallback without changing meaning
- inspect recent integrity and repair receipts

## Design tests

The model is not explicit enough if any of the following remains true:

- a button can disappear because of browser or ad-block behavior without a server-declared capability denial/degradation record
- routine administration still expects `Proceed anyway`, HSTS clearing, or unsafe override strings as the normal way forward
- recovering browser/workbench access can silently reset preferences or duplicate devices
- Linux/headless operators lose the only honest path to inspect or perform a high-signal control action because the browser projection is unhealthy
- browser-based link handoff and manual paste/import are semantically different workflows

## Outcome

A mature AnonSync surface should let an operator move from `why is this action unavailable here?` to `is that policy or client degradation?` to `what safe fallback exists?` to `can I repair control authority without mutating anything else?` without leaving the shared public model.
That is what this document locks in.
