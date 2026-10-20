#!/usr/bin/env python3
"""Summarize verified Sandwurm Ratox total-route-loss captures.

This analyzer rechecks the measurement-specific join across the pair manifest,
controller lifecycle, raw terminal/heartbeat captures, host detach journal, and
strict-SOCKS containment.  It complements, rather than replaces, the complete
pair-proof verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path


SCHEMA = "iotox.ratox-route-loss-analysis.v1"
SCENARIO = "ratox-route-loss"
ROUTES = ("direct-udp", "forced-tcp", "tox-tor")
CONNECTIONS = {"direct-udp": "udp", "forced-tcp": "tcp", "tox-tor": "tcp"}
SEEDS = {"vm-iotoxc": 20_260_829, "vm-iotoxd": 20_260_830}
SHA256 = re.compile(r"[0-9a-f]{64}")
REVISION = re.compile(r"[0-9a-f]{40}")
SESSION = re.compile(r"[0-9a-f]{32}")


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
        raise AnalysisError(f"cannot read canonical JSON {path}: {error}") from error
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def parse_capture(
    path: Path, schema: str, row_width: int
) -> tuple[str, list[list[str]]]:
    require(path.is_file() and not path.is_symlink(), f"missing capture: {path}")
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except (OSError, UnicodeError) as error:
        raise AnalysisError(f"cannot read ASCII capture {path}: {error}") from error
    metadata: dict[str, str] = {}
    rows: list[list[str]] = []
    for line in lines:
        fields = line.split("\t")
        if fields[0] == "sample":
            require(len(fields) == row_width, f"sample shape drifted in {path}")
            rows.append(fields)
        else:
            require(len(fields) == 2 and fields[0] not in metadata,
                    f"metadata is noncanonical in {path}")
            metadata[fields[0]] = fields[1]
    require(set(metadata) == {"peer-public-key-sha256", "samples", "schema"},
            f"capture metadata drifted in {path}")
    require(metadata["schema"] == schema and metadata["samples"] == "2",
            f"capture declaration drifted in {path}")
    require(SHA256.fullmatch(metadata["peer-public-key-sha256"]) is not None,
            f"peer commitment is invalid in {path}")
    require(len(rows) == 2, f"capture rows are incomplete in {path}")
    return metadata["peer-public-key-sha256"], rows


def lifecycle_metrics(lifecycle: dict) -> dict:
    initial = lifecycle.get("initial")
    loss = lifecycle.get("loss")
    recovery = lifecycle.get("recovery")
    require(all(isinstance(value, dict) for value in (initial, loss, recovery)),
            "route-loss lifecycle phases are absent")
    assert isinstance(initial, dict)
    assert isinstance(loss, dict)
    assert isinstance(recovery, dict)
    required_ints = (
        initial.get("online_epoch"),
        initial.get("incarnation"),
        initial.get("generation"),
        initial.get("input_sequence"),
        initial.get("output_sequence"),
        loss.get("release_us"),
        loss.get("heartbeat_started_us"),
        loss.get("heartbeat_deadline_us"),
        loss.get("heartbeat_timeout_us"),
        loss.get("controller_outcome_us"),
        recovery.get("online_epoch"),
        recovery.get("incarnation"),
        recovery.get("generation"),
        recovery.get("input_sequence"),
        recovery.get("output_sequence"),
        recovery.get("release_us"),
        recovery.get("route_ready_us"),
        recovery.get("resume_opened_us"),
    )
    require(all(isinstance(value, int) and value >= 0 for value in required_ints),
            "route-loss lifecycle contains a noncanonical counter")
    require(
        initial["session_state"] == "confirmed"
        and initial["online_epoch"] > 0
        and initial["generation"] == 1
        and initial["input_sequence"] == initial["output_sequence"] == 1,
        "initial route-loss identity is invalid",
    )
    offline = loss.get("offline")
    require(
        loss.get("session_state_at_heartbeat_timeout") == "confirmed"
        and loss.get("online_epoch_at_heartbeat_timeout") == initial["online_epoch"]
        and loss.get("controller_outcome") == "error-unavailable"
        and isinstance(offline, dict)
        and offline.get("session_state") == "offline"
        and offline.get("connection") == "offline"
        and offline.get("online_epoch") == initial["online_epoch"],
        "heartbeat/carrier signal separation is invalid",
    )
    require(
        recovery["session_state"] == "confirmed"
        and recovery["online_epoch"] > initial["online_epoch"]
        and recovery["incarnation"] == initial["incarnation"]
        and recovery["generation"] == initial["generation"] + 1
        and recovery["input_sequence"] == recovery["output_sequence"] == 2,
        "route-loss recovery identity is invalid",
    )
    require(
        loss["release_us"] <= loss["heartbeat_started_us"]
        < loss["heartbeat_deadline_us"] < loss["controller_outcome_us"]
        and 1_800_000 <= loss["heartbeat_timeout_us"] <= 3_000_000
        and recovery["release_us"] <= recovery["route_ready_us"]
        <= recovery["resume_opened_us"],
        "route-loss clocks are not ordered",
    )
    return {
        "heartbeat_timeout_us": loss["heartbeat_timeout_us"],
        "heartbeat_deadline_to_offline_us": (
            loss["controller_outcome_us"] - loss["heartbeat_deadline_us"]
        ),
        "route_restore_to_ready_us": (
            recovery["route_ready_us"] - recovery["release_us"]
        ),
        "ready_to_resume_open_us": (
            recovery["resume_opened_us"] - recovery["route_ready_us"]
        ),
        "initial_heartbeat_us": initial.get("heartbeat_us"),
        "initial_terminal_us": initial.get("terminal_us"),
        "recovered_heartbeat_us": recovery.get("heartbeat_us"),
        "recovered_terminal_us": recovery.get("terminal_us"),
    }


def analyze_root(proof_root: Path) -> dict:
    root = proof_root.resolve()
    manifest_path = root / "pair-manifest.json"
    manifest = load_json(manifest_path)
    route = manifest.get("route_mode")
    require(route in ROUTES, "unsupported route mode")
    require(manifest.get("scenario") == SCENARIO and manifest.get("status") == "passed",
            f"proof is not an accepted {SCENARIO} cell")
    connection = CONNECTIONS[route]

    loss_summary = manifest.get("ratox_route_loss")
    require(isinstance(loss_summary, dict), "route-loss summary is absent")
    require(
        loss_summary.get("schema") == "iotox-ratox-route-loss-v1"
        and loss_summary.get("loss_percent") == 100
        and loss_summary.get("heartbeat_timeout_ms") == 2000
        and loss_summary.get("detached_host_snapshot") is True
        and isinstance(loss_summary.get("heartbeat_missed_after_loss_ms"), int)
        and 1_800 <= loss_summary["heartbeat_missed_after_loss_ms"] < 30_000
        and isinstance(loss_summary.get("controller_offline_after_loss_ms"), int)
        and loss_summary["controller_offline_after_loss_ms"]
        > loss_summary["heartbeat_missed_after_loss_ms"]
        and isinstance(loss_summary.get("active_wall_ms"), int)
        and loss_summary["active_wall_ms"]
        >= loss_summary["controller_offline_after_loss_ms"],
        "route-loss parameters drifted",
    )
    qdiscs = loss_summary.get("qdiscs")
    require(isinstance(qdiscs, list) and len(qdiscs) == 2,
            "route-loss qdisc evidence is incomplete")
    require({entry.get("tap") for entry in qdiscs} == set(SEEDS),
            "route-loss TAP set drifted")
    for entry in qdiscs:
        tap = entry.get("tap")
        require(
            entry.get("kind") == "netem"
            and entry.get("loss_percent") == 100
            and entry.get("seed") == SEEDS[tap]
            and isinstance(entry.get("drops"), int)
            and entry["drops"] > 0,
            f"route-loss qdisc evidence is invalid on {tap}",
        )

    receipt_root = root / "client/live/workspace-export/guest-receipts/iotox"
    client = load_json(receipt_root / "pair.json")
    device = load_json(
        root / "device/live/workspace-export/guest-receipts/iotox/pair.json"
    )
    source_revision = client.get("source_revision")
    binary_sha256 = client.get("binary_sha256")
    require(REVISION.fullmatch(str(source_revision)) is not None,
            "client source revision is invalid")
    require(device.get("source_revision") == source_revision,
            "guest source revisions differ")
    require(SHA256.fullmatch(str(binary_sha256)) is not None
            and device.get("binary_sha256") == binary_sha256,
            "guest binary identities differ")

    lifecycle_path = receipt_root / "ratox-route-loss-probe.json"
    lifecycle = load_json(lifecycle_path)
    metrics = lifecycle_metrics(lifecycle)
    initial = lifecycle["initial"]
    loss = lifecycle["loss"]
    recovery = lifecycle["recovery"]
    require(
        lifecycle.get("schema") == "iotox-ratox-route-loss-probe-v1"
        and lifecycle.get("status") == "passed"
        and initial.get("connection") == connection
        and loss.get("carrier_at_heartbeat_timeout") == connection
        and recovery.get("connection") == connection,
        "route-loss lifecycle carrier is invalid",
    )

    terminal_path = receipt_root / "ratox-controller-capture.tsv"
    heartbeat_path = receipt_root / "ratox-heartbeat-capture.tsv"
    terminal_peer, terminal_rows = parse_capture(
        terminal_path, "iotox-ratox-terminal-probe-v1", 11
    )
    heartbeat_peer, heartbeat_rows = parse_capture(
        heartbeat_path, "iotox-ratox-heartbeat-probe-v1", 5
    )
    require(terminal_peer == heartbeat_peer == lifecycle.get("peer_public_key_sha256"),
            "route-loss captures name different peers")
    sessions = [row[5] for row in terminal_rows]
    require(
        all(SESSION.fullmatch(session) is not None for session in sessions)
        and sessions[0] == sessions[1]
        and hashlib.sha256(bytes.fromhex(sessions[0])).hexdigest()
        == lifecycle.get("session_id_sha256"),
        "route-loss capture changed session identity",
    )
    for ordinal, (terminal, heartbeat) in enumerate(
        zip(terminal_rows, heartbeat_rows), 1
    ):
        require(terminal[1] == heartbeat[1] == str(ordinal),
                "route-loss capture ordinal is invalid")
        require(heartbeat[4] == terminal[5],
                "route-loss heartbeat changed session identity")
        try:
            terminal_started, terminal_output, terminal_render = map(int, terminal[2:5])
            heartbeat_started, heartbeat_pong = map(int, heartbeat[2:4])
            input_sequence = int(terminal[6])
            output_sequence = int(terminal[8])
        except ValueError as error:
            raise AnalysisError("route-loss capture metric is not decimal") from error
        require(heartbeat_started < heartbeat_pong <= terminal_started
                < terminal_output <= terminal_render,
                "route-loss capture clocks are not ordered")
        require(input_sequence == output_sequence == ordinal,
                "route-loss capture byte position is invalid")
        phase = initial if ordinal == 1 else recovery
        require(
            phase.get("heartbeat_us") == heartbeat_pong - heartbeat_started
            and phase.get("terminal_us") == terminal_output - terminal_started
            and phase.get("render_us") == terminal_render - terminal_output,
            "route-loss lifecycle disagrees with raw timing captures",
        )

    status_path = (
        root / "device/live/workspace-export/guest-receipts/iotox/"
        "ratox-host-loss-status.txt"
    )
    events_path = status_path.with_name("ratox-host-loss-events.txt")
    status = status_path.read_text(encoding="ascii")
    events = events_path.read_text(encoding="ascii")
    for field in (
        "ratox-session-count=1",
        "ratox-live-session-count=1",
        "ratox-running-process-count=1",
        "ratox-attached-session-count=0",
    ):
        require(field in status.splitlines(), f"detached host status lacks {field}")
    require(
        any(
            "kind=peer-detached" in line
            and f"session-id={sessions[0].upper()}" in line
            for line in events.splitlines()
        ),
        "detached host journal lacks the exact peer-detached session",
    )

    containment = manifest.get("route_packet_containment")
    require(isinstance(containment, list), "route containment is not a list")
    if route == "tox-tor":
        require(
            len(containment) == 2
            and all(
                entry.get("tcp_only") is True
                and entry.get("only_proxy_destination") is True
                and entry.get("native_udp_packets") == 0
                and entry.get("direct_bootstrap_packets") == 0
                and entry.get("direct_peer_packets") == 0
                for entry in containment
            ),
            "strict SOCKS containment is incomplete",
        )
    else:
        require(containment == [], "native route claims SOCKS containment")

    return {
        "proof_id": root.name,
        "compact_export": (root / "compact-export.json").is_file(),
        "route_mode": route,
        "source_revision": source_revision,
        "binary_sha256": binary_sha256,
        "manifest_sha256": sha256(manifest_path),
        "lifecycle_sha256": sha256(lifecycle_path),
        "terminal_capture_sha256": sha256(terminal_path),
        "heartbeat_capture_sha256": sha256(heartbeat_path),
        "loss_active_ms": loss_summary.get("active_wall_ms"),
        "heartbeat_warning_after_loss_ms": loss_summary.get(
            "heartbeat_missed_after_loss_ms"
        ),
        "authoritative_offline_after_loss_ms": loss_summary.get(
            "controller_offline_after_loss_ms"
        ),
        "tap_drops": sum(entry["drops"] for entry in qdiscs),
        "captured_ipv4_egress_packets": sum(
            entry.get("egress_ipv4_packets", 0) for entry in containment
        ),
        "strict_socks_containment": route == "tox-tor",
        "metrics": metrics,
    }


def analyze(roots: list[Path]) -> dict:
    require(len(roots) == len(ROUTES), "exactly three proof roots are required")
    runs = [analyze_root(root) for root in roots]
    require({run["route_mode"] for run in runs} == set(ROUTES),
            "proof roots do not cover the exact route matrix")
    require(len({run["binary_sha256"] for run in runs}) == 1,
            "proof roots do not share one product binary")
    runs.sort(key=lambda run: ROUTES.index(run["route_mode"]))
    revisions = sorted({run["source_revision"] for run in runs})
    return {
        "schema": SCHEMA,
        "status": "passed",
        "scenario": SCENARIO,
        "binary_sha256": runs[0]["binary_sha256"],
        "source_revisions": revisions,
        "single_source_revision": len(revisions) == 1,
        "route_count": len(runs),
        "routes": runs,
        "policy": {
            "heartbeat_miss_is_warning_only": True,
            "authoritative_offline_detaches_controller": True,
            "detached_host_pty_is_retained": True,
            "resume_requires_reauthenticated_higher_epoch": True,
            "resume_preserves_session_incarnation_and_byte_positions": True,
            "automatic_route_migration_is_not_qualified": True,
            "generic_socks_is_not_actual_tor": True,
        },
    }


def self_test() -> None:
    lifecycle = {
        "initial": {
            "session_state": "confirmed", "online_epoch": 2,
            "incarnation": 7, "generation": 1,
            "input_sequence": 1, "output_sequence": 1,
            "heartbeat_us": 5, "terminal_us": 10,
        },
        "loss": {
            "release_us": 1, "heartbeat_started_us": 2,
            "heartbeat_deadline_us": 2_000_002,
            "heartbeat_timeout_us": 2_000_000,
            "controller_outcome_us": 30_000_002,
            "session_state_at_heartbeat_timeout": "confirmed",
            "online_epoch_at_heartbeat_timeout": 2,
            "controller_outcome": "error-unavailable",
            "offline": {
                "session_state": "offline", "connection": "offline",
                "online_epoch": 2,
            },
        },
        "recovery": {
            "session_state": "confirmed", "online_epoch": 3,
            "incarnation": 7, "generation": 2,
            "input_sequence": 2, "output_sequence": 2,
            "release_us": 31_000_000, "route_ready_us": 32_000_000,
            "resume_opened_us": 32_010_000,
            "heartbeat_us": 6, "terminal_us": 11,
        },
    }
    metrics = lifecycle_metrics(lifecycle)
    assert metrics["heartbeat_deadline_to_offline_us"] == 28_000_000
    assert metrics["route_restore_to_ready_us"] == 1_000_000
    assert metrics["ready_to_resume_open_us"] == 10_000
    with tempfile.TemporaryDirectory(prefix="iotox-ratox-loss-analysis-test.") as raw:
        capture = Path(raw) / "capture.tsv"
        capture.write_text(
            "peer-public-key-sha256\t" + "ab" * 32 + "\n"
            "samples\t2\n"
            "schema\tiotox-ratox-heartbeat-probe-v1\n"
            "sample\t1\t1\t2\t" + "01" * 16 + "\n"
            "sample\t2\t3\t4\t" + "01" * 16 + "\n",
            encoding="ascii",
        )
        peer, rows = parse_capture(
            capture, "iotox-ratox-heartbeat-probe-v1", 5
        )
        assert peer == "ab" * 32 and len(rows) == 2
    print("ratox route-loss analyzer self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize the exact three-cell Ratox route-loss matrix."
    )
    parser.add_argument("proof_root", nargs="*", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.self_test:
        self_test()
        return 0
    if not arguments.proof_root:
        parser.error("exactly three proof roots are required")
    try:
        print(json.dumps(analyze(arguments.proof_root), indent=2, sort_keys=True))
    except (AnalysisError, OSError, UnicodeError) as error:
        print(f"ratox route-loss analysis failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
