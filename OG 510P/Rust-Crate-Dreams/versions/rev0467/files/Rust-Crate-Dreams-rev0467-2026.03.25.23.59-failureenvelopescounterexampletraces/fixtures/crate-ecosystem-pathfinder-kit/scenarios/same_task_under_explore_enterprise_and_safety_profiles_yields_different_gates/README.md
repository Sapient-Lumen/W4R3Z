# Scenario — same task under explore, enterprise-offline, and safety-onramp profiles yields different gates

## What this scenario proves

The same task can produce multiple legitimate answers **without** the archive contradicting itself.

That is not indecision.
It is profile honesty.

This scenario assumes:
- one service-oriented task profile,
- one frozen starter set,
- one basis lock and one knowledge pack,
- but uneven support for offline delivery, target readiness, and lifecycle evidence.

### Expected outcomes

- `explore-default` — likely `pass`
- `enterprise-offline` — likely `conditional` until source-parity/materialization evidence is present
- `safety-onramp` — likely `manual_review_required` until target/MSRV/lifecycle floors are stronger

## Why it matters

Without this scenario, future passes may flatten:
- “works for prototype”
into
- “recommended generally,”

or flatten:
- “has docs and publishing-trust signals”
into
- “ready for higher-assurance adoption.”

The front-door stack should resist both.

## Artifacts in this scenario

- `policy-profile.pack.example.json`
- `profile-satisfaction.report.example.json`

The example report is intentionally written for the `safety-onramp` profile because that is where the evidence floor becomes most visible.
