# Remedy-hardening-attestation surface-claim-governance contract sheet page — audience budget, surface scope, and export policy

## Purpose

This page is the compact contract for how a case's currently honest sentence may be rendered across product surfaces.
It exists so the product can distinguish `internally known`, `safe to show to named operators`, `safe to export to named recipients`, `safe only with qualifiers`, `historical-only on this surface`, and `blocked from this audience entirely`.

## Core fields

- case identifier
- source egress-governance receipt identifier
- current governing receipt identifier
- current surface-claim-governance class
- current strongest internal sentence
- current strongest audience-safe sentence
- surface class
- audience class
- allowed sentence budget class
- required qualifier set
- blocked stronger phrase set
- export permission class
- copy or relay permission class
- stale-claim recall status
- supersession-banner policy class
- historical-only watermark policy class
- exact sentence template identifier in force
- prior surface artifact count still unrecalled
- next evidence that upgrades audience budget
- next evidence that forces downgrade, freeze, or recall

## Surface classes

The page must model at least these distinct classes:

- dashboard badge or chip
- list row summary
- detail page
- notification or toast
- activity or history line
- copied label or clipboard artifact
- share-link landing label
- exported receipt or report
- API response
- support-view diagnostic surface
- public or semi-public external statement

## Audience classes

The page must model at least these distinct audiences:

- case owner
- internal operator
- internal reviewer or auditor
- named dependent or named consumer
- named external recipient
- support or incident-response audience
- linked-family but not case-owned operator
- unknown external holder
- public audience

## Sentence-budget classes

The page must support at least these budget classes:

- no audience-facing sentence allowed
- local operational hint only
- internal-only sentence allowed
- named-cohort sentence allowed
- named-recipient sentence allowed
- governed-cohort sentence allowed
- ceiling-aware global sentence allowed
- historical-only rendering required
- export blocked pending recall or supersession

## Fixed rendering order

Every surface-claim-governance contract sheet must render the same sections in the same order:

1. **Strongest currently allowed sentence for this audience and surface**
2. **Required qualifiers and blocked stronger phrases**
3. **Export, copy, and relay policy**
4. **Stale-claim recall and supersession posture**
5. **Blocked stronger sentences**

## Hard rules

The page must never silently upgrade:

- `internal truth known` into `all surfaces may say it`
- `detail page may say it` into `notification may say it`
- `named-cohort sentence allowed` into `public sentence allowed`
- `copied once` into `still authoritative after downgrade`
- `current receipt stronger` into `older export automatically harmless`
- `historical visibility` into `current authority`

## Minimum operator questions answered

The page must let a later operator answer, without hunting across other pages:

- what this exact surface may currently say
- which audience that statement is safe for
- which qualifiers must appear every time
- which stronger phrases are blocked outright
- whether copying, quoting, or exporting is allowed
- whether older stronger artifacts are still live and must be recalled or watermarked
