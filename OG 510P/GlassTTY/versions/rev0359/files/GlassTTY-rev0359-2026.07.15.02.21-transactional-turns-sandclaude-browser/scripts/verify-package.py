#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import base64
import hashlib
import json
import re
import stat
import sys

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = [
    'SANDCLAUDE-BROWSER.json',
    'glassttyd',
    'README.md',
    'STATUS.md',
    'TASKS.md',
    'CUBE_STATE.md',
    'extension/manifest.json',
    'extension/src/adapters/chatgpt.ts',
    'extension/src/adapters/index.ts',
    'scripts/chatgpt-first-proof-kit.py',
    'scripts/chatgpt-first-proof-artifact-ledger.py',
    'scripts/chatgpt-first-proof-schema-validation.py',
    'scripts/chatgpt-first-proof-bundle-audit.py',
    'scripts/chatgpt-first-proof-evaluator.py',
    'schemas/chatgpt-first-proof-bundle.schema.json',
    'validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/README.md',
    'tools/chatgpt-surface-megathing.js',
    'tools/chatgpt-surface-capsule.js',
    'tools/chatgpt-sendpath-probe.js',
    'tools/chatgpt-composer-send-drill.js',
    'tools/chatgpt-surface-oracle.user.js',
    'tools/chatgpt-pageworld-restprobe.js',
    'docs/chatgpt-surface-megathing.md',
    'docs/chatgpt-sendpath-probe.md',
    'docs/chatgpt-surface-oracle-userscript.md',
    'docs/chatgpt-pageworld-restprobe.md',
    'docs/chatgpt-surface-drift.md',
    'docs/chatgpt-proof-rehearsal.md',
    'docs/chatgpt-proof-preflight.md',
    'docs/chatgpt-sidepanel-live-gate.md',
    'docs/chatgpt-proof-pack-exporter.md',
    'docs/chatgpt-proof-pack-check.md',
    'docs/chatgpt-proof-pack-integrity.md',
    'docs/chatgpt-proof-finalize-pack.md',
    'docs/chatgpt-proof-ingest.md',
    'docs/chatgpt-proof-attempt-audit.md',
    'docs/chatgpt-proof-transfer-audit.md',
    'docs/chatgpt-proof-privacy-review.md',
    'docs/chatgpt-proof-publish-bundle.md',
    'docs/chatgpt-proof-publish-verify.md',
    'docs/chatgpt-proof-status.md',
    'docs/chatgpt-proof-autopilot.md',
    'docs/chatgpt-sidepanel-recovery-vault.md',
    'docs/chatgpt-proof-recovery-vault.md',
    'docs/chatgpt-extension-readiness.md',
    'docs/chatgpt-sidepanel-attempt-readiness.md',
    'docs/chatgpt-visible-screenshot-capture.md',
    'scripts/chatgpt-proof-preflight.py',
    'scripts/chatgpt_proof_preflight.py',
    'scripts/chatgpt-proof-pack-exporter.py',
    'scripts/chatgpt_proof_pack_exporter.py',
    'scripts/chatgpt-proof-pack-check.py',
    'scripts/chatgpt_proof_pack_check.py',
    'scripts/chatgpt-proof-pack-integrity.py',
    'scripts/chatgpt_proof_pack_integrity.py',
    'scripts/chatgpt-proof-finalize-pack.py',
    'scripts/chatgpt_proof_finalize_pack.py',
    'scripts/chatgpt-proof-ingest.py',
    'scripts/chatgpt_proof_ingest.py',
    'scripts/chatgpt-proof-attempt-audit.py',
    'scripts/chatgpt_proof_attempt_audit.py',
    'scripts/chatgpt-proof-transfer-audit.py',
    'scripts/chatgpt_proof_transfer_audit.py',
    'scripts/chatgpt-proof-recovery-vault.py',
    'scripts/chatgpt_proof_recovery_vault.py',
    'scripts/chatgpt-proof-privacy-review.py',
    'scripts/chatgpt_proof_privacy_review.py',
    'scripts/chatgpt-proof-publish-bundle.py',
    'scripts/chatgpt_proof_publish_bundle.py',
    'scripts/chatgpt-proof-publish-verify.py',
    'scripts/chatgpt_proof_publish_verify.py',
    'scripts/chatgpt-proof-status.py',
    'scripts/chatgpt_proof_status.py',
    'scripts/chatgpt-proof-autopilot.py',
    'scripts/chatgpt_proof_autopilot.py',
    'scripts/chatgpt-extension-readiness.py',
    'scripts/chatgpt_extension_readiness.py',
    'scripts/chatgpt_contract_paths.py',
    'scripts/install-sandclaude.sh',
    'scripts/package-release.py',
    'scripts/sandclaude-browser-probe.sh',
    'validation/latest/chatgpt-proof-preflight.json',
    'validation/latest/chatgpt-proof-pack-export-summary.json',
    'validation/latest/chatgpt-proof-pack-check-summary.json',
    'validation/latest/chatgpt-proof-pack-integrity-summary.json',
    'validation/latest/chatgpt-proof-finalize-summary.json',
    'validation/latest/chatgpt-proof-ingest-summary.json',
    'validation/latest/chatgpt-proof-attempt-audit.json',
    'validation/latest/chatgpt-proof-transfer-audit.json',
    'validation/latest/chatgpt-proof-recovery-vault-summary.json',
    'validation/latest/chatgpt-proof-privacy-review.json',
    'validation/latest/chatgpt-proof-publish-summary.json',
    'validation/latest/chatgpt-proof-publish-verify-summary.json',
    'validation/latest/chatgpt-proof-operator-state.json',
    'validation/latest/chatgpt-proof-autopilot-summary.json',
    'validation/latest/chatgpt-proof-extension-readiness.json',
    'scripts/chatgpt-surface-report-audit.py',
    'scripts/chatgpt-surface-contract.py',
    'scripts/chatgpt-proof-rehearsal.py',
    'scripts/chatgpt_proof_rehearsal.py',
    'validation/latest/chatgpt-live-surface-contract-rev0352-2026.06.13.json',
    'validation/latest/chatgpt-live-surface-contract-fixture-rev0352.json',
]


