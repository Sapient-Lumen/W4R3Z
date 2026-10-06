# ADR-0154: Publish-session end conditions and no-auto-resume posture

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0152 moved temporary sharing onto `net.publish.session` so B/C users no longer had to
normalize shadow tunnels or casual public listeners.
ADR-0153 then made audience/publicness explicit.

One expensive ambiguity still remained:

**what keeps a “temporary” publish session from quietly surviving as a restart-persistent tunnel?**

Current relay products are useful precisely because they make outbound-first sharing ergonomic,
but they also show the drift risk:
- some developer/test modes are explicitly temporary,
- some configurations live in daemon state or service config until reset,
- and some products encourage running a persistent background service for durable publication.

DeriveBSD needs a sharper archive-level answer.
Otherwise `net.publish.session` can still regress into “install agent, keep config around, and the share comes back after restart”, which is exactly the folklore lane this boundary was meant to avoid.

## Decision

1. `net.publish.session` now requires a `lifecycle` object.

2. The lifecycle object records two facts:
   - `end_conditions`: the automatic conditions that terminate the publish session
   - `resume_policy`: what must happen after interruption or restart

3. The allowed `lifecycle.end_conditions` values are:
   - `lease-expiry`
   - `manual-revoke`
   - `local-service-unavailable`
   - `initiating-user-session-end`
   - `support-session-end`
   - `operator-session-end`
   - `maintenance-window-end`
   - `host-reboot`

4. Every `net.publish.session` must include at least these end conditions:
   - `lease-expiry`
   - `manual-revoke`
   - `local-service-unavailable`
   - `host-reboot`

5. `lifecycle.resume_policy` is now fixed to `new-session-with-fresh-authority`.
   A publish session may be recreated later, but that recreation must mint a new `net.publish.session`
   with fresh authority evidence. The earlier session does not auto-resume.

6. Authority joins now imply extra required end conditions:
   - `authority.trigger = trusted-ui` implies `initiating-user-session-end`
   - `authority.trigger = support-session` implies `support-session-end`
   - `authority.trigger = operator-session` implies `operator-session-end`
   - `authority.trigger = maintenance` implies `maintenance-window-end`

7. Product-shape posture is fixed as follows:
   - **B (`workstation`)** and **C (`general_os`)** temporary shares are explicitly reboot-cleared and session/lease-bound.
   - **A (`fleet_host`)** and **D (`appliance_factory`)** may still use publish sessions only as exceptional bounded tooling, and they do not get a restart-persistent publication escape hatch through this lane.
   - durable, restart-persistent, policy-owned publication belongs on the existing `net.listen.*` service exposure lane instead.

## Consequences

- “Temporary share” now means something operationally precise: revocable, reboot-cleared, and unable to auto-resume from stale daemon/config state.
- Support bundles and explain surfaces can answer not only who a share was for, but also what was supposed to end it.
- Implementations remain free to use different relay providers, but they must not collapse provider persistence knobs into ambient platform authority.
- Durable ingress stays where it belongs: on `net.listen.policy` / `net.listen.grant` / `net.listen.receipt`.

## Why this is narrow enough

This ADR does **not** define:
- the exact UI wording for “share will end on logout/reboot”,
- how every provider adapter tears down its own local config,
- a universal restore-token story,
- or which relay vendor ships first.

It only fixes the missing lifetime boundary needed to stop relay-backed temporary sharing from quietly becoming persistent tunnel folklore.
