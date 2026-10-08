# Web credential reset, state preservation, and no-duplicate-seat interface spec

## Purpose

The archive already had control-entry and listener-binding language.
What it still lacked was one stricter contract for a common but surprisingly dangerous control-surface recovery event:

> if I lose access to the local web surface, how do I regain access without accidentally creating a second apparent seat, resetting unrelated settings, or making the control-plane story less trustworthy than before?

Current Resilio docs make this seam concrete.
Their current WebUI password-reset page still says that deleting `settings.dat` and `settings.dat.old` resets login/password but also duplicates the device in `My devices` and resets global Sync preferences to defaults.
The same page separately says configuration-file reset avoids duplicate devices and avoids resetting global preferences.

That means current credential recovery still is not one semantic operation.
It forks into materially different side effects depending on the ritual used.

## Core decision

AnonSync must treat control-surface credential recovery as a first-class reviewed operation with **state-preservation guarantees**.

Credential reset must never silently widen into:

- duplicate seat identity or duplicate row appearance
- reset of unrelated global preferences
- ambiguity about which old sessions remain valid
- uncertainty about whether subject state or authority state changed

## Why this matters

Current Resilio behavior still leaves too much meaning distributed across troubleshooting steps:

- one reset path is easy but causes duplicate-seat visibility and preference reset
- another path uses configuration and preserves state better
- neither path makes the operator review session invalidation, preserved settings, or post-reset attestation as one whole event

AnonSync should therefore hold one stronger rule:

> recovering control access must preserve runtime identity unless the operator explicitly chooses a broader reset.

## Fixed review order

Every credential reset or local control recovery should render the same sections in the same order:

1. **Access problem**
2. **Preservation grade**
3. **State changes if applied**
4. **Session / endpoint consequences**
5. **Recovery attestation**

### 1) Access problem

Show:

- failed secret, lost secret, blocked login, endpoint drift, or unknown
- affected surface (`local web`, `desktop shell`, `headless web`, `api token`, `other`)
- whether engine/runtime is healthy while access is lost

### 2) Preservation grade

Each recovery method must carry one grade:

- `identity-preserving`
- `identity-preserving but session-resetting`
- `settings-resetting`
- `seat-duplicating risk`
- `full local control-plane reset`

### 3) State changes if applied

Show exactly what will change:

- secrets / sessions
- UI or global preferences
- seat rows / device appearance
- endpoint bindings
- subject registries and receipts

Anything unaffected should be stated explicitly.

### 4) Session / endpoint consequences

Show:

- sessions invalidated
- listener restart required or not
- control endpoints added/removed
- whether another seat or admin path can verify success

### 5) Recovery attestation

The attestation must preserve:

- recovery method chosen
- preservation grade shown
- settings preserved vs reset
- whether any duplicate-seat row was introduced or prevented
- post-reset endpoint and session state

## Main surface

Expose one **Recover control access** flow with two or three reviewed methods rather than one hidden troubleshooting ritual.

A good first page states plainly:

- `Reset secret only`
- `Reset sessions and secret`
- `Broader local control reset`

The most destructive option must not be the first or default path.

## Acceptance criteria

This spec is satisfied when:

- losing a local web password does not force the operator into filesystem ritual
- state-preserving reset is the normal path
- broader reset paths preview duplicate-row and settings-reset consequences before apply
- post-reset attestation proves whether runtime identity actually changed
