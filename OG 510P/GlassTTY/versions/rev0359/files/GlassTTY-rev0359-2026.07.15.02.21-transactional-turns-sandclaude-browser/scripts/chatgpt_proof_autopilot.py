#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_proof_attempt_audit import audit_file
from chatgpt_proof_transfer_audit import audit_transfer
from chatgpt_proof_finalize_pack import finalize_pack
from chatgpt_proof_ingest import ingest_capture
from chatgpt_proof_preflight import run_preflight
from chatgpt_proof_privacy_review import build_privacy_review
from chatgpt_proof_publish_bundle import publish_bundle as build_publish_bundle
from chatgpt_proof_publish_verify import verify_publish_bundle
from chatgpt_proof_status import build_status

ROOT = Path(__file__).resolve().parent.parent
LATEST = ROOT / 'validation' / 'latest'
LIVE_PACK = ROOT / 'validation' / 'live-proof-evidence' / 'chatgpt' / 'chatgpt-proof-evidence-pack'
DEFAULT_SUMMARY = LATEST / 'chatgpt-proof-autopilot-summary.json'
DEFAULT_OPERATOR_STATE = LATEST / 'chatgpt-proof-operator-state.json'
DEFAULT_CAPTURE = LATEST / 'chatgpt-first-proof-capture.json'
DEFAULT_CAPTURE_REDACTED = LATEST / 'chatgpt-first-proof-capture.redacted.json'
DEFAULT_ATTEMPT_AUDIT_SUMMARY = LATEST / 'chatgpt-proof-attempt-audit.json'
DEFAULT_TRANSFER_AUDIT_SUMMARY = LATEST / 'chatgpt-proof-transfer-audit.json'
DEFAULT_INGEST_SUMMARY = LATEST / 'chatgpt-proof-ingest-summary.json'
DEFAULT_FINALIZE_SUMMARY = LATEST / 'chatgpt-proof-finalize-summary.json'
DEFAULT_EXPORT_SUMMARY = LATEST / 'chatgpt-proof-pack-export-summary.json'
DEFAULT_CHECK_SUMMARY = LATEST / 'chatgpt-proof-pack-check-summary.json'
DEFAULT_PUBLISH_BUNDLE = LATEST / 'chatgpt-proof-publish-bundle.zip'
DEFAULT_PUBLISH_SUMMARY = LATEST / 'chatgpt-proof-publish-summary.json'
DEFAULT_PUBLISH_VERIFY_SUMMARY = LATEST / 'chatgpt-proof-publish-verify-summary.json'
SCHEMA_VERSION = 1

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def display_path(path: Path | None, *, root: Path = ROOT) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def compact_step(name: str, *, attempted: bool, ok: bool | None = None, verdict: str | None = None,
                 skipped_reason: str | None = None, report: JsonDict | None = None) -> JsonDict:
    row: JsonDict = {
        'name': name,
        'attempted': attempted,
    }
    if ok is not None:
        row['ok'] = bool(ok)
    if verdict is not None:
        row['verdict'] = verdict
    if skipped_reason:
        row['skipped_reason'] = skipped_reason
    if isinstance(report, dict):
        for key in ('blockers', 'warnings', 'next_actions', 'operator_next_commands'):
            value = report.get(key)
            if value:
                row[key] = value
        for key in ('summary_path', 'pack_dir', 'out', 'bundle', 'publish_bundle'):
            value = report.get(key)
            if value:
                row[key] = value
    return row


def privacy_inputs_complete(*, reviewer: str | None, decision: str,
                            attest_screenshot_reviewed: bool,
                            attest_no_unrelated_content: bool,
                            attest_local_only: bool) -> bool:
    return bool(
        reviewer
        and decision == 'pass'
        and attest_screenshot_reviewed
        and attest_no_unrelated_content
        and attest_local_only
    )


def _status(*, require_live: bool, live_pack_dir: Path, publish_bundle: Path) -> JsonDict:
    return build_status(
        summary_path=DEFAULT_OPERATOR_STATE,
        live_pack_dir=live_pack_dir,
        publish_bundle_path=publish_bundle,
        require_live=require_live,
    )


