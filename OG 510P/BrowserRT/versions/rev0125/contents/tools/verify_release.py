#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import stat
import sys
import unicodedata
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

NAME_RE = re.compile(r'^BrowserRT-(rev\d{4})-(\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.zip$')
MAX_ARCHIVE_FILES = 1600
MAX_ARCHIVE_ENTRY_BYTES = 2 * 1024 * 1024
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 12 * 1024 * 1024
ALLOWED_COMPRESSION_TYPES = {ZIP_STORED, ZIP_DEFLATED}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(msg: str) -> None:
    print(f'[verify_release] FAIL: {msg}')
    raise SystemExit(1)


def canonical_archive_path(name: str) -> str:
    return unicodedata.normalize('NFC', name).casefold()


def archive_path_failures(name: str) -> list[str]:
    failures = []
    if not name:
        failures.append('empty')
    if name.startswith('/') or name.startswith('\\'):
        failures.append('absolute')
    if '\\' in name:
        failures.append('backslash')
    parts = name.split('/')
    if any(part in {'', '.', '..'} for part in parts):
        failures.append('unsafe-segment')
    return failures




def archive_entry_budget_failures(info) -> list[str]:
    failures = []
    if info.compress_type not in ALLOWED_COMPRESSION_TYPES:
        failures.append(f'compression={info.compress_type}')
    if info.file_size > MAX_ARCHIVE_ENTRY_BYTES:
        failures.append(f'file-size={info.file_size}>max={MAX_ARCHIVE_ENTRY_BYTES}')
    if info.compress_size > MAX_ARCHIVE_ENTRY_BYTES:
        failures.append(f'compressed-size={info.compress_size}>max={MAX_ARCHIVE_ENTRY_BYTES}')
    return failures


def archive_entry_metadata_failures(info) -> list[str]:
    failures = []
    mode = (info.external_attr >> 16) & 0o177777
    if info.create_system != 3:
        failures.append(f'create-system={info.create_system}')
    if mode != 0o100644:
        failures.append(f'mode={oct(mode)}')
    if stat.S_IFMT(mode) != stat.S_IFREG:
        failures.append('non-regular-file')
    return failures


def get_object_path(obj, dotted):
    cur=obj
    for part in dotted.split('.'):
        if part:
            if not isinstance(cur,dict) or part not in cur: return None
            cur=cur[part]
    return cur

def expected_evidence_lineage(revision):
    return {
        'support-bundle-proof-artifact':('probe_id',f'{revision}-kernel-kit-support-bundle-probe',[('support-bundle-revision-current','supportBundle.revision',revision),('support-bundle-evidence-ledger-current','supportBundle.evidenceLedger.revision',revision)]),
        'support-bundle-audit-artifact':('audit_id',f'{revision}-kernel-kit-support-bundle-contract-audit',[]),
        'support-bundle-import-artifact':('probe_id',f'{revision}-kernel-kit-support-bundle-import-probe',[('import-source-probe-current','sourceProbeId',f'{revision}-kernel-kit-support-bundle-probe'),('import-report-current','reports.fromObject.revision',revision)]),
        'readiness-gate-artifact':('probe_id',f'{revision}-kernel-kit-readiness-gate-probe',[('readiness-gate-current','readinessGate.revision',revision)]),
        'browser-kernel-kit-artifact':('probe_id',f'{revision}-browser-kernel-kit-demo-probe',[('browser-proof-id-current','proofId',f'{revision}-browser-kernel-kit-demo')]),
        'browser-session-coordination-artifact':('probe_id',f'{revision}-browser-kernel-kit-session-coordination-checkpoint-probe',[('session-coordination-exclusive-denied','proof.exclusiveIfAvailableDenied',True),('session-coordination-queued-after-release','proof.queuedAcquiredAfterRelease',True),('session-coordination-stale-read-null','proof.staleReadReturnedNull',True)]),
        'browser-recovery-artifact':('probe_id',f'{revision}-browser-kernel-kit-recovery-checkpoint-probe',[('recovery-same-origin-profile','proof.sameOriginProfileRestartObserved',True),('recovery-interrupted-write-safe','proof.interruptedWriteNotAcceptedCorrupt',True),('recovery-open-failure-retry','proof.transientOpenFailureRetryObserved',True),('recovery-orphan-review-gate','proof.unsettledOrphanReviewGateObserved',True)]),
    }

def artifact_lineage_failures(artifact_id,path,parsed,revision,prefix):
    failures=[]; expected=expected_evidence_lineage(revision).get(artifact_id)
    for key,want in [('project','BrowserRT'),('revision',revision),('status','passed')]:
        if parsed.get(key)!=want: failures.append(f'{key}={parsed.get(key)!r}')
    if prefix not in path: failures.append(f'path-prefix={path!r}')
    if expected is None:
        failures.append(f'unknown-artifact-id={artifact_id!r}'); return failures
    identity_path,identity_value,extra=expected; actual_identity=get_object_path(parsed,identity_path)
    if actual_identity!=identity_value: failures.append(f'{identity_path}={actual_identity!r}')
    for name,dotted,value in extra:
        actual=get_object_path(parsed,dotted)
        if actual!=value: failures.append(f'{name}:{dotted}={actual!r}')
    return failures

