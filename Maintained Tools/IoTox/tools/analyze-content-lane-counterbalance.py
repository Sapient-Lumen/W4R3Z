#!/usr/bin/env python3
"""Aggregate verified ascending/descending content-lane Sandwurm proofs."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


SCHEMA = "iotox.content-lane-counterbalance.v1"
COMPACT_SCHEMA = "iotox.sandwurm-pair-compact-export.v0"
PAIR_NAME = re.compile(r"pair\.[A-Za-z0-9_]+")
SHA256 = re.compile(r"[0-9a-f]{64}")
CAPS = (1, 2, 4, 8)
ROUTES = ("direct-udp", "forced-tcp")
SCENARIO_ORDERS = {
    "sync-content-lane-science": (1, 2, 4, 8),
    "sync-content-lane-science-reverse": (8, 4, 2, 1),
}
SUMMARY_RELATIVE = Path(
    "client/live/workspace-export/guest-receipts/iotox/"
    "content-lane-science.tsv"
)
RECEIPT_RELATIVE = Path(
    "client/live/workspace-export/guest-receipts/iotox/pair.json"
)

VERIFIER_PATH = Path(__file__).with_name("verify-sandwurm-pair.py")
SPEC = importlib.util.spec_from_file_location(
    "iotox_sandwurm_pair_verifier_counterbalance", VERIFIER_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load the Sandwurm pair verifier")
PAIR_VERIFIER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PAIR_VERIFIER
SPEC.loader.exec_module(PAIR_VERIFIER)


class AnalysisError(RuntimeError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AnalysisError(detail)


def load_json(path: Path) -> dict:
    require(path.is_file() and not path.is_symlink(), f"missing regular file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AnalysisError(f"cannot read JSON {path}: {error}") from error
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def parse_summary(path: Path, expected_order: tuple[int, ...]) -> tuple[str, list[dict]]:
    require(path.is_file() and not path.is_symlink(), f"missing summary: {path}")
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as error:
        raise AnalysisError(f"cannot read summary {path}: {error}") from error
    require(len(lines) == 11, f"unexpected summary length: {path}")
    metadata: dict[str, str] = {}
    for line in lines[:6]:
        fields = line.split("\t")
        require(len(fields) == 2 and fields[0] not in metadata,
                f"malformed summary metadata: {path}")
        metadata[fields[0]] = fields[1]
    require(
        metadata == {
            "schema": "iotox-content-lane-science-v1",
            "artifact-sha256": metadata.get("artifact-sha256", ""),
            "artifact-bytes": "8388608",
            "content-chunks": "24",
            "content-objects": "26",
            "phase-order": ",".join(str(cap) for cap in expected_order),
        }
        and SHA256.fullmatch(metadata["artifact-sha256"]) is not None,
        f"summary metadata does not match the frozen experiment: {path}",
    )
    require(
        lines[6]
        == "columns\tcap\tduration-ms\tartifact-bps\tmax-active-lanes\t"
        "user-cpu-ticks\tsystem-cpu-ticks\tresident-high-water-kib\t"
        "transport-iterations\tresource-sha256",
        f"summary columns drifted: {path}",
    )
    rows: list[dict] = []
    for expected_cap, line in zip(expected_order, lines[7:], strict=True):
        fields = line.split("\t")
        require(len(fields) == 10 and fields[0] == "phase",
                f"malformed phase row: {path}")
        try:
            cap, duration, bps, active, user, system, hwm, iterations = (
                int(value) for value in fields[1:9]
            )
        except ValueError as error:
            raise AnalysisError(f"noninteger phase value: {path}") from error
        require(
            cap == expected_cap
            and duration > 0
            and bps == (8 * 1024 * 1024 * 1000) // duration
            and 1 <= active <= cap
            and user >= 0
            and system >= 0
            and hwm > 0
            and iterations > 0
            and SHA256.fullmatch(fields[9]) is not None,
            f"incoherent cap-{expected_cap} phase row: {path}",
        )
        rows.append(
            {
                "cap": cap,
                "duration_ms": duration,
                "artifact_bps": bps,
                "max_active_lanes": active,
                "cpu_ticks": user + system,
                "resident_high_water_kib": hwm,
                "transport_iterations": iterations,
            }
        )
    return metadata["artifact-sha256"], rows


def exact_distribution(values: list[int]) -> dict[str, int]:
    require(bool(values), "cannot summarize an empty distribution")
    return {
        "samples": len(values),
        "minimum": min(values),
        "maximum": max(values),
        "sum": sum(values),
        "mean_denominator": len(values),
        "mean_floor": sum(values) // len(values),
    }


def summarize_rows(rows: list[dict]) -> dict[str, dict[str, int]]:
    return {
        field: exact_distribution([int(row[field]) for row in rows])
        for field in (
            "duration_ms",
            "artifact_bps",
            "max_active_lanes",
            "cpu_ticks",
            "resident_high_water_kib",
            "transport_iterations",
        )
    }


def mean_is_greater(left: dict, right: dict) -> bool:
    return (
        int(left["sum"]) * int(right["mean_denominator"])
        > int(right["sum"]) * int(left["mean_denominator"])
    )


def best_cap(cap_summaries: dict[str, dict]) -> int:
    winner = CAPS[0]
    for cap in CAPS[1:]:
        if mean_is_greater(
            cap_summaries[str(cap)]["artifact_bps"],
            cap_summaries[str(winner)]["artifact_bps"],
        ):
            winner = cap
    return winner


def analyze(proofs: list[Path]) -> dict:
    require(len(proofs) >= 4, "at least four compact proofs are required")
    seen: set[Path] = set()
    proof_records: list[dict] = []
    grouped: dict[tuple[str, int], list[dict]] = defaultdict(list)
    order_counts: Counter[tuple[str, str]] = Counter()
    artifact_hashes: set[str] = set()
    binary_hashes: set[str] = set()

    for supplied in proofs:
        root = supplied.resolve()
        require(root not in seen, f"duplicate proof: {root}")
        seen.add(root)
        require(PAIR_NAME.fullmatch(root.name) is not None,
                f"invalid pair proof name: {root.name}")
        try:
            PAIR_VERIFIER.verify_pair(root)
        except (OSError, RuntimeError, ValueError) as error:
            raise AnalysisError(f"pair verification failed for {root}: {error}") from error
        compact = load_json(root / "compact-export.json")
        manifest = load_json(root / "pair-manifest.json")
        receipt = load_json(root / RECEIPT_RELATIVE)
        scenario = manifest.get("scenario")
        route = manifest.get("route_mode")
        require(
            compact.get("schema") == COMPACT_SCHEMA
            and compact.get("status") == "passed"
            and compact.get("contains_secrets") is False
            and compact.get("source_proof_id") == root.name
            and scenario in SCENARIO_ORDERS
            and route in ROUTES
            and manifest.get("status") == "passed"
            and manifest.get("identity_baseline_unchanged") is True
            and manifest.get("bootstrap_fixture_restart_count") == 0
            and manifest.get("device_daemon_restart_count") == 0,
            f"{root.name} is not an accepted compact counterbalance proof",
        )
        assert isinstance(scenario, str) and isinstance(route, str)
        expected_order = SCENARIO_ORDERS[scenario]
        artifact_sha256, rows = parse_summary(root / SUMMARY_RELATIVE, expected_order)
        binary_sha256 = receipt.get("binary_sha256")
        require(SHA256.fullmatch(str(binary_sha256)) is not None,
                f"invalid binary identity: {root.name}")
        artifact_hashes.add(artifact_sha256)
        binary_hashes.add(str(binary_sha256))
        order_name = "ascending" if expected_order[0] == 1 else "descending"
        order_counts[(route, order_name)] += 1
        for row in rows:
            grouped[(route, int(row["cap"]))].append(row)
        proof_records.append(
            {
                "proof": root.name,
                "route": route,
                "scenario": scenario,
                "order": order_name,
                "caps": {
                    str(row["cap"]): {
                        field: row[field]
                        for field in (
                            "duration_ms",
                            "artifact_bps",
                            "max_active_lanes",
                            "cpu_ticks",
                            "resident_high_water_kib",
                            "transport_iterations",
                        )
                    }
                    for row in rows
                },
            }
        )

    require(len(artifact_hashes) == 1, "proofs do not share one artifact")
    require(len(binary_hashes) == 1, "proofs do not share one IoTox binary")
    for route in ROUTES:
        ascending = order_counts[(route, "ascending")]
        descending = order_counts[(route, "descending")]
        require(
            ascending >= 1 and ascending == descending,
            f"{route} orders are not equally represented",
        )

    route_results: dict[str, dict] = {}
    aggregate_by_cap: dict[str, list[dict]] = {str(cap): [] for cap in CAPS}
    for route in ROUTES:
        caps: dict[str, dict] = {}
        expected_samples = order_counts[(route, "ascending")] * 2
        for cap in CAPS:
            rows = grouped[(route, cap)]
            require(len(rows) == expected_samples,
                    f"{route} cap {cap} sample count is unbalanced")
            caps[str(cap)] = summarize_rows(rows)
            aggregate_by_cap[str(cap)].extend(rows)
        route_results[route] = {
            "ascending_proofs": order_counts[(route, "ascending")],
            "descending_proofs": order_counts[(route, "descending")],
            "throughput_winner_cap": best_cap(caps),
            "caps": caps,
        }

    aggregate_caps = {
        str(cap): summarize_rows(aggregate_by_cap[str(cap)]) for cap in CAPS
    }
    return {
        "schema": SCHEMA,
        "contains_secrets": False,
        "artifact_sha256": next(iter(artifact_hashes)),
        "iotox_binary_sha256": next(iter(binary_hashes)),
        "proof_count": len(proof_records),
        "proofs": sorted(proof_records, key=lambda item: str(item["proof"])),
        "routes": route_results,
        "aggregate": {
            "throughput_winner_cap": best_cap(aggregate_caps),
            "caps": aggregate_caps,
        },
        "scope": {
            "single_construction_host": True,
            "physical_hosts": 0,
            "confidence_interval_qualified": False,
            "automatic_profile_selected": False,
        },
    }


def self_test() -> None:
    rows = [
        {
            "duration_ms": 20,
            "artifact_bps": 400,
            "max_active_lanes": 2,
            "cpu_ticks": 10,
            "resident_high_water_kib": 100,
            "transport_iterations": 20,
        },
        {
            "duration_ms": 22,
            "artifact_bps": 420,
            "max_active_lanes": 2,
            "cpu_ticks": 12,
            "resident_high_water_kib": 110,
            "transport_iterations": 18,
        },
    ]
    summary = summarize_rows(rows)
    require(
        summary["artifact_bps"]
        == {
            "samples": 2,
            "minimum": 400,
            "maximum": 420,
            "sum": 820,
            "mean_denominator": 2,
            "mean_floor": 410,
        },
        "exact distribution summary drifted",
    )
    synthetic = {
        str(cap): {
            "artifact_bps": exact_distribution(
                [100 + cap, 100 + cap]
            )
        }
        for cap in CAPS
    }
    require(best_cap(synthetic) == 8, "winner selection drifted")
    print("content-lane counterbalance analyzer self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("proof", nargs="*", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--output", type=Path)
    mode.add_argument("--verify-report", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        require(
            not arguments.proof
            and arguments.output is None
            and arguments.verify_report is None,
            "--self-test accepts no proof or report",
        )
        self_test()
        return 0
    require(
        arguments.output is not None or arguments.verify_report is not None,
        "--output or --verify-report is required",
    )
    result = analyze(arguments.proof)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.verify_report is not None:
        require(
            load_json(arguments.verify_report) == result
            and arguments.verify_report.read_bytes() == rendered.encode("utf-8"),
            "counterbalance report does not match the verified proof corpus",
        )
        print("content-lane counterbalance report verification: PASS")
        return 0
    assert arguments.output is not None
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AnalysisError, OSError) as error:
        print(f"content-lane counterbalance analysis failed: {error}", file=sys.stderr)
        raise SystemExit(1)
