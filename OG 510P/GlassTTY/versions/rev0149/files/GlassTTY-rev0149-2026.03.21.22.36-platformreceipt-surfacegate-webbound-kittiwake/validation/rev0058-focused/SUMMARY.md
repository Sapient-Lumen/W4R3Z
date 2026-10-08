# GlassTTY validation summary

- revision: rev0058
- timestamp: 2026-03-09T10:30:00Z
- overall_ok: True
- scope: direct-command focused validation in this container
- pytest_focused: 37 passed in 0.70s
- indexed_fixture_count: 11
- native_message_budget_fixture_count: 11

| step | ok | stdout | stderr |
|---|---:|---|---|
| extension_typecheck | yes | extension_typecheck.stdout.txt | extension_typecheck.stderr.txt |
| extension_build | yes | extension_build.stdout.txt | extension_build.stderr.txt |
| receiver_inventory_check | yes | receiver_inventory_check.stdout.txt | receiver_inventory_check.stderr.txt |
| receiver_priming_check | yes | receiver_priming_check.stdout.txt | receiver_priming_check.stderr.txt |
| pytest_focused | yes | pytest_focused.stdout.txt | pytest_focused.stderr.txt |
| doctor_pretty | yes | doctor_pretty.stdout.txt | doctor_pretty.stderr.txt |
| seed_fixture_corpus | yes | seed_fixture_corpus.stdout.txt | seed_fixture_corpus.stderr.txt |
| index_fixture_corpus | yes | index_fixture_corpus.stdout.txt | index_fixture_corpus.stderr.txt |
| compare_fixture_examples | yes | compare_fixture_examples.stdout.txt | compare_fixture_examples.stderr.txt |
| native_message_budget | yes | native_message_budget.stdout.txt | native_message_budget.stderr.txt |

## Notes

- `doctor.py --pretty` completed successfully, and in this container it still reports the native-host wrapper path as present/absolute but not executable (`executable=False`).
- The new browser-side resolver audit fields are proven only through shared-helper/deterministic validation here; no fresh live Chromium/native-messaging/browser round-trip exercised `bridge.probe.receiverAudit` or `fixture.capture` against a real supported tab in this environment.
- This bundle was built from direct commands because longer wrapper-level validation runs have been getting cut off mid-flight in this environment.
