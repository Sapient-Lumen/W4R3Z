from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

DEFAULT_CFT_CATALOG_URL = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json'
DEFAULT_CFT_VERSION_URL_TEMPLATE = 'https://googlechromelabs.github.io/chrome-for-testing/{version}.json'
CFT_NATIVE_MESSAGING_SPLIT_MAJOR = 146


CFT_BINARY_EXECUTABLES = {
    'chrome': {
        'linux64': Path('chrome-linux64/chrome'),
        'mac-arm64': Path('chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'),
        'mac-x64': Path('chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'),
        'win32': Path('chrome-win32/chrome.exe'),
        'win64': Path('chrome-win64/chrome.exe'),
    },
    'chromedriver': {
        'linux64': Path('chromedriver-linux64/chromedriver'),
        'mac-arm64': Path('chromedriver-mac-arm64/chromedriver'),
        'mac-x64': Path('chromedriver-mac-x64/chromedriver'),
        'win32': Path('chromedriver-win32/chromedriver.exe'),
        'win64': Path('chromedriver-win64/chromedriver.exe'),
    },
    'chrome-headless-shell': {
        'linux64': Path('chrome-headless-shell-linux64/chrome-headless-shell'),
        'mac-arm64': Path('chrome-headless-shell-mac-arm64/chrome-headless-shell'),
        'mac-x64': Path('chrome-headless-shell-mac-x64/chrome-headless-shell'),
        'win32': Path('chrome-headless-shell-win32/chrome-headless-shell.exe'),
        'win64': Path('chrome-headless-shell-win64/chrome-headless-shell.exe'),
    },
}


class ChromeForTestingError(RuntimeError):
    pass


def normalize_channel(channel: str) -> str:
    value = channel.strip().lower()
    mapping = {'stable': 'Stable', 'beta': 'Beta', 'dev': 'Dev', 'canary': 'Canary'}
    if value not in mapping:
        raise ChromeForTestingError(f'unsupported Chrome for Testing channel: {channel}')
    return mapping[value]


def detect_cft_platform(system: str | None = None, machine: str | None = None) -> str:
    system = (system or sys.platform).lower()
    machine = (machine or os.uname().machine if hasattr(os, 'uname') else '').lower()
    if system.startswith('linux'):
        return 'linux64'
    if system == 'darwin':
        return 'mac-arm64' if machine in {'arm64', 'aarch64'} else 'mac-x64'
    if system in {'win32', 'cygwin', 'msys'}:
        return 'win64' if '64' in machine else 'win32'
    raise ChromeForTestingError(f'unsupported platform for Chrome for Testing: system={system!r} machine={machine!r}')


def cft_root(env: dict[str, str] | None = None) -> Path:
    env = env or os.environ
    explicit = env.get('GLASSTTY_BROWSER_HOME')
    if explicit:
        return Path(explicit).expanduser()
    glasstty_home = Path(env.get('GLASSTTY_HOME', str(Path.home() / '.local' / 'share' / 'glasstty'))).expanduser()
    return glasstty_home / 'browsers' / 'chrome-for-testing'


def executable_relpath(binary: str, platform: str) -> Path:
    try:
        return CFT_BINARY_EXECUTABLES[binary][platform]
    except KeyError as exc:
        raise ChromeForTestingError(f'unsupported Chrome for Testing binary/platform combination: {binary} on {platform}') from exc


