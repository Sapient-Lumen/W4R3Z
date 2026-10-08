# 186 — Accessibility, readability, discoverability, localization, onboarding, and inclusive-access governance

## Status

`rev0180` adds a local accessibility/comprehension governance layer. The purpose is not to certify the archive as accessible, usable, translated, localized, or publicly supported. The purpose is to prevent the archive from treating availability, structure, and warnings as if they were accessible comprehension by readers with different abilities, tooling, languages, expertise, or support needs.

## Why this layer is needed

The preceding layer, `185`, governs ethics, public interest, affected-party, fairness/bias, misuse-sensitive release, and benefit/harm language. That is still incomplete if the archive cannot say who can find, read, navigate, understand, translate, or practically use the governance stack. A package can be ethically bounded and still inaccessible. A query surface can exist and still be unusable. A warning can be present and still be too dense for the relevant reader.

## New controlled surfaces

Rev0180 adds:

- `ACCESSIBILITY_REVIEW_PLAN.yml`
- `READABILITY_PLAIN_LANGUAGE_LEDGER.yml`
- `DISCOVERABILITY_NAVIGATION_MAP.yml`
- `LOCALIZATION_TRANSLATION_BOUNDARY.yml`
- `USER_GUIDANCE_ONBOARDING_LEDGER.yml`
- `INCLUSIVE_ACCESS_RISK_REGISTER.yml`
- `RUNBOOKS/accessibility-comprehension-inclusion-review-v1.md`
- `tools/check_accessibility_comprehension.py`

## Local checks

The checker blocks attempts to upgrade local rows into claims of WCAG conformance, accessibility certification, screen-reader testing, legal accessibility compliance, plain-language certification, comprehension testing, complete findability, public discovery service, official translation, multilingual support, public training, public support, complete documentation, equitable access, barrier elimination, or public accommodation.

## Claim boundary

Allowed language: `rev0180 records local accessibility, readability, discoverability, localization, onboarding, and inclusive-access risk boundaries for archive-governance surfaces.`

Forbidden upgrades include:

- WCAG conformant
- accessibility certified
- assistive-technology tested
- plain-language certified
- comprehension tested
- complete findability
- public discovery API
- official translation
- localized release
- multilingual support
- public support available
- training complete
- equitable access proven
- barriers eliminated
- public accommodation provided

## Place in the control sequence

`186` follows `185`. It does not add new metaphysical operators. It adds access and comprehension governance around the existing cube/control/gate stack.

## Residual debt

- no independent accessibility audit
- no WCAG conformance assessment
- no assistive-technology test matrix
- no disabled-reader or affected-party usability study
- no official translation or localization review
- no hosted accessible UI
- no public support, helpdesk, training, or accommodation service
- no proof that the archive is understandable by its intended or affected audiences