def maybe_run_preflight(*, execute: bool, steps: list[JsonDict]) -> JsonDict | None:
    if not execute:
        steps.append(compact_step('proof-preflight', attempted=False, skipped_reason='dry-run mode'))
        return None
    report = run_preflight(
        out=LATEST / 'chatgpt-proof-preflight.json',
        rehearsal_out=LATEST / 'chatgpt-proof-rehearsal.json',
        evaluation_out=LATEST / 'chatgpt-proof-rehearsal-evaluation',
    )
    steps.append(compact_step('proof-preflight', attempted=True, ok=bool(report.get('ok')), verdict=report.get('verdict'), report=report))
    return report


def run_autopilot(
    *,
    summary_out: Path = DEFAULT_SUMMARY,
    execute_safe: bool = False,
    execute_live: bool = False,
    input_path: Path | None = None,
    live_pack_dir: Path = LIVE_PACK,
    publish_bundle: Path = DEFAULT_PUBLISH_BUNDLE,
    require_complete: bool = False,
    clean: bool = False,
    reviewer: str | None = None,
    decision: str = 'pending',
    attest_screenshot_reviewed: bool = False,
    attest_no_unrelated_content: bool = False,
    attest_local_only: bool = False,
) -> JsonDict:
    steps: list[JsonDict] = []
    execute_any = execute_safe or execute_live
    initial_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
    stage = initial_status.get('current_stage')

    # Static/offline preflight is safe and useful to refresh whenever explicitly executing.
    if execute_any and stage in {'run-preflight', 'capture-live-proof', 'ingest-downloaded-proof-json'}:
        preflight = maybe_run_preflight(execute=True, steps=steps)
        if preflight and not preflight.get('ok'):
            final_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
            report = _build_report(
                steps=steps,
                initial_status=initial_status,
                final_status=final_status,
                summary_out=summary_out,
                require_complete=require_complete,
                halted_reason='preflight failed; live capture must not proceed',
            )
            write_json(summary_out, report)
            return report
    else:
        maybe_run_preflight(execute=False, steps=steps)

    if execute_live and input_path is not None:
        transfer_audit = audit_transfer(
            input_path,
            summary_out=DEFAULT_TRANSFER_AUDIT_SUMMARY,
            require_proof_capture=True,
            require_ready_to_download=True,
            require_full_screenshot=True,
        )
        steps.append(compact_step('proof-transfer-audit', attempted=True, ok=bool(transfer_audit.get('ok')), verdict=transfer_audit.get('verdict'), report=transfer_audit))
        if not transfer_audit.get('ok'):
            final_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
            report = _build_report(
                steps=steps,
                initial_status=initial_status,
                final_status=final_status,
                summary_out=summary_out,
                require_complete=require_complete,
                halted_reason='proof-transfer-audit failed; use a complete downloaded proof JSON or recover a full vault document before ingest',
            )
            write_json(summary_out, report)
            return report
        attempt_audit = audit_file(
            input_path,
            summary_out=DEFAULT_ATTEMPT_AUDIT_SUMMARY,
            require_ready_to_download=True,
        )
        steps.append(compact_step('proof-attempt-audit', attempted=True, ok=bool(attempt_audit.get('ok')), verdict=attempt_audit.get('verdict'), report=attempt_audit))
        if not attempt_audit.get('ok'):
            final_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
            report = _build_report(
                steps=steps,
                initial_status=initial_status,
                final_status=final_status,
                summary_out=summary_out,
                require_complete=require_complete,
                halted_reason='proof-attempt-audit failed; use the side-panel Download proof JSON button after the attempt is ready-to-download',
            )
            write_json(summary_out, report)
            return report
        ingest = ingest_capture(
            input_path,
            out=DEFAULT_CAPTURE,
            redacted_out=DEFAULT_CAPTURE_REDACTED,
            summary_out=DEFAULT_INGEST_SUMMARY,
            require_live_candidate=True,
            finalize=False,
            pack_dir=LATEST / 'chatgpt-proof-ingest-evidence-pack',
            clean=False,
        )
        steps.append(compact_step('proof-ingest', attempted=True, ok=bool(ingest.get('ok')), verdict=ingest.get('verdict'), report=ingest))
        if not ingest.get('ok'):
            final_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
            report = _build_report(
                steps=steps,
                initial_status=initial_status,
                final_status=final_status,
                summary_out=summary_out,
                require_complete=require_complete,
                halted_reason='proof-ingest failed; fix or recapture downloaded proof JSON',
            )
            write_json(summary_out, report)
            return report
    elif execute_live:
        steps.append(compact_step('proof-transfer-audit', attempted=False, skipped_reason='no --input proof JSON supplied'))
        steps.append(compact_step('proof-attempt-audit', attempted=False, skipped_reason='no --input proof JSON supplied'))
        steps.append(compact_step('proof-ingest', attempted=False, skipped_reason='no --input proof JSON supplied'))
    else:
        steps.append(compact_step('proof-transfer-audit', attempted=False, skipped_reason='not in --execute-live mode'))
        steps.append(compact_step('proof-attempt-audit', attempted=False, skipped_reason='not in --execute-live mode'))
        steps.append(compact_step('proof-ingest', attempted=False, skipped_reason='not in --execute-live mode'))

    mid_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
    if execute_live and DEFAULT_CAPTURE.exists():
        finalize = finalize_pack(
            DEFAULT_CAPTURE,
            live_pack_dir,
            final_summary_path=DEFAULT_FINALIZE_SUMMARY,
            export_summary_path=DEFAULT_EXPORT_SUMMARY,
            check_summary_path=DEFAULT_CHECK_SUMMARY,
            clean=clean,
            require_live=True,
            allow_placeholder_screenshot=False,
            require_privacy_pass=False,
            privacy_decision='pending',
        )
        steps.append(compact_step('proof-finalize-pack', attempted=True, ok=bool(finalize.get('ok')), verdict=finalize.get('verdict'), report=finalize))
        if not finalize.get('ok'):
            final_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
            report = _build_report(
                steps=steps,
                initial_status=initial_status,
                final_status=final_status,
                summary_out=summary_out,
                require_complete=require_complete,
                halted_reason='proof-finalize-pack failed; inspect operator handoff and pack check blockers',
            )
            write_json(summary_out, report)
            return report
    else:
        reason = 'not in --execute-live mode'
        if execute_live and not DEFAULT_CAPTURE.exists():
            reason = 'no normalized capture exists yet'
        steps.append(compact_step('proof-finalize-pack', attempted=False, skipped_reason=reason))

    have_privacy_inputs = privacy_inputs_complete(
        reviewer=reviewer,
        decision=decision,
        attest_screenshot_reviewed=attest_screenshot_reviewed,
        attest_no_unrelated_content=attest_no_unrelated_content,
        attest_local_only=attest_local_only,
    )
    if execute_live and live_pack_dir.exists() and have_privacy_inputs:
        privacy = build_privacy_review(
            live_pack_dir,
            json_out=live_pack_dir / 'privacy-redaction-review.json',
            markdown_out=live_pack_dir / 'privacy-redaction-review.md',
            reviewer=reviewer,
            decision=decision,
            require_live=True,
            require_pass=True,
            attest_screenshot_reviewed=attest_screenshot_reviewed,
            attest_no_unrelated_content=attest_no_unrelated_content,
            attest_local_only=attest_local_only,
        )
        steps.append(compact_step('proof-privacy-review', attempted=True, ok=bool(privacy.get('ok')), verdict=privacy.get('verdict'), report=privacy))
        if not privacy.get('ok'):
            final_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
            report = _build_report(
                steps=steps,
                initial_status=initial_status,
                final_status=final_status,
                summary_out=summary_out,
                require_complete=require_complete,
                halted_reason='proof-privacy-review failed; human pass attestation is required before publishing',
            )
            write_json(summary_out, report)
            return report
    elif execute_live:
        steps.append(compact_step(
            'proof-privacy-review',
            attempted=False,
            skipped_reason='missing reviewer/pass attestations; publish bundle will remain blocked',
        ))
    else:
        steps.append(compact_step('proof-privacy-review', attempted=False, skipped_reason='not in --execute-live mode'))

    post_privacy_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
    can_attempt_publish = execute_live and post_privacy_status.get('current_stage') == 'publish-and-verify'
    if can_attempt_publish:
        pub_report = build_publish_bundle(
            live_pack_dir,
            publish_bundle,
            summary_path=DEFAULT_PUBLISH_SUMMARY,
            require_live=True,
            require_privacy_pass=True,
        )
        steps.append(compact_step('proof-publish-bundle', attempted=True, ok=bool(pub_report.get('ok')), verdict=pub_report.get('verdict'), report=pub_report))
        if pub_report.get('ok'):
            verify = verify_publish_bundle(
                publish_bundle,
                summary_path=DEFAULT_PUBLISH_VERIFY_SUMMARY,
                expected_sha256=None,
                require_live=True,
                require_privacy_pass=True,
            )
            steps.append(compact_step('proof-publish-verify', attempted=True, ok=bool(verify.get('ok')), verdict=verify.get('verdict'), report=verify))
        else:
            steps.append(compact_step('proof-publish-verify', attempted=False, skipped_reason='publish bundle did not pass'))
    else:
        reason = 'not in --execute-live mode'
        if execute_live:
            reason = f'pipeline stage is {post_privacy_status.get("current_stage")}; publish requires privacy-reviewed live pack'
        steps.append(compact_step('proof-publish-bundle', attempted=False, skipped_reason=reason))
        steps.append(compact_step('proof-publish-verify', attempted=False, skipped_reason=reason))

    final_status = _status(require_live=True, live_pack_dir=live_pack_dir, publish_bundle=publish_bundle)
    report = _build_report(
        steps=steps,
        initial_status=initial_status,
        final_status=final_status,
        summary_out=summary_out,
        require_complete=require_complete,
        halted_reason=None,
    )
    write_json(summary_out, report)
    return report


