#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_proof_pack_check import DEFAULT_PACK_DIR, check_pack
from chatgpt_proof_pack_exporter import DEFAULT_INPUT, export_pack
from chatgpt_proof_pack_integrity import build_pack_integrity
from chatgpt_proof_privacy_review import build_privacy_review

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FINAL_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-finalize-summary.json'
DEFAULT_EXPORT_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-pack-export-summary.json'
DEFAULT_CHECK_SUMMARY = ROOT / 'validation' / 'latest' / 'chatgpt-proof-pack-check-summary.json'
SCHEMA_VERSION = 1

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def blocker_action(blocker: str) -> JsonDict:
    lowered = blocker.lower()
    if 'rehearsal_only=true' in lowered or 'rehearsal evidence pack' in lowered:
        return {
            'blocker': blocker,
            'operator_action': 'Use a real side-panel proof capture JSON instead of the offline rehearsal bundle.',
            'command_hint': 'glassttyd proof-finalize-pack --input <live-sidepanel-proof.json> --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --clean --pretty',
        }
    if 'placeholder' in lowered or '1x1' in lowered or 'screenshot' in lowered:
        return {
            'blocker': blocker,
            'operator_action': 'Capture a real visible ChatGPT screenshot from the side panel, copy proof JSON again, and rerun finalization.',
            'command_hint': 'In the side panel: Capture visible screenshot → Download proof JSON; then rerun proof-finalize-pack with --input pointing at the downloaded JSON and --require-live.',
        }
    if 'evaluator verdict' in lowered:
        return {
            'blocker': blocker,
            'operator_action': 'Inspect chatgpt-first-proof-evaluation.json and fix the missing proof checks before review.',
            'command_hint': 'cat <pack-dir>/chatgpt-first-proof-evaluation.json',
        }
    if 'missing artifact slots' in lowered or 'empty artifact slots' in lowered:
        return {
            'blocker': blocker,
            'operator_action': 'Re-export the pack from the complete proof capture, preferably with --clean.',
            'command_hint': 'glassttyd proof-finalize-pack --input <capture.json> --pack-dir <pack-dir> --clean --pretty',
        }
    if 'json parse failures' in lowered or 'failed to parse' in lowered:
        return {
            'blocker': blocker,
            'operator_action': 'Regenerate the malformed artifact; do not hand-edit JSON unless preserving valid UTF-8 and exact attempt IDs.',
            'command_hint': 'glassttyd proof-export-pack --input <capture.json> --pack-dir <pack-dir> --clean --pretty',
        }
    if 'harness_ok' in lowered:
        return {
            'blocker': blocker,
            'operator_action': 'Run the evaluator on bundle-manifest.json and resolve missing required checks.',
            'command_hint': 'python scripts/chatgpt-first-proof-evaluator.py --input <pack-dir>/bundle-manifest.json --pretty',
        }
    return {
        'blocker': blocker,
        'operator_action': 'Inspect the named artifact and rerun finalization after the evidence is corrected.',
        'command_hint': 'glassttyd proof-check-pack --pack-dir <pack-dir> --require-live --pretty',
    }


def build_operator_handoff(report: JsonDict) -> tuple[JsonDict, str]:
    check = report.get('check') if isinstance(report.get('check'), dict) else {}
    export = report.get('export') if isinstance(report.get('export'), dict) else {}
    pack_dir = report.get('pack_dir')
    blockers = report.get('blockers') if isinstance(report.get('blockers'), list) else []
    handoff = {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-proof-operator-handoff',
        'generated_at': utcnow(),
        'ok': report.get('ok'),
        'verdict': report.get('verdict'),
        'pack_dir': pack_dir,
        'require_live': report.get('require_live'),
        'attempt_id': export.get('attempt_id') or (check.get('manifest') if isinstance(check.get('manifest'), dict) else {}).get('attempt_id'),
        'artifact_count': {
            'present': check.get('present_artifact_count'),
            'expected': check.get('expected_artifact_count'),
            'complete': check.get('complete_artifact_set'),
        },
        'screenshot': check.get('screenshot'),
        'evaluation': check.get('evaluation'),
        'privacy_review': report.get('privacy_review'),
        'blockers': blockers,
        'blocker_actions': report.get('blocker_actions'),
        'operator_next_commands': report.get('operator_next_commands'),
    }
    lines = [
        '# ChatGPT proof operator handoff',
        '',
        f"- verdict: `{report.get('verdict')}`",
        f"- ok: `{report.get('ok')}`",
        f"- require_live: `{report.get('require_live')}`",
        f"- pack_dir: `{pack_dir}`",
        f"- attempt_id: `{handoff.get('attempt_id')}`",
        f"- artifact_count: `{check.get('present_artifact_count')}` / `{check.get('expected_artifact_count')}`",
        f"- evaluator_verdict: `{(check.get('evaluation') or {}).get('verdict') if isinstance(check.get('evaluation'), dict) else None}`",
        f"- privacy_review_verdict: `{(report.get('privacy_review') or {}).get('verdict') if isinstance(report.get('privacy_review'), dict) else None}`",
        '',
    ]
    if blockers:
        lines.extend(['## Blockers', ''])
        for action in report.get('blocker_actions') or []:
            lines.append(f"- {action.get('blocker')}")
            lines.append(f"  - action: {action.get('operator_action')}")
            lines.append(f"  - command: `{action.get('command_hint')}`")
        lines.append('')
    else:
        lines.extend([
            '## Ready path',
            '',
            '- Re-run `proof-check-pack --require-live` before making any live proof claim.',
            '- Human privacy/redaction review must be `privacy-review-pass` before publishing screenshots or transcripts.',
            '',
        ])
    lines.extend(['## Next commands', ''])
    for command in report.get('operator_next_commands') or []:
        lines.append(f'- `{command}`')
    lines.append('')
    return handoff, '\n'.join(lines)


