# rev0303 cloudtainer scratch firebreak audit

## Problem statement

This cloudtainer can hold both live field scratch and checker scratch in the same
`/scratch` tree. Packaging excludes scratch, but live routing happens before
packaging. A control that is safe in a clean release can still waste a session if a
maintainer runs lints, then asks the router what field action is next.

## Bad pattern

```text
make lint-owner-reply
# checker writes synthetic artifacts under scratch/check-*
# helper writes a review brief outside scratch/check-* that references a check seed
make owner-field-work OUT=scratch/ft0181-field-work/aiedu-sr-003
# router treats the helper artifact as field state
```

The bad pattern does not create accepted evidence. It does create false workflow
position: the maintainer can be routed to later review/decision preparation even
though no real owner reply exists.

## Firebreak rule

Field routing now treats these as non-field scratch unless the operator explicitly
chooses a different scratch root whose own children are field-lane artifacts:

- relative path parts beginning `check-`, `smoke-`, `test-`, or `fixture-`;
- JSON artifacts whose provenance references point into those non-field subtrees.

The rule is local and conservative. It does not delete scratch. It does not alter
packaging. It only prevents non-field scratch from ranking in the one-action field
router.

## Longer cleanup path

A future revision should make lane separation visible in paths, not only in code:

```text
scratch/field/ft0181/...
scratch/checks/<validator>/...
scratch/release/<stamp>/...
```

Then `owner-field-work` can default to `scratch/field/ft0181` and check tools can
never write into the router's default field scan root. Until that refactor, the
rev0303 collector guard is the practical correction.
