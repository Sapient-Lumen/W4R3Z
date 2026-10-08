# Redaction/publication gate and privacy floor

**Track:** Shared / A

Version v834 adds a redaction/public-publication gate. The goal is to keep evidence publication from becoming accidental publication of private voter, witness, staff, device, network, safety, or legal-review data.

## What changed

The new registry `artifacts/registries/redaction-publication-policy.csv` defines a public-release floor for common evidence families. The generated reports are:

- `artifacts/reports/redaction-publication-matrix.json`
- `artifacts/reports/redaction-publication-matrix.csv`
- `artifacts/reports/redaction-publication-burndown.json`
- `artifacts/reports/redaction-publication-burndown.csv`
- `artifacts/reports/public-release-preview-index.csv`
- `artifacts/reports/redaction-publication-no-go-notice.md`

The support files are:

- `artifacts/templates/public-release-redaction-worksheet.md`
- `artifacts/checklists/redaction-publication-checklist.md`
- `tools/redaction_publication_pack.py`
- `scripts/check_redaction_publication_pack.py`

## Why this matters

The stack is designed to make official-publication disputes easier to verify. That does not mean every local evidence object should be public. A parity snapshot can contain device or probe-route data. An intimidation report can contain names and precise locations. A witness set can contain private contact and safety information. A human-review worksheet can contain deliberation notes or legal-review material.

v834 therefore separates three things that earlier versions mentioned but did not gate as one generated pack:

1. the evidence family;
2. the minimum public fields that may be published after review;
3. the fields that must be removed, sealed, summarized, or routed through counsel/public-records review before release.

Informative alignment: `xref: nist_privacy_framework_page`; `source: nist_sp800_122_pdf`.

## Current decision

This archive reports `NO_GO_PUBLIC_RELEASE_REDACTION_REVIEW_INCOMPLETE`. That is intentional. Synthetic Example County material can be published as a rehearsal, but local or live evidence-derived public artifacts need jurisdiction-specific reviewer approval or a documented local exception.

## Boundaries

The redaction/publication pack is not live election evidence, not public-release authorization, not certification, not current voter instruction, not an outcome proof, not proof of intent or fraud, not a public-records ruling, and not legal advice.

## Promotion rule

No public-release claim should be made until the redaction matrix is regenerated with local reviewer approvals, public/private field decisions, and documented exceptions for every applicable policy row.
