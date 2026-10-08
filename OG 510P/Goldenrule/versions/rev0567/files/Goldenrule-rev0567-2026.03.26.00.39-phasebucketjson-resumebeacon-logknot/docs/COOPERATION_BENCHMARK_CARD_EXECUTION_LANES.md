# Cooperation Benchmark Card Execution Lanes

Generated execution-lane handoff surface for compact cooperation benchmark cards. This keeps current environment truth machine-checkable so inheritors can tell which validation lane is honestly available now rather than reconstructing it from session prose.

- preferred_lane_id: `python-integrity`
- available_lane_count: 1
- blocked_lane_count: 1
- python3_version: `Python 3.13.5`
- native_cargo_version: none
- native_rustc_version: none
- junest_rust_available: false

## Recommended entrypoints

- `./grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write`
- `./grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py`
- `make doctor`

## Lane summary

| lane_id | lane_kind | available | availability_basis | blocking_reason_codes |
|---|---|---:|---|---|
| `python-integrity` | `surface-integrity` | true | `python3` | — |
| `rust-harness` | `engine-harness` | false | `unavailable` | `junest-binary-missing`, `native-cargo-missing`, `native-rustc-missing` |

## Observation

| field | value |
|---|---|
| `python3_path` | `/opt/pyvenv/bin/python3` |
| `python3_version` | `Python 3.13.5` |
| `jsonschema_available` | true |
| `git_path` | `/usr/bin/git` |
| `git_version` | `git version 2.47.3` |
| `native_cargo_path` | none |
| `native_cargo_version` | none |
| `native_rustc_path` | none |
| `native_rustc_version` | none |
| `junest_bin_path` | none |
| `junest_home_path` | `.sandworm/toolroot/junest-home` |
| `junest_home_present` | false |
| `junest_cargo_version` | none |
| `junest_rustc_version` | none |
| `junest_rust_available` | false |
| `rust_exec_path` | `tools/rust_exec.sh` |
| `rust_exec_present` | true |

## Per-lane details

### `python-integrity`

- lane_kind: `surface-integrity`
- available: true
- availability_basis: `python3`
- summary: Build and verify the compact-card inventory, heads, citation, handoff, control-plane, next-action, and execution-lane surfaces.
- required_capabilities: `python3`, `python-jsonschema`
- blocking_reason_codes: none
- entrypoint_commands:
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_execution_lanes.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_control_plane.py --write`
  - `./grpy ./scripts/report/build_cooperation_benchmark_card_next_action.py --write`
- verification_commands:
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_execution_lanes.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_control_plane.py`
  - `./grpy ./scripts/test/check_cooperation_benchmark_card_next_action.py`
- recovery_commands: none
- handoff_paths: `docs/COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md`, `docs/COOPERATION_BENCHMARK_CARD_CONTROL_PLANE.md`, `docs/COOPERATION_BENCHMARK_CARD_NEXT_ACTION.md`

### `rust-harness`

- lane_kind: `engine-harness`
- available: false
- availability_basis: `unavailable`
- summary: Run the repo harness and Rust engine validation beyond compact-card surface checks.
- required_capabilities: `cargo`, `rustc`, `rust-exec`
- blocking_reason_codes: `junest-binary-missing`, `native-cargo-missing`, `native-rustc-missing`
- entrypoint_commands:
  - `make doctor`
  - `./scripts/test/run_harness.sh quick`
  - `./scripts/test/run_harness.sh full`
- verification_commands:
  - `make doctor`
  - `./scripts/test/run_harness.sh quick`
- recovery_commands: `bash ./scripts/doctor.sh`, `env SW_JUNEST_HOME="$PWD/.sandworm/toolroot/junest-home" /run/sandworm/toolroot/bin/junest setup`, `env SW_JUNEST_HOME="$PWD/.sandworm/toolroot/junest-home" /run/sandworm/toolroot/bin/junest ns -f -- sh -lc "pacman -Syy --noconfirm && pacman -Sy --noconfirm archlinux-keyring && pacman -S --noconfirm rust"`
- handoff_paths: `docs/ENVIRONMENT_SANDWORM.md`, `docs/REPRODUCIBILITY.md`, `docs/COOPERATION_BENCHMARK_CARD_EXECUTION_LANES.md`

