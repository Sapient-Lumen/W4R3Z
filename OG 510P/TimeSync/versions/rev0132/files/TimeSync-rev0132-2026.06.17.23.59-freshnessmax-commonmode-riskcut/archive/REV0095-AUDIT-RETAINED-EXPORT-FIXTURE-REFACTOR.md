# rev0095 audit — retained export and fixture refactor

## What was risky

retained-export validation previously checked retained status, profile-reference strength, and evidence-summary binding, but it did not centralize export-time monotonicity. That left a gap between historical records and current-policy interpretation. A retained artifact could be internally plausible yet temporally impossible: the evidence or policy check it carried could happen after the export timestamp.

The second risk was operational. Many negative fixtures are large near-copies of positive fixtures. That makes individual semantic failures hard to inspect and easy to accidentally change into a different failure mode.

## What changed

`tools/retained_export_temporal.py` now owns retained-export temporal relations and has self-tests. `tools/validate_archive.py` calls it from `check_retained_export(...)` instead of growing more inline timestamp code.

`tools/fixture_derivations.py` now validates a YAML manifest of patch-derived fixtures. The first converted family covers the three new retained-export negatives. This is intentionally incremental: it creates the machinery without forcing a noisy conversion of the whole corpus in one revision.

## Why this is not registry bureaucracy

No new vocabulary registry or policy catalog was added. The revision adds executable checks, three negative examples, and one small derivation mechanism that prevents copy drift. The rendered examples remain available for human auditors.

## Next useful extraction

The semantic-vector execution loop is now a good candidate for extraction into a tested helper. That would reduce `validate_archive.py` without changing semantics and would make fixture-derivation failures easier to report beside semantic-vector failures.
