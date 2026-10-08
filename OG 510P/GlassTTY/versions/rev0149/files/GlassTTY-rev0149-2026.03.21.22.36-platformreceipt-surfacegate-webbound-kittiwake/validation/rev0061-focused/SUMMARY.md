# GlassTTY validation summary

- revision: rev0061
- timestamp: 2026-03-09T12:10:00Z
- overall_ok: True
- baseline_archive: GlassTTY-rev0060-2026.03.09.11.18-policyhints-manifestaudit-gapadvice-sunbird.zip
- wrapper_validate_release: partial (preserved under `validation/rev0061-wrapper/`)
- live_browser_round_trip: not reproved here

| step | ok | returncode | stdout | stderr |
|---|---:|---:|---|---|
| extension_typecheck | yes | 0 | extension_typecheck.stdout.txt | extension_typecheck.stderr.txt |
| extension_build | yes | 0 | extension_build.stdout.txt | extension_build.stderr.txt |
| receiver_inventory_check | yes | 0 | receiver_inventory_check.stdout.json | receiver_inventory_check.stderr.txt |
| receiver_priming_check | yes | 0 | receiver_priming_check.stdout.json | receiver_priming_check.stderr.txt |
| pytest_focused | yes | 0 | pytest_focused.stdout.txt | pytest_focused.stderr.txt |
| doctor_pretty | yes | 0 | doctor_pretty.stdout.json | doctor_pretty.stderr.txt |
| seed_fixture_corpus | yes | 0 | seed_fixture_corpus.stdout.txt | seed_fixture_corpus.stderr.txt |
| index_fixture_corpus | yes | 0 | index_fixture_corpus.stdout.json | index_fixture_corpus.stderr.txt |
| compare_fixture_examples | yes | 0 | compare_fixture_examples.stdout.json | compare_fixture_examples.stderr.txt |
| native_message_budget | yes | 0 | native_message_budget.stdout.json | native_message_budget.stderr.txt |

## Notes

- `receiver_priming_check` now validates the new receiver-coverage experiment matrix, including the about:blank recommendation lane and the broader `match_origin_as_fallback` recommendation lane when an opaque related-frame gap is added.
- The wrapper-level `scripts/validate-release.py` run still appears fragile in this environment; only its early step artifacts are claimed.
