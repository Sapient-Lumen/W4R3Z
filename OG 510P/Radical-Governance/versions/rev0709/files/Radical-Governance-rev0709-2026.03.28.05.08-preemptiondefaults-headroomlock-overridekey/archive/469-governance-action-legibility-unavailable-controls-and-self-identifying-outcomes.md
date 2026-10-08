# 469 — Governance-action legibility, unavailable controls, and self-identifying outcomes

## One-line thesis

Consequential public-AI services and operator consoles should say exactly which action is unavailable or completed, why, and what unlock path or alternative route exists, rather than collapsing meaningful state into greyed-out controls or generic success and error prose.

## Why this matters

A rights-bearing service often fails at the moment where a person tries to *do* something, not merely read something.

A claimant tries to file an appeal and sees a disabled button with no reason. An operator tries to export a packet and gets a generic “error.” A reviewer sees “updated successfully” but cannot tell whether the system refreshed a notice, resubmitted a case, escalated an incident, or merely saved local draft state. A public record suggests that human review exists, yet the actual request control is unavailable with no visible path to unlock it. In those moments, governance becomes ambiguous at the exact point where contestability should be strongest.

The archive already requires notice, explanation, durable status, and alternative human channels. What it still lacked was one note dedicated to the **action surface itself**: the button, command, menu item, or request path that lets someone seek recourse, export evidence, trigger review, or acknowledge a consequential state change.

## Pattern pack

### 1. Name the exact action, not only the broad area

Controls should say what they do in operational language, such as:

- file appeal,
- request human review,
- download evidence packet,
- pause live use,
- refresh public record,
- or acknowledge incident notice.

Generic labels like “continue,” “manage,” “submit,” or “update” are often too weak for consequential governance.

### 2. If an action is unavailable, explain why in typed terms

An unavailable control should say whether it is blocked because of:

- missing prerequisite information,
- current case phase,
- expired authority,
- unresolved integrity check,
- role mismatch,
- temporary outage,
- legal or policy prohibition,
- or because the action has already been completed.

People should not have to reverse-engineer governance from a disabled surface.

### 3. Distinguish unavailable, prohibited, completed, and not-applicable

Those states are not interchangeable.

- **Unavailable** means the action may become reachable.
- **Prohibited** means the route is not allowed in this context.
- **Completed** means the action already occurred.
- **Not applicable** means the route does not belong to this case or role.

One shared “disabled” style can hide materially different governance meaning.

### 4. Show the unlock path or alternative route

If a meaningful action cannot be taken from the current surface, the archive should preserve the next honest route, such as:

- complete a prerequisite field,
- wait for a pending review stage,
- contact a named office,
- use a phone, webchat, or in-person assisted route,
- or open the canonical surface that owns the action.

A blocked digital control with no visible alternative is often a rights failure disguised as interface state.

### 5. Keep action outcomes self-identifying

When an action succeeds or fails, the resulting message should name the action that just happened. Prefer messages like:

- appeal filed,
- packet export blocked: missing witness,
- public notice refreshed,
- or override request rejected: expired authority.

Avoid outcome text that says only “done,” “saved,” “updated,” or “error” when the action itself matters for accountability.

### 6. Preserve accessible discoverability for unavailable controls where appropriate

If a control is intentionally shown to communicate that an option exists but is currently unreachable, the surface should preserve a discoverable explanation for assistive technology and keyboard users. Where a hidden control would erase meaningful knowledge, prefer a visibly unavailable control plus a clear description over silent removal.

### 7. Treat repeated blocked-action attempts as governance signal

If many users or operators repeatedly hit a blocked route, that is evidence. It may mean:

- the workflow is confusing,
- the action is exposed at the wrong time,
- eligibility rules are poorly explained,
- or the supposed fallback path is not actually functioning.

Blocked attempts belong in the governance telemetry story, not only the UI bug backlog.

## Guardrails

- Do not rely on color or disabled state alone to communicate consequential unavailability.
- Do not let generic outcome messages erase which action just succeeded or failed.
- Do not hide alternative channels or assisted routes when digital action is blocked.
- Do not collapse completed, prohibited, and temporarily unavailable into one fuzzy state.
- Do not remove a meaningful action surface so completely that users cannot learn the route exists.

## Failure modes

- **grey-button opacity**: a blocked control reveals no reason and no next step.
- **generic outcome laundering**: action-specific accountability disappears into “saved” or “error.”
- **silent recourse loss**: appeal or review exists in policy but not on the actionable surface.
- **state-collapse disabling**: prohibited, expired, and completed routes all look the same.
- **unmeasured blockage**: repeated failed attempts never become governance evidence.

## Practical tests

A governance-action surface passes when it can answer yes to all of the following:

1. Does each consequential action say what it actually does?
2. If the action is unavailable, does the surface explain why in typed terms?
3. Can users tell the difference between unavailable, prohibited, completed, and not-applicable states?
4. Is there a visible unlock path or alternative channel when the digital action cannot proceed?
5. Do success and failure messages identify the exact action that happened?

## Compression rule for the archive

If a consequential service can show **you cannot do this right now** but cannot also say **what this action is, why it is blocked, and what route remains open**, then the archive is still letting **interface silence impersonate governance**.
