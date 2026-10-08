#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatgpt_first_proof_artifact_ledger import sha256_file
from chatgpt_first_proof_evaluator import REVIEWABLE_VERDICT, REHEARSAL_VERDICT
from chatgpt_first_proof_kit import EXPECTED_REPLY, PROBE_TEXT
from chatgpt_proof_pack_check import png_dimensions

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACK_DIR = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack'
DEFAULT_JSON = ROOT / 'validation' / 'latest' / 'chatgpt-proof-privacy-review.json'
DEFAULT_MD = DEFAULT_PACK_DIR / 'privacy-redaction-review.md'
SCHEMA_VERSION = 1
EMAIL_RE = re.compile(r'(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b')
SECRET_RE = re.compile(r'(?i)\b(api[_-]?key|authorization|bearer|cookie|set-cookie|password|session[_-]?id|localstorage|sessionstorage|jwt|token)\b')
DATA_URL_RE = re.compile(r'data:image/(png|jpeg|webp);base64,', re.I)
ABS_PATH_RE = re.compile(r'/(mnt/data|home/oai|Users|private/var|tmp)/')

JsonDict = dict[str, Any]


def utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


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


def read_json_or_empty(path: Path) -> JsonDict:
    try:
        payload = read_json(path)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def scan_text(label: str, text: str, *, allow_data_url: bool = False) -> list[JsonDict]:
    findings: list[JsonDict] = []
    if not isinstance(text, str) or not text:
        return findings
    for match in EMAIL_RE.finditer(text):
        findings.append({'kind': 'possible_email', 'label': label, 'sample': match.group(0)[:96]})
    for match in SECRET_RE.finditer(text):
        findings.append({'kind': 'secret_keyword', 'label': label, 'sample': match.group(0)[:64]})
    if DATA_URL_RE.search(text) and not allow_data_url:
        findings.append({'kind': 'embedded_image_data_url', 'label': label, 'sample': 'data:image/...;base64,'})
    if ABS_PATH_RE.search(text):
        findings.append({'kind': 'absolute_local_path', 'label': label, 'sample': 'local path marker'})
    return findings


