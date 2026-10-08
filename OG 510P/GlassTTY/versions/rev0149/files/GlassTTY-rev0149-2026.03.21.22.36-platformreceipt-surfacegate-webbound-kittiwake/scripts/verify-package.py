#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import zipfile
from fnmatch import fnmatchcase
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

REQUIRED = [
    'README.md', 'STATUS.md', 'MEMORY.md', 'CHANGELOG.md', 'ARCHIVE_MANIFEST.json',
    'extension/manifest.json',
    'extension/options/index.html', 'extension/sidepanel/index.html', 'extension/probe/index.html', 'extension/offscreen/index.html',
    'extension/dist/background/main.js', 'extension/dist/content/main.js',
    'extension/dist/options/main.js', 'extension/dist/probe/main.js', 'extension/dist/offscreen/main.js',
    'extension/dist/sidepanel/main.js', 'daemon/src/glassttyd/cli.py',
    'fixtures/corpus/claude-synthetic-thread.json',
]
FORBIDDEN_SUBSTRINGS = ['/__pycache__/', '/.pytest_cache/', '/node_modules/', '/.venv/']
FORBIDDEN_SUFFIXES = ['.pyc', '.pyo', '.DS_Store']
MODULE_IMPORT_RE = re.compile(
    r'''(?:import|export)\s+(?:[^\"']+?\s+from\s+)?[\"']([^\"']+)[\"']|import\(\s*[\"']([^\"']+)[\"']\s*\)''',
    re.MULTILINE,
)
CSS_URL_RE = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", re.IGNORECASE)
CSS_IMPORT_RE = re.compile(r"@import\s+(?:url\(\s*)?(['\"]?)([^'\")\s;]+)\1\s*\)?", re.IGNORECASE)
RUNTIME_GET_URL_RE = re.compile(r"(?:chrome|browser)\.runtime\.getURL\(\s*['\"]([^'\"]+)['\"]\s*\)")
IMPORT_META_URL_RE = re.compile(r"new\s+URL\(\s*['\"]([^'\"]+)['\"]\s*,\s*import\.meta\.url\s*\)")
IMPORT_SCRIPTS_CALL_RE = re.compile(r"\bimportScripts\s*\(([^)]*)\)", re.MULTILINE)
WORKER_CONSTRUCTOR_RE = re.compile(r"new\s+(SharedWorker|Worker)\s*\(\s*['\"]([^'\"]+)['\"]")
STRING_LITERAL_RE = re.compile(r"['\"]([^'\"]+)['\"]")
LINKED_REL_TOKENS = {
    'stylesheet',
    'preload',
    'modulepreload',
    'icon',
    'manifest',
    'apple-touch-icon',
    'shortcut',
}
HTML_URL_ATTRS = {
    'audio': ('src',),
    'embed': ('src',),
    'iframe': ('src',),
    'img': ('src',),
    'input': ('src',),
    'object': ('data',),
    'script': ('src',),
    'source': ('src',),
    'track': ('src',),
    'video': ('src', 'poster'),
}
HTML_SRCSET_ATTRS = {
    'img': ('srcset',),
    'source': ('srcset',),
}
ARCHIVE_NAME_RE = re.compile(r'^GlassTTY-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<slug>.+)$')

JsonDict = dict[str, Any]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()




def sha256_zip_entry(archive: zipfile.ZipFile, path: str) -> str:
    digest = hashlib.sha256()
    with archive.open(path) as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()



