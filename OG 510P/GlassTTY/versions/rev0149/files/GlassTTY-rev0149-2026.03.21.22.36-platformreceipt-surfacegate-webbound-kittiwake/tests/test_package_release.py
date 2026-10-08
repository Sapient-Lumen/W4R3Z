from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / 'scripts' / 'verify-package.py'
PACKAGE_SCRIPT = ROOT / 'scripts' / 'package-release.sh'
REFRESH_SCRIPT = ROOT / 'scripts' / 'refresh-archive.py'




def build_archive_manifest(repo_name: str) -> str:
    prefix = 'GlassTTY-rev'
    if repo_name.startswith(prefix):
        parts = repo_name.split('-', 3)
        if len(parts) == 4:
            revision = int(parts[1][3:]) if parts[1].startswith('rev') else None
            stamp = parts[2]
            slug = parts[3]
            if revision is not None:
                return json.dumps(
                    {
                        'archive_name': repo_name,
                        'archive_revision': revision,
                        'archive_created_at_from_name': stamp,
                        'archive_slug': slug,
                    },
                    indent=2,
                ) + '\n'
    return '{}\n'

def build_manifest(*, web_accessible_resources: list[str] | None = None) -> str:
    resources = web_accessible_resources or ['assets/*.css', 'images/*.png', 'fonts/*.woff']
    return json.dumps(
        {
            'manifest_version': 3,
            'name': 'GlassTTY Bridge',
            'version': '0.0.0-test',
            'background': {'service_worker': 'dist/background/main.js', 'type': 'module'},
            'side_panel': {'default_path': 'sidepanel/index.html'},
            'options_page': 'options/index.html',
            'icons': {'16': 'images/icon.png'},
            'content_scripts': [
                {
                    'matches': ['https://claude.ai/*'],
                    'js': ['dist/content/main.js'],
                    'css': ['dist/content.css'],
                }
            ],
            'web_accessible_resources': [
                {
                    'resources': resources,
                    'matches': ['https://example.com/*'],
                }
            ],
        },
        indent=2,
    ) + '\n'


OPTIONS_HTML = '<!doctype html><style>.hero { background-image: url("../images/bg.png"); }</style><link rel="stylesheet" href="../styles/options.css"><img src="../images/hero.png" srcset="../images/hero-2x.png 2x"><video poster="../images/poster.png"></video><script type="module" src="../dist/options/main.js"></script>\n'
SIDEPANEL_HTML = '<!doctype html><script type="module" src="../dist/sidepanel/main.js"></script>\n'
PROBE_HTML = '<!doctype html><script type="module" src="../../dist/probe/main.js"></script>\n'
OFFSCREEN_HTML = '<!doctype html><script type="module" src="../../dist/offscreen/main.js"></script>\n'