def scan_json(value: Any, *, label: str = 'json', findings: list[JsonDict] | None = None, path: str = '$') -> list[JsonDict]:
    findings = [] if findings is None else findings
    if isinstance(value, dict):
        for key, child in value.items():
            scan_json(child, label=label, findings=findings, path=f'{path}.{key}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_json(child, label=label, findings=findings, path=f'{path}[{index}]')
    elif isinstance(value, str):
        allow_data_url = path.endswith('visible_tab_screenshot_data_url') or path.endswith('screenshot_data_url') or path.endswith('surface_screenshot_data_url')
        for finding in scan_text(f'{label}:{path}', value, allow_data_url=allow_data_url):
            findings.append(finding)
    return findings


def file_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception:
        return ''


def _expected_only_text(path: Path, expected: str) -> bool:
    return ' '.join(file_text(path).split()).strip() == expected


def build_privacy_review(
    pack_dir: Path = DEFAULT_PACK_DIR,
    *,
    json_out: Path | None = DEFAULT_JSON,
    markdown_out: Path | None = None,
    reviewer: str | None = None,
    reviewer_contact: str | None = None,
    decision: str | None = None,
    require_live: bool = False,
    require_pass: bool = False,
    attest_screenshot_reviewed: bool = False,
    attest_no_unrelated_content: bool = False,
    attest_local_only: bool = False,
) -> JsonDict:
    pack_dir = pack_dir.resolve()
    markdown_out = markdown_out or (pack_dir / 'privacy-redaction-review.md')
    manifest = read_json_or_empty(pack_dir / 'bundle-manifest.json')
    evaluation = read_json_or_empty(pack_dir / 'chatgpt-first-proof-evaluation.json')
    screenshot_meta = read_json_or_empty(pack_dir / 'surface-screenshot.metadata.json')
    transcript = read_json_or_empty(pack_dir / 'transcript-latest-action.json')
    submit_readback = read_json_or_empty(pack_dir / 'submit-prompt-readback.json')
    assistant_witness = read_json_or_empty(pack_dir / 'assistant-output-witness.json')
    user_witness = read_json_or_empty(pack_dir / 'user-turn-witness.json')

    blockers: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    rehearsal_only = bool(manifest.get('rehearsal_only'))
    evaluator_verdict = evaluation.get('verdict') if isinstance(evaluation.get('verdict'), str) else None
    screenshot_path = pack_dir / 'surface-screenshot.png'
    screenshot_exists = screenshot_path.exists()
    screenshot_dims = png_dimensions(screenshot_path)
    screenshot_placeholder = bool(screenshot_meta.get('placeholder_not_live'))

    if not (pack_dir / 'bundle-manifest.json').exists():
        blockers.append('bundle-manifest.json is missing; run proof-finalize-pack before privacy review')
    if not screenshot_exists:
        blockers.append('surface-screenshot.png is missing')
    elif not screenshot_dims.get('ok'):
        blockers.append(f'surface-screenshot.png is not a readable PNG: {screenshot_dims.get("error")}')
    elif screenshot_dims.get('width') == 1 and screenshot_dims.get('height') == 1:
        warnings.append('surface-screenshot.png is placeholder-sized 1x1')

    prompt_ok = _expected_only_text(pack_dir / 'probe-prompt.txt', PROBE_TEXT)
    composer_after_ok = _expected_only_text(pack_dir / 'composer-after.txt', PROBE_TEXT)
    assistant_text = transcript.get('text') or transcript.get('latest_text') or transcript.get('normalized_text')
    assistant_ok = isinstance(assistant_text, str) and ' '.join(assistant_text.split()).strip() == EXPECTED_REPLY
    readback_text = submit_readback.get('readback') or submit_readback.get('text') or submit_readback.get('composer_text')
    submit_readback_ok = isinstance(readback_text, str) and ' '.join(readback_text.split()).strip() == PROBE_TEXT
    if not prompt_ok:
        blockers.append('probe-prompt.txt is missing or does not exactly equal the checkpoint prompt')
    if not composer_after_ok:
        blockers.append('composer-after.txt is missing or does not exactly equal the checkpoint prompt')
    if not submit_readback_ok:
        warnings.append('submit-prompt-readback.json does not expose an exact checkpoint readback field recognized by privacy review')
    if not assistant_ok:
        warnings.append('transcript-latest-action.json does not expose the exact checkpoint reply field recognized by privacy review')

    scan_findings: list[JsonDict] = []
    for name, payload in [
        ('bundle-manifest.json', manifest),
        ('chatgpt-first-proof-evaluation.json', evaluation),
        ('surface-screenshot.metadata.json', screenshot_meta),
        ('transcript-latest-action.json', transcript),
        ('submit-prompt-readback.json', submit_readback),
        ('assistant-output-witness.json', assistant_witness),
        ('user-turn-witness.json', user_witness),
    ]:
        scan_findings.extend(scan_json(payload, label=name))
    for name in ('receiver-posture.md', 'composer-before.txt', 'composer-after.txt', 'probe-prompt.txt'):
        path = pack_dir / name
        if path.exists():
            scan_findings.extend(scan_text(name, file_text(path)))

    high_risk_findings = [f for f in scan_findings if f.get('kind') in {'possible_email', 'secret_keyword', 'embedded_image_data_url'}]
    if high_risk_findings:
        warnings.append(f'{len(high_risk_findings)} possible sensitive marker(s) found in reviewable text/json artifacts')

    normalized_decision = (decision or '').strip().lower() or 'pending'
    if normalized_decision not in {'pending', 'pass', 'fail'}:
        blockers.append(f'unknown privacy review decision: {decision!r}')
        normalized_decision = 'fail'

    human_attestation = {
        'reviewer': reviewer or None,
        'reviewer_contact': reviewer_contact or None,
        'decision': normalized_decision,
        'attest_screenshot_reviewed': bool(attest_screenshot_reviewed),
        'attest_no_unrelated_content': bool(attest_no_unrelated_content),
        'attest_local_only': bool(attest_local_only),
    }
    attestation_complete = bool(
        reviewer
        and normalized_decision == 'pass'
        and attest_screenshot_reviewed
        and attest_no_unrelated_content
        and attest_local_only
    )

    if require_live and rehearsal_only:
        blockers.append('require-live was set, but bundle-manifest.json declares rehearsal_only=true')
    if require_live and evaluator_verdict != REVIEWABLE_VERDICT:
        blockers.append(f'require-live was set, but evaluator verdict is {evaluator_verdict!r}')
    if require_live and screenshot_placeholder:
        blockers.append('require-live was set, but screenshot metadata marks placeholder_not_live')
    if require_pass and not attestation_complete:
        blockers.append('require-pass was set, but human privacy attestation is incomplete or not pass')

    if rehearsal_only:
        recommendations.append('This is a rehearsal pack. Keep privacy status not-live and do not publish it.')
    if screenshot_placeholder:
        recommendations.append('For live proof, capture a real visible ChatGPT screenshot and rerun finalization.')
    if not attestation_complete and not rehearsal_only:
        recommendations.append('Before publication/support use, rerun proof-privacy-review with reviewer and explicit attestations.')
    if high_risk_findings:
        recommendations.append('Inspect possible sensitive markers and redact or justify them before any external use.')

    if blockers:
        verdict = 'privacy-review-blocked'
        ok = False
    elif rehearsal_only:
        verdict = 'privacy-review-rehearsal-not-live'
        ok = True
    elif attestation_complete:
        verdict = 'privacy-review-pass'
        ok = True
    else:
        verdict = 'privacy-review-pending-human-attestation'
        ok = not require_pass

    report: JsonDict = {
        'schema_version': SCHEMA_VERSION,
        'tool': 'glasstty-chatgpt-proof-privacy-review',
        'generated_at': utcnow(),
        'ok': ok,
        'verdict': verdict,
        'pack_dir': display_path(pack_dir),
        'require_live': require_live,
        'require_pass': require_pass,
        'manifest': {
            'attempt_id': manifest.get('attempt_id'),
            'proof_mode': manifest.get('proof_mode'),
            'rehearsal_only': rehearsal_only,
        },
        'evaluation': {
            'verdict': evaluator_verdict,
            'harness_ok': evaluation.get('harness_ok'),
        },
        'screenshot': {
            'exists': screenshot_exists,
            'sha256': sha256_file(screenshot_path) if screenshot_exists else None,
            'dimensions': screenshot_dims,
            'placeholder_not_live': screenshot_placeholder,
            'metadata_source': screenshot_meta.get('source'),
        },
        'content_checks': {
            'probe_prompt_exact': prompt_ok,
            'composer_after_exact': composer_after_ok,
            'submit_readback_exact': submit_readback_ok,
            'assistant_latest_exact': assistant_ok,
            'possible_sensitive_marker_count': len(high_risk_findings),
            'possible_sensitive_markers': high_risk_findings[:20],
        },
        'human_attestation': human_attestation,
        'human_attestation_complete': attestation_complete,
        'publishable_without_additional_redaction': bool(attestation_complete and not high_risk_findings),
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations,
    }
    if json_out:
        write_json(json_out, report)
    write_text(markdown_out, privacy_markdown(report))
    return report


def privacy_markdown(report: JsonDict) -> str:
    att = report.get('human_attestation') if isinstance(report.get('human_attestation'), dict) else {}
    screenshot = report.get('screenshot') if isinstance(report.get('screenshot'), dict) else {}
    content = report.get('content_checks') if isinstance(report.get('content_checks'), dict) else {}
    lines = [
        '# Privacy/redaction review',
        '',
        f"- verdict: `{report.get('verdict')}`",
        f"- ok: `{report.get('ok')}`",
        f"- generated_at: `{report.get('generated_at')}`",
        f"- pack_dir: `{report.get('pack_dir')}`",
        f"- publishable_without_additional_redaction: `{report.get('publishable_without_additional_redaction')}`",
        '',
        '## Human attestation',
        '',
        f"- reviewer: `{att.get('reviewer')}`",
        f"- decision: `{att.get('decision')}`",
        f"- attest_screenshot_reviewed: `{att.get('attest_screenshot_reviewed')}`",
        f"- attest_no_unrelated_content: `{att.get('attest_no_unrelated_content')}`",
        f"- attest_local_only: `{att.get('attest_local_only')}`",
        f"- complete: `{report.get('human_attestation_complete')}`",
        '',
        '## Screenshot',
        '',
        f"- exists: `{screenshot.get('exists')}`",
        f"- sha256: `{screenshot.get('sha256')}`",
        f"- dimensions: `{screenshot.get('dimensions')}`",
        f"- placeholder_not_live: `{screenshot.get('placeholder_not_live')}`",
        '',
        '## Content checks',
        '',
        f"- probe_prompt_exact: `{content.get('probe_prompt_exact')}`",
        f"- composer_after_exact: `{content.get('composer_after_exact')}`",
        f"- submit_readback_exact: `{content.get('submit_readback_exact')}`",
        f"- assistant_latest_exact: `{content.get('assistant_latest_exact')}`",
        f"- possible_sensitive_marker_count: `{content.get('possible_sensitive_marker_count')}`",
        '',
    ]
    blockers = report.get('blockers') if isinstance(report.get('blockers'), list) else []
    warnings = report.get('warnings') if isinstance(report.get('warnings'), list) else []
    recommendations = report.get('recommendations') if isinstance(report.get('recommendations'), list) else []
    lines.extend(['## Blockers', ''])
    lines.extend([f'- {item}' for item in blockers] or ['- none'])
    lines.extend(['', '## Warnings', ''])
    lines.extend([f'- {item}' for item in warnings] or ['- none'])
    lines.extend(['', '## Recommendations', ''])
    lines.extend([f'- {item}' for item in recommendations] or ['- none'])
    lines.extend(['', '## Machine-readable summary', '', '```json', json.dumps({
        'schema_version': report.get('schema_version'),
        'tool': report.get('tool'),
        'verdict': report.get('verdict'),
        'ok': report.get('ok'),
        'human_attestation_complete': report.get('human_attestation_complete'),
        'publishable_without_additional_redaction': report.get('publishable_without_additional_redaction'),
    }, indent=2, sort_keys=True), '```', ''])
    return '\n'.join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Build or check structured privacy/redaction review for a ChatGPT proof evidence pack.')
    parser.add_argument('--pack-dir', type=Path, default=DEFAULT_PACK_DIR)
    parser.add_argument('--json-out', type=Path, default=DEFAULT_JSON)
    parser.add_argument('--markdown-out', type=Path)
    parser.add_argument('--reviewer')
    parser.add_argument('--reviewer-contact')
    parser.add_argument('--decision', choices=['pending', 'pass', 'fail'], default='pending')
    parser.add_argument('--require-live', action='store_true')
    parser.add_argument('--require-pass', action='store_true')
    parser.add_argument('--attest-screenshot-reviewed', action='store_true')
    parser.add_argument('--attest-no-unrelated-content', action='store_true')
    parser.add_argument('--attest-local-only', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    parser.add_argument('--require-ok', action='store_true')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_privacy_review(
        args.pack_dir,
        json_out=args.json_out,
        markdown_out=args.markdown_out,
        reviewer=args.reviewer,
        reviewer_contact=args.reviewer_contact,
        decision=args.decision,
        require_live=args.require_live,
        require_pass=args.require_pass,
        attest_screenshot_reviewed=args.attest_screenshot_reviewed,
        attest_no_unrelated_content=args.attest_no_unrelated_content,
        attest_local_only=args.attest_local_only,
    )
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    if args.require_ok and not report.get('ok'):
        return 1
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