def release_manifest_issues(archive: zipfile.ZipFile, names: list[str], names_set: set[str], *, root: str) -> tuple[JsonDict, list[str]]:
    manifest_path = f'{root}/RELEASE-MANIFEST.json'
    info: JsonDict = {'present': manifest_path in names_set}
    issues: list[str] = []
    if manifest_path not in names_set:
        issues.append('RELEASE-MANIFEST.json missing from packaged archive')
        return info, issues
    manifest = load_zip_json(archive, manifest_path)
    info['archive_name'] = manifest.get('archive_name')
    info['file_count'] = manifest.get('file_count')
    if manifest.get('archive_name') != root:
        issues.append(f'RELEASE-MANIFEST archive_name {manifest.get("archive_name")!r} does not match package root {root!r}')
    files = manifest.get('files')
    if not isinstance(files, list):
        issues.append('RELEASE-MANIFEST files must be a list')
        files = []
    manifest_entries = [item for item in files if isinstance(item, dict) and isinstance(item.get('path'), str)]
    manifest_relpaths = sorted(item['path'] for item in manifest_entries)
    actual_entries = sorted(
        name[len(root) + 1:]
        for name in names
        if name.startswith(f'{root}/') and not name.endswith('/') and name != manifest_path
    )
    if manifest_relpaths != actual_entries:
        missing = [item for item in actual_entries if item not in manifest_relpaths]
        extra = [item for item in manifest_relpaths if item not in actual_entries]
        if missing:
            issues.append(f'RELEASE-MANIFEST is missing packaged files: {missing}')
        if extra:
            issues.append(f'RELEASE-MANIFEST lists non-packaged files: {extra}')
    mismatches: list[JsonDict] = []
    for item in manifest_entries:
        rel = item['path']
        archive_path = f'{root}/{rel}'
        if archive_path not in names_set:
            continue
        archive_info = archive.getinfo(archive_path)
        expected_size = item.get('size')
        expected_sha = item.get('sha256')
        actual_size = archive_info.file_size
        actual_sha = sha256_zip_entry(archive, archive_path)
        if expected_size != actual_size or expected_sha != actual_sha:
            mismatches.append({
                'path': rel,
                'expected_size': expected_size,
                'actual_size': actual_size,
                'expected_sha256': expected_sha,
                'actual_sha256': actual_sha,
            })
    if mismatches:
        issues.append(f'RELEASE-MANIFEST file digest/size mismatches: {[item["path"] for item in mismatches]}')
    info['verified_file_count'] = len(manifest_entries)
    info['mismatches'] = mismatches
    return info, issues




def parse_archive_name(value: str) -> dict[str, Any]:
    match = ARCHIVE_NAME_RE.match(value)
    info: dict[str, Any] = {'archive_name': value, 'matches_pattern': bool(match)}
    if not match:
        return info
    info['archive_revision'] = int(match.group('revision'))
    info['archive_created_at_from_name'] = match.group('stamp')
    info['archive_slug'] = match.group('slug')
    return info


def infer_zip_root(names: list[str]) -> tuple[str | None, list[str], list[str]]:
    root_candidates = sorted({name.rstrip('/').split('/', 1)[0] for name in names if name.rstrip('/')})
    issues: list[str] = []
    if not root_candidates:
        return None, root_candidates, ['archive has no entries']
    if len(root_candidates) != 1:
        issues.append(f'archive must contain exactly one top-level root directory, found {root_candidates}')
    root = root_candidates[0]
    if root in names:
        issues.append(f'top-level root {root!r} is stored as a file, not just a directory prefix')
    return root, root_candidates, issues


def archive_identity_issues(manifest: JsonDict | None, *, root: str) -> tuple[dict[str, Any], list[str]]:
    root_info = parse_archive_name(root)
    manifest_info: dict[str, Any] = {'root': root_info}
    issues: list[str] = []
    if not manifest:
        if root_info.get('matches_pattern'):
            issues.append('ARCHIVE_MANIFEST.json could not be loaded for archive-shaped package root')
        return manifest_info, issues

    archive_name = manifest.get('archive_name')
    manifest_info['archive_name'] = archive_name
    if isinstance(archive_name, str):
        manifest_name_info = parse_archive_name(archive_name)
        manifest_info['parsed_archive_name'] = manifest_name_info
        if archive_name != root:
            issues.append(f'ARCHIVE_MANIFEST archive_name {archive_name!r} does not match package root {root!r}')
    elif root_info.get('matches_pattern'):
        issues.append('ARCHIVE_MANIFEST archive_name missing or not a string for archive-shaped package root')

    for key in ('archive_revision', 'archive_created_at_from_name', 'archive_slug'):
        actual = manifest.get(key)
        if key in manifest:
            manifest_info[key] = actual
        expected = root_info.get(key)
        if expected is not None and actual is not None and actual != expected:
            issues.append(f'ARCHIVE_MANIFEST {key} {actual!r} does not match root-derived {expected!r}')
    return manifest_info, issues

def parse_srcset_candidates(value: str) -> list[str]:
    candidates: list[str] = []
    for item in value.split(','):
        candidate = item.strip()
        if not candidate:
            continue
        url = candidate.split()[0]
        if url:
            candidates.append(url)
    return candidates


class ExtensionHtmlAssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.css_refs: list[str] = []
        self._style_depth = 0

    def _record_style_refs(self, value: str | None) -> None:
        if not value:
            return
        self.css_refs.extend(raw_ref for _kind, raw_ref in css_reference_tokens(value))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value for key, value in attrs}
        tag = tag.lower()
        self._record_style_refs(attr_map.get('style'))
        if tag == 'style':
            self._style_depth += 1
        if tag == 'link':
            href = attr_map.get('href')
            if href:
                rel_tokens = {token.lower() for token in (attr_map.get('rel') or '').split() if token.strip()}
                if not rel_tokens or rel_tokens & LINKED_REL_TOKENS:
                    self.refs.append(href)
        for attr_name in HTML_URL_ATTRS.get(tag, ()): 
            value = attr_map.get(attr_name)
            if not value:
                continue
            if tag == 'input' and attr_name == 'src' and (attr_map.get('type') or '').lower() != 'image':
                continue
            self.refs.append(value)
        for attr_name in HTML_SRCSET_ATTRS.get(tag, ()): 
            value = attr_map.get(attr_name)
            if value:
                self.refs.extend(parse_srcset_candidates(value))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() == 'style' and self._style_depth:
            self._style_depth -= 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == 'style' and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._style_depth:
            self._record_style_refs(data)



def load_zip_json(archive: zipfile.ZipFile, path: str) -> JsonDict:
    with archive.open(path) as fh:
        data = json.loads(fh.read().decode('utf-8'))
    if not isinstance(data, dict):
        raise ValueError(f'{path} is not a JSON object')
    return data



def extension_version_markers(archive: zipfile.ZipFile, names_set: set[str], *, root: str, manifest: JsonDict | None) -> tuple[JsonDict, list[str]]:
    markers: JsonDict = {
        'manifest_version': manifest.get('version') if isinstance(manifest, dict) else None,
        'package_json_version': None,
        'package_lock_version': None,
    }
    package_json_path = f'{root}/extension/package.json'
    package_lock_path = f'{root}/extension/package-lock.json'
    if package_json_path in names_set:
        package_json = load_zip_json(archive, package_json_path)
        markers['package_json_version'] = package_json.get('version')
    if package_lock_path in names_set:
        package_lock = load_zip_json(archive, package_lock_path)
        markers['package_lock_version'] = package_lock.get('version')
    populated = {str(value) for value in markers.values() if isinstance(value, str) and value.strip()}
    issues: list[str] = []
    if len(populated) > 1:
        issues.append('extension version markers disagree across manifest/package.json/package-lock.json')
    return markers, issues



def load_zip_text(archive: zipfile.ZipFile, path: str) -> str:
    with archive.open(path) as fh:
        return fh.read().decode('utf-8')



def strip_ref_suffix(ref: str) -> str:
    return ref.split('#', 1)[0].split('?', 1)[0]



def normalize_relpath(base_dir: str, ref: str) -> str | None:
    ref = strip_ref_suffix(ref.strip())
    if not ref or ref.startswith(('http://', 'https://', 'chrome-extension://', 'data:', 'mailto:', '#', '//')):
        return None
    base_parts = [part for part in base_dir.split('/') if part]
    if ref.startswith('/'):
        parts: list[str] = []
        ref_parts = [part for part in ref.split('/') if part]
    else:
        parts = base_parts[:]
        ref_parts = [part for part in ref.split('/') if part]
    for part in ref_parts:
        if part == '.':
            continue
        if part == '..':
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return '/'.join(parts)



def normalize_root_relative(ref: Any) -> str | None:
    if not isinstance(ref, str):
        return None
    return normalize_relpath('', ref)



def _add_ref(refs: set[str], path: str | None) -> None:
    if path:
        refs.add(f'extension/{path}')



def _add_icon_refs(refs: set[str], value: Any) -> None:
    if isinstance(value, str):
        _add_ref(refs, normalize_root_relative(value))
        return
    if isinstance(value, dict):
        for candidate in value.values():
            if isinstance(candidate, str):
                _add_ref(refs, normalize_root_relative(candidate))



