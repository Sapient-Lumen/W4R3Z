# 184 — Licensing, reuse, attribution, third-party content, contributor provenance, derivative redistribution, and compliance-boundary governance

## Purpose

Rev0178 adds legal/reuse-boundary governance. The archive now has lifecycle sustainability controls, but a package can be maintainable, preserved, portable, and releasable while still being unclear about who may reuse it, what attribution is requested, whether third-party content has been cleared, what contributor provenance is known, how derivatives should mark changes, and which legal or regulatory claims remain forbidden.

This document introduces a local licensing and reuse-governance layer. It does not create legal advice, license selection, copyright clearance, contributor assignment, regulatory compliance, public redistribution permission, endorsement, warranty, indemnity, or downstream legal support.

## Problem statement

Lifecycle sustainability prevents future-tense maintenance and preservation overclaims. But those controls do not answer six reuse questions:

1. Has a package-level legal license actually been selected and attached?
2. What attribution/citation language may be repeated without implying endorsement?
3. Are embedded third-party works, external anchors, quotations, generated text, and tool outputs distinguished?
4. What contributor provenance is locally recorded, and what assignments or contributor-license agreements remain absent?
5. What derivative or redistributed copies must not claim about authorization, support, endorsement, or compliance?
6. Which legal, regulatory, jurisdictional, and standards-compliance conclusions remain outside the archive's authority?

The new rule is: **availability is not permission**. A zip file can be downloadable and still not carry a public legal license grant or a cleared derivative-use path.

## New governed surfaces

Rev0178 adds these artifacts:

- `LICENSE_REUSE_POLICY.yml`
- `ATTRIBUTION_CITATION_LEDGER.yml`
- `THIRD_PARTY_CONTENT_REGISTER.yml`
- `CONTRIBUTOR_PROVENANCE_LEDGER.yml`
- `DERIVATIVE_REDISTRIBUTION_POLICY.yml`
- `COMPLIANCE_BOUNDARY_LEDGER.yml`
- `RUNBOOKS/legal-reuse-attribution-compliance-review-v1.md`
- `tools/check_legal_reuse.py`

The artifacts are deliberately local. They record absence, ambiguity, and forbidden upgrade claims as first-class governance evidence. They are not legal instruments.

## Control-stack position

Doc 184 follows doc 183. The intended control progression is now:

- doc 183 blocks maintainership, dependency-update, preservation, portability, succession, and sunset/end-of-life claim laundering;
- doc 184 blocks licensing, reuse, attribution, third-party content, contributor provenance, derivative redistribution, and compliance-boundary claim laundering.

## Reuse laundering failures

The checker treats the following as unsafe:

- a local license policy upgraded into a public legal license grant;
- an attribution/citation recommendation upgraded into endorsement, sponsorship, approval, or official status;
- a third-party content register upgraded into complete IP clearance;
- a contributor-provenance row upgraded into a contributor assignment, contributor license agreement, or warranty of authorship;
- a derivative-use policy upgraded into downstream redistribution permission, support, compatibility, or compliance guarantee;
- a compliance-boundary ledger upgraded into legal advice, regulatory review, jurisdictional approval, warranty, indemnity, or certification.

## Acceptance boundary

Rev0178 may say:

> The archive contains local licensing/reuse-boundary records for license-status, attribution/citation, third-party-content, contributor-provenance, derivative/redistribution, and compliance-boundary governance.

Rev0178 must not say:

> The archive grants a public license, provides legal advice, clears third-party content, records contributor assignments, authorizes derivatives, guarantees attribution sufficiency, gives regulatory compliance, or supplies warranty/indemnity.

## Required evidence

A legal/reuse claim now requires:

1. root legal/reuse artifacts;
2. current rev0178 records;
3. schemas for the six new record families;
4. query coverage;
5. fixture coverage;
6. control-stack coverage;
7. cube observations;
8. release-gate acceptance criteria;
9. checker reports;
10. public-claim warnings.

## Review trigger

Run the legal/reuse review whenever any of the following changes:

- a license, permission, copyright, public-domain, reuse, derivative, or redistribution claim;
- a citation, attribution, endorsement, sponsorship, or official-status claim;
- a quotation, external source, embedded image, dataset, code fragment, third-party excerpt, or imported artifact;
- a contributor identity, authorship, assignment, CLA/DCO, provenance, or generated-output claim;
- a warranty, indemnity, liability, regulatory, jurisdictional, standard-conformance, or legal-advice claim;
- a public package, mirror, repository, derivative, teaching packet, or downstream distribution boundary.

## Bet 107

A release can be locally valid, maintainable, portable, and preserved while still being legally ambiguous. Reuse governance prevents the archive from turning access to the package into permission to reuse it, derivative authority, or compliance assurance.
