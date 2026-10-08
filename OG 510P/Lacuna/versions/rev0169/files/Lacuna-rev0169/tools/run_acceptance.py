#!/usr/bin/env python3
"""Run Lacuna acceptance tests as bounded subprocesses.

The default recipient path is a short first-contact smoke suite covering the
release artifact audit, release-surface documents, and scenario-template
fail-closed guard. Expanded runs stay bounded by launching one test module at a
time, and the known heavy integration modules are split to individual unittest
methods when their opt-in guards are enabled. That makes the failing or timed-out
unit explicit instead of letting a long discovery run look like a hang.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import unittest
from dataclasses import dataclass
from pathlib import Path


SMOKE_MODULES = (
    "tests.test_artifact",
    "tests.test_release_surface",
    "tests.test_scenario_template_guard",
)

SPLIT_METHOD_MODULES = {
    "tests.test_checkpoint_runs",
    "tests.test_checkpoints",
    "tests.test_cli_e2e",
    "tests.test_scenario_bundles",
    "tests.test_scenarios",
}


@dataclass(frozen=True)
class AcceptanceItem:
    module: str
    target: str
    label: str


def discover_modules(root: Path) -> list[str]:
    return [f"tests.{path.stem}" for path in sorted((root / "tests").glob("test_*.py"))]


def parse_shard(value: str, item_count: int) -> tuple[int, int, int, int]:
    try:
        index_text, total_text = value.split("/", 1)
        index = int(index_text)
        total = int(total_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--shard must be formatted as N/M, for example 1/4") from exc
    if total < 1 or index < 1 or index > total:
        raise argparse.ArgumentTypeError("--shard must satisfy 1 <= N <= M")
    start = (item_count * (index - 1)) // total
    stop = (item_count * index) // total
    return index, total, start, stop


def _without_start_index(arguments: list[str]) -> list[str]:
    stripped: list[str] = []
    skip_next = False
    for argument in arguments:
        if skip_next:
            skip_next = False
            continue
        if argument == "--start-index":
            skip_next = True
            continue
        if argument.startswith("--start-index="):
            continue
        stripped.append(argument)
    return stripped


def _flatten_tests(suite: unittest.TestSuite) -> list[str]:
    targets: list[str] = []
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            targets.extend(_flatten_tests(test))
        else:
            targets.append(test.id())
    return sorted(dict.fromkeys(targets))


def discover_method_targets(root: Path, module: str) -> list[str]:
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "src"))
    suite = unittest.defaultTestLoader.loadTestsFromName(module)
    return _flatten_tests(suite)


def build_items(root: Path, modules: list[str], *, split_opt_in_modules: bool) -> list[AcceptanceItem]:
    items: list[AcceptanceItem] = []
    for module in modules:
        if split_opt_in_modules and module in SPLIT_METHOD_MODULES:
            targets = discover_method_targets(root, module)
            items.extend(
                AcceptanceItem(module=module, target=target, label=target)
                for target in targets
            )
        else:
            items.append(AcceptanceItem(module=module, target=module, label=module))
    return items


def main(argv: list[str] | None = None) -> int:
    original_argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=60.0, help="per-module or per-method timeout in seconds")
    parser.add_argument("--pattern", default=None, help="optional substring filter for module names")
    parser.add_argument("--shard", default=None, metavar="N/M", help="run a contiguous 1-indexed item shard, for example 2/4")
    parser.add_argument("--heavy", action="store_true", help="enable checkpoint/scenario integration tests guarded by LACUNA_HEAVY_TESTS")
    parser.add_argument("--bundle", action="store_true", help="enable replicated scenario-bundle lifecycle tests guarded by LACUNA_BUNDLE_TESTS")
    parser.add_argument("--schema", action="store_true", help="enable optional jsonschema validations guarded by LACUNA_SCHEMA_TESTS")
    parser.add_argument("--e2e", action="store_true", help="enable launcher/subprocess E2E tests guarded by LACUNA_E2E_TESTS")
    parser.add_argument("--all", action="store_true", help="run the expanded list and enable --heavy, --bundle, --schema, and --e2e")
    parser.add_argument("--all-modules", action="store_true", help="run the expanded module list instead of the first-contact smoke suite")
    parser.add_argument("--start-index", type=int, default=0, help=argparse.SUPPRESS)
    parser.add_argument("--exec-chain", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    expanded = bool(args.all_modules or args.pattern or args.shard or args.heavy or args.bundle or args.schema or args.e2e or args.all)
    modules = discover_modules(root) if expanded else list(SMOKE_MODULES)
    if args.pattern:
        modules = [module for module in modules if args.pattern in module]
    if not modules:
        print("no test modules selected", file=sys.stderr)
        return 2

    heavy = args.heavy or args.all
    bundle = args.bundle or args.all
    schema = args.schema or args.all
    e2e = args.e2e or args.all

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("PYTHONUNBUFFERED", "1")
    env["PYTHONPATH"] = str(root / "src")
    env.setdefault("LACUNA_FAST_TEST_IO", "1")
    if heavy:
        env["LACUNA_HEAVY_TESTS"] = "1"
    if bundle:
        env["LACUNA_BUNDLE_TESTS"] = "1"
        env.setdefault("LACUNA_HEAVY_TESTS", "1")
    if schema:
        env["LACUNA_SCHEMA_TESTS"] = "1"
    if e2e:
        env["LACUNA_E2E_TESTS"] = "1"

    # Keep the runner's own discovery environment aligned with the child test
    # processes so class-level skip decorators and optional guards are resolved
    # the same way when we split heavy modules into method targets.
    os.environ.update({key: value for key, value in env.items() if key.startswith("LACUNA_")})

    items = build_items(
        root,
        modules,
        split_opt_in_modules=bool(heavy or bundle or e2e),
    )
    shard_label = ""
    if args.shard:
        try:
            shard_index, shard_total, start, stop = parse_shard(args.shard, len(items))
        except argparse.ArgumentTypeError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        items = items[start:stop]
        shard_label = f" shard {shard_index}/{shard_total}"

    if not items:
        print("no test items selected", file=sys.stderr)
        return 2
    total_items = len(items)
    if args.start_index < 0 or args.start_index > total_items:
        print("--start-index is outside the selected item range", file=sys.stderr)
        return 2
    items = items[args.start_index:]
    if not items:
        print(f"ACCEPTANCE PASS: {total_items}/{total_items} items")
        return 0

    flags = []
    if heavy:
        flags.append("heavy")
    if bundle:
        flags.append("bundle")
    if schema:
        flags.append("schema")
    if e2e:
        flags.append("e2e")
    suffix = f" ({', '.join(flags)} enabled)" if flags else ""
    started = time.perf_counter()
    suite_name = "expanded" if expanded else "smoke"
    selected_label = (
        f"{suite_name} {total_items} items"
        if args.start_index == 0
        else f"{suite_name} items {args.start_index + 1}-{total_items} of {total_items}"
    )
    print(
        f"Lacuna acceptance{shard_label}: {selected_label}, "
        f"{args.timeout:g}s timeout each{suffix}",
        flush=True,
    )

    for index, item in enumerate(items, start=args.start_index + 1):
        print(f"\n[{index:02d}/{total_items:02d}] {item.label}", flush=True)
        before = time.perf_counter()
        command = [sys.executable, "-m", "unittest", "-q", item.target] if schema else [sys.executable, "-S", "-m", "unittest", "-q", item.target]
        process = subprocess.Popen(
            command,
            cwd=root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        heartbeat_seconds = 1.0
        output = ""
        while True:
            elapsed = time.perf_counter() - before
            remaining = args.timeout - elapsed
            if remaining <= 0:
                process.kill()
                timed_out_output, _ = process.communicate()
                output = timed_out_output or ""
                if output:
                    print(output.rstrip())
                print(f"TIMEOUT after {elapsed:.2f}s: {item.label}")
                return 124
            try:
                completed_output, _ = process.communicate(timeout=min(heartbeat_seconds, remaining))
                output = completed_output or ""
                break
            except subprocess.TimeoutExpired:
                elapsed = time.perf_counter() - before
                print(f"... {item.label} still running after {elapsed:.1f}s", flush=True)
        elapsed = time.perf_counter() - before

        returncode = process.returncode
        if output:
            print(output.rstrip())
        if returncode != 0:
            if "unittest.case.SkipTest:" in output:
                print(f"SKIP {item.label} elapsed={elapsed:.2f}s", flush=True)
            else:
                print(f"FAIL {item.label} exit={returncode} elapsed={elapsed:.2f}s")
                return returncode
        else:
            print(f"PASS {item.label} elapsed={elapsed:.2f}s", flush=True)
        if args.exec_chain and index < total_items:
            next_args = _without_start_index(original_argv) + ["--start-index", str(index)]
            runner_env = os.environ.copy()
            runner_env["PYTHONDONTWRITEBYTECODE"] = "1"
            runner_env.setdefault("PYTHONUNBUFFERED", "1")
            runner_env.setdefault("PYTHONPATH", str(root / "src"))
            os.execvpe(sys.executable, [sys.executable, str(Path(__file__).resolve()), *next_args], runner_env)

    total = time.perf_counter() - started
    print(f"\nACCEPTANCE PASS: {total_items}/{total_items} items in final segment {total:.2f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
