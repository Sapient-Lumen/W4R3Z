#!/usr/bin/env python3
"""Validate revision lineage aliases agree with the current packaged state."""
from __future__ import annotations
import json, sys
from pathlib import Path

ALIAS_KEYS = ('lineage', 'entries', 'revisions')

def add(checks, name, ok, detail=''):
    checks.append({'name': name, 'ok': bool(ok), 'detail': '' if detail is None else str(detail)})

def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))

def run(root: Path):
    checks = []
    state = load_json(root / 'STATE.json')
    lineage = load_json(root / 'REVISION_LINEAGE.json')
    rev = state.get('revision')
    artifact = state.get('artifact')
    updated_at = state.get('updated_at')

    add(checks, 'lineage_top_current_revision', lineage.get('current_revision') == rev, lineage.get('current_revision'))
    add(checks, 'lineage_top_current_artifact', lineage.get('current_artifact') == artifact, lineage.get('current_artifact'))
    add(checks, 'lineage_top_updated_at', lineage.get('updated_at') == updated_at, lineage.get('updated_at'))

    arrays = {}
    for key in ALIAS_KEYS:
        arr = lineage.get(key)
        add(checks, f'lineage_alias_exists:{key}', isinstance(arr, list), type(arr).__name__)
        if not isinstance(arr, list):
            continue
        arrays[key] = arr
        ids = [e.get('revision') for e in arr if isinstance(e, dict)]
        add(checks, f'lineage_alias_current_once:{key}', ids.count(rev) == 1, f'{rev} count={ids.count(rev)}')
        current = [e for e in arr if isinstance(e, dict) and e.get('status') == 'current']
        add(checks, f'lineage_alias_one_current:{key}', len(current) == 1, f'count={len(current)}')
        if current:
            add(checks, f'lineage_alias_current_matches_state:{key}', current[0].get('revision') == rev, current[0].get('revision'))
            add(checks, f'lineage_alias_current_artifact_matches_state:{key}', current[0].get('artifact') == artifact, current[0].get('artifact'))
        rev_entry = [e for e in arr if isinstance(e, dict) and e.get('revision') == rev]
        if rev_entry:
            add(checks, f'lineage_alias_rev_entry_artifact:{key}', rev_entry[0].get('artifact') == artifact, rev_entry[0].get('artifact'))

    if len(arrays) >= 2:
        base_key, base_arr = next(iter(arrays.items()))
        for key, arr in arrays.items():
            if key == base_key:
                continue
            add(checks, f'lineage_alias_synchronized:{base_key}_vs_{key}', arr == base_arr, f'{base_key} len={len(base_arr)} {key} len={len(arr)}')

        # Parent integrity is a release-truth invariant, not a cosmetic field.
        current_positions = [i for i, e in enumerate(base_arr) if isinstance(e, dict) and e.get('revision') == rev]
        if len(current_positions) == 1:
            pos = current_positions[0]
            entry = base_arr[pos]
            parent = entry.get('previous_revision')
            previous_entry = base_arr[pos - 1] if pos > 0 and isinstance(base_arr[pos - 1], dict) else {}
            add(checks, 'lineage_current_parent_present', isinstance(parent, str) and bool(parent), parent)
            add(checks, 'lineage_current_parent_is_immediate_predecessor', pos > 0 and previous_entry.get('revision') == parent, f"declared={parent} immediate={previous_entry.get('revision')}")
            add(checks, 'lineage_current_head_matches_state', entry.get('current_head') == state.get('current_head'), entry.get('current_head'))
            add(checks, 'lineage_current_created_at_matches_state', entry.get('created_at') == updated_at, entry.get('created_at'))

            receipt = load_json(root / 'REVISION_RECEIPT.json')
            release = load_json(root / 'RELEASE_MANIFEST.json')
            add(checks, 'revision_receipt_parent_matches_lineage', receipt.get('previous_revision') == parent and receipt.get('from_revision') == parent, f"previous={receipt.get('previous_revision')} from={receipt.get('from_revision')} lineage={parent}")
            add(checks, 'revision_receipt_input_artifact_matches_parent', receipt.get('input_artifact') == previous_entry.get('artifact') and receipt.get('previous_artifact') == previous_entry.get('artifact'), f"input={receipt.get('input_artifact')} parent_artifact={previous_entry.get('artifact')}")
            parent_hash = entry.get('previous_artifact_sha256')
            add(checks, 'lineage_parent_artifact_hash_present', isinstance(parent_hash, str) and len(parent_hash) == 64, parent_hash)
            add(checks, 'revision_receipt_parent_hash_matches_lineage', receipt.get('input_artifact_sha256') == parent_hash and receipt.get('previous_artifact_sha256') == parent_hash, f"receipt={receipt.get('input_artifact_sha256')} lineage={parent_hash}")
            add(checks, 'revision_receipt_created_at_matches_lineage', receipt.get('created_at') == entry.get('created_at'), receipt.get('created_at'))
            add(checks, 'release_manifest_parent_matches_lineage', release.get('previous_revision') == parent and release.get('previous_artifact') == previous_entry.get('artifact'), f"revision={release.get('previous_revision')} artifact={release.get('previous_artifact')}")
            add(checks, 'release_manifest_parent_hash_matches_lineage', release.get('previous_artifact_sha256') == parent_hash, f"release={release.get('previous_artifact_sha256')} lineage={parent_hash}")
            add(checks, 'release_manifest_created_at_matches_lineage', release.get('created_at') == entry.get('created_at'), release.get('created_at'))
    return checks

def main(root='.'):
    checks = run(Path(root))
    ok = all(c.get('ok') for c in checks)
    print(json.dumps({'ok': ok, 'checks': checks, 'failed': [c for c in checks if not c.get('ok')]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else '.'))
