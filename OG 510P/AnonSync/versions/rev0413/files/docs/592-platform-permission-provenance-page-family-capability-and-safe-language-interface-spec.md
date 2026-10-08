# Platform permission provenance page — family, capability, and safe-language interface spec

## Purpose

Give the operator one reviewed answer to:

- what exact platform permission family is in play
- which product capability families depend on it
- what grant state the seat currently has
- what sentence is still true if the permission is absent, narrowed, revoked, or unknown
- what stronger sentence the product must forbid

This page is the platform-permission companion to storage-class, runtime-profile, control-grade, and capture-source pages.
It should appear whenever a mobile or constrained seat depends on OS-mediated permission for meaningful product power.

## Inputs

- seat identifier
- platform family (`android`, `ios`, `kindle`, `desktop-constrained`, `unknown-mobile`)
- permission family (`storage-write`, `storage-read`, `camera-scan`, `accounts-identity`, `startup-autostart`, `wake-lock`, `notification-delivery`, `network-access`, `network-state`, `other`)
- current grant state (`granted`, `denied`, `limited`, `revoked-after-use`, `not-requested-yet`, `unknown`)
- prompting action class (`scan-qr`, `write-arrival`, `enable-autostart`, `receive-request-alert`, `support-send`, `background-check`, `general-bringup`, `unknown`)
- capability families touched
- strongest safe sentence
- stronger forbidden sentence
- nearest repair or fallback action

## Primary questions this page must answer

1. What exact OS/platform power is being requested or relied on?
2. What exact product capability becomes possible because of it?
3. What remains true if the permission is absent or later revoked?
4. Is the current seat blocked, narrowed, deferred, or fully enabled for this capability family?
5. What is the least-widening honest next step?

## Layout

### A. Permission verdict strip

Fields:

- permission family
- current grant state
- seat / platform family
- current capability verdict
- strongest safe sentence

Example verdicts:

- `Camera scan permission denied; manual claim path still available`
- `Storage-write permission granted; arrival materialization allowed on this seat`
- `Notification permission absent; background alerts unavailable, sync core status separate`
- `Wake-lock / sleep authority limited; background freshness now policy-bounded`

### B. Permission-family card

Show:

- OS/platform permission label
- human explanation of why the product asked for it
- whether it is required, optional, or conditionally required
- first feature family that triggered the request
- whether denial is permanent, re-requestable, or system-settings only

This card exists so the operator can stop treating the OS dialog as unexplained native noise.

### C. Capability-family card

Show:

- capability families unlocked or narrowed
- whether each family is `enabled`, `degraded`, `blocked`, or `unrelated`
- strongest affected user-visible action
- strongest unaffected nearby action

Capability families may include:

- `arrival materialization`
- `backup / capture`
- `qr / local scan claim`
- `autostart`
- `background freshness`
- `connection-request alerts`
- `support/send-link convenience`
- `network route participation`

### D. Claim-ceiling card

Show three sentences together:

- strongest approved sentence
- stronger forbidden sentence
- what missing grant or proof blocks the stronger claim

Example:

- approved: `This seat can still join by manual key entry, but QR scanning is unavailable.`
- forbidden: `This seat cannot connect to shares at all.`
- blocker: `camera permission is denied, but non-camera intake paths remain available.`

### E. Adjacent actions

Offer only actions that preserve meaning:

- `Review permission consequence`
- `Retry narrower path`
- `Open platform settings handoff`
- `Continue without this permission`
- `Export permission receipt`

## Behavior rules

- This page must appear before the product overstates failure or success because of a platform permission state.
- OS permission labels are supporting evidence, not sufficient explanation on their own.
- If several permissions affect one capability family, the page must separate them rather than collapsing them into one `allow access` claim.
- A denied permission must not automatically imply total feature failure when narrower fallback still exists.

## Output object

```text
platform_permission_provenance {
  seat_id,
  platform_family,
  permission_family,
  grant_state,
  prompting_action_class,
  capability_families[],
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  next_review_actions[]
}
```

## Acceptance tests

- Denying camera permission must still allow the page to say whether manual key/link intake remains available.
- Denying notification permission must not silently collapse into `sync stopped` if the core may still run.
- A storage-write denial must distinguish read/inspect paths from byte-arrival materialization paths.
- Wake-lock / auto-sleep state must be shown as a freshness or liveness narrowing, not generic product failure.
