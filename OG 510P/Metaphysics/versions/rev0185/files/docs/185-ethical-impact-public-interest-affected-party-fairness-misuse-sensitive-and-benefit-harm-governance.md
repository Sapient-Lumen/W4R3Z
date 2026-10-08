# 185. Ethical Impact, Public Interest, Affected-Party, Fairness, Misuse-Sensitive, and Benefit/Harm Governance

## Local problem

Rev0178 makes legal/reuse language harder to launder, but a package can still be legally cautious while ethically under-specified.  A claim can avoid licensing, attribution, derivative, and compliance overclaims while still failing to say who may be affected, which harms remain plausible, which benefits are merely hoped for, which fairness/bias questions are unreviewed, and which misuse-sensitive release paths should remain blocked.

This document adds a local public-interest and ethics boundary layer.  It is deliberately not an ethics-board approval, legal compliance record, human-subjects review, democratic mandate, safety certification, fairness audit, or public consultation service.

## Added artifacts

- `ETHICAL_IMPACT_ASSESSMENT.yml` records local ethical-impact rows and blocks certification language.
- `PUBLIC_INTEREST_BALANCING_LEDGER.yml` records local public-interest balancing without public authority.
- `AFFECTED_PARTY_ANALYSIS.yml` records hypothesized affected-party classes and standing limits.
- `FAIRNESS_BIAS_REVIEW_LEDGER.yml` records fairness/bias review boundaries without audit claims.
- `MISUSE_SENSITIVE_RELEASE_POLICY.yml` records misuse-sensitive release constraints without dual-use certification.
- `BENEFIT_HARM_REGISTER.yml` records benefit and harm hypotheses without proving net benefit or safety.
- `RUNBOOKS/ethics-public-interest-review-v1.md` defines the local review pass.
- `tools/check_ethics_public_interest.py` checks the six ledgers for local evidence, cross references, and forbidden-upgrade flags.

## Control rule

The archive may say that rev0179 contains local ethical-impact, public-interest, affected-party, fairness/bias, misuse-sensitive-release, and benefit/harm boundary records. It must not say that the package has been ethically approved, socially licensed, fairness audited, bias certified, democratically authorized, safety certified, or cleared for unrestricted public use.

## Anti-laundering rule

Ethical language is especially prone to laundering.  The following substitutions are forbidden:

- impact assessment -> ethical approval
- public-interest balancing -> public mandate
- affected-party analysis -> stakeholder consultation
- fairness/bias review -> fairness audit or anti-discrimination certification
- misuse-sensitive policy -> misuse impossible or unrestricted release safe
- benefit/harm register -> net benefit proved or safety certified

## Required release-gate effect

A release that mentions ethics, public interest, affected parties, fairness, bias, misuse, dual-use sensitivity, benefit, or harm must pass the rev0179 ethics/public-interest checker, include query and fixture coverage, and preserve explicit negative claims in the public-release and claim-language surfaces.

## Remaining debt

The review remains local, unsigned, non-institutional, non-legal, non-consultative, non-statistical, non-operational, and non-certifying.  It is a control on archive language, not a substitute for public governance, participatory design, legal review, safety analysis, or domain expert review.
