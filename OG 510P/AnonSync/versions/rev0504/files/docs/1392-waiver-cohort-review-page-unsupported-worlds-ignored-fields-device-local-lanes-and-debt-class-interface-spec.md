# Waiver cohort review page — unsupported worlds, ignored fields, device-local lanes, and debt class

## Purpose

This page answers the cohort exception question that one-subject waiver inspection does not finish:

> across all candidate subjects, who is cleanly conformant, who is excluded by a typed waiver, which waiver classes dominate the debt, and which exceptions are nearing expiry or safe retirement?

## Core decision

Every serious profile rollout or audit must render one first-class **Waiver cohort review**.
The page owns:

- exception counts
- debt classes
- expiry risk
- removable vs sticky exceptions
- safe next actions

## Fixed page order

1. waiver summary strip
2. debt-class ledger
3. cohort buckets
4. expiry-and-rereview queue
5. safe action tray
6. waiver cohort receipt

### 1) Waiver summary strip

Show:

- profile id
- active profile revision
- reviewed cohort id
- total subjects reviewed
- fully conformant subjects
- active-waiver subjects
- expired-waiver subjects
- hard-out-of-policy subjects
- unknown subjects

### 2) Debt-class ledger

Every non-clean subject must receive exactly one top-line debt class:

- `unsupported-world debt`
- `unsupported-surface debt`
- `ignored-runtime debt`
- `local-parallel debt`
- `missing-prerequisite debt`
- `migration-gap debt`
- `temporary-hold debt`
- `evidence-gap debt`
- `hard-out-of-policy debt`
- `unknown`

For each class show:

- count
- affected fields
- whether rollout is blocked
- whether expiry exists
- what stronger sentence remains blocked

## Hard rule

`expired waiver` may never be rendered in the same visual style as `active waiver`.
The product must make debt staleness obvious.

### 3) Cohort buckets

Group subjects into explicit buckets:

- cleanly conformant
- conformant except for active typed waiver
- blocked pending prerequisite
- blocked by migration gap
- allowed local-parallel exception
- unsupported-world exclusions
- expired exceptions requiring rereview
- hard out-of-policy subjects
- unknown or insufficient-witness subjects

For each bucket show:

- count
- representative reason
- next safe action

### 4) Expiry-and-rereview queue

Sort all active and expired waivers by operational urgency:

- already expired
- expires soon
- prerequisite now satisfied
- migration apparently complete but not rechecked
- still blocked with no owner
- durable justified exception

For each row show:

- waiver id
- owner
- days to expiry
- likely retirement trigger
- whether rollout is waiting on it

### 5) Safe action tray

Only actions compatible with the proven debt class may be offered:

- `renew waiver`
- `retire waiver`
- `collect missing evidence`
- `complete prerequisite`
- `rebind successor world`
- `convert to hard out-of-policy`
- `exclude from rollout`
- `roll forward around exception`

For each action show:

- whether conformance count changes
- whether rollout eligibility changes
- whether the action changes values, governance, or neither

### 6) Waiver cohort receipt

Emit one compact receipt with:

- profile id
- profile revision
- cohort id
- subject counts by debt class
- expired-waiver count
- near-expiry count
- offered safe actions
- strongest safe cohort sentence
- blocked stronger sentence

## Copy rules

- Never say `mostly conformant` without publishing typed waiver counts.
- Never hide expired waivers inside an `exceptions` subtotal.
- Never let unsupported worlds count as profile members.
- Never let active waivers impersonate permanent design decisions.
- Never let `mobile is different` stand in for a debt class.

## Example strongest-safe sentence patterns

- `Eighty-three subjects are cleanly conformant; twelve more are currently excluded by active typed waivers, most of them local-parallel mobile lanes and one migration-gap service fork.`
- `Five subjects remain blocked by missing prerequisites, so the next profile revision cannot yet be applied to them.`
- `Two Linux WebUI subjects currently show the field but remain classified as ignored-runtime debt rather than supported conformance.`
- `Three waivers are expired and now block any stronger claim that this cohort is governance-clean.`