def manifest_references(manifest: JsonDict) -> set[str]:
    refs: set[str] = set()
    background = manifest.get('background')
    if isinstance(background, dict):
        worker = background.get('service_worker')
        if isinstance(worker, str) and worker.strip():
            refs.add(f"extension/{worker.strip().lstrip('/')}" )
    options_page = manifest.get('options_page')
    if isinstance(options_page, str) and options_page.strip():
        refs.add(f"extension/{options_page.strip().lstrip('/')}" )
    side_panel = manifest.get('side_panel')
    if isinstance(side_panel, dict):
        default_path = side_panel.get('default_path')
        if isinstance(default_path, str) and default_path.strip():
            refs.add(f"extension/{default_path.strip().lstrip('/')}" )
    action = manifest.get('action')
    if isinstance(action, dict):
        popup = action.get('default_popup')
        if isinstance(popup, str) and popup.strip():
            refs.add(f"extension/{popup.strip().lstrip('/')}" )
        _add_icon_refs(refs, action.get('default_icon'))
    _add_icon_refs(refs, manifest.get('icons'))
    devtools_page = manifest.get('devtools_page')
    if isinstance(devtools_page, str) and devtools_page.strip():
        refs.add(f"extension/{devtools_page.strip().lstrip('/')}" )
    chrome_url_overrides = manifest.get('chrome_url_overrides')
    if isinstance(chrome_url_overrides, dict):
        for candidate in chrome_url_overrides.values():
            if isinstance(candidate, str) and candidate.strip():
                refs.add(f"extension/{candidate.strip().lstrip('/')}" )
    sandbox = manifest.get('sandbox')
    if isinstance(sandbox, dict):
        for candidate in sandbox.get('pages') or []:
            if isinstance(candidate, str) and candidate.strip():
                refs.add(f"extension/{candidate.strip().lstrip('/')}" )
    for script in manifest.get('content_scripts') or []:
        if not isinstance(script, dict):
            continue
        for key in ('js', 'css'):
            for rel in script.get(key) or []:
                if isinstance(rel, str) and rel.strip():
                    refs.add(f"extension/{rel.strip().lstrip('/')}" )
    return refs



def web_accessible_rules(manifest: JsonDict) -> list[JsonDict]:
    rules: list[JsonDict] = []
    for index, entry in enumerate(manifest.get('web_accessible_resources') or []):
        if not isinstance(entry, dict):
            continue
        resources = [
            normalized
            for resource in entry.get('resources') or []
            if isinstance(resource, str)
            for normalized in [normalize_root_relative(resource)]
            if normalized
        ]
        rules.append({
            'index': index,
            'resources': resources,
            'matches': [candidate for candidate in entry.get('matches') or [] if isinstance(candidate, str)],
            'extension_ids': [candidate for candidate in entry.get('extension_ids') or [] if isinstance(candidate, str)],
            'use_dynamic_url': entry.get('use_dynamic_url') is True,
        })
    return rules



def html_asset_references(archive: zipfile.ZipFile, names: set[str], html_paths: set[str], *, extension_root: str) -> set[str]:
    refs: set[str] = set()
    for html_path in html_paths:
        if html_path not in names or not html_path.startswith(extension_root + '/'):
            continue
        web_path = html_path[len(extension_root) + 1:]
        base_dir = posixpath.dirname(web_path)
        parser = ExtensionHtmlAssetParser()
        parser.feed(load_zip_text(archive, html_path))
        for raw_ref in parser.refs:
            normalized = normalize_relpath(base_dir, raw_ref)
            if normalized:
                refs.add(f'{extension_root}/{normalized}')
        for raw_ref in parser.css_refs:
            normalized = normalize_css_ref(base_dir, raw_ref)
            if normalized:
                refs.add(f'{extension_root}/{normalized}')
    return refs



def normalize_css_ref(base_dir: str, ref: str) -> str | None:
    ref = ref.strip()
    if not ref:
        return None
    if ref.startswith('chrome-extension://'):
        parsed = urlsplit(ref)
        path = parsed.path or ''
        return normalize_relpath('', path)
    if ref.startswith(('http://', 'https://', 'data:', 'blob:', 'about:', 'javascript:', '#', '//')):
        return None
    return normalize_relpath(base_dir, ref)



def css_reference_tokens(text: str) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for match in CSS_IMPORT_RE.finditer(text):
        refs.append(('import', match.group(2)))
    for match in CSS_URL_RE.finditer(text):
        refs.append(('url', match.group(2)))
    return refs