def finalize_pack(
    source_path: Path = DEFAULT_INPUT,
    pack_dir: Path = DEFAULT_PACK_DIR,
    *,
    final_summary_path: Path = DEFAULT_FINAL_SUMMARY,
    export_summary_path: Path = DEFAULT_EXPORT_SUMMARY,
    check_summary_path: Path = DEFAULT_CHECK_SUMMARY,
    clean: bool = False,
    require_live: bool = False,
    allow_placeholder_screenshot: bool | None = None,
    require_privacy_pass: bool = False,
    privacy_reviewer: str | None = None,
    privacy_decision: str = 'pending',
    privacy_attest_screenshot_reviewed: bool = False,
    privacy_attest_no_unrelated_content: bool = False,
    privacy_attest_local_only: bool = False,
) -> JsonDict:
    export_summary = export_pack(
        source_path,
        pack_dir,
        summary_path=export_summary_path,
        clean=clean,
        allow_placeholder_screenshot=allow_placeholder_screenshot,
    )
    privacy_review = build_privacy_review(
        pack_dir,
        json_out=pack_dir / 'privacy-redaction-review.json',
        markdown_out=pack_dir / 'privacy-redaction-review.md',
        reviewer=privacy_reviewer,
        decision=privacy_decision,
        require_live=require_live,
        require_pass=require_privacy_pass,
        attest_screenshot_reviewed=privacy_attest_screenshot_reviewed,
        attest_no_unrelated_content=privacy_attest_no_unrelated_content,
        attest_local_only=privacy_attest_local_only,
    )
    check_report = check_pack(
        pack_dir,
        summary_path=check_summary_path,
        require_live=require_live,
        allow_rehearsal=not require_live,
        require_privacy_pass=require_privacy_pass,
    )
    export_ok = bool(export_summary.get('ok'))
    check_ok = bool(check_report.get('ok'))
    privacy_ok = bool(privacy_review.get('ok'))
    ok = export_ok and check_ok and privacy_ok
    rehearsal_only = bool(check_report.get('manifest', {}).get('rehearsal_only')) if isinstance(check_report.get('manifest'), dict) else False
    if require_live and require_privacy_pass and ok:
        verdict = 'live-proof-pack-finalized-privacy-reviewed'
    elif require_live and ok:
        verdict = 'live-proof-pack-finalized-review-ready'
    elif ok and rehearsal_only:
        verdict = 'rehearsal-proof-pack-finalized-not-live'
    elif ok:
        verdict = 'proof-pack-finalized-live-status-unconfirmed'
    else:
        verdict = 'proof-pack-finalization-blocked'
    blockers = []
    if not export_ok:
        blockers.append('proof-export-pack did not produce an ok summary')
    if not privacy_ok:
        blockers.append('proof-privacy-review did not produce an ok summary')
    blockers.extend([b for b in check_report.get('blockers', []) if isinstance(b, str)])
    blockers.extend([b for b in privacy_review.get('blockers', []) if isinstance(b, str)])
    blocker_actions = [blocker_action(blocker) for blocker in blockers]
    live_pack_dir = ROOT / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'
    operator_next_commands = [
        f'glassttyd proof-check-pack --pack-dir {display_path(pack_dir)} --pretty',
    ]
    if require_live:
        operator_next_commands[0] = f'glassttyd proof-check-pack --pack-dir {display_path(pack_dir)} --require-live --pretty'
        operator_next_commands.append(
            f'glassttyd proof-privacy-review --pack-dir {display_path(pack_dir)} --require-live --reviewer <name> --decision pass --attest-screenshot-reviewed --attest-no-unrelated-content --attest-local-only --pretty'
        )
    else:
        operator_next_commands.append(
            f'glassttyd proof-finalize-pack --input <live-sidepanel-proof.json> --pack-dir {display_path(live_pack_dir)} --require-live --clean --pretty'
        )
    report: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-finalize-pack',
        'generated_at': utcnow(),
        'ok': ok,
        'verdict': verdict,
        'source_path': display_path(source_path),
        'pack_dir': display_path(pack_dir),
        'require_live': require_live,
        'export_summary_path': display_path(export_summary_path),
        'check_summary_path': display_path(check_summary_path),
        'final_summary_path': display_path(final_summary_path),
        'export': export_summary,
        'check': check_report,
        'privacy_review': privacy_review,
        'blockers': blockers,
        'blocker_actions': blocker_actions,
        'operator_next_commands': operator_next_commands,
        'operator_notes': [
            'This command runs export and pack-check as one operator-facing finalization gate.',
            'A rehearsal finalization proves local plumbing only; it must not be treated as a live ChatGPT proof.',
            'A live finalization still requires human privacy/redaction review before publication.',
        ],
    }
    handoff_json, handoff_markdown = build_operator_handoff(report)
    write_json(pack_dir / 'operator-handoff.json', handoff_json)
    write_text(pack_dir / 'OPERATOR-HANDOFF.md', handoff_markdown)
    report['operator_handoff_json_path'] = display_path(pack_dir / 'operator-handoff.json')
    report['operator_handoff_markdown_path'] = display_path(pack_dir / 'OPERATOR-HANDOFF.md')
    integrity_summary_path = ROOT / 'validation' / 'latest' / 'chatgpt-proof-pack-integrity-summary.json'
    integrity = build_pack_integrity(
        pack_dir,
        summary_path=integrity_summary_path,
        write_pack_file=True,
        refresh_ledger=True,
    )
    report['pack_integrity'] = integrity
    report['pack_integrity_summary_path'] = display_path(integrity_summary_path)
    report['pack_integrity_path'] = display_path(pack_dir / 'evidence-pack-integrity.json')
    if not integrity.get('ok'):
        report['ok'] = False
        report['verdict'] = 'proof-pack-finalization-blocked'
        report.setdefault('blockers', []).append('proof-pack-integrity did not produce an ok summary')
    write_json(final_summary_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Export and check a ChatGPT proof capture as a single operator-facing finalization gate.')
    parser.add_argument('--input', type=Path, default=DEFAULT_INPUT)
    parser.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_FINAL_SUMMARY)
    parser.add_argument('--export-summary-out', type=Path, default=DEFAULT_EXPORT_SUMMARY)
    parser.add_argument('--check-summary-out', type=Path, default=DEFAULT_CHECK_SUMMARY)
    parser.add_argument('--clean', action='store_true')
    parser.add_argument('--require-live', action='store_true')
    parser.add_argument('--allow-placeholder-screenshot', action='store_true')
    parser.add_argument('--no-placeholder-screenshot', action='store_true')
    parser.add_argument('--require-privacy-pass', action='store_true')
    parser.add_argument('--privacy-reviewer')
    parser.add_argument('--privacy-decision', choices=['pending', 'pass', 'fail'], default='pending')
    parser.add_argument('--privacy-attest-screenshot-reviewed', action='store_true')
    parser.add_argument('--privacy-attest-no-unrelated-content', action='store_true')
    parser.add_argument('--privacy-attest-local-only', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    allow: bool | None = None
    if args.allow_placeholder_screenshot:
        allow = True
    if args.no_placeholder_screenshot:
        allow = False
    report = finalize_pack(
        args.input,
        args.pack_dir,
        final_summary_path=args.summary_out,
        export_summary_path=args.export_summary_out,
        check_summary_path=args.check_summary_out,
        clean=args.clean,
        require_live=args.require_live,
        allow_placeholder_screenshot=allow,
        require_privacy_pass=args.require_privacy_pass,
        privacy_reviewer=args.privacy_reviewer,
        privacy_decision=args.privacy_decision,
        privacy_attest_screenshot_reviewed=args.privacy_attest_screenshot_reviewed,
        privacy_attest_no_unrelated_content=args.privacy_attest_no_unrelated_content,
        privacy_attest_local_only=args.privacy_attest_local_only,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
