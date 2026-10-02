#!/usr/bin/env python3
"""Run Clang's path-sensitive analyzer on IoTox's critical admission units.

Each invocation is derived from CMake's qualified Clang Debug compilation
Database so include paths, preprocessor state, language mode, and warnings stay
aligned with the normal build. Every selected unit runs in explicit deep mode.
A nonzero analyzer exit or any emitted diagnostic fails the lane.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from typing import NoReturn, Sequence

DEFAULT_TARGETS: tuple[str, ...] = (
    "src/terminal_profile.cpp",
    "src/terminal_cgroup.cpp",
    "src/agent.cpp",
    "src/cli.cpp",
    "src/local/runtime_tree.cpp",
    "src/security/identity.cpp",
    "src/route_worker.cpp",
    "src/sync_service.cpp",
    "src/sync_subscriber.cpp",
    "src/sync_transfer.cpp",
    "src/sync_tree.cpp",
    "src/update_bundle.cpp",
    "src/update_state.cpp",
)


def die(message: str) -> NoReturn:
    print(f"focused static analysis: {message}", file=sys.stderr)
    raise SystemExit(2)


def parse_positive_timeout(value: str) -> int:
    try:
        timeout = int(value, 10)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"timeout must be an integer: {value}"
        ) from error
    if timeout < 1 or timeout > 3600:
        raise argparse.ArgumentTypeError(
            f"timeout must be in 1..3600 seconds: {value}"
        )
    return timeout


def load_compile_database(path: Path) -> list[dict[str, object]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        die(f"cannot read compile database {path}: {error}")
    except json.JSONDecodeError as error:
        die(f"invalid compile database {path}: {error}")
    if not isinstance(payload, list):
        die(f"compile database root is not an array: {path}")

    entries: list[dict[str, object]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            die(f"compile database entry {index} is not an object")
        entries.append(item)
    return entries


def command_arguments(entry: dict[str, object]) -> list[str]:
    arguments = entry.get("arguments")
    if isinstance(arguments, list) and all(
        isinstance(argument, str) for argument in arguments
    ):
        return list(arguments)

    command = entry.get("command")
    if isinstance(command, str):
        return shlex.split(command)
    die("compile database entry has neither string command nor string arguments")


def resolve_entry_file(entry: dict[str, object]) -> Path:
    file_value = entry.get("file")
    directory_value = entry.get("directory")
    if not isinstance(file_value, str) or not isinstance(directory_value, str):
        die("compile database entry lacks string file/directory fields")
    file_path = Path(file_value)
    if not file_path.is_absolute():
        file_path = Path(directory_value) / file_path
    return file_path.resolve()


def analyzer_arguments(
    entry: dict[str, object], source: Path
) -> tuple[list[str], Path]:
    directory_value = entry.get("directory")
    if not isinstance(directory_value, str):
        die(f"compile database entry lacks directory for {source}")
    directory = Path(directory_value).resolve()

    original = command_arguments(entry)
    if not original:
        die(f"empty compile command for {source}")
    compiler_name = Path(original[0]).name.lower()
    if "clang" not in compiler_name:
        die(f"compile command for {source} is not Clang: {original[0]}")

    result: list[str] = []
    skip_next = False
    options_with_argument = {"-o", "-MF", "-MT", "-MQ"}
    source_resolved = source.resolve()
    for argument in original:
        if skip_next:
            skip_next = False
            continue
        if argument in options_with_argument:
            skip_next = True
            continue
        if argument in {"-c", "-MD", "-MMD", "-MP"}:
            continue

        candidate = Path(argument)
        if not argument.startswith("-"):
            try:
                if not candidate.is_absolute():
                    candidate = directory / candidate
                if candidate.resolve() == source_resolved:
                    continue
            except OSError:
                pass
        result.append(argument)

    if skip_next:
        die(f"compile command ends with an incomplete output option for {source}")
    if not result:
        die(f"compile command lost its compiler for {source}")

    result.extend(
        (
            "--analyze",
            # Some compiler wrappers inject linker-only flags after their own
            # argument parsing because they do not recognize --analyze as a
            # compile-only mode. Keep project diagnostics fatal while ignoring
            # only that driver-level unused-linker-input warning.
            "-Wno-unused-command-line-argument",
            "-Xanalyzer",
            "-analyzer-output=text",
            "-Xanalyzer",
            "-analyzer-config",
            "-Xanalyzer",
            "mode=deep",
            "-o",
            "/dev/null",
            str(source_resolved),
        )
    )
    return result, directory


def analyzer_environment() -> dict[str, str]:
    """Keep compiler inputs while removing wrapper-only link injection.

    Nix compiler wrappers may add their dynamic-linker selection through
    NIX_LDFLAGS even for Clang's non-linking --analyze mode. Clang diagnoses
    that linker-only argument as unused under the project's -Werror policy.
    Static analysis never links, so carrying either host or target link flags
    into this subprocess is both unnecessary and misleading.
    """
    environment = os.environ.copy()
    environment.pop("NIX_LDFLAGS", None)
    environment.pop("NIX_LDFLAGS_FOR_TARGET", None)
    return environment


def main(argv: Sequence[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    default_database = Path(
        os.environ.get(
            "IOTOX_STATIC_ANALYZER_COMPILE_COMMANDS",
            root / "build" / "clang-debug" / "compile_commands.json",
        )
    )
    default_timeout_text = os.environ.get(
        "IOTOX_STATIC_ANALYZER_TIMEOUT_SECONDS", "600"
    )
    try:
        default_timeout = parse_positive_timeout(default_timeout_text)
    except argparse.ArgumentTypeError as error:
        die(f"invalid IOTOX_STATIC_ANALYZER_TIMEOUT_SECONDS: {error}")

    parser = argparse.ArgumentParser(
        description="Run deep path-sensitive Clang analysis on critical IoTox units."
    )
    parser.add_argument(
        "--compile-commands",
        type=Path,
        default=default_database,
        help="CMake compile_commands.json from the qualified Clang build",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=parse_positive_timeout,
        default=default_timeout,
        help="per-translation-unit timeout in 1..3600 seconds",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=list(DEFAULT_TARGETS),
        help="repository-relative C++ translation units",
    )
    args = parser.parse_args(argv)

    database_path = args.compile_commands.resolve()
    entries = load_compile_database(database_path)
    indexed: dict[Path, list[dict[str, object]]] = {}
    for entry in entries:
        indexed.setdefault(resolve_entry_file(entry), []).append(entry)

    failures = 0
    diagnostics = 0
    seen_targets: set[Path] = set()
    for relative in args.targets:
        source = (root / relative).resolve()
        try:
            source.relative_to(root)
        except ValueError:
            die(f"target escapes repository root: {relative}")
        if source in seen_targets:
            die(f"duplicate analyzer target: {relative}")
        seen_targets.add(source)

        matching_entries = indexed.get(source, [])
        if not matching_entries:
            print(
                f"FAIL focused-static-analysis {relative}: absent from {database_path}",
                file=sys.stderr,
            )
            failures += 1
            continue
        if len(matching_entries) != 1:
            print(
                f"FAIL focused-static-analysis {relative}: "
                f"compile database contains {len(matching_entries)} entries",
                file=sys.stderr,
            )
            failures += 1
            continue

        command, directory = analyzer_arguments(matching_entries[0], source)
        print(f"==> focused-static-analysis {relative} mode=deep", flush=True)
        try:
            completed = subprocess.run(
                command,
                cwd=directory,
                env=analyzer_environment(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.timeout_seconds,
                check=False,
            )
        except OSError as error:
            print(
                f"FAIL focused-static-analysis {relative}: "
                f"cannot execute analyzer: {error}",
                file=sys.stderr,
            )
            failures += 1
            continue
        except subprocess.TimeoutExpired as error:
            output = error.stdout or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            if output.strip():
                print(output.rstrip())
            print(
                f"FAIL focused-static-analysis {relative}: exceeded "
                f"{args.timeout_seconds} seconds",
                file=sys.stderr,
            )
            failures += 1
            continue

        output = completed.stdout or ""
        nonempty_lines = [line for line in output.splitlines() if line.strip()]
        diagnostics += len(nonempty_lines)
        if output.strip():
            print(output.rstrip())
        if completed.returncode != 0 or nonempty_lines:
            print(
                f"FAIL focused-static-analysis {relative}: "
                f"exit={completed.returncode} diagnostics={len(nonempty_lines)}",
                file=sys.stderr,
            )
            failures += 1
        else:
            print(f"PASS focused-static-analysis {relative}")

    if failures:
        print(
            f"focused-static-analysis=fail files={len(args.targets)} "
            f"failures={failures} diagnostics={diagnostics}",
            file=sys.stderr,
        )
        return 1
    print(
        f"focused-static-analysis=pass files={len(args.targets)} diagnostics=0"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