SCRIPT_REF_IGNORE = {
    'test_chatgpt_executable_adapter_policy.py',
    'test_chatgpt_first_proof_artifact_ledger.py',
    'test_chatgpt_first_proof_bundle_audit.py',
    'test_chatgpt_first_proof_evaluator.py',
    'test_chatgpt_first_proof_kit.py',
    'test_chatgpt_first_proof_schema_validation.py',
    'cli.py',
}


def stale_script_references() -> list[str]:
    scripts_dir = ROOT / 'scripts'
    tests_dir = ROOT / 'tests'
    existing = {path.name for path in scripts_dir.iterdir() if path.is_file()}
    existing_tests = {path.name for path in tests_dir.glob('*.py')} if tests_dir.exists() else set()
    failures: list[str] = []
    scan_paths = [p for p in scripts_dir.iterdir() if p.is_file()]
    daemon_cli = ROOT / 'daemon' / 'src' / 'glassttyd' / 'cli.py'
    if daemon_cli.exists():
        scan_paths.append(daemon_cli)
    for path in scan_paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        refs = sorted(set(re.findall(r'([A-Za-z0-9_-]+\.py)', text)))
        missing = [
            ref for ref in refs
            if ref not in existing
            and ref not in existing_tests
            and ref not in SCRIPT_REF_IGNORE
            and ref != path.name
        ]
        if missing:
            failures.append(f'{path.relative_to(ROOT)} references missing script(s): {", ".join(missing)}')
    return failures


