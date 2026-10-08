# Control access, endpoint exposure, and session-boundary spec

## Purpose

The archive already had a daemon API, loopback HTTP, and local bearer-token language.
What it still lacked was a durable public contract for a more operational question:

> who or what can currently control this daemon, through which endpoint, with which scope, and what changed when that access was exposed, rotated, or revoked?

This document answers that question.
It exists so AnonSync does not recreate the same failure mode visible in existing sync products, where control access is reconstructed from bind addresses, browser prompts, cookie behavior, config-file edits, and password-reset ritual.

## Resilio-derived motivation

Current Resilio docs still distribute control access across several separate surfaces:

- WebUI is the default and only interface on Linux-based machines and the default for Windows service installs
- moving from localhost-only to LAN reachability can mean unchecking `Allow connection from this device only`, editing `listen` to `0.0.0.0`, and restarting the service
- workstation WebUI passwords are optional, while NAS installs require them, and browser cookies last only for the browser session
- enabling HTTPS by config yields self-signed-certificate browser warnings with a separate remediation article
- one password-reset path says to delete settings files in the storage folder, which resets global preferences and duplicates the device in `My devices`
- service-account changes can quietly move the active storage folder and thereby change which state universe the operator is actually controlling

Those are useful support notes.
They are not one durable operator-facing control-access model.

## Core rule

Control access is explicit state.
Endpoint exposure, credential issuance, session authority, browser/proxy posture, mutation elevation, and access revocation are separate public facts.
They may be related.
They may not collapse into one overloaded notion of “the WebUI password” or “whatever browser is currently open”.

## Public objects

### Control access policy

A durable rule set describing how the daemon may be administered.

Fields:

- `control_access_policy_id`
- `primary_local_transport` (`unix-socket`, `named-pipe`)
- `loopback_http` (`disabled`, `enabled`)
- `allowed_exposure_classes[]` (`local-only`, `ssh-tunnel-reviewed`, `reverse-proxy-reviewed`, `trusted-lan-reviewed`, `custom-reviewed`)
- `authn_classes[]` (`os-user`, `issued-bearer-token`, `signed-browser-session`, `trusted-proxy-assertion`)
- `default_token_ttls`
- `default_session_ttls`
- `hostcheck_policy` (`strict-localhost`, `proxy-reviewed`, `custom-reviewed`)
- `trusted_proxy_refs[]`
- `browser_session_policy`
- `created_at`
- `updated_at`

### Control endpoint

A first-class record describing one reachable control-plane entry point.

Fields:

- `control_endpoint_id`
- `transport` (`unix-socket`, `named-pipe`, `loopback-http`, `ssh-forward`, `reverse-proxy`, `direct-http-reviewed`)
- `bind`
- `exposure_class`
- `authn_class`
- `tls_posture` (`not-applicable`, `local-http`, `daemon-tls`, `proxy-tls`)
- `hostcheck_policy`
- `proxy_ref` nullable
- `state_root_ref`
- `risk_state` (`local-only`, `reviewed-exposed`, `degraded`, `blocked`)
- `active_session_count`
- `last_verified_at`

### Access token

A durable credential object used by automation or interactive clients.
The secret value may be short-lived or one-time reveal, but the token object remains inspectable.

Fields:

- `access_token_id`
- `audience` (`cli`, `workbench`, `tui`, `automation`, `bridge`)
- `scope` (`observe`, `mutate`, `admin`)
- `issuance_mode` (`interactive`, `automation`, `delegated`)
- `expires_at`
- `idle_timeout` nullable
- `last_used_at` nullable
- `revoked_at` nullable
- `bound_endpoint_refs[]`
- `actor_ref`
- `created_at`

### Control session

A first-class record describing one active or recent authenticated control session.

Fields:

- `control_session_id`
- `endpoint_ref`
- `token_ref` nullable
- `client_kind` (`cli`, `workbench-browser`, `tui`, `automation`, `api-wrapper`)
- `scope`
- `origin_summary`
- `proxy_chain[]`
- `issued_at`
- `last_seen_at`
- `expires_at`
- `revoked_at` nullable
- `csrf_or_hostcheck_state`
- `state_root_ref`

### Mutation grant

A first-class short-lived authority object for reviewed interactive mutation.

Fields:

- `mutation_grant_id`
- `action_family` (`grant-change`, `control-expose`, `destructive-allow`, `successor-apply`, `compromise-apply`, `other`)
- `subject_scope`
- `issuer_session_ref` nullable
- `issuer_token_ref` nullable
- `approved_endpoint_refs[]`
- `state_root_ref`
- `user_presence_class`
- `batch_budget`
- `issued_at`
- `expires_at`
- `consumed_at` nullable
- `revoked_at` nullable

