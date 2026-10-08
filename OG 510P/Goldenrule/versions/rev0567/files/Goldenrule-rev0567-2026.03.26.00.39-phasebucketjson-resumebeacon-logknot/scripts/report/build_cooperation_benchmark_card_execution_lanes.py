#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_execution_lanes.schema.json'
TITLE = '# Cooperation Benchmark Card Execution Lanes'
SUBTITLE = (
    'Generated execution-lane handoff surface for compact cooperation benchmark cards. '
    'This keeps current environment truth machine-checkable so inheritors can tell which validation lane '
    'is honestly available now rather than reconstructing it from session prose.'
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _run(cmd: list[str], env: dict[str, str] | None = None, timeout: int = 10) -> str | None:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False, env=env, timeout=timeout)
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    text = (proc.stdout or proc.stderr).strip()
    return text.splitlines()[0].strip() if text else None


def _which(name: str) -> str | None:
    return shutil.which(name)


def _normalize_repo_local_path(path_value: str | None) -> str | None:
    if not path_value:
        return path_value
    path = Path(path_value)
    candidate = path if path.is_absolute() else (ROOT / path)
    try:
        resolved = candidate.resolve(strict=False)
        root_resolved = ROOT.resolve(strict=False)
        if resolved.is_relative_to(root_resolved):
            return resolved.relative_to(root_resolved).as_posix()
    except Exception:
        pass
    return path_value


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'unable to load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect() -> dict[str, Any]:
    schema = _load_json(SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)

    python3_path = _which('python3')
    git_path = _which('git')
    native_cargo_path = _which('cargo')
    native_rustc_path = _which('rustc')
    python3_version = _run(['python3', '--version']) if python3_path else None
    git_version = _run(['git', '--version']) if git_path else None
    native_cargo_version = _run(['cargo', '--version']) if native_cargo_path else None
    native_rustc_version = _run(['rustc', '--version']) if native_rustc_path else None

    junest_bin_path = os.environ.get('JUNEST_BIN') or '/run/sandworm/toolroot/bin/junest'
    if not Path(junest_bin_path).exists():
        junest_bin_path = None
    observed_junest_home = os.environ.get('SW_JUNEST_HOME') or str(ROOT / '.sandworm' / 'toolroot' / 'junest-home')
    junest_home_present = Path(observed_junest_home).is_dir()
    junest_home_path = _normalize_repo_local_path(observed_junest_home)
    junest_cargo_version = None
    junest_rustc_version = None
    if junest_bin_path and junest_home_present:
        env = dict(os.environ)
        env['SW_JUNEST_HOME'] = junest_home_path
        junest_cargo_version = _run([junest_bin_path, 'ns', '-f', '--', 'sh', '-lc', 'cargo --version'], env=env)
        junest_rustc_version = _run([junest_bin_path, 'ns', '-f', '--', 'sh', '-lc', 'rustc --version'], env=env)
    junest_rust_available = bool(junest_cargo_version and junest_rustc_version)

    rust_exec_path = str((ROOT / 'tools' / 'rust_exec.sh').relative_to(ROOT))
    rust_exec_present = (ROOT / rust_exec_path).exists()

    python_blocking: list[str] = []
    if not python3_path:
        python_blocking.append('python3-missing')
    if importlib.util.find_spec('jsonschema') is None:
        python_blocking.append('python-jsonschema-missing')
    python_lane = {
        'lane_id': 'python-integrity',
        'lane_kind': 'surface-integrity',
        'summary': 'Build and verify the compact-card inventory, heads, citation, handoff, control-plane, next-action, and execution-lane surfaces.',
        'available': not python_blocking,
        'availability_basis': 'python3' if not python_blocking else 'unavailable',
        'required_capabilities': ['python3', 'python-jsonschema'],
        'blocking_reason_codes': python_blocking,
        'entrypoint_commands': [
            './grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write',
            './grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write',
        ],
        'verification_commands': [
            './grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py',
            './grpy ./scripts/test/check_cooperation_benchmark_card_next_action.py',
        ],
        'recovery_commands': [
            'python3 -m pip install jsonschema',
        ] if python_blocking else [],
        'handoff_paths': [
            'docs/COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md',
            'docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md',
            'docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md',
        ],
    }

    rust_blocking: list[str] = []
    availability_basis = 'unavailable'
    if native_cargo_version and native_rustc_version:
        availability_basis = 'native-rust'
    elif junest_rust_available:
        availability_basis = 'junest-rust'
    else:
        if not rust_exec_present:
            rust_blocking.append('rust-exec-missing')
        if not native_cargo_version:
            rust_blocking.append('native-cargo-missing')
        if not native_rustc_version:
            rust_blocking.append('native-rustc-missing')
        if not junest_bin_path:
            rust_blocking.append('junest-binary-missing')
        elif not junest_home_present:
            rust_blocking.append('junest-home-missing')
        elif not junest_rust_available:
            rust_blocking.append('junest-rust-toolchain-missing')
    rust_available = availability_basis != 'unavailable'
    rust_lane = {
        'lane_id': 'rust-harness',
        'lane_kind': 'engine-harness',
        'summary': 'Run the repo harness and Rust engine validation beyond compact-card surface checks.',
        'available': rust_available,
        'availability_basis': availability_basis,
        'required_capabilities': ['cargo', 'rustc', 'rust-exec'],
        'blocking_reason_codes': [] if rust_available else sorted(set(rust_blocking)),
        'entrypoint_commands': [
            'make doctor',
            './scripts/test/run_harness.sh quick',
            './scripts/test/run_harness.sh full',
        ],
        'verification_commands': [
            'make doctor',
            './scripts/test/run_harness.sh quick',
        ],
        'recovery_commands': [
            'bash ./scripts/doctor.sh',
            'env SW_JUNEST_HOME="$PWD/.sandworm/toolroot/junest-home" /run/sandworm/toolroot/bin/junest setup',
            'env SW_JUNEST_HOME="$PWD/.sandworm/toolroot/junest-home" /run/sandworm/toolroot/bin/junest ns -f -- sh -lc "pacman -Syy --noconfirm && pacman -Sy --noconfirm archlinux-keyring && pacman -S --noconfirm rust"',
        ] if not rust_available else [],
        'handoff_paths': [
            'docs/ENVIRONMENT_SANDWORM.md',
            'docs/REPRODUCIBILITY.md',
            'docs/COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md',
        ],
    }

    lanes = [python_lane, rust_lane]
    data = {
        'execution_surface_kind': 'cooperation_benchmark_card_execution_lanes',
        'preferred_for_environment_handoff': True,
        'observation': {
            'python3_path': python3_path,
            'python3_version': python3_version,
            'jsonschema_available': importlib.util.find_spec('jsonschema') is not None,
            'git_path': git_path,
            'git_version': git_version,
            'native_cargo_path': native_cargo_path,
            'native_cargo_version': native_cargo_version,
            'native_rustc_path': native_rustc_path,
            'native_rustc_version': native_rustc_version,
            'junest_bin_path': junest_bin_path,
            'junest_home_path': junest_home_path,
            'junest_home_present': junest_home_present,
            'junest_cargo_version': junest_cargo_version,
            'junest_rustc_version': junest_rustc_version,
            'junest_rust_available': junest_rust_available,
            'rust_exec_path': rust_exec_path,
            'rust_exec_present': rust_exec_present,
        },
        'counts': {
            'available_lane_count': sum(1 for lane in lanes if lane['available']),
            'blocked_lane_count': sum(1 for lane in lanes if not lane['available']),
        },
        'preferred_lane_id': 'rust-harness' if rust_available else 'python-integrity',
        'recommended_entrypoints': [
            './grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write',
            './grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py',
            'make doctor',
        ],
        'lanes': lanes,
    }
    jsonschema.validate(data, schema)
    return data


