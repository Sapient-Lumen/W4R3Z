# Pattern-control fields

Revision: rev0017

Pattern-control information may currently appear in:

- `records/patterns/*/type_payload.red_team_controls`
- `PATTERN-REDTEAM-LEDGER.json`
- `PATTERN-CONTROL-LEDGER.json`
- graph edges of type `positive_control_for_pattern`, `negative_control_needed_for_pattern`, or `pattern_scope_caution`

Minimum fields for a promoted control relation:

- `pattern_id`
- `control_record_id`
- `control_role`: `support`, `positive_control`, `negative_control`, `caught_before_harm`, `counterexample`, `scope_caution`
- `why_it_fits_or_does_not_fit`
- `what_it_prevents_the_pattern_from_overclaiming`
- `remaining_controls_needed`

A positive control cannot by itself mature a pattern. A mature pattern requires at least one positive control, one negative control, a counterexample search, and a decision about splitting/merging.