### Access receipt

A durable record that access posture changed.

Fields:

- `access_receipt_id`
- `action` (`issue-token`, `revoke-token`, `open-endpoint`, `close-endpoint`, `trust-proxy`, `revoke-session`, `rotate-access-posture`)
- `subject_ref`
- `actor_ref`
- `report_refs[]`
- `effective_delta`
- `created_at`

## Rules

1. **Local IPC is the primary control surface.**  
   Unix socket or named pipe comes first. HTTP and browser surfaces are secondary projections.

2. **Leaving localhost is a reviewed exposure change, not a harmless bind tweak.**  
   SSH tunnel, reverse proxy, and non-loopback listener are different exposure classes and should render as such.

3. **Credential issuance is separate from session creation and from mutation elevation.**  
   An issued token, an active browser session, a trusted proxy assertion, and a short-lived mutation grant are not interchangeable.

4. **Browser warnings are symptoms, not the security model.**  
   A product should never rely on “click through”, HSTS-clearing, or magic browser override strings as its real access story.

5. **Access repair must not mutate unrelated durable state.**  
   Resetting browser/session credentials should not silently duplicate devices, reset global preferences, or otherwise change control subjects unrelated to the access problem.

6. **Proxy and tunnel posture must be inspectable.**  
   If a reverse proxy, SSH tunnel, or forwarded header is part of control access, the operator should be able to inspect that fact directly.

7. **Interactive and automation authority stay distinct.**  
   A long-lived automation token should not masquerade as an ordinary browser session, and vice versa.

8. **Sessions are revocable, inspectable, and bounded.**  
   The operator should be able to answer who is connected now, through which endpoint, with what scope, and until when.

9. **Browser/workbench inspectability is not enough for high-signal apply.**  
   Dangerous mutation should require a short-lived reviewed mutation grant or an equivalently explicit mutate/admin credential object.

## Exposure classes

AnonSync does not need infinite deployment shapes in v1.
It does need a stable vocabulary for the common ones:

- `local-only`
- `ssh-tunnel-reviewed`
- `reverse-proxy-reviewed`
- `trusted-lan-reviewed`
- `custom-reviewed`

The important rule is that each class says what network surface exists and what compensating control is expected.
No class should merely mean “someone changed the bind address somewhere”.

## CLI contract

Minimal commands:

```text
anonsync access show
anonsync access endpoint list
anonsync access endpoint show cep_01J...
anonsync access gate show --action control-expose --subject endpoint:cep_01J...
anonsync access grant issue --action control-expose --subject endpoint:cep_01J... --ttl 10m
anonsync access grant show mgr_01J...
anonsync access grant revoke mgr_01J...
anonsync access expose plan --class ssh-tunnel-reviewed
anonsync access expose apply apl_01J... --grant mgr_01J...
anonsync access token issue --audience automation --scope mutate --ttl 8h
anonsync access token revoke tok_01J...
anonsync access session list
anonsync access session show css_01J...
anonsync access session revoke css_01J...
anonsync access receipt show acr_01J...
```

These commands should answer:

- whether control is still local-only or intentionally exposed
- which endpoint, proxy, or tunnel currently carries a session
- whether current inspectability is enough or a reviewed mutation grant is still required
- whether a token or mutation grant is interactive, automation-oriented, active, consumed, or revoked
- what receipt proves that access or mutation-elevation posture changed

## Workbench contract

The workbench should expose an `Access` page distinct from both `Attention` and `System State`.
Its job is not to replace the daemon API.
Its job is to answer:

- what control surfaces exist right now
- which are local-only versus reviewed-exposed
- which sessions and tokens are active
- what risky access or mutation-elevation change happened recently

The page should support:

- filtering endpoints by exposure class and risk state
- filtering sessions by client kind, scope, and expiry posture
- revoking sessions and tokens without leaving the workbench
- jumping from an access receipt to the backing plan, report, or subject
- inspecting trusted-proxy and hostcheck posture without raw config archaeology

## Design tests

The model is not explicit enough if any of the following remains true:

- the operator still needs to edit raw config files just to know whether the control plane is reachable beyond localhost
- password or credential reset can silently mutate unrelated device or preference state
- browser trust-warning bypass is still treated as a normal administration workflow
- reverse-proxy, SSH-forwarded, and direct-exposed access all look semantically the same
- session revocation is not later auditable

## Outcome

A mature AnonSync surface should let an operator move from `who can currently control this daemon?` to `through which endpoint?` to `with what scope?` to `what changed when I exposed or revoked it?` without leaving the shared public model.
That is what this document locks in.