def render(data: dict[str, Any]) -> str:
    observation = data['observation']
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- preferred_lane_id: `{data['preferred_lane_id']}`",
        f"- available_lane_count: {data['counts']['available_lane_count']}",
        f"- blocked_lane_count: {data['counts']['blocked_lane_count']}",
        f"- python3_version: {('`' + observation['python3_version'] + '`') if observation['python3_version'] else 'none'}",
        f"- native_cargo_version: {('`' + observation['native_cargo_version'] + '`') if observation['native_cargo_version'] else 'none'}",
        f"- native_rustc_version: {('`' + observation['native_rustc_version'] + '`') if observation['native_rustc_version'] else 'none'}",
        f"- junest_rust_available: {str(observation['junest_rust_available']).lower()}",
        '',
        '## Recommended entrypoints',
        '',
    ]
    for command in data['recommended_entrypoints']:
        lines.append(f'- `{command}`')
    lines.extend(['', '## Lane summary', '', '| lane_id | lane_kind | available | availability_basis | blocking_reason_codes |', '|---|---|---:|---|---|'])
    for lane in data['lanes']:
        blocking = ', '.join('`' + code + '`' for code in lane['blocking_reason_codes']) or '—'
        lines.append(
            f"| `{lane['lane_id']}` | `{lane['lane_kind']}` | {str(lane['available']).lower()} | `{lane['availability_basis']}` | {blocking} |"
        )
    lines.extend(['', '## Observation', '', '| field | value |', '|---|---|'])
    for key, value in observation.items():
        if isinstance(value, bool):
            rendered = str(value).lower()
        elif value is None:
            rendered = 'none'
        else:
            rendered = f'`{value}`'
        lines.append(f'| `{key}` | {rendered} |')
    lines.extend(['', '## Per-lane details', ''])
    for lane in data['lanes']:
        lines.append(f"### `{lane['lane_id']}`")
        lines.append('')
        lines.append(f"- lane_kind: `{lane['lane_kind']}`")
        lines.append(f"- available: {str(lane['available']).lower()}")
        lines.append(f"- availability_basis: `{lane['availability_basis']}`")
        lines.append(f"- summary: {lane['summary']}")
        lines.append(f"- required_capabilities: {', '.join('`' + value + '`' for value in lane['required_capabilities'])}")
        lines.append(f"- blocking_reason_codes: {', '.join('`' + value + '`' for value in lane['blocking_reason_codes']) if lane['blocking_reason_codes'] else 'none'}")
        lines.append('- entrypoint_commands:')
        for command in lane['entrypoint_commands']:
            lines.append(f"  - `{command}`")
        lines.append('- verification_commands:')
        for command in lane['verification_commands']:
            lines.append(f"  - `{command}`")
        lines.append(f"- recovery_commands: {', '.join('`' + value + '`' for value in lane['recovery_commands']) if lane['recovery_commands'] else 'none'}")
        lines.append(f"- handoff_paths: {', '.join('`' + value + '`' for value in lane['handoff_paths'])}")
        lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_execution_lanes.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f'cooperation-benchmark-card-execution-lanes: wrote {out_md}')
        print(f'cooperation-benchmark-card-execution-lanes: wrote {out_json}')
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-execution-lanes: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-execution-lanes: ok ({data['preferred_lane_id']})")
    print(f'cooperation-benchmark-card-execution-lanes: wrote {out_json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
