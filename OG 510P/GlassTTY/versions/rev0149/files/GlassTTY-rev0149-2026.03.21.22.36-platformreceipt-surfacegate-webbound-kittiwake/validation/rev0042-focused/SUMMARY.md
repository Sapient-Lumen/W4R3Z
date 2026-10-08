# GlassTTY rev0042 focused validation summary

- timestamp: 2026-03-08T18:35:26.184629+00:00
- overall_ok: True
- note: Focused manual validation bundle. scripts/validate-release.py itself still stopped early in this container, so rev0042 preserves the exact commands that passed individually.

| step | ok | stdout artifact | stderr artifact |
|---|---:|---|---|
| extension_typecheck | yes | extension_typecheck.stdout.txt | extension_typecheck.stderr.txt |
| extension_build | yes | extension_build.stdout.txt | extension_build.stderr.txt |
| pytest_protocol | yes | pytest_protocol.stdout.txt | pytest_protocol.stderr.txt |
| pytest_state | yes | pytest_state.stdout.txt | pytest_state.stderr.txt |
| pytest_broker | yes | pytest_broker.stdout.txt | pytest_broker.stderr.txt |
| pytest_cli | yes | pytest_cli.stdout.txt | pytest_cli.stderr.txt |
| pytest_plan_fixture | yes | pytest_plan_fixture.stdout.txt | pytest_plan_fixture.stderr.txt |
| pytest_native_budget | yes | pytest_native_budget.stdout.txt | pytest_native_budget.stderr.txt |
| pytest_index_constraints | yes | pytest_index_constraints.stdout.txt | pytest_index_constraints.stderr.txt |
| pytest_validate_release | yes | pytest_validate_release.stdout.txt | pytest_validate_release.stderr.txt |
| doctor_pretty | yes | doctor_pretty.json | doctor_pretty.stderr.txt |
| seed_fixture_corpus | yes | seed_fixture_corpus.log | seed_fixture_corpus.stderr.txt |
| index_fixture_corpus | yes | index_fixture_corpus.json | index_fixture_corpus.stderr.txt |
| compare_fixture_examples | yes | compare_fixture_examples.json | compare_fixture_examples.stderr.txt |
| native_message_budget | yes | native_message_budget.json | native_message_budget.stderr.txt |
