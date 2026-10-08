# Name posture page: local title, disk basename, outward alias, and residue interface spec

## Purpose

This page exists because `the name` is not one stable truth.
A serious product can have several simultaneously real label planes:

- subject title
- local UI title
- on-disk basename
- current outward artifact label
- peer-visible alias if one exists

The page must let an operator answer one blunt question without lore:

> what names exist for this subject right now, who sees each one, and which of them are deliberate truth versus leftover residue?

## Core decision

AnonSync should make **Name posture** first-class.
Every serious subject must publish, in one stable object:

- active name planes now
- audience for each plane
- propagation scope for each plane
- residue status
- outward-artifact freshness status
- strongest safe sentence

## Fixed page order

Every name-posture page should render the same sections in the same order:

1. **Names now**
2. **Audience and scope**
3. **Residue and reset state**
4. **Outward artifact freshness**
5. **Changed-name history**
6. **Claim ceiling**

### 1) Names now

Show:

- subject and seat
- subject title
- local UI title
- on-disk basename here
- current outward artifact label if any
- one next honest action

The operator must be able to answer: **what names currently exist?**

### 2) Audience and scope

For each plane show:

- `local only`, `this path only`, `future artifacts`, `already-issued artifacts`, `peer-visible`, `unknown`
- strongest basis
- operator-visible reason

The operator must be able to answer: **who sees each name?**

### 3) Residue and reset state

Show whether a plane is:

- `baseline`
- `intentional override`
- `disconnect residue`
- `stale carry-forward`
- `unknown`

Also show whether a simple reset can restore baseline.

The operator must be able to answer: **is this name deliberate or just left over?**

### 4) Outward artifact freshness

Show whether currently visible links / QR / outbound labels are:

- `fresh`
- `fresh but plane-limited`
- `stale under later rename`
- `regeneration required`
- `unknown`

The operator must be able to answer: **would I safely hand out this artifact now?**

### 5) Changed-name history

Show recent events such as:

- folder renamed locally
- local UI title overridden
- sharing-time label changed
- disconnect preserved local override
- reset returned to baseline
- outward artifact regenerated

The operator must be able to answer: **what changed recently?**

### 6) Claim ceiling

Show:

- strongest safe sentence
- stronger forbidden sentence
- evidence timestamp
- main uncertainty if present

Examples:

- `This seat shows a local title override; peers still use the subject's other names.`
- `The QR currently on screen may be stale under the renamed label until regenerated.`

## Rules

### Rule 1 — name planes must not collapse into one slot

The page may not use only one unlabeled title if more than one plane differs.

### Rule 2 — residue must be named explicitly

The page may not let disconnect-preserved or stale labels read as if they are the canonical current truth.

### Rule 3 — artifact freshness must be adjacent to outward labels

The page may not show an outward label without saying whether the visible artifact still reflects it.

## Acceptance criteria

A later operator can:

- identify every current name plane
- see who each plane reaches
- tell whether a visible name is residue or intentional
- know whether the outward artifact is fresh enough to use
- quote one honest sentence without support folklore
