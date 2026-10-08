# meta-0465 — Mission kernel, reproducibility, schema completeness, live gaps, and route-gravity audit

## Change summary

This note records the rev0785 deep-read and the first repairs made from it.

## Substantive priority

The archive’s heart is evidence continuity for public power, not accumulation of topics or generated agreement. The current repair phrase is **no governance by self-consistent cube**.

## Audit/refactor

Rev0785 makes default generated output reproducible from the release timestamp; adds a byte-stability check; enforces schema coverage for every canonical metadata/source JSON file; adds the missing route-merge and source-catalog schemas; repairs unrelated foundational tags; adds a compact `MISSION.md`; and restores live gaps for affected-person evidence, retirement, source preservation, archive governance, and power/material outcomes.

Validation also exposed a routing-parser defect: any Markdown bullet could be treated as a numbered note, and exactly-three-digit filename assumptions would fail at note `1000`. The filename grammar is now centralized, excludes `MISSION.md`, and accepts three or more digits.

## Validation target

`make lint` must pass from the working tree and a clean ZIP extraction, including the second-build hash comparison.
