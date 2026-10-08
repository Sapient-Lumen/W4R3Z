# 710 — Accessibility/language gate and public-answer usability floor

**Track:** Shared / Release maintenance + Track A pilot readiness

## Purpose

v835 adds a voter-facing publication gate for a failure mode that earlier releases did not make explicit enough: a packet can be digest-correct, redaction-reviewed, and still not be usable by the people who need it. The gate keeps local public release at **NO-GO** until accessibility, language-access, plain-language, fallback, and human-help review are recorded.

This is a release-safety control, not an accessibility certification. It does not determine jurisdiction-specific language coverage, legal duties, current voter instructions, or public-release authorization.

## External anchors

- `xref:ada_voting_and_polling_places_page` — voting access and effective communication are treated as public-facing civil-rights requirements, not optional design polish.
- `xref:eac_language_access_resources_page` and `source:eac_language_access_program_checklist_pdf` — language-access planning needs local coverage facts, translated material discipline, and review, not ad hoc last-mile translation.
- `xref:justice_language_minority_citizens_page` — language-access obligations are legal and jurisdiction-specific; the archive must not guess coverage or compliance.
- `xref:w3c_tr_wcag22` — WCAG-style testable criteria are useful as a review discipline, but this archive does not claim formal conformance.

## New artifacts

- `artifacts/registries/accessibility-language-publication-policy.csv` defines 14 policy rows for notices, status pages, language-access parity, alternate formats, assistive technology, hotline/help routes, translated corrections, media/screenshot accessibility, polling-location/map accessibility, AI-assisted translations, emergency notices, intimidation/safety answers, offline/low-bandwidth copies, and the gate itself.
- `artifacts/templates/accessibility-language-review-worksheet.md` records local reviewer approval, exceptions, accessible text equivalents, language parity, fallback routes, human-help routes, and public/private separation.
- `artifacts/checklists/accessibility-language-publication-checklist.md` gives the release maintainer a short go/no-go review path.
- `tools/accessibility_language_pack.py` generates the deterministic matrix, burndown, public preview index, and no-go notice.
- `scripts/check_accessibility_language_pack.py` fails the release if the generated pack drifts, loses the no-go boundary, or forgets the synthetic/non-certifying status.

## Release decision

The current synthetic release decision is:

```text
NO_GO_PUBLIC_RELEASE_ACCESSIBILITY_LANGUAGE_REVIEW_INCOMPLETE
```

That means synthetic example outputs may ship, but local voter-facing artifacts should not be promoted until each applicable row is locally approved or explicitly excepted.

## What this prevents

- Publishing a verified notice that screen-reader users cannot use.
- Publishing an English-only correction while a translated stale notice remains visible.
- Treating a map screenshot as adequate polling-place guidance without a text equivalent.
- Publishing an AI-assisted translation without source text, human approval, and prohibited-use/PII checks.
- Treating an offline copy as current voter instruction without a check date, digest, and fallback channel.
- Publishing safety/intimidation guidance that is hard to understand, overclaiming, or lacks a safe escalation route.

## Public-language rule

A public evidence summary is not voter-ready merely because the bytes verify. A voter-ready public answer needs the minimum usability floor: accessible text, plain language, local language-access review where applicable, fallback channel, human help route, review timestamp, and a boundary sentence saying what the answer does and does not prove.

## Gate integration

The new gate is wired into:

- `artifacts/registries/pilot-operational-invariants.csv`
- `artifacts/registries/release-go-no-go-criteria.csv`
- `artifacts/registries/release-maintainer-handoff.csv`
- `artifacts/registries/local-pilot-intake-requirements.csv`
- `artifacts/registries/standards-crosswalk.csv`
- `tools/release_maintainer_handoff_pack.py`
- `tools/release_go_no_go_pack.py`
- `scripts/release_gate_steps.py`

## Non-claims

This release does not certify WCAG, ADA, Section 203, state-law, local-language, public-records, emergency-communications, or election-office compliance. It only makes those review steps visible and blocks synthetic release outputs from being mistaken for locally approved voter-facing public answers.