def css_graph_references(archive: zipfile.ZipFile, names: set[str], entry_paths: set[str], *, extension_root: str) -> tuple[set[str], list[JsonDict]]:
    css_paths = {path for path in entry_paths if path.startswith(extension_root + '/') and path.endswith('.css')}
    discovered: set[str] = set()
    refs: set[str] = set()
    missing: list[JsonDict] = []
    queue = sorted(css_paths)
    while queue:
        css_path = queue.pop(0)
        if css_path in discovered or css_path not in names:
            continue
        discovered.add(css_path)
        web_path = css_path[len(extension_root) + 1:]
        base_dir = posixpath.dirname(web_path)
        text = load_zip_text(archive, css_path)
        for kind, raw_ref in css_reference_tokens(text):
            normalized = normalize_css_ref(base_dir, raw_ref)
            if not normalized:
                continue
            resolved = f'{extension_root}/{normalized}'
            refs.add(resolved)
            if resolved not in names:
                missing.append({
                    'importer': css_path,
                    'referenceKind': kind,
                    'reference': raw_ref,
                    'resolved': resolved,
                })
                continue
            if resolved.endswith('.css') and resolved not in discovered:
                queue.append(resolved)
    return refs, missing



def content_script_css_paths(manifest: JsonDict) -> set[str]:
    refs: set[str] = set()
    for script in manifest.get('content_scripts') or []:
        if not isinstance(script, dict):
            continue
        for rel in script.get('css') or []:
            if isinstance(rel, str) and rel.strip():
                refs.add(f"extension/{rel.strip().lstrip('/')}")
    return refs



def matching_web_accessible_patterns(rel_path: str, rules: list[JsonDict]) -> list[str]:
    return [pattern for rule in rules for pattern in rule['resources'] if fnmatchcase(rel_path, pattern)]



def content_script_css_web_accessible_checks(paths: set[str], *, root: str, rules: list[JsonDict]) -> tuple[list[JsonDict], list[JsonDict]]:
    checks: list[JsonDict] = []
    missing: list[JsonDict] = []
    for path in sorted(paths):
        if not path.startswith(f'{root}/extension/'):
            continue
        rel = path[len(root) + len('/extension/'):]
        matched = matching_web_accessible_patterns(rel, rules)
        record = {
            'path': path,
            'matchedPatterns': matched,
            'matchCount': len(matched),
        }
        checks.append(record)
        if not matched:
            missing.append(record)
    return checks, missing



def module_resolution_candidates(base_dir: str, specifier: str) -> list[str]:
    normalized = normalize_relpath(base_dir, specifier)
    if not normalized:
        return []
    if normalized.endswith(('.js', '.mjs', '.json')):
        return [normalized]
    return [
        normalized,
        f'{normalized}.js',
        f'{normalized}.mjs',
        f'{normalized}/index.js',
        f'{normalized}/index.mjs',
    ]



def script_asset_reference_tokens(text: str) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for match in RUNTIME_GET_URL_RE.finditer(text):
        refs.append(('runtime.getURL', match.group(1)))
    for match in IMPORT_META_URL_RE.finditer(text):
        refs.append(('new URL(import.meta.url)', match.group(1)))
    for match in IMPORT_SCRIPTS_CALL_RE.finditer(text):
        for literal in STRING_LITERAL_RE.finditer(match.group(1)):
            refs.append(('importScripts', literal.group(1)))
    for match in WORKER_CONSTRUCTOR_RE.finditer(text):
        refs.append((f'new {match.group(1)}()', match.group(2)))
    return refs



