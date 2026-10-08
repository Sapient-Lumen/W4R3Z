---
project: Immoral Wealth
status: validation_report
revision_current: rev0367
generated_at: 2026-06-18T14:06:00Z
---

# Validation report — rev0364

Command: `python tools/validate_archive.py`

```text
ERROR: Scoreboard schema failed: cases/stablecoins-money-market-treasury-liquidity-backstop-rev0319-scoreboard.json: 'severity' is a required property

Failed validating 'required' in schema['properties']['evidence_debt_register']['items']:
    {'type': 'object',
     'required': ['question', 'severity', 'next_evidence'],
     'properties': {'question': {'type': 'string'},
                    'severity': {'enum': ['low',
                                          'medium',
                                          'high',
                                          'blocking']},
                    'next_evidence': {'type': 'string'},
                    'source_ids': {'type': 'array',
                                   'items': {'type': 'string',
                                             'pattern': '^S[0-9]{2,3}$'}}},
     'additionalProperties': False}

On instance['evidence_debt_register'][5]:
    {'question': 'actual PPSI/FPSI supervisory reporting data and public '
                 'disclosure availability under PS-01/PS-02',
     'why_it_matters': 'The forms identify the data needed to test the '
                       'case; certification requires actual data '
                       'availability and issuer-level stress facts, not '
                       'just proposed form architecture.',
     'next_evidence': 'Final forms, OMB/PRA disposition, filing '
                      'instructions, public disclosure policy, and first '
                      'actual issuer reports or public aggregate releases.',
     'source_ids': ['S549', 'S550', 'S551'],
     'status': 'opened_rev0364'}
ERROR: Case memo/scoreboard source_refresh_due mismatch: cases/stablecoins-money-market-treasury-liquidity-backstop-rev0319-case.md has 2026-09-30, cases/stablecoins-money-market-treasury-liquidity-backstop-rev0319-scoreboard.json has 2026-08-31
ERROR: Missing current validation report: reports/validation-report-rev0364.md
ERROR: rev0326 stablecoin case must refresh by 2026-09-30 while GENIUS Act rulemaking is live
ERROR: MECHANICAL_EVIDENCE_SUMMARY scoreboard_source_ids count mismatch
ERROR: report-provenance-quarantine mismatch counts are stale
FAILED: 6 errors, 0 warnings
```