def verify(path: Path) -> None:
    m = NAME_RE.match(path.name)
    if not m:
        fail(f'bad BrowserRT release filename: {path.name}')
    with ZipFile(path) as zf:
        names = zf.namelist()
        if len(names) > MAX_ARCHIVE_FILES:
            fail(f'zip file count budget rejected: {len(names)}>{MAX_ARCHIVE_FILES}')
        total_uncompressed = sum(info.file_size for info in zf.infolist())
        if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
            fail(f'zip uncompressed size budget rejected: {total_uncompressed}>{MAX_ARCHIVE_UNCOMPRESSED_BYTES}')
        duplicate_names = sorted({name for name in names if names.count(name) > 1})
        if duplicate_names:
            fail(f'duplicate zip entry names rejected: {duplicate_names[:5]}')
        unsafe_names = {name: archive_path_failures(name) for name in names if archive_path_failures(name)}
        if unsafe_names:
            first = sorted(unsafe_names.items())[0]
            fail(f'unsafe zip entry path rejected: {first[0]} {first[1]}')
        canonical_name_index = {}
        canonical_name_collisions = []
        for name in names:
            canonical = canonical_archive_path(name)
            previous = canonical_name_index.setdefault(canonical, name)
            if previous != name:
                canonical_name_collisions.append((previous, name))
        if canonical_name_collisions:
            fail(f'case-colliding zip entry names rejected: {canonical_name_collisions[:5]}')
        unsafe_budget = {info.filename: archive_entry_budget_failures(info) for info in zf.infolist() if archive_entry_budget_failures(info)}
        if unsafe_budget:
            first = sorted(unsafe_budget.items())[0]
            fail(f'zip entry budget rejected: {first[0]} {first[1]}')
        unsafe_metadata = {info.filename: archive_entry_metadata_failures(info) for info in zf.infolist() if archive_entry_metadata_failures(info)}
        if unsafe_metadata:
            first = sorted(unsafe_metadata.items())[0]
            fail(f'unsafe zip entry metadata rejected: {first[0]} {first[1]}')
        if 'RELEASE-MANIFEST.json' not in names:
            fail('missing RELEASE-MANIFEST.json')
        manifest = json.loads(zf.read('RELEASE-MANIFEST.json').decode('utf-8'))
        if manifest.get('archive_name') != path.name:
            fail('manifest archive_name does not match filename')
        if manifest.get('revision') != m.group(1):
            fail('manifest revision does not match filename')
        if manifest.get('packaging_timestamp') != m.group(2):
            fail('manifest timestamp does not match filename')
        if manifest.get('slug') != m.group(3):
            fail('manifest slug does not match filename')
        file_rows = manifest.get('files')
        if not isinstance(file_rows, list) or not file_rows:
            fail('manifest files list missing')
        manifest_row_paths = []
        for row in file_rows:
            if not isinstance(row, dict) or not isinstance(row.get('path'), str):
                fail('manifest file row missing string path')
            path_failures = archive_path_failures(row['path'])
            if row['path'] == 'RELEASE-MANIFEST.json':
                path_failures.append('manifest-self-entry')
            if path_failures:
                fail(f'unsafe manifest file path rejected: {row["path"]} {path_failures}')
            manifest_row_paths.append(row['path'])
        duplicate_manifest_paths = sorted({path for path in manifest_row_paths if manifest_row_paths.count(path) > 1})
        if duplicate_manifest_paths:
            fail(f'duplicate manifest file paths rejected: {duplicate_manifest_paths[:5]}')
        canonical_manifest_index = {}
        canonical_manifest_collisions = []
        for row_path in manifest_row_paths:
            canonical = canonical_archive_path(row_path)
            previous = canonical_manifest_index.setdefault(canonical, row_path)
            if previous != row_path:
                canonical_manifest_collisions.append((previous, row_path))
        if canonical_manifest_collisions:
            fail(f'case-colliding manifest file paths rejected: {canonical_manifest_collisions[:5]}')
        manifest_paths = set(manifest_row_paths)
        zip_paths = set(names) - {'RELEASE-MANIFEST.json'}
        if manifest_paths != zip_paths:
            missing = sorted(zip_paths - manifest_paths)[:5]
            extra = sorted(manifest_paths - zip_paths)[:5]
            fail(f'manifest path mismatch missing={missing} extra={extra}')
        manifest_index = {row['path']: row for row in file_rows}
        for row in file_rows:
            data = zf.read(row['path'])
            if len(data) != row['size']:
                fail(f'size mismatch for {row["path"]}')
            if sha256(data) != row['sha256']:
                fail(f'sha256 mismatch for {row["path"]}')
        prefix = 'REV' + m.group(1)[3:]
        seal_path = f'artifacts/validation/{prefix}-KERNEL-KIT-SUPPORT-BUNDLE-PACKAGE-EVIDENCE-SEAL-PROBE.json'
        if seal_path not in manifest_paths:
            fail(f'missing package evidence seal artifact: {seal_path}')
        try:
            seal = json.loads(zf.read(seal_path).decode('utf-8'))
        except Exception as exc:
            fail(f'package evidence seal artifact is not valid JSON: {exc}')
        if seal.get('format') != 'browserrt-kernel-kit-support-bundle-package-evidence-seal-v1':
            fail('package evidence seal format mismatch')
        if seal.get('status') != 'passed':
            fail(f'package evidence seal status is {seal.get("status")!r}')
        if seal.get('proof', {}).get('releaseManifestVerifierExpected') is not True:
            fail('package evidence seal did not expect release manifest verification')
        if seal.get('proof', {}).get('allSealedArtifactsLineageBound') is not True:
            fail('package evidence seal did not bind sealed artifact lineage')
        if seal.get('proof', {}).get('staleOrWrongRevisionEvidenceRejected') is not True:
            fail('package evidence seal did not reject stale or wrong-revision evidence')
        sealed_rows = seal.get('sealedArtifactRows')
        if not isinstance(sealed_rows, list) or len(sealed_rows) < 5:
            fail('package evidence seal sealedArtifactRows missing or too small')
        sealed_ids = {row.get('id') for row in sealed_rows if isinstance(row, dict)}
        required_ids = {
            'support-bundle-proof-artifact',
            'support-bundle-audit-artifact',
            'support-bundle-import-artifact',
            'readiness-gate-artifact',
            'browser-kernel-kit-artifact',
            'browser-session-coordination-artifact',
            'browser-recovery-artifact',
        }
        if not required_ids.issubset(sealed_ids):
            fail(f'package evidence seal missing required ids: {sorted(required_ids - sealed_ids)}')
        for sealed in sealed_rows:
            sealed_path = sealed.get('path')
            if not sealed_path or sealed_path not in manifest_index:
                fail(f'package evidence seal row not present in release manifest: {sealed_path}')
            manifest_row = manifest_index[sealed_path]
            if sealed.get('size') != manifest_row.get('size'):
                fail(f'package evidence seal size mismatch for {sealed_path}')
            if sealed.get('sha256') != manifest_row.get('sha256'):
                fail(f'package evidence seal sha256 mismatch for {sealed_path}')
            if sealed.get('status') != 'sealed':
                fail(f'package evidence seal row not sealed: {sealed_path}')
            if sealed.get('lineageStatus') != 'bound':
                fail(f'package evidence seal row lineage not bound: {sealed_path}')
        lineage_rows = seal.get('evidenceLineageRows')
        if not isinstance(lineage_rows, list) or len(lineage_rows) < 6:
            fail('package evidence seal lineage rows missing or too small')
        lineage_index = {row.get('id'): row for row in lineage_rows if isinstance(row, dict)}
        for required_id in required_ids:
            if lineage_index.get(required_id, {}).get('status') != 'bound':
                fail(f'package evidence seal lineage row not bound: {required_id}')
        if lineage_index.get('cube-sanity-command', {}).get('status') != 'command-only':
            fail('package evidence seal cube-sanity lineage row must remain command-only')
        if seal.get('lineageNegativeCheck', {}).get('rejected') is not True:
            fail('package evidence seal lineage negative check did not reject stale revision')
        seal_row_index = {row.get('id'): row for row in sealed_rows if isinstance(row, dict)}
        for required_id in sorted(required_ids):
            sealed = seal_row_index.get(required_id)
            if not sealed:
                fail(f'package evidence seal missing row for independent lineage check: {required_id}')
            sealed_path = sealed.get('path')
            try:
                parsed_artifact = json.loads(zf.read(sealed_path).decode('utf-8'))
            except Exception as exc:
                fail(f'package evidence artifact is not valid JSON for independent lineage check: {sealed_path}: {exc}')
            lineage_failures = artifact_lineage_failures(required_id, sealed_path, parsed_artifact, m.group(1), prefix)
            if lineage_failures:
                fail(f'package evidence seal independent lineage check failed for {required_id}: {lineage_failures}')
        for info in zf.infolist():
            if info.date_time[5] != 0:
                fail(f'non-normalized seconds for {info.filename}')
    print(f'[verify_release] OK: {path}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: verify_release.py /path/to/BrowserRT-rev####-YYYY.MM.DD.HH.MM-slug.zip')
    verify(Path(sys.argv[1]))

# Static marker: verify_release re-parses zip-contained evidence artifacts for independent lineage check.
# Static marker: verify_release rejects duplicate zip entries, unsafe archive paths, non-regular ZIP metadata, case-normalization collisions, and ZIP bomb/compression-budget risks before manifest trust.