CONSOLE_TOOL_LIMITS = {
    'tools/chatgpt-surface-megathing.js': 88,
    'tools/chatgpt-surface-capsule.js': 88,
    'tools/chatgpt-composer-send-drill.js': 88,
    'tools/chatgpt-sendpath-probe.js': 88,
    'tools/chatgpt-pageworld-restprobe.js': 100,
    'tools/chatgpt-surface-oracle.user.js': 100,
}


def sandclaude_handoff_failures() -> list[str]:
    failures: list[str] = []
    marker_path = ROOT / 'SANDCLAUDE-BROWSER.json'
    try:
        marker = json.loads(marker_path.read_text(encoding='utf-8'))
    except Exception as exc:
        return [f'SANDCLAUDE-BROWSER.json is invalid: {exc}']
    if marker.get('schema') != 'sandclaude.browser-bundle.v1':
        failures.append('Sandclaude browser marker has the wrong schema')
    if marker.get('name') != 'GlassTTY':
        failures.append('Sandclaude browser marker has the wrong product name')
    if marker.get('extension') != 'extension':
        failures.append('Sandclaude browser marker must load extension/')
    native = marker.get('native_host')
    if not isinstance(native, dict):
        failures.append('Sandclaude browser marker is missing native_host')
        native = {}
    expected_entrypoint = 'scripts/native-host-entrypoint.sh'
    if native.get('name') != 'com.glasstty.bridge' or native.get('entrypoint') != expected_entrypoint:
        failures.append('Sandclaude browser marker has the wrong native-host contract')
    if marker.get('probe') != 'scripts/sandclaude-browser-probe.sh':
        failures.append('Sandclaude browser marker has the wrong probe entrypoint')

    executable_paths = [ROOT / 'glassttyd', ROOT / expected_entrypoint,
                        ROOT / 'scripts/install-sandclaude.sh',
                        ROOT / 'scripts/sandclaude-browser-probe.sh']
    for path in executable_paths:
        if not path.is_file() or not (path.stat().st_mode & stat.S_IXUSR):
            failures.append(f'Sandclaude handoff executable is missing or not executable: {path.relative_to(ROOT)}')

    try:
        manifest = json.loads((ROOT / 'extension/manifest.json').read_text(encoding='utf-8'))
        package = json.loads((ROOT / 'extension/package.json').read_text(encoding='utf-8'))
        lock = json.loads((ROOT / 'extension/package-lock.json').read_text(encoding='utf-8'))
        versions = {manifest.get('version'), package.get('version'), lock.get('version'),
                    lock.get('packages', {}).get('', {}).get('version')}
        if len(versions) != 1 or None in versions:
            failures.append('extension manifest, package, and lockfile versions disagree')
        key = manifest.get('key')
        if not isinstance(key, str) or not key:
            failures.append('extension manifest has no stable key for native messaging')
        else:
            digest = hashlib.sha256(base64.b64decode(key, validate=True)).hexdigest()[:32]
            extension_id = ''.join('abcdefghijklmnop'[int(char, 16)] for char in digest)
            if not re.fullmatch(r'[a-p]{32}', extension_id):
                failures.append('extension manifest key did not produce a valid Chromium extension id')
    except Exception as exc:
        failures.append(f'Sandclaude extension identity validation failed: {exc}')
    return failures


def console_tool_failures() -> list[str]:
    failures: list[str] = []
    for rel, limit in CONSOLE_TOOL_LIMITS.items():
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        if '\u2028' in text or '\u2029' in text:
            failures.append(f'{rel} contains U+2028/U+2029 line separator characters')
        for index, line in enumerate(text.splitlines(), 1):
            if len(line) > limit:
                failures.append(f'{rel}:{index} exceeds paste-safe line limit {limit}')
                break
        if 'eval(' in text or 'new Function' in text:
            failures.append(f'{rel} uses eval/new Function, which is CSP-hostile')
        if "createElement('script'" in text or 'createElement("script"' in text:
            failures.append(f'{rel} injects script tags, which is CSP-hostile')
    return failures



