# rev0305 field lane cleanliness report refactor

## Purpose

`make owner-field-report` gives maintainers a fast view of the live `FT-0181`
field lane without treating scratch as evidence. It is designed to reduce the
temptation to inspect or route from the old shared scratch root.

## What it reports

The report summarizes:

- selected field scratch root;
- operator-local as-of date;
- router outcome and recommended command;
- counts of known field artifacts;
- legacy top-level scratch items outside `scratch/field` and `scratch/checks`;
- executed/recorded field dates that fall after the operator-local date.

## What it does not do

The report is explicitly `LOCAL_SCRATCH_HYGIENE_NOT_EVIDENCE`. It cannot be cited
as owner evidence, custody, public-summary support, service-record authority,
lifecycle movement, or `FT-0181` closure.

## Use

```bash
make owner-field-report
```

For deterministic session replay:

```bash
CUBE_AS_OF_DATE=2026-06-16 make owner-field-report
```
