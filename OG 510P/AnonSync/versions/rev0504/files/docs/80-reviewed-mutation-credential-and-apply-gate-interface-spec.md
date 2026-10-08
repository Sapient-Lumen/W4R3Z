# Reviewed mutation credential and apply-gate interface spec

The archive already has a control-access model, a session-boundary model, reviewed bring-up, and a browser-independent control-integrity model.
What it still lacked was a durable public answer to a narrower practical question:

> when a currently visible control session wants to mutate real state, what must the operator see before apply, and what stops an ambient browser tab, cookie, or remembered password from masquerading as reviewed mutation authority?

This document answers that question.
It exists so AnonSync does not recreate the same failure mode visible in existing sync products, where the operator can inspect state in a browser yet still has to guess whether the current session is really allowed to widen exposure, rotate authority, replay destructive changes, or rewrite grants.

## Why this needs its own spec

The access/session model says who is connected.
The control-integrity model says whether the current client can render control honestly.
Those are necessary, but they still leave one dangerous gap:

- a browser session can be real, healthy, and authenticated, yet still be the wrong thing to trust for a high-signal mutation
- a remembered password or injected config credential can reopen the workbench without answering whether the current operator just re-proved mutation intent
- a state-root or service-user change can reopen a different control universe while the browser still looks familiar

AnonSync should not let `I still have the tab open` or `the password worked` stand in for one explicit mutation contract.

## Resilio-derived motivation

Current Resilio docs still distribute mutation authority across several separate support notes:

- `Configuring WebUI` says WebUI is the default and only interface on Linux-based machines, that workstation passwords are optional, and that browser cookies last only for the browser session
- the same doc says login/password can be defined in config, then later stored in Sync settings after acceptance
- `Guide to Linux, and Sync peculiarities` says Linux/headless startup uses flags such as `--storage`, `--identity`, and `--webui.listen`, and the default bind is loopback unless the operator explicitly widens it
- `Sync Service Troubleshooting on Windows` says changing the service account can open a different storage folder entirely, leaving prior folders absent and requiring re-add/re-share
- `Browser warning "Your connection is not private"` still treats browser click-through, HSTS clearing, or custom cert injection as practical trust bootstrap for WebUI over HTTPS

Those are useful support notes.
They are not one durable mutation-authority contract.

## Core rule

Observe and mutate are separate public states.
A healthy browser/workbench session may be enough to inspect.
It is not automatically enough to apply non-trivial mutation.

Non-trivial mutation should require one of the following explicit authority objects:

- a reviewed short-lived **mutation grant** bound to subject scope, session/channel, endpoint, and active state root
- a separately issued mutate/admin credential object whose scope and audience are already explicit enough to satisfy the same gate

The product should never rely on ambient session cookies, remembered workstation passwords, or browser continuity alone as proof that the current actor may now mutate important state.

## Entry points that must converge

The product may offer several ergonomic entry points:

- a danger action in the workbench
- a CLI `apply` command that hits a protected subject
- a TUI review sheet
- an API client attempting a high-signal mutation
- an automation client using a dedicated mutate/admin token

But these must converge on the same public gate model.
The operator should never have to wonder whether one surface required renewed authority while another merely trusted that the browser session already existed.

## Fixed review order

Every non-trivial mutation gate should render the same sections in the same order:

1. **Current session and endpoint**
2. **Requested mutation and subject scope**
3. **Required authority and grant scope**
4. **Binding and freshness**
5. **Blockers and fallback**
6. **Receipt promise**

### 1) Current session and endpoint

This section should show:

- current session ID and client kind
- endpoint exposure class and trust posture
- bound state root / runtime target
- whether the current session is observe-only, mutate-capable, or admin-capable
- any integrity finding that already weakens confidence in the channel

The operator must be able to answer: **which control path am I using right now, and what authority does it honestly have before any new grant is issued?**

### 2) Requested mutation and subject scope

This section should show:

- requested action family (`grant-change`, `delete-wave-allow`, `control-expose`, `root-move`, `successor-cutover`, `compromise-apply`, `other`)
- subject reference and stable IDs
- blast-radius summary
- whether the mutation is local-only, share-scoped, constellation-scoped, or daemon-global
- whether the change is reversible, destructive, or continuity-sensitive

The operator must be able to answer: **what exactly am I trying to change, and how far does it reach?**

### 3) Required authority and grant scope

This section should show:

- whether current authority already satisfies the gate or a mutation grant is required
- the minimal admissible grant scope
- whether the grant is one-shot, batch-bounded, or reusable for a short reviewed window
- whether higher authority is blocked on a stronger review family instead of a simple grant

The operator must be able to answer: **what fresh authority, if any, is required for this mutation and how narrowly can it be expressed?**

### 4) Binding and freshness

This section should show:

- channel binding (`workbench-browser`, `cli`, `tui`, `automation`)
- endpoint binding and active state-root binding
- grant TTL / idle window
- required user-presence or re-auth class
- invalidation conditions such as root change, session rotation, or endpoint drift

The operator must be able to answer: **what keeps this authority narrow, and what would automatically invalidate it?**

### 5) Blockers and fallback

This section should show:

- gate blockers (`grant-required`, `re-auth-required`, `endpoint-mismatch`, `state-root-mismatch`, `integrity-degraded`, `review-escalation-required`)
- safe next action (`issue grant`, `switch to CLI`, `open broader review`, `stop`)
- whether a safer browser-independent path exists immediately
- whether the request must hand off into compromise, bring-up, successor, or destructive-replay review instead of simple apply

The operator must be able to answer: **what stops apply right now, and what is the honest next step?**

### 6) Receipt promise

This section should show:

- which receipt will prove the authority elevation and later mutation
- whether the grant itself emits a receipt, or only the later mutation does, or both
- what later evidence will prove the channel, endpoint, scope, and expiry posture that existed at apply time

The operator must be able to answer: **what later evidence will prove that this mutation was explicitly authorized rather than casually implied by an old session?**

## Public objects

### Mutation gate result

A first-class gate evaluation describing what authority is currently required for one attempted mutation.

Fields:

- `mutation_gate_result_id`
- `action`
- `subject_ref`
- `current_session_ref` nullable
- `current_token_ref` nullable
- `required_authority` (`none`, `mutation-grant`, `mutate-token`, `admin-token`, `broader-review-required`)
- `gate_state` (`ready`, `grant-required`, `re-auth-required`, `endpoint-mismatch`, `state-root-mismatch`, `integrity-degraded`, `blocked`)
- `acceptable_scope_summary`
- `blocking_reason_refs[]`
- `safe_next_actions[]`
- `evaluated_at`

### Mutation grant

A first-class short-lived authority object for reviewed interactive mutation.

Fields:

- `mutation_grant_id`
- `action_family`
- `subject_scope`
- `issuer_session_ref` nullable
- `issuer_token_ref` nullable
- `approved_channels[]`
- `approved_endpoint_refs[]`
- `state_root_ref`
- `user_presence_class` (`same-session-confirmed`, `re-authenticated`, `hardware-backed`, `delegated-none`)
- `batch_budget`
- `issued_at`
- `expires_at`
- `consumed_at` nullable
- `revoked_at` nullable
- `receipt_promise`

## What should normally require a grant or equivalent explicit mutate credential

The exact v1 line can stay somewhat conservative, but the product should assume that at least these classes are non-trivial:

- widening control exposure beyond local-only
- issuing or revoking powerful tokens
- successor cutover, state-root move/import, or reviewed continuity apply
- live authority changes on shares, peers, or constellations
- destructive replay acceptance or share-wide delete/overwrite approval
- compromise containment that freezes, revokes, rotates, or widens observation
- topology or path actions that can rewrite containment or propagation boundaries

Purely presentational actions such as opening details, filtering lists, or acknowledging a delivery lane should not need a mutation grant unless they are secretly doing more than presentation.

