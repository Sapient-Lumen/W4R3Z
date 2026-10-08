# Accessibility, comprehension, and inclusive-access review runbook v1

## Purpose

Use this runbook before repeating any claim that the archive is accessible, easy to understand, findable, translated, localized, supported, inclusive, or usable by a broad public.

## Required local artifacts

- `ACCESSIBILITY_REVIEW_PLAN.yml`
- `READABILITY_PLAIN_LANGUAGE_LEDGER.yml`
- `DISCOVERABILITY_NAVIGATION_MAP.yml`
- `LOCALIZATION_TRANSLATION_BOUNDARY.yml`
- `USER_GUIDANCE_ONBOARDING_LEDGER.yml`
- `INCLUSIVE_ACCESS_RISK_REGISTER.yml`
- `tools/check_accessibility_comprehension.py`

## Review sequence

1. Confirm all accessibility/comprehension root artifacts are present.
2. Confirm no artifact claims WCAG conformance, accessibility certification, legal accessibility compliance, plain-language certification, comprehension testing, official translation, localization completion, public support, or barrier elimination.
3. Confirm row cross-references resolve across guidance, inclusive-access risk, affected-party, and evidence artifacts.
4. Run `python3 tools/check_accessibility_comprehension.py .`.
5. Regenerate reports and query-regression output.
6. Treat failures as release-blocking for accessibility, comprehension, localization, support, or inclusive-access claims.

## Boundary

Passing this runbook means only that local archive records preserve the boundary. It is not an audit, conformance test, legal review, user study, or support commitment.
