# Route posture page — helper policy, desired path, and fallback contract interface spec

## Purpose

The archive already had measurement planning and topology slicing.
What it still lacked was one fixed page for another ordinary question:

> before we judge the observed path, what route posture was this subject actually trying to use?

AnonSync should therefore model intended connectivity as a first-class **route posture page**.
The product must never force the operator to reconstruct desired route behavior from scattered toggles, defaults, and support memory.

## Core decision

Every serious connectivity or speed claim must preserve five truths before route judgment:

1. desired discovery helpers
2. desired transport class
3. allowed fallback classes
4. required symmetry across peers
5. policy that would count as divergence

## Fixed review order

1. **Subject and incident scope**
2. **Discovery-helper posture**
3. **Desired transport contract**
4. **Allowed fallback ladder**
5. **Peer symmetry obligations**
6. **Known policy exceptions**

## 1) Subject and incident scope

Show:

- folder / subject under review
- incident or investigation id
- whether the question is connectivity, speed, stability, or policy conformance
- whether this posture is global, per-folder, or pair-specific

The operator must be able to answer:

> what exact subject does this route posture belong to?

## 2) Discovery-helper posture

Publish each helper as an explicit state, not a footnote:

- tracker allowed / required / disabled
- LAN search allowed / required / disabled
- predefined hosts absent / optional / required
- relay allowed / disallowed / emergency-only
- local listening-port expectations

The page must never collapse `configured` and `required` into the same word.

## 3) Desired transport contract

State the desired effective path in plain language, for example:

- `direct path preferred and expected`
- `direct path required for success`
- `relay acceptable only as temporary fallback`
- `predefined-host direct path expected across this pair`
- `LAN-local direct path expected`

Also publish the reason, such as performance, policy, privacy, or network shape.

## 4) Allowed fallback ladder

The page must show the ordered fallback ladder the product considers acceptable, for example:

1. direct by learned public/local address
2. direct by predefined host
3. relayed path if direct unavailable
4. fail closed rather than relay

This prevents the operator from confusing `works somehow` with `works as intended`.

## 5) Peer symmetry obligations

Show whether the route posture must match across:

- all peers in the subject
- only the measured pair
- only one uploader cohort
- only one network segment

Also show where asymmetric posture is allowed, such as mixed predefined-host availability or mixed relay permission.

## 6) Known policy exceptions

List any intentional exceptions, for example:

- roaming/mobile peer may relay
- remote seat behind managed proxy may require tracker + relay
- one legacy node lacks LAN search
- one seat intentionally excluded from direct ingress

## Compact rendering obligations

Any compact card for route posture must still preserve:

- subject scope
- desired transport contract
- relay policy
- helper posture summary
- divergence trigger sentence

## Anti-clone rule

Do not clone workflows where the desired route must be inferred from a few buried toggles or defaults after the incident has already happened.

## Receipt consequence

Every later route-evidence or divergence review must link back to the exact route-posture version it is judging.
