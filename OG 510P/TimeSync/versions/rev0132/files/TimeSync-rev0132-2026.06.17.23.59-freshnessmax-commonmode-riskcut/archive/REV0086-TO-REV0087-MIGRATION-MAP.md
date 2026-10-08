# Migration map — rev0086 to rev0087

## Additions

- `compatibility_drift` may appear in profile compatibility statements when the statement is used for drift review, aggregate lifecycle portability, or discovery downgrade review.
- `version_negotiation` may include digest-bound downgrade proof fields.
- `semantic-version-negotiation` moves to `negotiation_version: rev0087` and may include `downgrade_proof_policy`.

## Required behavior changes

- Weaker, unknown, incomparable, or unproven digest-rollover profile drift must fail closed for current compatibility use.
- Current-use discovery downgrade requires a proof digest and stronger-or-equal semantics.
- Unsupported newer versions remain metadata-only, omitted, or rejected unless explicitly supported.

## Documentation audit

Rendered profile Markdown files now must include all non-satisfying evidence classes listed in the normative profile catalog.
