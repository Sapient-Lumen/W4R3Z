# rev0063 refactor/audit notes

## Substantive refactor

Added `src/muc5/threat_closure.py` as a reusable closure-forensics layer instead of burying the rev0063 logic in a single script.  The module provides:

```text
ThreatClosureArm
rev0063_threat_closure_arms()
threat_closure_specs()
annotate_threat_closure_rows()
threat_closure_summary_rows()
threat_closure_mechanism_rows()
threat_closure_trace_features_from_spec()
summarize_threat_closure_features()
compare_threat_closure_by_life()
threat_closure_gate_report()
```

This lets later revisions ask the same closure questions against other opponent decks or candidate pilots without reimplementing C++-shadow rollout setup, target-seat annotation, or overdraw feature extraction.

## Policy-audit change

Added a public-information-only `threat_closure` profile in `src/muc5/public_agents.py`.  It uses only the same public observation boundary as other public agents, including own hand and own library count.  It does not inspect hidden opponent hand/library contents.

The new profile is intentionally conservative:

```text
- avoid attacks that self-deck before combat damage
- prefer smallest surviving lethal attack packet
- avoid Jace zero when own library is low
- do not ultimate self
- avoid redundant Overlord casts when current board can close
- preserve Overlords/lands over Jace/counters in discard choices against inert controls
```

Existing `threat_rush` behavior is unchanged.  The new profile is a comparison instrument, not a replacement promotion.

## Live audit issue found

Plain `pytest` can fail in this unpacked environment because the current repo root may not stay on the import path for `src.muc5`.  The stable command is:

```bash
PYTHONPATH=. python -m pytest -q
```

The validation artifacts and README use the stable command.  This is a workflow/import-path footgun, not a simulator semantic issue.

## Retention discipline

rev0063 generated 21,771 C++ shadow transition rows but ships only a 240-row transition sample.  No full `rev0063*_cpp_transitions.csv` or `rev0063*_transition_rows.csv` ballast is packaged.
