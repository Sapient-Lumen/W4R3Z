# GlassTTY validation summary

- revision: rev0059
- timestamp: 2026-03-09T10:42:00Z
- overall_ok: True
- scope: direct-command focused validation in this container
- pytest_focused: 37 passed in 0.68s
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
| refresh_archive | yes | refresh_archive.stdout.txt | refresh_archive.stderr.txt |


## Notes

- `bridge.probe.receiverAudit.coverageAudit` and fixture `receiver_coverage_*` metadata are proven here through shared-helper/deterministic extension validation only; no fresh live Chromium/native-messaging/browser round-trip exercised a real related-frame tab in this container.
- `receiver_priming_check` now proves that `about:blank` descendants are surfaced as `related_frame_url` instead of a generic unsupported bucket, while ordinary unsupported hosts remain `unsupported_url`.
- This bundle was built from direct commands because longer wrapper-level validation runs have been getting cut off mid-flight in this environment.
