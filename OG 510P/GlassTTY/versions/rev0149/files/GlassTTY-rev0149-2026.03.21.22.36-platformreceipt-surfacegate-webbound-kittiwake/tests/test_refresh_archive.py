from __future__ import annotations

import json
import subprocess
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / 'scripts' / 'refresh-archive.py'
spec = importlib.util.spec_from_file_location('refresh_archive', MODULE_PATH)
assert spec and spec.loader
MODULE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MODULE)

summarize_validation = MODULE.summarize_validation
parse_archive_name = MODULE.parse_archive_name


def test_summarize_validation_uses_summary_json_when_report_missing(tmp_path: Path) -> None:
    validation_dir = tmp_path / 'validation-sample'
    validation_dir.mkdir()
    (validation_dir / 'summary.json').write_text(
        json.dumps(
            {
                'extension_typecheck_ok': True,
                'extension_build_ok': True,
                'package_verify_ok': True,
                'package_zip': 'validation/sample/package-check.zip',
                'resume_report': 'validation/sample/report.json',
                'resume_proof_summary': 'validation/sample/resume-proof-summary.json',
            },
            indent=2,
        )
        + '\n',
        encoding='utf-8',
    )

    info = summarize_validation(validation_dir)

    assert info['exists'] is True
    assert info['summary_json'].endswith('summary.json')
    assert info['overall_ok'] is True
    assert info['check_count'] == 3
    assert info['check_ok_count'] == 3
    assert info['package_zip'] == 'validation/sample/package-check.zip'
    assert info['resume_report'] == 'validation/sample/report.json'
    assert info['resume_proof_summary'] == 'validation/sample/resume-proof-summary.json'


def test_summarize_validation_prefers_report_json(tmp_path: Path) -> None:
    validation_dir = tmp_path / 'validation-report'
    validation_dir.mkdir()
    (validation_dir / 'summary.json').write_text(json.dumps({'extension_typecheck_ok': False}) + '\n', encoding='utf-8')
    (validation_dir / 'report.json').write_text(
        json.dumps(
            {
                'ok': True,
                'steps': [
                    {'name': 'alpha', 'ok': True, 'required': True},
                    {'name': 'beta', 'ok': False, 'required': False},
                ],
            },
            indent=2,
        )
        + '\n',
        encoding='utf-8',
    )

    info = summarize_validation(validation_dir)

    assert info['overall_ok'] is True
    assert info['step_count'] == 2
    assert info['required_ok_count'] == 1
    assert 'check_count' not in info


def test_summarize_validation_surfaces_package_zip_proof_from_report(tmp_path: Path) -> None:
    validation_dir = tmp_path / 'validation-report'
    validation_dir.mkdir()
    (validation_dir / 'report.json').write_text(
        json.dumps(
            {
                'ok': True,
                'package_zip_retained': False,
                'package_zip_proof': {
                    'path': 'validation/sample/package-check.zip',
                    'retained': False,
                    'size_bytes': 321,
                    'sha256': 'b' * 64,
                },
                'steps': [],
            },
            indent=2,
        )
        + '\n',
        encoding='utf-8',
    )

    info = summarize_validation(validation_dir)

    assert info['package_zip_retained'] is False
    assert info['package_zip_proof']['size_bytes'] == 321


def test_parse_archive_name_accepts_zip_filename() -> None:
    parsed = parse_archive_name('GlassTTY-rev0073-2026.03.17.00.21-identitytight-packagerename-manifestlock-oystercatcher.zip')
    assert parsed['archive_name'] == 'GlassTTY-rev0073-2026.03.17.00.21-identitytight-packagerename-manifestlock-oystercatcher'
    assert parsed['archive_revision'] == 73
    assert parsed['archive_slug'] == 'identitytight-packagerename-manifestlock-oystercatcher'


def test_refresh_archive_supports_explicit_archive_name_override(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev0072-2026.03.16.23.59-profilepreflight-nativehostledger-browseranchor-curlew'
    repo.mkdir()
    (repo / 'docs').mkdir()
    (repo / 'extension').mkdir()
    (repo / 'daemon').mkdir()
    (repo / 'tests').mkdir()
    (repo / 'fixtures').mkdir()
    (repo / 'validation').mkdir()
    target_name = 'GlassTTY-rev0073-2026.03.17.00.21-identitytight-packagerename-manifestlock-oystercatcher'
    result = subprocess.run(
        [
            sys.executable,
            str(MODULE_PATH),
            '--root',
            str(repo),
            '--archive-name',
            target_name,
            '--summary',
            'identity override test',
            '--codename',
            'oystercatcher',
            '--revision',
            '73',
        ],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = json.loads((repo / 'ARCHIVE_MANIFEST.json').read_text(encoding='utf-8'))
    assert manifest['archive_name'] == target_name
    assert manifest['archive_revision'] == 73
    assert manifest['archive_slug'] == 'identitytight-packagerename-manifestlock-oystercatcher'
    assert manifest['worktree_name'] == repo.name