def script_graph_references(archive: zipfile.ZipFile, names: set[str], entry_paths: set[str], *, extension_root: str) -> tuple[set[str], list[JsonDict], set[str], list[JsonDict], set[str]]:
    module_paths = {path for path in entry_paths if path.startswith(extension_root + '/') and path.endswith(('.js', '.mjs'))}
    discovered: set[str] = set()
    missing_modules: list[JsonDict] = []
    asset_refs: set[str] = set()
    missing_assets: list[JsonDict] = []
    css_entry_paths: set[str] = set()
    queue = sorted(module_paths)
    while queue:
        module_path = queue.pop(0)
        if module_path in discovered or module_path not in names:
            continue
        discovered.add(module_path)
        web_path = module_path[len(extension_root) + 1:]
        base_dir = posixpath.dirname(web_path)
        text = load_zip_text(archive, module_path)
        for match in MODULE_IMPORT_RE.finditer(text):
            specifier = match.group(1) or match.group(2)
            if not specifier or specifier.startswith(('http://', 'https://', 'data:', 'chrome-extension://')):
                continue
            candidates = module_resolution_candidates(base_dir, specifier)
            if not candidates:
                continue
            resolved = next((f'{extension_root}/{candidate}' for candidate in candidates if f'{extension_root}/{candidate}' in names), None)
            if resolved:
                if resolved not in discovered:
                    queue.append(resolved)
                continue
            missing_modules.append({
                'importer': module_path,
                'specifier': specifier,
                'candidates': [f'{extension_root}/{candidate}' for candidate in candidates],
            })
        for kind, raw_ref in script_asset_reference_tokens(text):
            if kind == 'runtime.getURL':
                normalized = normalize_root_relative(raw_ref)
            else:
                normalized = normalize_relpath(base_dir, raw_ref)
            if not normalized:
                continue
            resolved = f'{extension_root}/{normalized}'
            asset_refs.add(resolved)
            if resolved not in names:
                missing_assets.append({
                    'importer': module_path,
                    'referenceKind': kind,
                    'reference': raw_ref,
                    'resolved': resolved,
                })
                continue
            if resolved.endswith(('.js', '.mjs')) and resolved not in discovered:
                queue.append(resolved)
            if resolved.endswith('.css'):
                css_entry_paths.add(resolved)
    return discovered, missing_modules, asset_refs, missing_assets, css_entry_paths



def web_accessible_matches(names: set[str], *, root: str, rules: list[JsonDict]) -> tuple[list[JsonDict], list[JsonDict]]:
    extension_files = sorted(
        name[len(root) + len('/extension/'):]
        for name in names
        if name.startswith(f'{root}/extension/') and not name.endswith('/')
    )
    matched: list[JsonDict] = []
    missing: list[JsonDict] = []
    for rule in rules:
        for pattern in rule['resources']:
            pattern_matches = [f'{root}/extension/{rel}' for rel in extension_files if fnmatchcase(rel, pattern)]
            record = {
                'ruleIndex': rule['index'],
                'pattern': pattern,
                'matchCount': len(pattern_matches),
                'matches': pattern_matches,
            }
            matched.append(record)
            if not pattern_matches:
                missing.append(record)
    return matched, missing