## Rules

1. **Observe is the default; mutate is explicit.**  
   Especially for browser/workbench sessions, ordinary visibility should not imply high-signal apply authority.

2. **Ambient browser continuity is not mutation proof.**  
   Cookie survival, remembered password acceptance, or tab continuity is never sufficient evidence on its own.

3. **Mutation grants must be narrow.**  
   They should be bound to subject scope, channel, endpoint, state root, time, and a declared action family.

4. **Repair does not silently elevate.**  
   Auth repair may restore inspectability or session continuity. It should not quietly mint fresh mutation authority.

5. **State-root or endpoint drift invalidates interactive elevation.**  
   If the daemon attaches different state, the endpoint changes class, or integrity degrades materially, the old grant should fail closed.

6. **Batch elevation must say its budget.**  
   If one grant can cover several operations, the operator should see the batch scope and exhaustion rule directly.

7. **Higher-order review beats casual elevation.**  
   Some actions should hand off into bring-up, compromise, destructive-replay, or successor review rather than accepting a generic grant.

8. **CLI and workbench must tell the same truth.**  
   A headless operator must be able to inspect the same gate and grant state that a browser operator sees.

## CLI contract

Minimal commands:

```text
anonsync access gate show --action control-expose --subject endpoint:cep_01J...
anonsync access grant issue --action control-expose --subject endpoint:cep_01J... --ttl 10m
anonsync access grant show mgr_01J...
anonsync access grant revoke mgr_01J...
anonsync access grant list
```

Any protected `apply` path should be able to say exactly why it stopped, for example:

```text
$ anonsync access gate show --action grant-change --subject share:shr_01J...
Mutation gate
-------------
1. Current session and endpoint
   Session: css_01J... (cli)
   Endpoint: local-only unix-socket
   Current authority: observe

2. Requested mutation and subject scope
   Action family: grant-change
   Subject: share engineering-notes
   Blast radius: share authority + future delegate memory

3. Required authority and grant scope
   Required authority: mutation-grant
   Minimal grant scope: share:shr_01J... / action-family grant-change
   Batch budget: one reviewed apply

4. Binding and freshness
   Channel binding: cli
   State root: srt_01J...
   TTL if issued now: 10m
   User presence: re-authenticated

5. Blockers and fallback
   Gate state: grant-required
   Safe next action: issue mutation grant

6. Receipt promise
   Grant receipt will prove scope, binding, TTL, and later consume state.
```

## Workbench contract

The `Access` page should grow a `Mutation authority` lane in addition to endpoints, sessions, tokens, and integrity findings.
That lane should show:

- current session authority state (`observe`, `mutate`, `admin`)
- recent gate checks that blocked apply
- active mutation grants and their expiry/batch budget
- which dangerous actions require a fresh grant instead of trusting the ambient session
- receipts proving grant issue, consume, expiry, or revocation

When a workbench operator presses a dangerous action, the product should not merely flash `Confirm password` or `Are you sure?` unless that dialog also renders the fixed review order above.

## Cross-surface parity rule

GUI, browser/workbench, TUI, and CLI may differ in layout density.
They may not differ in:

- whether current authority is observe-only or mutate-capable
- whether the attempted action is blocked on grant, re-auth, broader review, or true policy denial
- what subject scope the grant would cover
- what endpoint and state-root binding would invalidate it
- what receipt proves the authority that existed at apply time

If one surface renders those facts while another merely asks for the password again, the product has already regressed.

## Why this is worth the trouble

A privacy-respecting, Linux-first sync product cannot treat `authenticated browser session` as the end of the story.
It has to make one further distinction legible:

- being able to see state
- being able to mutate state

A fixed mutation-gate grammar is how AnonSync avoids rebuilding a system where access is inspectable on paper, yet the most important changes still depend on whether a browser tab happened to be open, which service account launched the daemon, or whether a remembered credential got accepted without a fresh review of blast radius.
