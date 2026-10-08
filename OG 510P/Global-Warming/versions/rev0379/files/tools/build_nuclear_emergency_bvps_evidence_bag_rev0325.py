#!/usr/bin/env python3
"""Build a local/anonymized evidence bag manifest for BVPS emergency-preparedness packets.

This script computes SHA-256 hashes of the original files and writes manifest outputs.
It does not make readiness decisions. Its output can only enter the cube as hold,
context, reopen, or candidate-for-adjudication-not-closure.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, mimetypes, os, zipfile
from datetime import datetime, timezone
from pathlib import Path

PUBLIC_SUFFIXES = {'.txt','.csv','.json','.xml','.md'}
SENSITIVE_HINTS = ('pii','medical','student','afn','route','credential','password','patient','dosimetry','security')

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def classify_redaction(path: Path) -> str:
    low = str(path).lower()
    if any(h in low for h in SENSITIVE_HINTS):
        return 'sensitive_annex'
    if path.suffix.lower() in PUBLIC_SUFFIXES:
        return 'public_surrogate'
    return 'sensitive_annex_review_required'

def build(args):
    input_dir = Path(args.input_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    bag_id = args.bag_id
    now = datetime.now(timezone.utc).isoformat()
    manifest_rows = []
    for path in sorted(p for p in input_dir.rglob('*') if p.is_file()):
        rel = path.relative_to(input_dir).as_posix()
        st = path.stat()
        redaction = classify_redaction(path)
        artifact_id = f"{bag_id}-{len(manifest_rows)+1:04d}"
        manifest_rows.append({
            'bag_id': bag_id,
            'packet_id': args.packet_id,
            'artifact_id': artifact_id,
            'relative_path': rel,
            'artifact_role': args.default_artifact_role,
            'site_or_overlay': args.site_or_overlay,
            'source_authority_class': args.source_authority_class,
            'source_owner_role': args.owner_role,
            'collecting_actor_role': args.collector_role,
            'capture_time_utc': now,
            'timezone': args.timezone,
            'clock_source': args.clock_source,
            'clock_drift_seconds': args.clock_drift_seconds,
            'media_type': mimetypes.guess_type(path.name)[0] or 'application/octet-stream',
            'byte_size': str(st.st_size),
            'sha256_original': sha256_file(path),
            'redaction_class': redaction,
            'sha256_redacted_surrogate': '',
            'chain_of_custody_event_id': f"{bag_id}-CUSTODY-001",
            'acceptance_state': 'candidate_for_adjudication_not_closure',
            'claim_effect': 'no_auto_closure',
            'counterevidence_path': args.counterevidence_path,
        })
    manifest_path = output_dir / f'{bag_id}-manifest.csv'
    fields = list(manifest_rows[0].keys()) if manifest_rows else ['bag_id','packet_id','artifact_id','relative_path']
    with manifest_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(manifest_rows)
    packet = {
        'bag_id': bag_id,
        'packet_id': args.packet_id,
        'site_or_overlay': args.site_or_overlay,
        'created_utc': now,
        'artifact_count': len(manifest_rows),
        'claim_effect': 'no_auto_closure',
        'accepted_state_ceiling': 'candidate_for_adjudication_not_closure',
        'manifest_sha256': sha256_file(manifest_path),
        'originals_preserved_before_redaction': True,
    }
    packet_path = output_dir / f'{bag_id}-packet.json'
    packet_path.write_text(json.dumps(packet, indent=2), encoding='utf-8')
    zip_path = output_dir / f'{bag_id}-evidence-bag.zip'
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.write(manifest_path, manifest_path.name)
        z.write(packet_path, packet_path.name)
        for path in sorted(p for p in input_dir.rglob('*') if p.is_file()):
            z.write(path, 'originals/' + path.relative_to(input_dir).as_posix())
    print(json.dumps({'bag_id': bag_id, 'artifact_count': len(manifest_rows), 'manifest': str(manifest_path), 'packet': str(packet_path), 'zip': str(zip_path), 'claim_effect': 'no_auto_closure'}, indent=2))
    return 0

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-dir', required=True)
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--bag-id', required=True)
    ap.add_argument('--packet-id', required=True)
    ap.add_argument('--site-or-overlay', default='BVPS_ANON_EXERCISE')
    ap.add_argument('--source-authority-class', default='local_anonymized')
    ap.add_argument('--owner-role', default='packet_owner')
    ap.add_argument('--collector-role', default='collector')
    ap.add_argument('--default-artifact-role', default='exercise_evidence')
    ap.add_argument('--timezone', default='America/New_York')
    ap.add_argument('--clock-source', default='operator_declared_clock_source')
    ap.add_argument('--clock-drift-seconds', default='unknown')
    ap.add_argument('--counterevidence-path', default='required_in_adjudication_queue')
    args = ap.parse_args(argv)
    return build(args)
if __name__ == '__main__':
    raise SystemExit(main())
