# Entitlement-provenance contract sheet page — license source, usage lane, and feature afterlife

## Purpose

This page answers one ordinary question:

> why is this capability active here, by what entitlement source, for what usage lane, under what grant topology, and what happens if that entitlement changes?

The page exists because `licensed`, `Pro`, `free`, `trial`, `activated`, and `feature available` are not interchangeable.

## Core decision

Every serious feature or upgrade claim must render one first-class **Entitlement-provenance contract sheet**.
The page owns:

- subject capability
- current node / participant unit
- entitlement source
- usage lane
- grant topology
- revocation authority
- feature-afterlife class
- strongest safe sentence now

## Fixed page order

1. entitlement strip
2. topology card
3. usage-legitimacy card
4. feature-afterlife card
5. proof card
6. receipts

### 1) Entitlement strip

Show:

- subject capability: `identity-linking`, `local-share`, `priority`, `upgrade-to-v3`, `business-sharing`, `server-use`, `unknown`
- current node / participant unit
- entitlement source: `site-issued-v3-noncommercial`, `legacy-home-pro`, `legacy-family-pro`, `business-owner`, `linked-device-inheritance`, `shared-seat`, `trial`, `none`, `unknown`
- usage lane: `personal-noncommercial`, `family-noncommercial`, `commercial-workstation`, `commercial-server`, `unknown`
- current entitlement class: `legitimate-and-active`, `active-but-wrong-lane`, `active-but-revocable`, `expired`, `trial-only`, `unsupported`, `unknown`
- one honest next action

### 2) Topology card

Publish:

- grant topology: `standalone-key`, `single-person-key-many-devices`, `family-pack-many-persons`, `business-owner-identity`, `linked-device-cascade`, `shared-seat-fanout`, `unknown`
- grant authority holder
- revocation authority holder
- whether the current node depends on another authority holder staying active
- whether ownership can move or be stolen by re-application elsewhere

The operator must be able to answer: **who actually granted this capability here, and who can take it away?**

### 3) Usage-legitimacy card

Show:

- declared usage lane
- permitted usage lane for the current entitlement
- platform/support qualifiers: `workstation-only`, `server-supported`, `home-only`, `noncommercial-only`, `unknown`
- legitimacy verdict: `matched`, `mismatched`, `partially-qualified`, `unknown`
- what stronger sentence is blocked

The operator must be able to answer: **is this feature merely active, or active in the right lane?**

### 4) Feature-afterlife card

Show:

- afterlife class: `survives-key-reapply`, `falls-on-owner-loss`, `falls-on-seat-reclaim`, `falls-on-expiry`, `falls-on-wrong-server-posture`, `survives-as-basic-sync`, `unknown`
- affected features
- whether the cliff is immediate, next-start, next-check, or unknown
- whether recovery requires re-apply, re-share, lane change, or product/version change

### 5) Proof card

Show:

- best evidence that the capability is entitled now
- best evidence that it is not
- weakest missing proof still preventing a stronger sentence

### 6) Receipts

Always link:

- latest entitlement lineage receipt
- latest participant-unit receipt if grant topology depends on owner / linked family / seat
- latest capability-floor receipt if version or platform compatibility also caps the claim

## Copy rules

- Never collapse `activated` into `legitimate for this usage lane`.
- Never collapse `legacy key exists` into `current feature afterlife is safe`.
- Never collapse `Business applied` into `server use supported`.
- Never collapse `owner currently active` into `this seat is independent`.
- Never collapse `trial enabled` into `durable entitlement`.
