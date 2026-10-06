# ADR-0051: Remote assistance posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has a credible **capability-lane** model for remote assistance:
`docs/291-remote-assistance-sessions-as-evidence.md` composes ScreenCast / RemoteDesktop / data transfer / networking / consent into a receipted `support.session` workflow.

What the archive still lacked was the **product-shape default**.
Without that, A–D drift toward incompatible assumptions:

- A quietly grows a “just install a remote agent” host story,
- B forgets that remote control must be visible and secure-attention-gated,
- C normalizes legacy backdoors as ambient compatibility,
- D ships support hooks that are unacceptable in regulated or factory images.

We do **not** need to solve every protocol/relay/recording detail here.
We do need a stable, checkable answer to:

- which product shapes allow remote assistance by default,
- whether GUI control is even in scope,
- whether prompts or quorum are the authority model,
- and whether persistent remote-support state may exist outside explicit leases/policy.

## Decision

We define remote assistance as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json`.

### A) `fleet_host`

Default posture: `brokered-tty-console-recorded-no-gui-control`

- Remote assistance is an **operator/session** story, not a desktop-remoting story.
- Default support path is brokered TTY / serial / console assistance.
- If network transport is needed, it should be outbound-initiated or otherwise policy-derived; interactive host-side prompts are not the authority model.
- Recording/evidence is on-by-default for the support path.
- General-purpose remote GUI control of the host is out of scope by default.

### B) `workstation`

Default posture: `visible-user-mediated-view-or-control-with-lease`

- Remote assistance may include view-only and remote-control sessions.
- Sessions must be **visible**, **trusted-UI-mediated**, and **timeboxed**.
- Remote control requires a secure-attention transition before control becomes active.
- Clipboard/file transfer remain separate grants.
- Persistence must not become ambient authority: if the underlying portal/backend can remember permissions, DeriveBSD still treats the effective authority as a lease or explicit durable policy object with revoke.

### C) `general_os`

Default posture: `brokered-explicit-lease-no-ambient-agent`

- A brokered support path exists for both operator and desktop-ish use cases.
- The default must still be explicit start + lease + revoke, not a permanently enabled background agent.
- Compatibility adapters are allowed, but only as explicit, reviewable adapter lanes.

### D) `appliance_factory`

Default posture: `disabled-by-default-maintenance-only-recorded`

- Production / evidence-bearing appliance images do **not** ship with ambient remote-support authority enabled by default.
- Remote assistance, if enabled at all, is a maintenance-window / support-image / attended-station workflow.
- Recording and retained evidence are the default.
- Interactive prompts are not the authority model for production lanes.

## Consequences

- Product profiles now carry a stable `remote_assistance` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward ambient agents or stealth control.
- Open questions narrow to implementation detail: relay/transport choices, recording detail defaults, redaction/retention budgets, and quorum thresholds for high-risk scopes.

## Non-goals

- Choosing a concrete remoting protocol or relay service.
- Designing the full UI transport stack.
- Freezing the exact recording/export policy for every deployment.
