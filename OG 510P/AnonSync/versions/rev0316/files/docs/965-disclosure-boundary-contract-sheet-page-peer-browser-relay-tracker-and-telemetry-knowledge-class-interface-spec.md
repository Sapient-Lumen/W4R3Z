# Disclosure boundary contract sheet page — peer, browser, relay, tracker, and telemetry knowledge class interface spec

## Purpose

This page exists so the product can answer one ordinary operator question without support archaeology:

> for this share / open / connection / telemetry posture, which observer classes can learn which facts, by what carrier, and with what proof ceiling?

The page must not flatten disclosure into one badge such as `private` or `end-to-end encrypted`.
It must publish the actual knowledge classes separately.

## Contract summary

Every disclosure-boundary sheet should keep the same sections in the same order:

1. **Action / subject scope**
2. **Observer classes**
3. **Fact families**
4. **Effective disclosure matrix**
5. **Blocked stronger sentence**
6. **Allowed next actions**

## 1) Action / subject scope

Show:

- subject / share / artifact / route under review
- action class (`share-link issue`, `browser open`, `peer discovery`, `relay fallback`, `telemetry export`, `local parse only`)
- current carrier(s)
- proof freshness
- whether this is live state, saved policy, or imported receipt

## 2) Observer classes

Render stable rows for at least these classes:

- `local operator and local runtime`
- `chosen peer`
- `browser or handler environment`
- `carrier service page`
- `tracker / discovery infrastructure`
- `relay infrastructure`
- `telemetry recipient`
- `unknown or uncontrolled observer`

The page may hide irrelevant rows only if it explicitly says `not in path for this action`.

## 3) Fact families

Render stable columns for facts that commonly get over-claimed:

- subject label / folder name
- approximate size or content-summary hints
- artifact family / protocol family
- share or subject identifier
- temporary access token / capability token
- public IP / local IP / route facts
- peer presence or runtime activity
- OS / client version / posture facts
- payload bytes
- mutation authority or approval facts

The product may add more fact families, but it may not collapse these into one generic `metadata` column when different observer classes see different subsets.

## 4) Effective disclosure matrix

Each matrix cell must use one of these values:

- `not in path`
- `cannot learn`
- `can infer weakly`
- `can learn explicitly`
- `local-only parse`
- `carried ciphertext only`
- `unknown / unproven`

### Example

A relay row might honestly say:

- payload bytes → `carried ciphertext only`
- subject label → `cannot learn` or `unknown / unproven` depending on evidence basis
- route participation → `can learn explicitly`

A browser landing-page row might honestly say:

- subject label → `local-only parse` or `can learn explicitly` depending on implementation
- artifact family → `can learn explicitly`
- payload bytes → `cannot learn`

The point is to make the overclaim impossible.

## 5) Blocked stronger sentence

Every sheet must show one stronger sentence the system refuses to claim.
Examples:

- `reject saying “no third party learns anything”`
- `reject saying “browser open was fully local”`
- `reject saying “relay participates but learns no route facts”`
- `reject saying “telemetry disabled means no infrastructure contact at all”`

## 6) Allowed next actions

Permit only actions that match the current ceiling:

- `Open carrier disclosure review`
- `Inspect browser-open boundary`
- `Narrow helper / discovery budget`
- `Disable or review telemetry export`
- `Export disclosure receipt`

## Object model

### Disclosure boundary sheet

- `disclosure_boundary_sheet_id`
- `subject_ref` nullable
- `action_ref` nullable
- `carrier_refs[]`
- `observer_classes[]`
- `fact_families[]`
- `matrix_cells[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `proof_freshness_class`
- `source_basis_refs[]`
- `receipt_refs[]`

## CLI shape

```text
anonsync disclosure show --action share-link:alpha
anonsync disclosure show --subject finance-share --carrier browser-open
```

## Non-goals

This page does not itself mutate route or sharing policy.
It explains the current disclosure truth and routes to the correct review object.

## Result

AnonSync should make disclosure truth as explicit as connectivity truth.
If the operator still has to infer who learned what from marketing language plus protocol folklore, this page has failed.