def seed_minimal_repo(
    repo: Path,
    *,
    include_options_bundle: bool = True,
    include_module_dependency: bool = True,
    include_stylesheet: bool = True,
    include_web_accessible_asset: bool = True,
    include_html_media_assets: bool = True,
    include_html_inline_style_asset: bool = True,
    include_script_runtime_asset: bool = True,
    include_script_worker_asset: bool = True,
    include_script_classic_dependency: bool = True,
    include_script_relative_worker_asset: bool = True,
    web_accessible_resources: list[str] | None = None,
) -> None:
    text_files = {
        'README.md': '# repo\n',
        'STATUS.md': '# status\n',
        'MEMORY.md': '# memory\n',
        'CHANGELOG.md': '# changelog\n',
        'ARCHIVE_MANIFEST.json': build_archive_manifest(repo.name),
        'daemon/src/glassttyd/cli.py': 'print("ok")\n',
        'fixtures/corpus/claude-synthetic-thread.json': '{}\n',
        'extension/manifest.json': build_manifest(web_accessible_resources=web_accessible_resources),
        'extension/options/index.html': OPTIONS_HTML,
        'extension/sidepanel/index.html': SIDEPANEL_HTML,
        'extension/probe/index.html': PROBE_HTML,
        'extension/offscreen/index.html': OFFSCREEN_HTML,
        'extension/dist/background/main.js': 'import { helper } from "../shared/protocol";\nconst iconUrl = chrome.runtime.getURL("images/icon.png");\nconst workerUrl = new URL("../workers/helper.js", import.meta.url);\nconsole.log(helper, iconUrl, workerUrl);\n',
        'extension/dist/content/main.js': 'import "../shared/protocol";\n',
        'extension/dist/content.css': '@import url("../assets/theme.css");\n@font-face { src: url("../fonts/ui.woff") format("woff"); }\nbody { color: black; }\n',
        'extension/dist/probe/main.js': '// probe\n',
        'extension/dist/offscreen/main.js': '// offscreen\n',
        'extension/dist/sidepanel/main.js': '// sidepanel\n',
        'extension/dist/options/main.js': 'import "../shared/protocol";\nconst relativeWorker = new Worker("../workers/relative-worker.js");\nconsole.log(relativeWorker);\n',
        'extension/dist/shared/protocol.js': 'export const helper = true;\n',
        'extension/dist/workers/helper.js': 'importScripts("./classic-helper.js");\nself.postMessage("ok");\n',
        'extension/dist/workers/relative-worker.js': 'importScripts("./classic-helper.js");\nself.postMessage("relative");\n',
        'extension/dist/workers/classic-helper.js': 'self.__glass = true;\n',
        'extension/styles/options.css': 'body { background: url("../images/icon.png"); }\n',
        'extension/assets/theme.css': 'body { background-image: url("../images/icon.png"); }\n',
    }
    binary_files = {
        'extension/images/icon.png': b'\x89PNG\r\n\x1a\n',
        'extension/images/hero.png': b'\x89PNG\r\n\x1a\nhero',
        'extension/images/hero-2x.png': b'\x89PNG\r\n\x1a\nhero2x',
        'extension/images/poster.png': b'\x89PNG\r\n\x1a\nposter',
        'extension/images/bg.png': b'\x89PNG\r\n\x1a\nbg',
        'extension/fonts/ui.woff': b'wOFF',
    }

    if not include_options_bundle:
        text_files.pop('extension/dist/options/main.js')
    if not include_module_dependency:
        text_files.pop('extension/dist/shared/protocol.js')
    if not include_stylesheet:
        text_files.pop('extension/styles/options.css')
    if not include_web_accessible_asset:
        text_files.pop('extension/assets/theme.css')
    if not include_html_media_assets:
        binary_files.pop('extension/images/hero.png')
        binary_files.pop('extension/images/hero-2x.png')
        binary_files.pop('extension/images/poster.png')
    if not include_html_inline_style_asset:
        binary_files.pop('extension/images/bg.png')
    if not include_script_runtime_asset:
        binary_files.pop('extension/images/icon.png')
    if not include_script_worker_asset:
        text_files.pop('extension/dist/workers/helper.js')
    if not include_script_classic_dependency:
        text_files.pop('extension/dist/workers/classic-helper.js')
    if not include_script_relative_worker_asset:
        text_files.pop('extension/dist/workers/relative-worker.js')

    for rel, text in text_files.items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
    for rel, blob in binary_files.items():
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)


