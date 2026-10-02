#!/usr/bin/env python3
"""Audit the retained Sandwurm route-policy population as one seeded campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path


CORE_SCENARIOS = (
    "sync-tree-route-startup-order",
    "sync-tree-route-startup-admission",
    "sync-tree-route-population-loss",
    "sync-tree-route-cancel-race",
    "sync-tree-route-cancel-race-loss-first",
    "sync-tree-route-common-link-fairness",
)
THROUGHPUT = "sync-tree-route-throughput"
ROUTES = ("direct-udp", "forced-tcp")
HEX64 = frozenset("0123456789abcdef")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as source:
        value = json.load(source)
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            checksum.update(block)
    return checksum.hexdigest()


def exact_hash(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in HEX64 for character in value)
    )


def proof(root: Path) -> dict:
    compact = load(root / "compact-export.json")
    require(
        compact.get("schema") == "iotox.sandwurm-pair-compact-export.v0"
        and compact.get("status") == "passed"
        and compact.get("contains_secrets") is False,
        f"invalid compact export: {root}",
    )
    files = compact.get("files")
    require(isinstance(files, dict) and len(files) >= 7, "bad compact file set")
    for relative, expected in files.items():
        require(
            isinstance(relative, str)
            and relative == Path(relative).as_posix()
            and not Path(relative).is_absolute()
            and ".." not in Path(relative).parts
            and exact_hash(expected)
            and digest(root / relative) == expected,
            f"compact file commitment mismatch: {relative}",
        )
    manifest = load(root / "pair-manifest.json")
    require(
        manifest.get("schema") == "iotox.sandwurm-pair-manifest.v0"
        and manifest.get("status") == "passed"
        and manifest.get("receipts_contain_secrets") is False,
        f"invalid pair manifest: {root}",
    )
    require(
        manifest.get("compact_export", {}).get("source_manifest_sha256")
        == compact.get("source_manifest_sha256"),
        "source-manifest commitment mismatch",
    )
    route = manifest.get("route_mode")
    scenario = manifest.get("scenario")
    require(route in ROUTES and scenario in (*CORE_SCENARIOS, THROUGHPUT),
            "proof is outside the route campaign")
    receipts = []
    for role in ("client", "device"):
        path = root / role / "live/workspace-export/guest-receipts/iotox/pair.json"
        receipt = load(path)
        require(
            receipt.get("status") == "passed"
            and receipt.get("route_mode") == route
            and receipt.get("scenario") == scenario
            and receipt.get("contains_secrets") is False,
            f"invalid {role} route receipt",
        )
        receipts.append(receipt)
    return {
        "id": root.name,
        "route": route,
        "scenario": scenario,
        "span_ns": manifest.get("rendezvous_monotonic_span_ns", 0),
        "receipt": receipts[0],
        "binary_sha256": manifest.get("receipts", {}).get("client", {}).get(
            "binary_sha256", ""
        ),
        "manifest_sha256": digest(root / "pair-manifest.json"),
    }


def qualify(root: Path, seed: int) -> dict:
    cells = []
    for candidate in sorted(root.glob("pair.*")):
        if not (candidate / "pair-manifest.json").is_file():
            continue
        manifest = load(candidate / "pair-manifest.json")
        if (
            manifest.get("route_mode") in ROUTES
            and manifest.get("scenario") in (*CORE_SCENARIOS, THROUGHPUT)
        ):
            cells.append(proof(candidate))
    require(cells, "no route-policy proof population found")
    population: dict[tuple[str, str], list[dict]] = {}
    for cell in cells:
        population.setdefault((cell["route"], cell["scenario"]), []).append(cell)
    for route in ROUTES:
        for scenario in CORE_SCENARIOS:
            require(population.get((route, scenario)),
                    f"missing {route}/{scenario} cell")
    require(len(population.get(("direct-udp", THROUGHPUT), [])) >= 3,
            "direct-UDP throughput distribution is too small")
    require(len(population.get(("forced-tcp", THROUGHPUT), [])) >= 1,
            "forced-TCP throughput observation is absent")

    schedule = sorted(
        cells,
        key=lambda cell: hashlib.sha256(
            f"iotox-route-policy-v1:{seed}:{cell['id']}".encode()
        ).digest(),
    )
    timings: set[int] = set()
    artifact_sizes: set[int] = set()
    throughput_samples: list[int] = []
    speedups: list[int] = []
    resource_hashes: set[str] = set()
    for cell in schedule:
        receipt = cell["receipt"]
        for key, value in receipt.items():
            if isinstance(value, int) and value > 0:
                if key.endswith(("delay_ms", "hold_ms")):
                    timings.add(value)
                if key.endswith("artifact_bytes"):
                    artifact_sizes.add(value)
            if key.endswith("resource_sha256") and exact_hash(value):
                resource_hashes.add(value)
        if cell["scenario"] == THROUGHPUT:
            require(receipt.get("sync_tree_route_throughput_observed") is True,
                    "throughput cell lacks positive observation")
            for phase in ("fixed_a", "adaptive_a", "adaptive_b", "fixed_b"):
                value = receipt.get(
                    f"sync_tree_route_throughput_{phase}_duration_ms"
                )
                require(isinstance(value, int) and value > 0,
                        "throughput phase duration is absent")
                throughput_samples.append(value)
            speedup = receipt.get("sync_tree_route_throughput_adaptive_speedup_ppm")
            require(isinstance(speedup, int) and speedup > 0,
                    "adaptive throughput ratio is absent")
            speedups.append(speedup)
    require({250, 500, 750, 1000, 5000, 20000}.issubset(timings),
            "required startup/fault timing strata are absent")
    require(len(artifact_sizes) >= 4 and max(artifact_sizes) >= 16 * 1024 * 1024,
            "larger-object population is absent")
    require(len(throughput_samples) >= 16, "throughput duration population is too small")
    cumulative_ms = sum(int(cell["span_ns"]) // 1_000_000 for cell in cells)
    require(cumulative_ms >= 7_200_000,
            "accepted campaign population is shorter than two cumulative hours")
    schedule_commitment = hashlib.sha256(
        "\n".join(cell["id"] for cell in schedule).encode()
    ).hexdigest()
    return {
        "schema": "iotox.route-policy-campaign.v1",
        "status": "passed",
        "seed": seed,
        "selection_algorithm": "sha256(iotox-route-policy-v1:seed:proof-id)",
        "schedule_sha256": schedule_commitment,
        "cells": len(cells),
        "routes": list(ROUTES),
        "scenarios": sorted({cell["scenario"] for cell in cells}),
        "cumulative_observation_ms": cumulative_ms,
        "timing_strata_ms": sorted(timings),
        "artifact_size_strata_bytes": sorted(artifact_sizes),
        "throughput_phase_samples": len(throughput_samples),
        "throughput_duration_min_ms": min(throughput_samples),
        "throughput_duration_max_ms": max(throughput_samples),
        "adaptive_speedup_ppm_min": min(speedups),
        "adaptive_speedup_ppm_max": max(speedups),
        "resource_commitments": len(resource_hashes),
        "binary_commitments": len({cell["binary_sha256"] for cell in cells}),
        "proof_manifest_set_sha256": hashlib.sha256(
            "\n".join(sorted(cell["manifest_sha256"] for cell in cells)).encode()
        ).hexdigest(),
        "contains_secrets": False,
    }


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def self_test() -> None:
    require(exact_hash("ab" * 32), "digest recognizer failed")
    require(not exact_hash("AB" * 32), "uppercase digest was accepted")
    ids = ["pair.a", "pair.b", "pair.c"]
    first = sorted(ids, key=lambda value: hashlib.sha256(
        f"iotox-route-policy-v1:7:{value}".encode()).digest())
    second = sorted(reversed(ids), key=lambda value: hashlib.sha256(
        f"iotox-route-policy-v1:7:{value}".encode()).digest())
    require(first == second, "seeded schedule depends on discovery order")
    with tempfile.TemporaryDirectory(prefix="iotox-route-campaign-") as raw:
        output = Path(raw) / "receipt.json"
        write(output, {"status": "passed"})
        require(load(output)["status"] == "passed", "atomic receipt failed")
    print("route-policy campaign self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof-root", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--seed", type=int, default=20260901)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    require(args.proof_root is not None and args.evidence is not None,
            "--proof-root and --evidence are required")
    result = qualify(args.proof_root.resolve(), args.seed)
    write(args.evidence.resolve(), result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
