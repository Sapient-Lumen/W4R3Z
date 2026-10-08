# 933 — CDF independent verifier transcript and release-gate risk burn-down

**Track:** Shared

v895 made K03 executable by adding a primary synthetic BD/CVR/ERR replay bridge. That was real progress, but it still left a high-risk seam: a single adapter could confirm its own interpretation of the synthetic export fixture. K03's live acceptance gate explicitly names an independent verifier transcript, so the next release must produce a second parser/tally path rather than another registry statement.

v896 adds `tools/cdf_replay_independent_verifier.py` and gates it with `scripts/check_cdf_independent_replay_verifier.py`.

## What the new verifier does

The independent verifier:

- reads the same synthetic minimal Ballot Definition, Cast Vote Records, and Election Results projection files as raw JSON inputs;
- indexes reporting units, ballot styles, contests, options, and selection limits without importing the primary replay adapter;
- recomputes CVR-derived option totals;
- independently parses published ERR totals;
- compares every contest/option row;
- checks that the primary adapter's comparison rows match the independent rows;
- checks that the shipped CRO vote rows match the independent published totals; and
- writes `artifacts/reports/cdf-independent-replay-verifier-rev0896.json` plus `artifacts/examples/example_county_2026_municipal_pilot/cdf/public-cdf-independent-verifier.md`.

## Negative controls now required

The gate requires these failures before the release can pass:

- mismatched ERR total fails with `ERR_TOTAL_MISMATCH`;
- unknown CVR option fails with `CVR_UNKNOWN_OPTION`;
- selection-limit/overvote fails with `CVR_SELECTION_LIMIT_EXCEEDED`;
- deliberately altered primary comparison rows fail with `PRIMARY_REPLAY_COMPARISON_ROWS_DISAGREE`; and
- deliberately altered CRO vote rows fail with `PRIMARY_CRO_VOTE_ROWS_DISAGREE`.

This matters because the verifier now catches both bad export bytes and bad downstream replay artifacts. The previous v895 bridge caught export-level problems but did not release-gate an independent transcript or prove that a stale/altered primary report would be detected.

## Refactor audit

The CDF lane also had a smaller drift smell: the generated mapping manifest still described EEL as `not included in v895 replay fixture`. v896 makes that boundary derive from the current archive version, so future revisions do not carry a stale embedded version string.

The release-gate inventory now includes `scripts/check_cdf_independent_replay_verifier.py` immediately after `scripts/check_cdf_export_replay.py`. The go/no-go pack and offline drill plan also name the independent verifier so the publication decision cannot summarize the primary adapter while silently omitting the second transcript.

## Boundaries

This is still a synthetic minimal projection. It is not full NIST CDF conformance, not the NIST CDF Test Method, not live jurisdiction export evidence, not external reviewer execution, not certification, not outcome proof, not current voter instruction, and not legal advice.

The remaining K03 blockers are unchanged: actual jurisdiction export bytes, a real adapter transcript, external independent reviewer execution, and local authority approval remain required before any live-pilot or public-release claim.
