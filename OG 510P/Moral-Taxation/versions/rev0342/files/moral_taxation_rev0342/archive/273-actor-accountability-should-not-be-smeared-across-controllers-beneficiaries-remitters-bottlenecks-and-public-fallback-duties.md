# 273. Actor accountability should not be smeared across controllers, beneficiaries, remitters, bottlenecks, and public fallback duties

## Thesis

A tax route can be technically complete and still morally underspecified if it names the instrument and incidence but not the accountable actor. Rev0291 adds an actor-accountability layer so the cube can distinguish control, benefit, remittance, bottleneck access, protected burden, and public fallback duty.[S322][S324][S667]

## Closed rule

Do not infer responsibility from title, proximity, interface, or payment handling alone. Require a responsibility chain: practical power, legal or contractual duty, beneficial upside, channel control, evidence of willfulness or neglect where penalty-like liability is proposed, and a fallback duty when the state relies on a private mandatory channel.

## Why this matters

- A payroll vendor, officer, platform, bank, insurer, app store, or preparer can be responsible in some settings and merely adjacent in others.
- A legal remitter can collect from the burden bearer while the remedy mistakenly reimburses the wrong party.
- A public agency can mandate a private rail and then pretend the rail's failure is the taxpayer's failure.
- A beneficiary can receive the rent while enforcement targets the conduit.

## New release invariant

Every route record now has an actor-accountability profile. The checker rejects missing profiles, family drift, missing actor fields, absent non-responsible actor lists, missing burden bearers, missing evidence requirements, source-currentness mismatch, and stale audit counts.

## Source cues

[S322]: ../SOURCES.md#S322
[S324]: ../SOURCES.md#S324
[S667]: ../SOURCES.md#S667
