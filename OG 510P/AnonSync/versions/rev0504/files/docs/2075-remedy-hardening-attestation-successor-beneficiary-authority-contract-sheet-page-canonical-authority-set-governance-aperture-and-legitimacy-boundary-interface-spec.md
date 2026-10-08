# Remedy-hardening-attestation successor beneficiary-authority contract sheet page — canonical authority set, governance aperture, and legitimacy boundary

## Purpose

This page is the operator-facing sheet for deciding whether the beneficiary who remains on a live update lane is actually governed by the reviewed canonical authority set.
It exists to stop `still subscribed`, `change arrived`, or `certificate validated` from being mistaken for `the right sovereign set still controls what can bind this beneficiary`.

## Core question

The page must answer:

**which actor or actor-set is actually allowed to issue binding future fixes, supersessions, withdrawals, permission changes, or onward delegations for this beneficiary-facing result now?**

## Minimum fields

The contract sheet must show at least:

- action identifier
- source beneficiary-continuity receipt identifier
- named beneficiary identifier
- governed slice identifier
- intended canonical authority set
- actual currently empowered authority set
- folder or lane architecture class
- authority aperture class
- owner / editor / revoker / delegator matrix
- linked-device owner spread summary
- approval-memory or auto-approval scope
- onward-share or onward-delegation risk summary
- strongest honest authority sentence now
- blocked stronger authority sentence now

## Standing ladder

The page must support at least these distinct standings:

- continuity proved, authority set still unproven
- subscribed lane, but authority aperture wider than reviewed
- canonical authority set for named seat only
- canonical authority set plus revocation power for named slice only
- multiple legitimate owners, exclusive-sovereign sentence blocked
- standard-key onward-share risk present
- approval carry-forward widened future admission scope
- later delegation or linked-device spread narrowed prior authority confidence
- receipt superseded

## Required comparisons

The sheet must compare:

- continuity standing versus authority standing
- intended authority set versus actual empowered set
- reviewed governance aperture versus actual current aperture
- expected single-sovereign control versus observed multi-owner spread
- expected bounded admission scope versus approval-memory carry-forward
- expected no-onward-legitimation posture versus observed re-share or delegation posture

## Required layout

### Header

Show:

- action name
- beneficiary name
- authority posture
- aperture badge
- strongest honest sentence now

### Left column — intended governance

Show:

- governed slice
- intended canonical authority set
- intended rights matrix
- intended admission scope
- forbidden substitute states

### Center column — observed authority facts

Show:

- lane architecture class
- current empowered actor set
- owner / revoker / delegator roster
- linked-device spread
- remembered approval scope
- onward-share posture

Every row in this column must have:

- current value
- evidence source
- whether it widens or narrows legitimacy confidence

### Right column — consequence for beneficiary truth

Show:

- whether the beneficiary is governed by one sovereign, several sovereigns, or an aperture wider than reviewed
- whether future supersessions are canonical for the full governed slice, named seat only, or still blocked
- whether revocation or delegation power is centralized, shared, or under-specified
- what stronger sentence remains blocked

### Footer decision rail

The footer must make it impossible to flatten these into one answer:

- live lane, authority unclear
- live lane, reviewed sovereign set for named seat only
- live lane, multi-owner governance
- live lane, approval carry-forward widened aperture
- live lane, onward-share risk widens legitimacy surface
- stronger canonical-authority sentence still blocked

## Interaction requirements

The interface must support:

- clicking any actor chip to open a rights drawer showing `may update / may share / may revoke / may delegate / may approve`
- clicking any aperture badge to reveal what widened it: linked devices, multi-owner state, remembered approvals, key shareability, or delegation
- clicking the blocked-sentence rail to reveal the minimum missing proof needed to upgrade the authority sentence
- pinning one actor as the reviewed sovereign reference so every divergence from that reference stays visible while scrolling

## Hard rules

The page must never allow:

- `cryptographically authenticated` to silently become `reviewed-canonical authority`
- `current owner` to silently become `exclusive sovereign`
- `future updates still arrive` to silently become `authority boundary still matches review`
- `one identity` to silently become `one physically bounded decision-maker`