def main() -> None:
    parser = argparse.ArgumentParser(description='Verify that a packaged GlassTTY zip includes critical runtime files and excludes common cache junk.')
    parser.add_argument('zip_path')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        names_set = set(names)

        root, root_candidates, root_issues = infer_zip_root(names)
        if not root:
            raise SystemExit(f'could not infer archive root from {zip_path}')

        missing = [f'{root}/{rel}' for rel in REQUIRED if f'{root}/{rel}' not in names_set]
        forbidden = [name for name in names if any(token in name for token in FORBIDDEN_SUBSTRINGS) or any(name.endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)]

        manifest_path = f'{root}/extension/manifest.json'
        archive_manifest_path = f'{root}/ARCHIVE_MANIFEST.json'
        manifest: JsonDict | None = None
        archive_manifest: JsonDict | None = None
        release_manifest_info: JsonDict = {}
        release_manifest_mismatches: list[str] = []
        manifest_refs_missing: list[str] = []
        html_refs_missing: list[str] = []
        manifest_refs: list[str] = []
        html_refs: list[str] = []
        css_refs: list[str] = []
        css_refs_missing: list[JsonDict] = []
        module_refs: list[str] = []
        module_refs_missing: list[JsonDict] = []
        script_asset_refs: list[str] = []
        script_asset_refs_missing: list[JsonDict] = []
        web_accessible_rule_records: list[JsonDict] = []
        web_accessible_missing: list[JsonDict] = []
        content_script_css_accessible_checks: list[JsonDict] = []
        content_script_css_accessible_missing: list[JsonDict] = []
        extension_version_info: JsonDict = {}
        extension_version_mismatches: list[str] = []
        if archive_manifest_path in names_set:
            archive_manifest = load_zip_json(archive, archive_manifest_path)
        archive_identity, archive_identity_mismatches = archive_identity_issues(archive_manifest, root=root)
        release_manifest_info, release_manifest_mismatches = release_manifest_issues(archive, names, names_set, root=root)
        if manifest_path in names_set:
            manifest = load_zip_json(archive, manifest_path)
            manifest_refs = sorted(manifest_references(manifest))
            manifest_refs_missing = [f'{root}/{rel}' for rel in manifest_refs if f'{root}/{rel}' not in names_set]
            html_paths = {f'{root}/extension/options/index.html', f'{root}/extension/sidepanel/index.html', f'{root}/extension/probe/index.html', f'{root}/extension/offscreen/index.html'}
            html_paths.update(
                path for path in (f'{root}/{rel}' for rel in manifest_refs)
                if path.endswith('.html')
            )
            html_refs = sorted(html_asset_references(archive, names_set, html_paths, extension_root=f'{root}/extension'))
            html_refs_missing = [rel for rel in html_refs if rel not in names_set]
            css_entry_paths = {path for path in ({f'{root}/{rel}' for rel in manifest_refs} | set(html_refs)) if path.endswith('.css')}
            module_entry_paths = {path for path in ({f'{root}/{rel}' for rel in manifest_refs} | set(html_refs)) if path.endswith(('.js', '.mjs'))}
            module_ref_set, module_refs_missing, script_asset_ref_set, script_asset_refs_missing, js_css_entry_paths = script_graph_references(archive, names_set, module_entry_paths, extension_root=f'{root}/extension')
            module_refs = sorted(module_ref_set)
            script_asset_refs = sorted(script_asset_ref_set)
            css_ref_set, css_refs_missing = css_graph_references(archive, names_set, css_entry_paths | js_css_entry_paths, extension_root=f'{root}/extension')
            css_refs = sorted(css_ref_set)
            web_accessible_ruleset = web_accessible_rules(manifest)
            web_accessible_rule_records, web_accessible_missing = web_accessible_matches(names_set, root=root, rules=web_accessible_ruleset)
            content_css_entry_paths = {f'{root}/{rel}' for rel in content_script_css_paths(manifest)}
            content_css_ref_set, _ = css_graph_references(archive, names_set, content_css_entry_paths, extension_root=f'{root}/extension')
            existing_content_css_refs = {path for path in content_css_ref_set if path in names_set}
            content_script_css_accessible_checks, content_script_css_accessible_missing = content_script_css_web_accessible_checks(existing_content_css_refs, root=root, rules=web_accessible_ruleset)
            extension_version_info, extension_version_mismatches = extension_version_markers(archive, names_set, root=root, manifest=manifest)

    report = {
        'ok': not root_issues and not archive_identity_mismatches and not release_manifest_mismatches and not missing and not forbidden and not manifest_refs_missing and not html_refs_missing and not css_refs_missing and not module_refs_missing and not script_asset_refs_missing and not web_accessible_missing and not content_script_css_accessible_missing and not extension_version_mismatches,
        'zip_path': str(zip_path),
        'zip_size_bytes': zip_path.stat().st_size,
        'zip_sha256': sha256_file(zip_path),
        'zip_entry_count': len(names),
        'root': root,
        'rootCandidates': root_candidates,
        'rootIssues': root_issues,
        'archiveIdentity': archive_identity,
        'archiveIdentityMismatches': archive_identity_mismatches,
        'releaseManifest': release_manifest_info,
        'releaseManifestMismatches': release_manifest_mismatches,
        'missing': missing,
        'forbidden': forbidden,
        'required_count': len(REQUIRED),
        'manifestReferencedFiles': manifest_refs,
        'manifestReferencedMissing': manifest_refs_missing,
        'htmlReferencedFiles': sorted(html_refs),
        'htmlReferencedMissing': html_refs_missing,
        'cssReferencedFiles': css_refs,
        'cssReferencedMissing': css_refs_missing,
        'moduleReferencedFiles': module_refs,
        'moduleReferencedMissing': module_refs_missing,
        'scriptAssetReferencedFiles': script_asset_refs,
        'scriptAssetReferencedMissing': script_asset_refs_missing,
        'webAccessibleResourceChecks': web_accessible_rule_records,
        'webAccessibleResourceMissing': web_accessible_missing,
        'contentScriptCssWebAccessibleChecks': content_script_css_accessible_checks,
        'contentScriptCssWebAccessibleMissing': content_script_css_accessible_missing,
        'extensionVersionMarkers': extension_version_info,
        'extensionVersionMismatches': extension_version_mismatches,
    }
    print(json.dumps(report, indent=2 if args.pretty else None))
    raise SystemExit(0 if report['ok'] else 1)


if __name__ == '__main__':
    main()
