# Safety-critical channel-parity and surface-capability spec

The archive already has control-access policy, browser/control integrity, mutation gates, bring-up review, exit review, and the wider pattern language.
This document answers the narrower practical question those abstractions still left open:

> what must a real operator surface literally show when the same requested action is entered from different channels, so AnonSync does not drift back into browser-only semantics, Linux/WebUI caveats, config-mode feature loss, or "try it from another client" folklore?

This is the channel-parity companion to `55-control-access-and-session-boundary-spec.md`, the action-availability companion to `79-browser-independent-control-integrity-and-auth-repair-spec.md`, the apply-safety companion to `80-reviewed-mutation-credential-and-apply-gate-interface-spec.md`, and the multi-surface honesty companion to `39-interface-pattern-language.md`.

## Why this needs its own spec

Resilio's docs make the seam unusually clear.
`Guide to Linux, and Sync peculiarities` says Linux has no native GUI, that most parameters need manual configuration, and that share-link intake and license activation on Linux are handled through `Enter a key or link` in the WebUI.
`Configuring WebUI` says WebUI is the default and only interface on Linux-based machines.
`Running Sync in configuration mode` says config mode can set up only Standard folders and that if shared folders are specified in the config file the WebUI is disabled.
`Sync doesn't start when opening Link in browser` says opening a share link is impossible when Sync is accessed through WebUI and must instead be handled by manual paste.
`There's no Share button in Web UI…` says browser incompatibility or ad-blocking can make the Share button disappear.
`Power user preferences` adds that `disable_remove_from_all_devices` is ignored in Linux WebUI.

The lesson is not merely that browsers can be annoying.
The lesson is that a useful product can still leave one of the most dangerous control questions under-specified:

- is this action really unsupported, or only unavailable in the current client/channel?
- does changing channel preserve the same review, subject, scope, and safety grammar, or does the action quietly become weaker or different?
- does a Linux/headless operator still get the strongest destructive-action guardrails, or do those guardrails only exist on some richer surface?
- when a channel fails, how does the operator continue the same reviewed action without starting over from folklore?

AnonSync should not clone that shape.

## Core rule

Every safety-critical control action should have one server-declared capability identity and one review identity.
A channel may be:

- fully supported
- inspect-only
- degraded but handoff-capable
- honestly unavailable

A channel may not silently redefine the action's semantics, omit mandatory review sections, or offer a weaker confirm path just because the richer surface is absent.

## Which actions are in scope

This spec is primarily about actions whose safety meaning cannot be allowed to drift by surface.
That includes at least:

- destructive share/device/constellation exit or delete actions
- control exposure changes that leave local-only posture
- authority or grant mutations with non-trivial blast radius
- successor, replacement, or continuity-sensitive apply steps
- compromise, stale-state, or destructive-replay review outcomes
- any action whose safe use depends on mutation grants, special receipts, or broader reviewed proof

Low-risk read-only inspection can be more freely projected.
High-signal apply paths cannot.

## Entry points that must converge

The product may offer several ergonomic entry points:

- a workbench button that says `Continue in CLI`
- a workbench explanation that says the current browser is degraded and names the safe fallback
- CLI `access capability show ccp_01J...`
- CLI `access handoff create --action exit-share --subject share:shr_01J... --to cli`
- a daemon-side refusal that emits capability+integrity state and an optional handoff instead of letting the action simply disappear
- an API client that inspects the same review subject and render-order before apply

But these must all converge on the same public capability, integrity, gate, and receipt model.
The operator should never have to guess whether one channel is the real product and another is an underpowered convenience shell.

## Fixed review order

Every non-trivial channel-parity review should render the same sections in the same order:

1. **Requested action and subject**
2. **Capability and semantic parity**
3. **Current channel and degradation facts**
4. **Safe fallback and handoff**
5. **Apply guarantees and review continuity**
6. **Receipt promise**

### 1) Requested action and subject

This section should show:

- the exact requested action family
- the subject and blast radius
- whether the action is inspect-only, guarded, or high-signal apply
- which review family owns the action (`exit`, `authority-mutation`, `control-expose`, `successor`, `other`)

The operator must be able to answer: **what action am I actually trying to perform, on what subject, and how dangerous is it?**

### 2) Capability and semantic parity

This section should show:

- which channels can render the action honestly
- whether the action is fully supported, inspect-only, degraded-but-handoffable, or unavailable on the current channel
- whether parity is mandatory for this action or whether inspect-only projection is acceptable
- whether the current channel would lose review sections, scope truth, admissible actions, or receipt meaning if it tried to continue locally

The operator must be able to answer: **is the action genuinely supported here, and if not, what semantic truth would be lost?**

### 3) Current channel and degradation facts

This section should show:

