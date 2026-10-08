# Policy exception and waiver control

A mature archive needs a way to record exceptional handling without
turning exceptions into hidden policy. This surface defines the minimum
record for waivers, emergency exceptions, temporary deviations, and
operator overrides.

The default is no exception.

## Exception states

| State | Meaning | Effect |
|---|---|---|
| `PX0` | no active exception | ordinary policy applies |
| `PX1` | requested but not approved | no effect |
| `PX2` | approved, narrow, and expiring | effect limited to stated scope |
| `PX3` | expired or closed | no continuing effect |
| `PX4` | rejected | no effect |
| `PXX` | prohibited exception request | reject and investigate |

## Non-waivable controls

Do not approve an exception that waives:

- `SRC2+` real-source evidence for closing `FT-0181`;
- protected-route separation for accessibility, disability, safeguarding,
  or other sensitive facts;
- action-authority ceilings for grading, discipline, eligibility,
  benefits, standing, or official records;
- public-summary evidence limits;
- learner-facing remedy, appeal, inspection, or correction routes;
- no-fake-real-import checks.

If one of those controls is wrong, revise the policy through a new
surface and ledger entry. Do not bypass it with an exception.

## Required exception record

Any active exception must name:

- requester and accountable owner;
- affected service, surface, or followthrough item;
- exact waived control;
- start and expiry dates;
- learner-facing effect;
- public-summary effect;
- fallback and rollback;
- reviewer independence check;
- reason it is not a prohibited exception.

## Current posture

rev0220 includes a no-active-exception record for the `FT-0181` release
candidate. That record is not evidence of service quality. It simply
prevents a hidden waiver from explaining away the remaining real-data
block.