def version_key(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for token in version.split('.'):
        try:
            parts.append(int(token))
        except ValueError:
            parts.append(-1)
    return tuple(parts)


def major_version(version: str | None) -> int | None:
    if not version:
        return None
    token = version.split('.', 1)[0]
    try:
        return int(token)
    except ValueError:
        return None


def infer_browser_family(path: str | os.PathLike[str] | None, *, source: str | None = None) -> str | None:
    if source == 'chrome-for-testing':
        return 'chrome-for-testing'
    if not path:
        return None
    candidate = Path(path)
    lowered_parts = [part.lower() for part in candidate.parts]
    joined = '/'.join(lowered_parts)
    name = candidate.name.lower()
    cft_markers = {
        'chrome-linux64',
        'chrome-mac-arm64',
        'chrome-mac-x64',
        'chrome-win32',
        'chrome-win64',
    }
    if 'chrome-for-testing' in joined or 'google chrome for testing.app' in joined or any(marker in lowered_parts for marker in cft_markers):
        return 'chrome-for-testing'
    if 'chromium' in name or '/chromium/' in joined:
        return 'chromium'
    if 'google-chrome' in name or name == 'chrome' or 'google/chrome' in joined:
        return 'chrome'
    return None


def infer_cft_version_from_path(path: str | os.PathLike[str] | None) -> str | None:
    if not path:
        return None
    candidate = Path(path)
    for parent in candidate.parents:
        if parent.name and parent.name[0].isdigit() and '.' in parent.name:
            return parent.name
    return None


def native_messaging_targets(browser_family: str | None, *, version: str | None = None) -> list[str]:
    if browser_family == 'chromium':
        return ['chromium']
    if browser_family == 'chrome':
        return ['chrome']
    if browser_family == 'chrome-for-testing':
        major = major_version(version)
        if major is None:
            return ['chrome', 'chrome-for-testing']
        if major < CFT_NATIVE_MESSAGING_SPLIT_MAJOR:
            return ['chrome']
        return ['chrome-for-testing']
    return []


def native_messaging_notes(browser_family: str | None, *, version: str | None = None) -> list[str]:
    notes: list[str] = []
    if browser_family == 'chrome-for-testing':
        major = major_version(version)
        if major is None:
            notes.append('Chrome for Testing version is unknown; install both Chrome and Chrome-for-Testing native-host manifests to be safe.')
        elif major < CFT_NATIVE_MESSAGING_SPLIT_MAJOR:
            notes.append(f'Chrome for Testing {version} still uses Google Chrome native-messaging locations until Chrome {CFT_NATIVE_MESSAGING_SPLIT_MAJOR}.')
        else:
            notes.append(f'Chrome for Testing {version} uses dedicated chrome-for-testing native-messaging locations in Chrome {CFT_NATIVE_MESSAGING_SPLIT_MAJOR}+.')
    return notes


def augment_browser_choice(choice: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(choice)
    family = enriched.get('browser_family') or infer_browser_family(enriched.get('path'), source=enriched.get('source'))
    version = enriched.get('version')
    if family == 'chrome-for-testing' and not version:
        version = infer_cft_version_from_path(enriched.get('path'))
    targets = native_messaging_targets(family, version=version)
    enriched['browser_family'] = family
    enriched['version'] = version
    enriched['native_messaging_targets'] = targets
    enriched['native_messaging_primary_target'] = targets[0] if targets else None
    enriched['native_messaging_notes'] = native_messaging_notes(family, version=version)
    return enriched


def local_cft_installations(*, binary: str = 'chrome', platform: str | None = None, root: Path | None = None, env: dict[str, str] | None = None) -> list[dict[str, Any]]:
    platform = platform or detect_cft_platform()
    root = (root or cft_root(env)).expanduser()
    rel = executable_relpath(binary, platform)
    installs: list[dict[str, Any]] = []
    if not root.exists():
        return installs
    for candidate in sorted(root.iterdir(), key=lambda item: version_key(item.name), reverse=True):
        if not candidate.is_dir():
            continue
        executable = candidate / rel
        if executable.exists():
            installs.append({
                'version': candidate.name,
                'binary': binary,
                'platform': platform,
                'root': str(root),
                'install_dir': str(candidate),
                'executable': str(executable),
                'exists': True,
            })
    return installs


def latest_local_cft_install(*, binary: str = 'chrome', platform: str | None = None, root: Path | None = None, env: dict[str, str] | None = None) -> dict[str, Any] | None:
    installs = local_cft_installations(binary=binary, platform=platform, root=root, env=env)
    return installs[0] if installs else None


def fetch_json(url: str, timeout: float = 20.0) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode('utf-8'))


def fetch_cft_catalog(*, url: str = DEFAULT_CFT_CATALOG_URL, timeout: float = 20.0) -> dict[str, Any]:
    payload = fetch_json(url, timeout=timeout)
    if not isinstance(payload, dict):
        raise ChromeForTestingError(f'unexpected Chrome for Testing catalog payload from {url}')
    return payload


def fetch_cft_version_manifest(version: str, *, timeout: float = 20.0, url_template: str = DEFAULT_CFT_VERSION_URL_TEMPLATE) -> dict[str, Any]:
    payload = fetch_json(url_template.format(version=version), timeout=timeout)
    if not isinstance(payload, dict):
        raise ChromeForTestingError(f'unexpected Chrome for Testing version payload for {version}')
    return payload


def resolve_cft_download_entry(entry: dict[str, Any], *, binary: str, platform: str, source: str) -> dict[str, Any]:
    downloads = entry.get('downloads')
    if not isinstance(downloads, dict):
        raise ChromeForTestingError(f'Chrome for Testing {source} entry is missing downloads')
    candidates = downloads.get(binary)
    if not isinstance(candidates, list):
        raise ChromeForTestingError(f'Chrome for Testing {source} entry has no {binary} downloads')
    for candidate in candidates:
        if isinstance(candidate, dict) and candidate.get('platform') == platform and candidate.get('url'):
            return {
                'source': source,
                'version': entry.get('version'),
                'revision': entry.get('revision'),
                'binary': binary,
                'platform': platform,
                'url': candidate['url'],
            }
    raise ChromeForTestingError(f'Chrome for Testing {source} entry has no {binary} asset for {platform}')


def resolve_cft_channel_asset(catalog: dict[str, Any], *, channel: str, binary: str, platform: str) -> dict[str, Any]:
    channels = catalog.get('channels') if isinstance(catalog, dict) else None
    if not isinstance(channels, dict):
        raise ChromeForTestingError('Chrome for Testing catalog is missing the channels object')
    channel_name = normalize_channel(channel)
    channel_entry = channels.get(channel_name)
    if not isinstance(channel_entry, dict):
        raise ChromeForTestingError(f'Chrome for Testing catalog has no {channel_name} channel entry')
    return resolve_cft_download_entry(channel_entry, binary=binary, platform=platform, source=f'channel:{channel_name}')


def resolve_cft_version_asset(version_manifest: dict[str, Any], *, binary: str, platform: str) -> dict[str, Any]:
    return resolve_cft_download_entry(version_manifest, binary=binary, platform=platform, source=f'version:{version_manifest.get("version") or "unknown"}')


def install_cft_asset(*, asset: dict[str, Any], root: Path | None = None, env: dict[str, str] | None = None, force: bool = False, timeout: float = 120.0) -> dict[str, Any]:
    root = (root or cft_root(env)).expanduser()
    root.mkdir(parents=True, exist_ok=True)
    version = str(asset.get('version') or '')
    binary = str(asset.get('binary') or '')
    platform = str(asset.get('platform') or '')
    url = str(asset.get('url') or '')
    if not version or not binary or not platform or not url:
        raise ChromeForTestingError(f'incomplete Chrome for Testing asset descriptor: {asset!r}')

    rel = executable_relpath(binary, platform)
    install_dir = root / version
    executable = install_dir / rel
    if executable.exists() and not force:
        return {
            'ok': True,
            'skipped': True,
            'reason': 'already-installed',
            'version': version,
            'binary': binary,
            'platform': platform,
            'install_dir': str(install_dir),
            'executable': str(executable),
            'url': url,
        }

    if install_dir.exists() and force:
        shutil.rmtree(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='glasstty-cft-') as tmp_name:
        tmp_dir = Path(tmp_name)
        archive_path = tmp_dir / 'asset.zip'
        with urllib.request.urlopen(url, timeout=timeout) as response, archive_path.open('wb') as handle:
            shutil.copyfileobj(response, handle)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(install_dir)

    if not executable.exists():
        raise ChromeForTestingError(f'installed Chrome for Testing asset does not contain expected executable: {executable}')
    try:
        mode = executable.stat().st_mode
        executable.chmod(mode | 0o111)
    except OSError:
        pass
    metadata_path = install_dir / 'install.json'
    metadata_path.write_text(json.dumps({
        'version': version,
        'binary': binary,
        'platform': platform,
        'url': url,
        'source': asset.get('source'),
        'revision': asset.get('revision'),
    }, indent=2) + '\n', encoding='utf-8')
    return {
        'ok': True,
        'skipped': False,
        'version': version,
        'binary': binary,
        'platform': platform,
        'install_dir': str(install_dir),
        'executable': str(executable),
        'metadata_path': str(metadata_path),
        'url': url,
    }


def discover_browser_executable(*, env: dict[str, str] | None = None) -> dict[str, Any]:
    env = env or os.environ
    explicit = env.get('GLASSTTY_CHROMIUM_BIN') or env.get('CHROMIUM_BIN')
    if explicit:
        path = Path(explicit).expanduser()
        return augment_browser_choice({'source': 'explicit-env', 'path': str(path), 'exists': path.exists()})

    local_cft = latest_local_cft_install(binary='chrome', env=env)
    if local_cft:
        return augment_browser_choice({'source': 'chrome-for-testing', 'path': local_cft['executable'], 'exists': True, 'version': local_cft['version']})

    system = shutil.which('chromium') or shutil.which('google-chrome')
    return augment_browser_choice({'source': 'system-path' if system else None, 'path': system, 'exists': bool(system)})
