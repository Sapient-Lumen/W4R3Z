#!/usr/bin/env python3
"""Validate rev0863 mission/right/identity triage surfaces."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"mission-recenter-rights-identity-rev0863: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def require_file(rel: str) -> Path:
    path = ROOT / rel
    if path.is_symlink() or not path.is_file():
        fail(f"missing regular file: {rel}")
    return path


def load_json(rel: str) -> dict:
    path = require_file(rel)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f"invalid JSON {rel}: {exc}")
    if not isinstance(data, dict):
        fail(f"JSON object expected: {rel}")
    return data


def require_text(rel: str, snippets: list[str]) -> None:
    text = require_file(rel).read_text(encoding='utf-8', errors='ignore')
    missing = [s for s in snippets if s not in text]
    if missing:
        fail(f"{rel} missing snippets: {missing}")


def main() -> int:
    audit = load_json('AUDIT/MISSION_RECENTER_RIGHTS_IDENTITY_TRIAGE_REV0863.json')
    rights_packet = load_json('RIGHTS/RIGHTS_DECISION_PACKET_REV0863.json')
    patch_manifest = load_json('PATCH_BUNDLE_MANIFEST.json')
    rights = load_json('RIGHTS/component_license_ledger.json')
    release = load_json('RELEASE_MANIFEST.json')
    spdx = load_json('SBOM/EvidenceVault-file-inventory.spdx.json')
    full = load_json('PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_absence.full.rev0862.json')
    minimum = load_json('PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/archive_payload_search_absence.minimum.rev0862.json')

    if audit.get('revision') != 'rev0863' or audit.get('status') != 'mission_recentered_publication_block_preserved':
        fail('rev0863 audit status mismatch')
    if rights_packet.get('status') != 'decision_packet_only_publication_still_blocked':
        fail('rights decision packet status mismatch')
    if patch_manifest.get('overlay_revision') != 'rev0863':
        fail('patch bundle manifest revision mismatch')
    if patch_manifest.get('canonical_base_revision_declared_by_release_manifest') != release.get('revision'):
        fail('patch bundle canonical base mismatch')
    if release.get('revision') != 'rev0826':
        fail('carried canonical release manifest no longer declares rev0826; update identity interpretation')

    if rights.get('status') != 'publication_blocked_pending_rights_decision':
        fail('rights status drifted')
    if rights.get('root_license_or_notice_file_present') is not False:
        fail('root rights sentinel unexpectedly present in rights ledger')
    for sentinel in ['LICENSE', 'COPYING', 'NOTICE']:
        if (ROOT / sentinel).exists():
            fail(f'root rights sentinel was invented: {sentinel}')
    if not all(c.get('license_concluded') == 'NOASSERTION' for c in rights.get('components', [])):
        fail('component license conclusion was changed without rights closure')

    if len(spdx.get('packages', [])) != 0:
        fail('SPDX package count changed; rev0863 expected carried file-inventory BOM')
    if full.get('selected_path_count') != 17 or full.get('status_counts', {}).get('missing') != 17:
        fail('full streamfold absence report drifted')
    if minimum.get('selected_path_count') != 4 or minimum.get('status_counts', {}).get('missing') != 4:
        fail('minimum streamfold absence report drifted')

    readme_first = require_file('README.md').read_text(encoding='utf-8', errors='ignore').splitlines()[0]
    overlay_first = require_file('OVERLAY_COMMANDS.md').read_text(encoding='utf-8', errors='ignore').splitlines()[0]
    if 'rev0863' not in readme_first:
        fail('README top heading is not rev0863')
    if 'rev0863' not in overlay_first:
        fail('OVERLAY_COMMANDS top heading is not rev0863')
    require_text('README.md', ['PATCH_BUNDLE_MANIFEST.json', 'RIGHTS/RIGHTS_DECISION_PACKET_REV0863', 'publication-blocked'])
    require_text('OVERLAY_COMMANDS.md', ['validate_mission_recenter_rights_identity_rev0863.py', 'validate_streamfold_archive_payload_search_rev0862.py', 'Do not use `make gate`'])
    require_text('AUDIT/MISSION_RECENTER_RIGHTS_IDENTITY_TRIAGE_REV0863.md', ['proof-carrying evidence vault', 'comfort work', 'Non-claims'])
    require_text('RIGHTS/RIGHTS_DECISION_PACKET_REV0863.md', ['not a license grant', 'Owner/upstream questions'])
    require_text('PATCH_BUNDLE_MANIFEST.json', ['mission/right/identity triage overlay'])

    if (ROOT / 'scripts/build_papers.sh').exists():
        fail('unexpected canonical build script appeared; update makefile-surface finding')

    print('mission-recenter-rights-identity-rev0863: OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
