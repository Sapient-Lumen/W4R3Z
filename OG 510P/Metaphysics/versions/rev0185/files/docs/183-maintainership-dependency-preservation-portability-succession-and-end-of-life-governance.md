# 183 — Maintainership, dependency update, preservation, portability, succession, and end-of-life governance

## Purpose

Rev0177 adds lifecycle sustainability governance. The archive now has many local gates, checkers, ledgers, and warning surfaces. That creates a new risk: the package can appear operationally mature while lacking a maintainable future. A system can be validated today and still be brittle tomorrow if no one owns dependency review, preservation, handoff, portability, or sunset language.

This document introduces a local lifecycle layer. It does not create public support, a hosted service, a legal maintenance obligation, a preservation guarantee, a portability certification, a named legal successor, or downstream migration authority.

## Problem statement

Security and abuse governance prevents unsafe claims about adversarial use, secrets, vulnerability intake, and hardening. But those controls do not answer six later questions:

1. Who locally stewards the package after release?
2. How are tool and format dependencies reviewed without claiming automated dependency scanning?
3. What is preserved, and what preservation guarantees remain forbidden?
4. Which formats make the archive portable, and which interoperability claims remain blocked?
5. What happens if the local maintainer cannot continue?
6. How does the archive sunset a surface without pretending to recall downstream copies?

The new rule is: **release survival is not release permission**. A package can pass every local gate and still lack lifecycle sustainability evidence.

## New governed surfaces

Rev0177 adds these artifacts:

- `MAINTAINERSHIP_STEWARDSHIP_LEDGER.yml`
- `DEPENDENCY_UPDATE_POLICY.yml`
- `PRESERVATION_ARCHIVAL_PLAN.yml`
- `PORTABILITY_INTEROPERABILITY_MATRIX.yml`
- `SUCCESSION_CONTINUITY_PLAN.yml`
- `SUNSET_END_OF_LIFE_LEDGER.yml`
- `RUNBOOKS/lifecycle-sustainability-preservation-review-v1.md`
- `tools/check_lifecycle_sustainability.py`

The artifacts are deliberately local. They record stewardship boundaries and review triggers. They do not establish service operations or external obligations.

## Control-stack position

Doc 183 follows doc 182. The intended control progression is now:

- doc 182 blocks security, threat-model, abuse, vulnerability, hardening, trust-boundary, and secret/key-material claim laundering;
- doc 183 blocks maintainership, dependency-update, preservation, portability, succession, and sunset claim laundering.

## Lifecycle laundering failures

The checker treats the following as unsafe:

- maintainership ledger upgraded into a public support or maintenance SLA;
- dependency policy upgraded into automated dependency scanning or vulnerability monitoring;
- preservation plan upgraded into archival guarantee, public repository status, or long-term hosting;
- portability matrix upgraded into standards conformance, certified interoperability, or migration guarantee;
- succession plan upgraded into legal successor designation or transferable authority;
- sunset ledger upgraded into public end-of-life notification, downstream recall, or migration service.

## Acceptance boundary

Rev0177 may say:

> The archive contains local lifecycle sustainability records for maintainership, dependency review, preservation, portability, succession, and sunset/end-of-life boundaries.

Rev0177 must not say:

> The archive has public support, guaranteed maintenance, automated dependency scanning, archival preservation, certified interoperability, legal succession, downstream migration, or public end-of-life notice service.

## Required evidence

A lifecycle claim now requires:

1. root lifecycle artifacts;
2. current rev0177 records;
3. schemas for the six new record families;
4. query coverage;
5. fixture coverage;
6. control-stack coverage;
7. cube observations;
8. release-gate acceptance criteria;
9. checker reports;
10. public-claim warnings.

## Review trigger

Run the lifecycle review whenever any of the following changes:

- a maintainer role or accountability assignment;
- a Python/YAML/tooling dependency;
- a file format, package structure, manifest rule, or compression method;
- a publication, mirror, archive, or repository claim;
- a handoff, delegation, succession, or abandonment claim;
- a sunset, deprecation, withdrawal, or end-of-life claim.

## Bet 106

A package can be locally validated, secure-boundary checked, and releasable while still being unsustainable. Lifecycle governance prevents the archive from turning present-tense control into future-tense promises.
