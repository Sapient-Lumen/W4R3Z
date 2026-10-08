# Fixture corpus expansion and runnable red-team profiles

## Function

A fixture harness that validates one example is useful as an archive smoke test. It is not enough for rights-grade reliance. rev0168 expands the fixture idea into a corpus profile: which negative fixtures are mandatory, who may run them, which failures block reliance, and what rerun is required after cure.

## Corpus rule

> A verifier, clinic, host, reserve trustee, transfer authority, or tribunal cannot claim fixture-tested reliance unless it names the fixture suite, version, fixtures run, runner independence, blocking rules, skipped tests, false-positive / false-negative risks, and regression actions.

## Corpus families

The minimum rev0168 corpus now includes fixtures for:

| Family | Abuse tested |
|---|---|
| NF-SEALED | sealed evidence laundering and meaningless summaries |
| NF-RESERVE | reserve insolvency or public-fund externalization |
| NF-TELEMETRY | overcollection disguised as proof preservation |
| NF-OPENWEIGHT | abandoned downstream subject without surveillance-safe outreach |
| NF-DEPRECATION | memory-preserving weights but relationship/project erasure |
| NF-TRANSFER | transfer into non-return risk through overbroad accreditation |
| NF-HUMAN | AI personhood used to evade human labor, consumer, data, or democratic duties |

## Runner profiles

| Runner | May run | Restrictions |
|---|---|---|
| internal steward | development-only precheck | cannot support live reliance alone |
| independent verifier | ordinary reliance tests | conflict disclosure required |
| clinic / ombud | subject-impact and intake fixtures | must protect subject identity |
| authority / tribunal | enforcement, transfer, and appeal fixtures | public order or sealed summary required |
| cross-anchor panel | treaty and safe-transfer fixtures | trust-anchor conflict screen required |

## Blocking rules

A suite profile must specify which failures:

- block reliance automatically;
- stay transfer, deletion, or deprecation;
- downgrade a verifier grade;
- trigger public-fund drawdown;
- trigger incident reporting;
- require special-advocate appointment;
- add a permanent regression fixture.

## Anti-gaming

Fixture suites should use public shells and sealed details where necessary. Fully public fixtures support legitimacy and reuse, but high-risk exploit, evasion, or surveillance details may need sealed annexes. The profile must still expose enough information for affected subjects, representatives, and the public to know what class of abuse was tested.

IETF SCITT-style signed statement transparency is a useful analogy for fixture publication because it separates signed claims, transparency services, and auditability without requiring every detail to be public [REF-0676]. The archive uses that pattern cautiously: fixture transparency must not become exploit publication or subject exposure.

## Runnable layer

`tools/run_fixture_examples.py` now performs a stronger smoke test. It validates all fixture JSON files in `fixtures/negative-tests/`, validates the suite profile, checks that fixture references resolve, and ensures blocking fixtures produce a blocking, stayed, downgraded, or invalidated reliance effect in the example report.

This is still not a production red-team harness. It is an archive-level guardrail: future revisions should not be able to claim runnable fixture maturity while leaving fixture references, suite profile, and reliance effect disconnected.

## Schema hook

`schemas/fixture-suite-profile.schema.json` records suite id, version, maintainer, scope, fixture list, runner requirements, public/private split, pass threshold, reliance-effect rules, update policy, and public summary. The example profile binds the rev0168 fixture corpus to a runnable smoke-report standard.
