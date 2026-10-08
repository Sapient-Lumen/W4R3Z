# Runtime stop contract sheet page: projection, runtime, boot re-entry, and platform class

This page exists so `close`, `quit`, `exit`, `stop service`, and `disable startup` stop pretending to mean the same thing.
A sync runtime can outlive a window, survive a logout, fail to survive a platform boundary, or return later at boot.
One page must declare which class of stop the operator is actually asking for.

## Operator question

> What exactly am I trying to stop, what runtime class exists on this device, what may continue after the current projection disappears, and what future boot or service posture can bring it back?

## When this page must appear

Render this page whenever the operator:

- closes or hides a desktop projection
- invokes a quit / exit / stop action
- stops a service-managed runtime
- disables or enables boot/startup re-entry
- inspects whether a runtime is truly stopped now
- reviews cross-platform stop semantics after confusion or unexpected restart

## Fixed page order

1. **Current runtime class**
2. **Requested stop scope**
3. **Projection vs runtime truth**
4. **Boot / service re-entry posture**
5. **Residual activity ceiling**
6. **Receipt promise**

## 1) Current runtime class

Show:

- host platform
- runtime class: `desktop-app`, `desktop-hidden-runtime`, `windows-service`, `linux-headless`, `android-runtime`, `ios-foreground-only`, `unknown`
- current principal / service seat if relevant
- current projection class: `visible-window`, `hidden-window`, `webui-tab`, `service-only`, `foreground-mobile`, `no-projection`, `unknown`

The operator must be able to answer: **what kind of runtime exists here before I press anything?**

## 2) Requested stop scope

Show:

- requested verb: `hide`, `close-projection`, `quit-app`, `exit-runtime`, `stop-service`, `disable-startup-only`, `pause-not-stop`, `unknown`
- scope strength: `projection-only`, `runtime-intent`, `service-intent`, `future-boot-only`, `ambiguous`
- strongest safe sentence currently allowed about the request

The operator must be able to answer: **am I asking to hide a surface, stop a runtime, stop a service, or only change future boot behavior?**

## 3) Projection vs runtime truth

Show:

- whether the projection can disappear while runtime work continues
- whether the runtime can continue without any logged-in user
- whether background work is unavailable on this platform
- whether an explicit `Exit`-class verb exists and is stronger than navigation-away

The operator must be able to answer: **what can still be alive after this surface goes away?**

## 4) Boot / service re-entry posture

Show:

- auto-start posture: `enabled`, `disabled`, `not-supported`, `unknown`
- service re-entry posture: `service-managed`, `user-startup-managed`, `manual-only`, `unknown`
- whether the current stop action leaves future automatic re-entry unchanged
- whether reboot/login/logout can re-create the runtime later

The operator must be able to answer: **could this come back later even if it stops now?**

## 5) Residual activity ceiling

Show:

- current residual class: `none-observed`, `draining`, `still-publishing`, `startup-scheduled`, `unknown`
- whether notifications, indexing, or route presence still imply live work
- stronger forbidden sentence if no-further-publication is not yet proven

The operator must be able to answer: **what claim about `fully stopped` is still too strong right now?**

## 6) Receipt promise

Show:

- the receipt id that will be written
- what the receipt will preserve about runtime class, stop scope, re-entry posture, residual ceiling, and blocked stronger sentence
- which later event should reopen this contract automatically

## Primary actions

Use only actions that match the reviewed truth.
Examples:

- `Hide projection only`
- `Exit runtime now`
- `Stop service and watch for drain`
- `Disable future startup`
- `Open stop proof`

Do not use vague primaries such as `Close Sync`, `Turn off`, or `Stop everything` unless the product has actually proven that stronger sentence.

## What this page must never imply

It must never imply that these are the same:

- closing a window and stopping the runtime
- stopping the runtime and disabling future boot re-entry
- Android navigation-away and explicit exit
- desktop hidden runtime and iOS foreground-only runtime
- stop intent and no-further-publication proof

## CLI projection expectation

A headless projection such as `anonsync runtime stop show --view contract` must render the same sections and verdicts without requiring GUI-only nuance.
