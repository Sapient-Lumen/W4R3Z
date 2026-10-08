# Publication-lineage receipt page — viewer scope, redaction basis, and blocked reliance sentences

## Purpose

This page is the compact carry-forward receipt for what exact publication was made to whom, why that scope was chosen, and what stronger reliance sentence the product refused to make.
It exists so later operators can answer `what exactly did this audience get, and what were they still not entitled to conclude?` without reopening the whole case.

## Mandatory receipt fields

- source act identifier
- publication version identifier
- viewer class or named audience
- eligibility basis
- redaction profile name
- highest publication class earned
- highest reliance class earned
- strongest blocked stronger sentence
- supersession / retraction status
- next event that could widen or narrow reliance

## Required compact verdicts

At minimum the receipt must be able to state verdicts like:

- `internal full view only; participant publication pending`
- `participant redacted view live; external reliance blocked`
- `public summary live; named-actor evidence withheld`
- `adjudicator-grade publication live; participant still redacted`
- `encrypted custody only; no semantic publication`
- `earlier public summary superseded; current reliance narrowed`

## Required comparisons

The receipt must keep these comparisons explicit:

- `audience included` vs `audience decision-enabled`
- `redacted publication` vs `full publication`
- `publication still visible` vs `publication still relied on`
- `same principal mirrored` vs `new audience authorized`
- `custody` vs `comprehension`

## Failure modes the receipt must prevent

- later operators assuming that because a viewer got something, they got everything
- later operators assuming that because a publication happened, reliance is unlimited
- losing the reason a viewer was narrowed to metadata-only or redacted-only access
- losing the fact that an encrypted host never held semantic rights
- losing which stronger publication sentence was intentionally blocked

## Stronger-sentence guard

This receipt may say `the viewer received a redacted participant notice and may rely on response obligations only`.
It may not say `the viewer had full decision-grade publication` unless that stronger sentence was actually earned.