def _build_report(*, steps: list[JsonDict], initial_status: JsonDict, final_status: JsonDict,
                  summary_out: Path, require_complete: bool, halted_reason: str | None) -> JsonDict:
    complete = final_status.get('current_stage') == 'complete'
    attempted = [step for step in steps if step.get('attempted')]
    failed = [step for step in attempted if step.get('ok') is False]
    blockers: list[str] = []
    if halted_reason:
        blockers.append(halted_reason)
    if failed:
        blockers.extend(f'{step.get("name")}: {step.get("verdict")}' for step in failed)
    if require_complete and not complete:
        blockers.append(f'proof pipeline incomplete: current stage is {final_status.get("current_stage")}')
    return {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-autopilot',
        'generated_at': utcnow(),
        'ok': not blockers,
        'verdict': 'proof-autopilot-complete' if complete else ('proof-autopilot-halted' if blockers else 'proof-autopilot-awaiting-operator'),
        'require_complete': require_complete,
        'summary_path': display_path(summary_out),
        'initial_stage': initial_status.get('current_stage'),
        'final_stage': final_status.get('current_stage'),
        'next_action': final_status.get('next_action'),
        'steps': steps,
        'blockers': blockers,
        'warnings': [],
        'operator_state_path': display_path(DEFAULT_OPERATOR_STATE),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Run a guided, resumable ChatGPT proof pipeline autopilot without hiding live-proof blockers.')
    parser.add_argument('--input', type=Path, help='Downloaded side-panel proof JSON to ingest when using --execute-live')
    parser.add_argument('--summary-out', type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument('--live-pack-dir', type=Path, default=LIVE_PACK)
    parser.add_argument('--publish-bundle', type=Path, default=DEFAULT_PUBLISH_BUNDLE)
    parser.add_argument('--execute-safe', action='store_true', help='Run safe offline gates such as preflight, but do not ingest/finalize/publish live captures')
    parser.add_argument('--execute-live', action='store_true', help='Run live-candidate ingest/finalize/privacy/publish steps when the required inputs and gates are present')
    parser.add_argument('--clean', action='store_true', help='Clean the live pack directory when finalizing a live capture')
    parser.add_argument('--require-complete', action='store_true', help='Exit non-zero unless the full live publish/verify pipeline is complete')
    parser.add_argument('--reviewer')
    parser.add_argument('--decision', choices=['pending', 'pass', 'fail'], default='pending')
    parser.add_argument('--attest-screenshot-reviewed', action='store_true')
    parser.add_argument('--attest-no-unrelated-content', action='store_true')
    parser.add_argument('--attest-local-only', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_autopilot(
        summary_out=args.summary_out,
        execute_safe=args.execute_safe,
        execute_live=args.execute_live,
        input_path=args.input,
        live_pack_dir=args.live_pack_dir,
        publish_bundle=args.publish_bundle,
        require_complete=args.require_complete,
        clean=args.clean,
        reviewer=args.reviewer,
        decision=args.decision,
        attest_screenshot_reviewed=args.attest_screenshot_reviewed,
        attest_no_unrelated_content=args.attest_no_unrelated_content,
        attest_local_only=args.attest_local_only,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