def runtime_artifact_failures() -> list[str]:
    failures: list[str] = []
    for path in ROOT.rglob('*'):
        rel = path.relative_to(ROOT).as_posix()
        parts = set(path.parts)
        if path.is_dir() and path.name in {'__pycache__', '.pytest_cache'}:
            failures.append(f'runtime cache directory must be cleaned before packaging: {rel}')
        elif path.is_file() and path.suffix in {'.pyc', '.pyo'}:
            failures.append(f'compiled Python cache must be cleaned before packaging: {rel}')
    return failures


def pack_integrity_failures() -> list[str]:
    failures: list[str] = []
    summary_path = ROOT / 'validation' / 'latest' / 'chatgpt-proof-pack-integrity-summary.json'
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding='utf-8'))
        except Exception as exc:
            failures.append(f'chatgpt-proof-pack-integrity-summary.json is not valid JSON: {exc}')
        else:
            if summary.get('verdict') != 'proof-pack-integrity-ok' or summary.get('ok') is not True:
                failures.append('latest proof-pack-integrity summary must be ok after rehearsal finalization')
    pack_integrity = ROOT / 'validation' / 'latest' / 'chatgpt-proof-rehearsal-evidence-pack' / 'evidence-pack-integrity.json'
    if not pack_integrity.exists():
        failures.append('rehearsal evidence pack must include evidence-pack-integrity.json after finalization')
    return failures


def publish_gate_failures() -> list[str]:
    failures: list[str] = []
    rehearsal_publish_zip = ROOT / 'validation' / 'latest' / 'chatgpt-proof-publish-bundle.zip'
    if rehearsal_publish_zip.exists():
        failures.append('publish bundle zip must not be present for rehearsal/latest packaging; proof-publish-bundle should block until live+privacy-pass evidence exists')
    summary_path = ROOT / 'validation' / 'latest' / 'chatgpt-proof-publish-summary.json'
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding='utf-8'))
        except Exception as exc:
            failures.append(f'chatgpt-proof-publish-summary.json is not valid JSON: {exc}')
        else:
            if summary.get('verdict') != 'proof-publish-bundle-blocked' or summary.get('zip_created') is not False:
                failures.append('latest proof-publish summary must record a blocked rehearsal publish gate with zip_created=false')
    verify_summary_path = ROOT / 'validation' / 'latest' / 'chatgpt-proof-publish-verify-summary.json'
    if verify_summary_path.exists():
        try:
            verify_summary = json.loads(verify_summary_path.read_text(encoding='utf-8'))
        except Exception as exc:
            failures.append(f'chatgpt-proof-publish-verify-summary.json is not valid JSON: {exc}')
        else:
            if verify_summary.get('verdict') != 'proof-publish-verify-blocked' or verify_summary.get('bundle_exists') is not False:
                failures.append('latest proof-publish-verify summary must record a blocked missing publish zip with bundle_exists=false')
    return failures

def main() -> int:
    missing = [rel for rel in REQUIRED if not (ROOT / rel).exists()]
    stale = stale_script_references()
    console = console_tool_failures()
    runtime = runtime_artifact_failures()
    publish = publish_gate_failures()
    integrity = pack_integrity_failures()
    handoff = sandclaude_handoff_failures()
    if missing or stale or console or runtime or publish or integrity or handoff:
        for rel in missing:
            print(f'missing: {rel}', file=sys.stderr)
        for item in stale:
            print(f'stale-reference: {item}', file=sys.stderr)
        for item in console:
            print(f'console-tool: {item}', file=sys.stderr)
        for item in runtime:
            print(f'runtime-artifact: {item}', file=sys.stderr)
        for item in publish:
            print(f'publish-gate: {item}', file=sys.stderr)
        for item in integrity:
            print(f'pack-integrity: {item}', file=sys.stderr)
        for item in handoff:
            print(f'sandclaude-handoff: {item}', file=sys.stderr)
        return 1
    print('package verification passed: ChatGPT-only files, scripts, drift contracts, rehearsal tools, publish gates, and paste-safe console tools are coherent')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