- the current channel/client kind (`workbench-browser`, `cli`, `tui`, `api-wrapper`, `automation`)
- any client-specific degradation, incompatibility, policy block, or trust issue affecting the action
- whether the action is missing because of browser render failure, policy, role/scope, unsupported substrate, or deliberate inspect-only posture
- whether the action is absent only visually or also blocked by daemon policy

The operator must be able to answer: **why is this action degraded here, and is that because of rendering, trust, policy, or real unsupported scope?**

### 4) Safe fallback and handoff

This section should show:

- the preferred fallback channel order for this action
- whether a cross-channel handoff can preserve the same subject, review family, mutation gate, and blocker context
- whether a fresh review is required because the target channel changes trust, endpoint, or state-root posture
- whether the handoff is inspect-only or apply-capable

The operator must be able to answer: **how do I continue the same action safely in another channel without restarting the meaning from scratch?**

### 5) Apply guarantees and review continuity

This section should show:

- whether the same mandatory review grammar will remain intact after handoff
- whether the same mutation grant or gate evaluation still applies in the target channel
- whether the target channel can perform apply or only continue inspection/preflight
- which facts would force the action to stop and reopen broader review instead of continuing seamlessly

The operator must be able to answer: **if I switch channels, do I still have the same reviewed action, or am I crossing into a different control story?**

### 6) Receipt promise

This section should show:

- which receipt or handoff receipt will exist after defer, handoff, apply, or refusal
- what it will later prove about capability state, degradation facts, chosen channel, preserved review identity, and any reopened review boundary
- whether the receipt remains provisional because integrity, endpoint, or state-root facts changed during handoff
- what later audit survives if the action is resumed from yet another channel

The operator must be able to answer: **what later evidence will prove why this action continued here, moved elsewhere, or stopped?**

## Public objects

### Review handoff

A first-class object describing a safe cross-channel continuation of one reviewed action.

Fields:

- `review_handoff_id`
- `action`
- `subject_ref`
- `review_family`
- `source_channel`
- `target_channel`
- `capability_ref`
- `integrity_report_refs[]`
- `mutation_gate_ref` nullable
- `preserved_section_order[]`
- `requires_fresh_review`
- `expires_at`
- `consumed_at` nullable
- `created_at`

### Handoff receipt

A first-class receipt proving that one reviewed action was continued, refused, or reopened across channels without silently changing semantics.

Fields:

- `handoff_receipt_id`
- `review_handoff_ref`
- `result` (`continued`, `reopened-review`, `expired`, `refused`, `consumed-with-apply`)
- `source_channel`
- `target_channel`
- `preserved_subject_ref`
- `preserved_review_family`
- `gate_continuity_state`
- `created_at`

## What the surface must never imply

The channel-parity surface must never imply that these are the same thing:

- a missing button versus a genuinely unsupported action
- inspect-only projection versus apply-capable projection
- browser/client degradation versus policy denial
- switching channels versus reopening a weaker or different action
- a degraded local render versus permission to bypass the reviewed grammar entirely
- `not shown here` versus `safe to perform without review elsewhere`

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## Linux/headless parity rule

A Linux-first product has to assume that important actions will be entered from browsers, SSH sessions, TUIs, headless automation, and recovery shells.
So surface capability and handoff truth must survive across those channels.
It is not acceptable for one richer surface to show mandatory review grammar while Linux/headless falls back to missing buttons, weakened destructive controls, or `try another client` folklore.

## Relationship to nearby specs

Channel-parity review should often hand off to nearby review families, but it should not dissolve into them.

- **Control-integrity review** explains why one client is degraded.
  Channel-parity review explains how the same action survives that degradation.
- **Mutation-gate review** explains whether current authority is enough to apply.
  Channel-parity review explains whether changing channels preserves that gate story.
- **Exit / authority / successor / compromise review** explain the subject-specific action grammar.
  Channel-parity review explains whether that grammar remains intact across surfaces.
- **Bring-up review** explains whether the operator is even controlling the intended state universe.
  Channel-parity review explains whether a channel change crosses into a different universe and therefore must reopen review.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync access handoff show <review_handoff_id> --view review`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether the current channel is inspect-only, degraded-but-handoffable, or honestly unavailable for a safety-critical action.

## Why this is worth the trouble

AnonSync only justifies its extra interface complexity if action meaning also becomes easier to keep stable.
A fixed channel-parity and handoff grammar is how the archive avoids rebuilding a system where Linux/WebUI quirks, config-mode loss, disappearing buttons, manual link-paste fallback, and ignored safety preferences are all individually documented, yet the full meaning of “can I perform this action here, and if not, how do I continue the same reviewed action safely elsewhere?” still depends on which support article the operator happened to remember first.
