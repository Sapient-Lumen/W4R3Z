# Forbidden-network review page — stoppage class, detection loss, and wake condition interface spec

## Purpose

Make network ineligibility a reviewed action instead of a vague `stopped` badge.
This page exists to answer:

> if a share is policy-ineligible on the current network, what exact class of stoppage is this, what capability is suspended, and what is the least-widening path back?

Current official Resilio docs make this seam concrete because `Stopped. Forbidden network`, global mobile-data policy, and sleep/battery stoppage still live in different pages.
AnonSync should own the review directly.

## Core decision

Any meaningful network-ineligibility state must compile to one first-class **Forbidden-network review** page before the product treats it as ordinary absence or generic offline behavior.

The page owns:

- stoppage class
- affected capability families
- exact wake / re-entry condition
- least-widening repair options
- receipt and re-entry path

## Fixed page order

1. **Current stoppage class**
2. **Capability suspension**
3. **Least-widening re-entry options**
4. **Claim ceiling after chosen repair**
5. **Receipt and wake basis**

### 1) Current stoppage class

Show:

- current network class
- current core activity state
- stoppage class (`share-policy`, `seat-policy`, `sleep-policy`, `battery-policy`, `mixed`, `unknown`)
- whether the share is visible, hidden, or pathless despite stoppage

The operator must be able to answer:

> what exact kind of stoppage is this?

### 2) Capability suspension

Show rows for each affected capability family with columns:

- family
- before state
- suspended state now
- strongest blocked behavior
- strongest unaffected nearby behavior

Typical rows:

- `peer connection`
- `change detection`
- `transfer / fetch`
- `background freshness`
- `manual local browse`
- `placeholder clear / materialize`

The operator must be able to answer:

> what exactly is no longer happening because of this stoppage?

### 3) Least-widening re-entry options

Show only honest options such as:

- `wait for approved Wi‑Fi network`
- `enable mobile data seat-wide`
- `widen only this share from Wi‑Fi only to any allowed network`
- `wake the core without widening network scope`
- `plug in and let charge-specific wake cadence apply`
- `use another seat that is already eligible`

The operator must be able to answer:

> what is the narrowest change that would restore this share?

### 4) Claim ceiling after chosen repair

Show together:

- strongest approved sentence if the chosen repair is applied
- strongest approved sentence if no repair is applied
- stronger forbidden sentence
- blocker or residue that prevents the stronger claim

### 5) Receipt and wake basis

Show:

- receipt class to emit
- whether automatic re-entry is expected
- whether a future network / wake observation is required before the claim can strengthen
- best reopen path after policy or network change

## Main surface

The compact mutation sheet should never collapse to `Use mobile data?` or `Share stopped`.
It should always show:

- stoppage class
- suspended capability
- one least-widening re-entry option
- the strongest safe sentence afterward

## States

Use a small stable vocabulary:

- `eligible`
- `share-blocked`
- `seat-blocked`
- `sleep-blocked`
- `battery-blocked`
- `mixed-blocked`
- `unknown`

## Receipt fields

Suggested durable receipt fields:

- `network_eligibility_receipt_id`
- `seat_ref`
- `share_ref`
- `current_network_class`
- `stoppage_class`
- `capability_suspensions[]`
- `repair_options_presented[]`
- `strongest_safe_sentence`
- `wake_basis`
- `generated_at`

## Success criteria

The page is successful only when an operator can answer:

1. which policy layer caused stoppage
2. what exact capability is suspended
3. what least-widening repair exists
4. what sentence the product may honestly say afterward
5. what later event proves the share is eligible again
