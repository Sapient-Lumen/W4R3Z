from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]

REQUIRED_SIDE_PANEL_BUTTONS = [
    'proof-attempt-readiness',
    'proof-write-capture',
    'proof-live-gate-check',
    'proof-capture-screenshot',
    'proof-submit',
    'proof-read-latest',
    'proof-download-json',
    'proof-save-vault',
    'proof-restore-vault',
    'proof-download-vault',
]

REQUIRED_MANIFEST_PERMISSIONS = {
    'storage',
    'tabs',
    'sidePanel',
    'scripting',
    'webNavigation',
}

REQUIRED_DIST_FILES = [
    'extension/dist/background/main.js',
    'extension/dist/content/main.js',
    'extension/dist/sidepanel/main.js',
]

ALLOWED_HOST_PERMISSIONS = ['https://chatgpt.com/*']
EXPECTED_CONTENT_MATCHES = ['https://chatgpt.com/*']


def project_root_from_here() -> Path:
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> JsonDict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def _contains_all(text: str, needles: list[str]) -> dict[str, bool]:
    return {needle: needle in text for needle in needles}


def check_extension_readiness(root: Path | None = None, *, require_build: bool = False, summary_path: Path | None = None) -> JsonDict:
    root = (root or project_root_from_here()).resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    manifest_path = root / 'extension' / 'manifest.json'
    package_path = root / 'extension' / 'package.json'
    sidepanel_html_path = root / 'extension' / 'sidepanel' / 'index.html'
    sidepanel_ts_path = root / 'extension' / 'src' / 'sidepanel' / 'main.ts'
    protocol_ts_path = root / 'extension' / 'src' / 'shared' / 'protocol.ts'

    manifest = read_json(manifest_path)
    package_json = read_json(package_path)
    sidepanel_html = sidepanel_html_path.read_text(encoding='utf-8') if sidepanel_html_path.exists() else ''
    sidepanel_ts = sidepanel_ts_path.read_text(encoding='utf-8') if sidepanel_ts_path.exists() else ''
    protocol_ts = protocol_ts_path.read_text(encoding='utf-8') if protocol_ts_path.exists() else ''

    if manifest is None:
        blockers.append('extension/manifest.json is missing or unreadable')
        manifest = {}
    if package_json is None:
        blockers.append('extension/package.json is missing or unreadable')
        package_json = {}
    if not sidepanel_html:
        blockers.append('extension/sidepanel/index.html is missing or empty')
    if not sidepanel_ts:
        blockers.append('extension/src/sidepanel/main.ts is missing or empty')

    host_permissions = manifest.get('host_permissions') if isinstance(manifest.get('host_permissions'), list) else []
    permissions = manifest.get('permissions') if isinstance(manifest.get('permissions'), list) else []
    content_scripts = manifest.get('content_scripts') if isinstance(manifest.get('content_scripts'), list) else []
    content_matches: list[str] = []
    for script in content_scripts:
        if isinstance(script, dict) and isinstance(script.get('matches'), list):
            content_matches.extend(value for value in script['matches'] if isinstance(value, str))

    if manifest.get('manifest_version') != 3:
        blockers.append('extension manifest is not Manifest V3')
    if host_permissions != ALLOWED_HOST_PERMISSIONS:
        blockers.append('host_permissions must be exactly https://chatgpt.com/* for the ChatGPT-only cube')
    if sorted(content_matches) != sorted(EXPECTED_CONTENT_MATCHES):
        blockers.append('content script matches must be exactly https://chatgpt.com/*')
    missing_permissions = sorted(REQUIRED_MANIFEST_PERMISSIONS.difference(value for value in permissions if isinstance(value, str)))
    if missing_permissions:
        blockers.append(f'missing extension permissions: {", ".join(missing_permissions)}')
    if manifest.get('side_panel', {}).get('default_path') != 'sidepanel/index.html':
        blockers.append('side panel default path is not sidepanel/index.html')

    package_version = package_json.get('version')
    manifest_version = manifest.get('version')
    if package_version != manifest_version:
        blockers.append('extension/package.json version and manifest version differ')

    html_buttons = _contains_all(sidepanel_html, REQUIRED_SIDE_PANEL_BUTTONS)
    missing_buttons = [button for button, present in html_buttons.items() if not present]
    if missing_buttons:
        blockers.append(f'side panel is missing proof controls: {", ".join(missing_buttons)}')

    required_source_markers = {
        'live_gate_constant': 'PROOF_LIVE_GATE_EXPECTED' in sidepanel_ts,
        'attempt_readiness_function': 'runProofAttemptReadiness' in sidepanel_ts,
        'recovery_vault_key': 'glasstty.chatgpt.firstProof.recoveryVault.v1' in sidepanel_ts,
        'download_proof_json': 'downloadProofCaptureJson' in sidepanel_ts,
        'download_proof_json_readiness_gate': 'Proof capture JSON download blocked by attempt readiness.' in sidepanel_ts,
        'download_proof_json_attempt_audit_handoff': 'proof-attempt-audit --input' in sidepanel_ts,
        'visible_screenshot_capture': 'captureVisibleProofScreenshot' in sidepanel_ts,
        'proof_operator_readiness_message_type': "'proof.operator_readiness'" in protocol_ts,
    }
    for marker, present in required_source_markers.items():
        if not present:
            blockers.append(f'missing side-panel source marker: {marker}')

    dist_files = {path: (root / path).exists() for path in REQUIRED_DIST_FILES}
    missing_dist = [path for path, present in dist_files.items() if not present]
    if missing_dist and require_build:
        blockers.append(f'extension build outputs are missing: {", ".join(missing_dist)}')
    elif missing_dist:
        warnings.append(f'extension build outputs are missing until npm --prefix extension run build is run: {", ".join(missing_dist)}')

    if manifest.get('minimum_chrome_version'):
        min_chrome = manifest.get('minimum_chrome_version')
    else:
        min_chrome = None
        warnings.append('minimum_chrome_version is not set')

    if not blockers:
        recommendations.append('Load extension/ as an unpacked extension, open https://chatgpt.com/, open the GlassTTY side panel, and press Run attempt readiness before starting the live proof.')
    else:
        recommendations.append('Fix blockers before attempting live proof; the side panel may be unable to capture gated evidence safely.')
    if missing_dist:
        recommendations.append('Run npm --prefix extension run build before loading or reloading the unpacked extension.')

    report: JsonDict = {
        'schema_version': 1,
        'tool': 'glasstty-chatgpt-extension-readiness',
        'project_root': os.fspath(root),
        'ok': not blockers,
        'verdict': 'extension-readiness-ok' if not blockers else 'extension-readiness-blocked',
        'blockers': blockers,
        'warnings': warnings,
        'recommendations': recommendations,
        'manifest': {
            'path': os.fspath(manifest_path.relative_to(root)) if manifest_path.exists() else os.fspath(manifest_path),
            'manifest_version': manifest.get('manifest_version'),
            'name': manifest.get('name'),
            'version': manifest_version,
            'package_version': package_version,
            'minimum_chrome_version': min_chrome,
            'permissions': permissions,
            'host_permissions': host_permissions,
            'content_matches': sorted(content_matches),
            'side_panel_default_path': manifest.get('side_panel', {}).get('default_path') if isinstance(manifest.get('side_panel'), dict) else None,
        },
        'sidepanel': {
            'html_path': os.fspath(sidepanel_html_path.relative_to(root)) if sidepanel_html_path.exists() else os.fspath(sidepanel_html_path),
            'source_path': os.fspath(sidepanel_ts_path.relative_to(root)) if sidepanel_ts_path.exists() else os.fspath(sidepanel_ts_path),
            'required_buttons': html_buttons,
            'source_markers': required_source_markers,
        },
        'build_outputs': dist_files,
        'operator_next_action': 'Run npm --prefix extension run build, load extension/, open ChatGPT, then press Run attempt readiness.' if missing_dist else 'Load extension/, open ChatGPT, then press Run attempt readiness.',
    }

    if summary_path is not None:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description='Check static browser-extension readiness for the ChatGPT live proof path.')
    parser.add_argument('--root', default=os.fspath(project_root_from_here()))
    parser.add_argument('--summary-out', default=None)
    parser.add_argument('--require-build', action='store_true')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    report = check_extension_readiness(Path(args.root), require_build=args.require_build, summary_path=Path(args.summary_out) if args.summary_out else None)
    print(json.dumps(report, indent=2 if args.pretty else None, sort_keys=bool(args.pretty)))
    return 0 if report.get('ok') else 2


if __name__ == '__main__':
    raise SystemExit(main())