def package_and_verify(repo: Path, archive: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    subprocess.run(['bash', str(PACKAGE_SCRIPT), str(repo), str(archive)], check=True, capture_output=True, text=True)
    result = subprocess.run([sys.executable, str(VERIFY_SCRIPT), str(archive)], check=False, capture_output=True, text=True)
    return result, json.loads(result.stdout)




def test_verify_package_flags_extension_version_marker_mismatch(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo)
    (repo / 'extension' / 'package.json').write_text(json.dumps({'name': 'glasstty-extension', 'version': '0.0.2'}, indent=2) + '\n', encoding='utf-8')
    (repo / 'extension' / 'package-lock.json').write_text(json.dumps({'name': 'glasstty-extension', 'version': '0.0.3'}, indent=2) + '\n', encoding='utf-8')
    archive = tmp_path / 'bad-version.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 1
    assert report['extensionVersionMarkers']['manifest_version'] == '0.0.0-test'
    assert report['extensionVersionMarkers']['package_json_version'] == '0.0.2'
    assert report['extensionVersionMarkers']['package_lock_version'] == '0.0.3'
    assert report['extensionVersionMismatches']


def archive_entries(path: Path) -> list[str]:
    import zipfile

    with zipfile.ZipFile(path) as archive:
        return archive.namelist()



def test_package_release_supports_relative_output_path(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo)
    relative_archive = Path('validation') / 'relative.zip'
    result = subprocess.run(
        ['bash', str(PACKAGE_SCRIPT), str(repo), str(relative_archive)],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    archive = repo / relative_archive
    assert archive.exists()
    verify = subprocess.run([sys.executable, str(VERIFY_SCRIPT), str(archive)], check=False, capture_output=True, text=True)
    report = json.loads(verify.stdout)
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert report['ok'] is True


def test_package_release_supports_nested_output_dir_inside_repo_tree(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo)
    out_dir = repo / 'validation' / 'release-artifacts'
    out_dir.mkdir(parents=True)
    (out_dir / 'note.txt').write_text('seed\n', encoding='utf-8')
    archive = out_dir / 'package-check.zip'
    result = subprocess.run(
        ['bash', str(PACKAGE_SCRIPT), str(repo), str(archive)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert archive.exists()
    verify = subprocess.run([sys.executable, str(VERIFY_SCRIPT), str(archive)], check=False, capture_output=True, text=True)
    report = json.loads(verify.stdout)
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert report['ok'] is True


def test_verify_package_passes_for_minimal_good_archive(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo)
    archive = tmp_path / 'good.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 0, result.stdout + result.stderr
    assert report['ok'] is True
    assert report['zip_size_bytes'] == archive.stat().st_size
    assert report['zip_entry_count'] > 0
    assert len(report['zip_sha256']) == 64
    assert report['releaseManifest']['archive_name'] == report['root']
    assert report['releaseManifestMismatches'] == []
    assert 'extension/options/index.html' in report['manifestReferencedFiles']
    assert any(name.endswith('extension/dist/options/main.js') for name in report['htmlReferencedFiles'])
    assert any(name.endswith('extension/styles/options.css') for name in report['htmlReferencedFiles'])
    assert any(name.endswith('extension/images/hero.png') for name in report['htmlReferencedFiles'])
    assert any(name.endswith('extension/images/hero-2x.png') for name in report['htmlReferencedFiles'])
    assert any(name.endswith('extension/images/poster.png') for name in report['htmlReferencedFiles'])
    assert any(name.endswith('extension/images/bg.png') for name in report['htmlReferencedFiles'])
    assert any(name.endswith('extension/assets/theme.css') for name in report['cssReferencedFiles'])
    assert any(name.endswith('extension/fonts/ui.woff') for name in report['cssReferencedFiles'])
    assert any(name.endswith('extension/images/icon.png') for name in report['cssReferencedFiles'])
    assert any(name.endswith('extension/dist/shared/protocol.js') for name in report['moduleReferencedFiles'])
    assert any(name.endswith('extension/images/icon.png') for name in report['scriptAssetReferencedFiles'])
    assert any(name.endswith('extension/dist/workers/helper.js') for name in report['scriptAssetReferencedFiles'])
    assert any(name.endswith('extension/dist/workers/relative-worker.js') for name in report['scriptAssetReferencedFiles'])
    assert any(name.endswith('extension/dist/workers/helper.js') for name in report['moduleReferencedFiles'])
    assert any(name.endswith('extension/dist/workers/relative-worker.js') for name in report['moduleReferencedFiles'])
    assert any(name.endswith('extension/dist/workers/classic-helper.js') for name in report['scriptAssetReferencedFiles'])
    assert any(name.endswith('extension/dist/workers/classic-helper.js') for name in report['moduleReferencedFiles'])
    assert any(check['pattern'] == 'assets/*.css' and check['matchCount'] == 1 for check in report['webAccessibleResourceChecks'])
    assert report['contentScriptCssWebAccessibleMissing'] == []


def test_verify_package_flags_missing_dist_bundle(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo, include_options_bundle=False)
    archive = tmp_path / 'bad.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 1
    assert any(name.endswith('extension/dist/options/main.js') for name in report['missing'])
    assert any(name.endswith('extension/dist/options/main.js') for name in report['htmlReferencedMissing'])


def test_verify_package_flags_missing_module_dependency(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo, include_module_dependency=False)
    archive = tmp_path / 'bad-module.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 1
    assert report['moduleReferencedMissing']
    candidates = '\n'.join('\n'.join(item['candidates']) for item in report['moduleReferencedMissing'])
    assert 'extension/dist/shared/protocol.js' in candidates


def test_verify_package_flags_missing_stylesheet_and_css_asset(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo, include_stylesheet=False, include_web_accessible_asset=False)
    archive = tmp_path / 'bad-assets.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 1
    assert any(name.endswith('extension/styles/options.css') for name in report['htmlReferencedMissing'])
    assert any(item['resolved'].endswith('extension/assets/theme.css') for item in report['cssReferencedMissing'])


def test_verify_package_flags_content_script_css_assets_missing_web_accessible_rules(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo, web_accessible_resources=['assets/*.css'])
    archive = tmp_path / 'bad-war.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 1
    missing_paths = {item['path'] for item in report['contentScriptCssWebAccessibleMissing']}
    assert any(path.endswith('extension/fonts/ui.woff') for path in missing_paths)
    assert any(path.endswith('extension/images/icon.png') for path in missing_paths)


def test_verify_package_flags_missing_html_media_and_inline_style_assets(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo, include_html_media_assets=False, include_html_inline_style_asset=False)
    archive = tmp_path / 'bad-html-assets.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 1
    missing = set(report['htmlReferencedMissing'])
    assert any(path.endswith('extension/images/hero.png') for path in missing)
    assert any(path.endswith('extension/images/hero-2x.png') for path in missing)
    assert any(path.endswith('extension/images/poster.png') for path in missing)


def test_package_release_excludes_validation_binary_blobs_by_default(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo)
    (repo / 'validation' / 'rev9999-focused').mkdir(parents=True, exist_ok=True)
    (repo / 'validation' / 'rev9999-focused' / 'package-check.zip').write_bytes(b'zip-blob')
    (repo / 'validation' / 'rev9999-focused' / 'diff-vs-prev.patch').write_text('patch\n', encoding='utf-8')
    archive = tmp_path / 'slim.zip'

    subprocess.run(['bash', str(PACKAGE_SCRIPT), str(repo), str(archive)], check=True, capture_output=True, text=True)
    names = archive_entries(archive)

    assert not any(name.endswith('validation/rev9999-focused/package-check.zip') for name in names)
    assert not any(name.endswith('validation/rev9999-focused/diff-vs-prev.patch') for name in names)


def test_package_release_can_keep_validation_binary_blobs_when_requested(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo)
    (repo / 'validation' / 'rev9999-focused').mkdir(parents=True, exist_ok=True)
    (repo / 'validation' / 'rev9999-focused' / 'package-check.zip').write_bytes(b'zip-blob')
    archive = tmp_path / 'fat.zip'

    subprocess.run(
        ['bash', str(PACKAGE_SCRIPT), str(repo), str(archive)],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, 'GLASSTTY_PACKAGE_INCLUDE_VALIDATION_BINARIES': '1'},
    )
    names = archive_entries(archive)

    assert any(name.endswith('validation/rev9999-focused/package-check.zip') for name in names)


def test_verify_package_flags_missing_script_runtime_asset_and_worker(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(
        repo,
        include_script_runtime_asset=False,
        include_script_worker_asset=False,
        include_script_classic_dependency=False,
        include_script_relative_worker_asset=False,
    )
    archive = tmp_path / 'bad-script-assets.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 1
    missing = report['scriptAssetReferencedMissing']
    assert any(item['resolved'].endswith('extension/images/icon.png') and item['referenceKind'] == 'runtime.getURL' for item in missing)
    assert any(item['resolved'].endswith('extension/dist/workers/helper.js') and item['referenceKind'] == 'new URL(import.meta.url)' for item in missing)
    assert any(item['resolved'].endswith('extension/dist/workers/relative-worker.js') and item['referenceKind'] == 'new Worker()' for item in missing)


def test_verify_package_flags_missing_importscripts_dependency(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo, include_script_classic_dependency=False)
    archive = tmp_path / 'bad-classic-worker.zip'
    result, report = package_and_verify(repo, archive)
    assert result.returncode == 1
    missing = report['scriptAssetReferencedMissing']
    assert any(item['resolved'].endswith('extension/dist/workers/classic-helper.js') and item['referenceKind'] == 'importScripts' for item in missing)


def test_package_release_uses_output_archive_name_as_zip_root_for_release_names(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev0071-2026.03.16.23.29-nativehostaudit-autotarget-browserfit-lapwing'
    seed_minimal_repo(repo)
    archive_name = 'GlassTTY-rev0073-2026.03.17.00.21-identitytight-packagerename-manifestlock-oystercatcher'
    subprocess.run(
        [
            sys.executable,
            str(REFRESH_SCRIPT),
            '--root',
            str(repo),
            '--archive-name',
            archive_name,
            '--summary',
            'test archive identity',
            '--codename',
            'oystercatcher',
            '--revision',
            '73',
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    archive = tmp_path / f'{archive_name}.zip'
    result = subprocess.run(
        ['bash', str(PACKAGE_SCRIPT), str(repo), str(archive)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    entries = archive_entries(archive)
    assert entries
    assert all(name.startswith(f'{archive_name}/') for name in entries)
    verify = subprocess.run([sys.executable, str(VERIFY_SCRIPT), str(archive)], check=False, capture_output=True, text=True)
    report = json.loads(verify.stdout)
    assert verify.returncode == 0, verify.stdout + verify.stderr
    assert report['root'] == archive_name
    assert report['archiveIdentityMismatches'] == []


def test_verify_package_flags_archive_identity_mismatch(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev0071-2026.03.16.23.29-nativehostaudit-autotarget-browserfit-lapwing'
    seed_minimal_repo(repo)
    archive = tmp_path / 'GlassTTY-rev0071-2026.03.16.23.29-nativehostaudit-autotarget-browserfit-lapwing.zip'
    subprocess.run(['bash', str(PACKAGE_SCRIPT), str(repo), str(archive)], check=True, capture_output=True, text=True)
    with zipfile.ZipFile(archive, 'a') as zf:
        zf.writestr(
            'GlassTTY-rev0071-2026.03.16.23.29-nativehostaudit-autotarget-browserfit-lapwing/ARCHIVE_MANIFEST.json',
            json.dumps(
                {
                    'archive_name': 'GlassTTY-rev0070-2026.03.16.23.10-profileledger-debugport-doctorvisibility-avocet',
                    'archive_revision': 70,
                    'archive_created_at_from_name': '2026.03.16.23.10',
                    'archive_slug': 'profileledger-debugport-doctorvisibility-avocet',
                }
            ),
        )
    verify = subprocess.run([sys.executable, str(VERIFY_SCRIPT), str(archive)], check=False, capture_output=True, text=True)
    report = json.loads(verify.stdout)
    assert verify.returncode == 1
    assert report['archiveIdentityMismatches']
    assert any('archive_name' in item for item in report['archiveIdentityMismatches'])


def test_package_release_embeds_release_manifest(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo)
    archive = tmp_path / 'release-manifest.zip'
    subprocess.run(['bash', str(PACKAGE_SCRIPT), str(repo), str(archive)], check=True, capture_output=True, text=True)
    with zipfile.ZipFile(archive) as zf:
        root = zf.namelist()[0].split('/', 1)[0]
        payload = json.loads(zf.read(f'{root}/RELEASE-MANIFEST.json').decode('utf-8'))
    assert payload['archive_name'] == root
    assert payload['file_count'] >= 1
    relpaths = {item['path'] for item in payload['files']}
    assert 'extension/manifest.json' in relpaths
    assert 'RELEASE-MANIFEST.json' not in relpaths


def test_verify_package_flags_release_manifest_mismatch(tmp_path: Path) -> None:
    repo = tmp_path / 'GlassTTY-rev9999-test'
    seed_minimal_repo(repo)
    archive = tmp_path / 'bad-release-manifest.zip'
    subprocess.run(['bash', str(PACKAGE_SCRIPT), str(repo), str(archive)], check=True, capture_output=True, text=True)
    with zipfile.ZipFile(archive, 'a') as zf:
        root = zf.namelist()[0].split('/', 1)[0]
        manifest = json.loads(zf.read(f'{root}/RELEASE-MANIFEST.json').decode('utf-8'))
        manifest['files'][0]['sha256'] = '0' * 64
        zf.writestr(f'{root}/RELEASE-MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    verify = subprocess.run([sys.executable, str(VERIFY_SCRIPT), str(archive)], check=False, capture_output=True, text=True)
    report = json.loads(verify.stdout)
    assert verify.returncode == 1
    assert report['releaseManifestMismatches']
    assert 'digest/size mismatches' in report['releaseManifestMismatches'][0]
