# rev0085 refactor audit

rev0085 factors paired transfer evidence checks into `src/muc5/population_pair_forensics.py`.

## New shared functions

- `pair_integrity_rows`
- `summarize_pair_integrity`
- `paired_sign_summary`
- `grouped_sign_summary_rows`
- `tie_mechanism_summary`
- `grouped_tie_mechanism_rows`
- `binomial_tail_at_least`

## Why this matters

The previous candidate-transfer audit could say that a candidate lost by mean and pair counts, but it did not distinguish:

- point-negative but statistically weak evidence,
- exact paired sign-test support,
- all-tie indistinguishability,
- and same-score mechanism drift.

That logic is now reusable for future adaptive counter candidates. Any new candidate can be blocked for pair-integrity failure, familywise exact sign-test failure, or non-equivalent tie behavior before it is allowed anywhere near a broad population gate.

## Audit/refactor result

The refactor found no implementation bug in rev0084's pair matching. It did find an interpretation bug: the selected-cell holdout had been described as negative-transfer, but exact paired testing shows it is only point-negative. The broad transfer panel remains a statistically supported reason to quarantine the candidate.
