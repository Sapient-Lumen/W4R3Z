"""Ensure hot operator commands match the executable fail-fast stage contracts."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
commands = context.get("commands")
if not isinstance(commands, dict):
    raise SystemExit("context-pack commands must be an object")

score_command = commands.get("score_external_response")
if not isinstance(score_command, str):
    raise SystemExit("context-pack missing score_external_response command")
for token in ["RESPONSE=", "EVIDENCE=", "SCORE_SHEET=", "SUMMARY_OUT="]:
    if token not in score_command:
        raise SystemExit(f"context-pack score command missing current required token: {token}")

for token in [
    "score-external-response:",
    'SCORE_SHEET required (path to completed post-response score sheet JSON)',
    '--score-sheet "$(SCORE_SHEET)"',
    "prepare-external-custody:",
    "ATTEST_CLEAN_PREANSWER=yes required",
    "prepare_priority_zero_clean_response_custody_record.py",
]:
    if token not in makefile:
        raise SystemExit(f"Makefile operator contract missing token: {token}")

responder_readme = (ROOT / "handoffs/priority-zero-preanswer-clamped-external-replay-responder-readme-2026-06-16.md").read_text(encoding="utf-8")
for token in [
    "prepare_priority_zero_external_replay_response.py init",
    "prepare_priority_zero_external_replay_response.py finalize",
    "--bundle-file <original-responder-bundle.zip>",
    "--attest-clean-preanswer",
    "fails before custody is spent",
]:
    if token not in responder_readme:
        raise SystemExit(f"current responder README missing runnable fail-fast token: {token}")

custody_readme = (ROOT / "handoffs/priority-zero-preanswer-clamped-clean-response-custody-readme-2026-06-16.md").read_text(encoding="utf-8")
for token in [
    "prepare_priority_zero_clean_response_custody_record.py",
    "--custodian-id",
    "--attest-clean-preanswer",
    "No response, custody-open, or custody-freeze timestamp is accepted as a CLI argument",
]:
    if token not in custody_readme:
        raise SystemExit(f"current custody README missing runnable fail-fast token: {token}")

scorer_readme = (ROOT / "handoffs/priority-zero-preanswer-clamped-external-replay-scorer-readme-2026-06-16.md").read_text(encoding="utf-8")
for token in [
    "prepare_priority_zero_external_replay_score_sheet.py init",
    "prepare_priority_zero_external_replay_score_sheet.py finalize",
    "SCORE_SHEET=<completed-score-sheet.json>",
    "captures scorer-kit initialization time",
    "captures `scored_at` automatically",
]:
    if token not in scorer_readme:
        raise SystemExit(f"current scorer README missing runnable command token: {token}")

manual_timestamp_flags = [
    "--response-frozen-at",
    "--custody-kit-opened-at",
    "--custody-record-frozen-at",
    "--scorer-kit-opened-at",
    "--scored-at",
]
for surface, text in [
    ("Makefile", makefile),
    ("current custody README", custody_readme),
    ("current scorer README", scorer_readme),
]:
    for flag in manual_timestamp_flags:
        if flag in text:
            raise SystemExit(f"{surface} retained current manual stage-time flag: {flag}")

print("check_operator_command_surface_contract: OK")
