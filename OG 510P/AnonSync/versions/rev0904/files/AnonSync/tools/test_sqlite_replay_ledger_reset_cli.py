#!/usr/bin/env python3
"""End-to-end oracle for the digest-pinned replay-ledger reset CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Sequence

REQUEST_FORMAT = "anonsync-sqlite-replay-ledger-reset-request-v3"
STATE_FORMAT = "anonsync-sqlite-replay-ledger-reset-state-v2"
RECEIPT_FORMAT = "anonsync-sqlite-replay-ledger-reset-receipt-v4"
COMMIT_PROTOCOL = (
    "sqlite-wal-begin-immediate-exact-state-in-place-no-namespace-delete"
)
RECOVERY_PROTOCOL = (
    "replay-exact-digest-pinned-request-to-fresh-immutable-receipt-path"
)
ZERO_COUNTS = {
    "durable_line_count": 0,
    "durable_head_hash": "GENESIS",
    "effect_transition_line_count": 0,
    "effect_transition_head_hash": "GENESIS",
    "ledger_entry_rows": 0,
    "effect_transition_rows": 0,
    "effect_outbox_rows": 0,
    "ingress_sender_replay_rows": 0,
}


class Oracle:
    def __init__(self) -> None:
        self.checks = 0

    def require(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise RuntimeError(message)

    def run(
        self,
        command: Sequence[os.PathLike[str] | str],
        expected_returncode: int,
        label: str,
    ) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [os.fspath(item) for item in command],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        self.require(
            completed.returncode == expected_returncode,
            f"{label} returned {completed.returncode}, expected "
            f"{expected_returncode}; stdout={completed.stdout!r}; "
            f"stderr={completed.stderr!r}",
        )
        return completed


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path} did not contain a JSON object")
    return value


def write_request(
    path: Path,
    state: dict[str, Any],
    intent_id: str,
    operator_id: str,
    reason: str,
) -> tuple[dict[str, Any], str]:
    request = {
        "format": REQUEST_FORMAT,
        "backend_name": "sqlite-wal",
        "ledger_path": state["ledger_path"],
        "reset_intent_id": intent_id,
        "operator_id": operator_id,
        "reason": reason,
        "expected": state["expected"],
    }
    encoded = (json.dumps(request, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    path.write_bytes(encoded)
    return request, hashlib.sha256(encoded).hexdigest()


def inspect(
    oracle: Oracle,
    core: Path,
    ledger: Path,
    report: Path,
    label: str,
) -> dict[str, Any]:
    oracle.run(
        [
            core,
            "--ledger-reset-state",
            ledger,
            "--ledger-reset-state-report",
            report,
        ],
        0,
        label,
    )
    state = load_json(report)
    oracle.require(state.get("format") == STATE_FORMAT, f"{label} format drift")
    oracle.require(
        state.get("backend_name") == "sqlite-wal", f"{label} backend drift"
    )
    oracle.require(
        Path(str(state.get("ledger_path"))) == ledger.resolve(),
        f"{label} path was not exact and normalized",
    )
    expected = state.get("expected")
    oracle.require(isinstance(expected, dict), f"{label} expected state missing")
    namespace = expected.get("namespace_identity")
    oracle.require(
        isinstance(namespace, dict), f"{label} namespace identity missing"
    )
    expected_namespace_fields = {
        "parent_device",
        "parent_inode",
        "database_device",
        "database_inode",
    }
    oracle.require(
        set(namespace) == expected_namespace_fields,
        f"{label} namespace identity fields drifted",
    )
    parsed_namespace: dict[str, int] = {}
    for field in sorted(expected_namespace_fields):
        encoded = namespace.get(field)
        oracle.require(
            isinstance(encoded, str)
            and encoded.isdigit()
            and (encoded == "0" or not encoded.startswith("0")),
            f"{label} {field} was not canonical uint64 decimal text",
        )
        parsed = int(encoded)
        oracle.require(
            0 <= parsed <= (1 << 64) - 1,
            f"{label} {field} exceeded uint64 range",
        )
        parsed_namespace[field] = parsed
    database_stat = ledger.stat()
    parent_stat = ledger.parent.stat()
    oracle.require(
        parsed_namespace["database_device"] == database_stat.st_dev
        and parsed_namespace["database_inode"] == database_stat.st_ino,
        f"{label} did not bind the inspected database object",
    )
    oracle.require(
        parsed_namespace["parent_device"] == parent_stat.st_dev
        and parsed_namespace["parent_inode"] == parent_stat.st_ino,
        f"{label} did not bind the inspected parent directory",
    )
    observation = state.get("observation")
    oracle.require(isinstance(observation, dict), f"{label} observation missing")
    owner_generation = str(observation.get("connection_owner_generation", ""))
    oracle.require(
        owner_generation.isdigit() and int(owner_generation) > 0,
        f"{label} owner generation was not positive decimal evidence",
    )
    return state


def assert_empty_state(
    oracle: Oracle, state: dict[str, Any], identity: str, label: str
) -> None:
    expected = state["expected"]
    oracle.require(
        expected.get("ledger_instance_id") == identity,
        f"{label} durable identity did not equal reset receipt",
    )
    for field, value in ZERO_COUNTS.items():
        oracle.require(expected.get(field) == value, f"{label} {field} not empty")


def verify_receipt(
    oracle: Oracle,
    receipt: dict[str, Any],
    request: dict[str, Any],
    request_sha256: str,
) -> str:
    oracle.require(
        set(receipt)
        == {
            "format",
            "backend_name",
            "durable_outcome",
            "request_sha256",
            "reset_intent_id",
            "operator_id",
            "reason_sha256",
            "ledger_path",
            "prior",
            "new",
            "commit_protocol",
            "recovery_protocol",
            "reset_receipt_sha256",
        },
        "receipt fields drifted or reintroduced attempt-local observations",
    )
    oracle.require(receipt.get("format") == RECEIPT_FORMAT, "receipt format drift")
    oracle.require(receipt.get("backend_name") == "sqlite-wal", "receipt backend drift")
    oracle.require(
        receipt.get("durable_outcome") == "committed",
        "receipt durable event classification drift",
    )
    oracle.require(
        receipt.get("request_sha256") == request_sha256,
        "receipt did not bind exact request bytes",
    )
    oracle.require(
        receipt.get("reset_intent_id") == request["reset_intent_id"],
        "receipt did not bind reset intent",
    )
    oracle.require(
        receipt.get("operator_id") == request["operator_id"],
        "receipt did not bind operator",
    )
    oracle.require(
        receipt.get("reason_sha256")
        == hashlib.sha256(request["reason"].encode("utf-8")).hexdigest(),
        "receipt did not bind exact reason bytes",
    )
    oracle.require(
        receipt.get("ledger_path") == request["ledger_path"],
        "receipt did not bind normalized ledger path",
    )
    oracle.require(
        receipt.get("prior") == request["expected"],
        "receipt prior evidence did not reproduce exact request expectation",
    )
    new_state = receipt.get("new")
    oracle.require(isinstance(new_state, dict), "receipt new state missing")
    identity = str(new_state.get("ledger_instance_id", ""))
    oracle.require(
        len(identity) == 64 and identity == identity.lower(),
        "receipt identity was not lowercase SHA-256 text",
    )
    oracle.require(
        receipt.get("reset_receipt_sha256") == identity,
        "durable reset receipt and new ledger identity diverged",
    )
    for field, value in ZERO_COUNTS.items():
        oracle.require(new_state.get(field) == value, f"receipt {field} not empty")
    oracle.require(
        receipt.get("commit_protocol") == COMMIT_PROTOCOL,
        "receipt commit protocol drift",
    )
    oracle.require(
        receipt.get("recovery_protocol") == RECOVERY_PROTOCOL,
        "receipt recovery protocol drift",
    )
    return identity


def seed(oracle: Oracle, fixture: Path, ledger: Path, label: str) -> None:
    completed = oracle.run([fixture, "--seed-ledger", ledger], 0, label)
    oracle.require(
        completed.stdout.strip() == ledger.resolve().as_posix(),
        f"{label} did not report exact seeded path",
    )


def exercise_committed_path(
    oracle: Oracle, core: Path, fixture: Path, root: Path
) -> None:
    ledger = (root / "committed.sqlite").resolve()
    seed(oracle, fixture, ledger, "seed committed-path ledger")
    inode_before = ledger.stat().st_ino

    main_alias_report = oracle.run(
        [
            core,
            "--ledger-reset-state",
            ledger,
            "--ledger-reset-state-report",
            ledger,
        ],
        1,
        "reject state report over ledger main file",
    )
    oracle.require(
        "refuses publication inside the SQLite ledger namespace"
        in main_alias_report.stderr,
        "state report main-file alias did not fail at the namespace fence",
    )
    oracle.require(
        ledger.stat().st_ino == inode_before,
        "state report main-file alias replaced the ledger",
    )

    wal_alias = Path(str(ledger) + "-wal")
    wal_alias_report = oracle.run(
        [
            core,
            "--ledger-reset-state",
            ledger,
            "--ledger-reset-state-report",
            wal_alias,
        ],
        1,
        "reject state report over ledger WAL name",
    )
    oracle.require(
        "refuses publication inside the SQLite ledger namespace"
        in wal_alias_report.stderr,
        "state report sidecar alias did not fail at the namespace fence",
    )
    oracle.require(
        not wal_alias.exists(),
        "state report sidecar alias created a WAL-named output",
    )

    hardlink_report = root / "state-report-hardlink.sqlite"
    os.link(ledger, hardlink_report)
    hardlink_alias_report = oracle.run(
        [
            core,
            "--ledger-reset-state",
            ledger,
            "--ledger-reset-state-report",
            hardlink_report,
        ],
        1,
        "reject state report through ledger hardlink",
    )
    oracle.require(
        "refuses publication inside the SQLite ledger namespace"
        in hardlink_alias_report.stderr,
        "state report hardlink alias did not fail at the object-equivalence fence",
    )
    oracle.require(
        hardlink_report.stat().st_ino == inode_before,
        "state report hardlink alias replaced the aliased object",
    )
    hardlink_report.unlink()

    state = inspect(
        oracle, core, ledger, root / "state-before.json", "inspect committed path"
    )
    for field in (
        "ledger_entry_rows",
        "effect_transition_rows",
        "effect_outbox_rows",
        "ingress_sender_replay_rows",
    ):
        oracle.require(state["expected"].get(field) == 1, f"fixture {field} drift")

    reason = "focused CLI exact-state reset"
    request_path = root / "request.json"
    request, request_sha256 = write_request(
        request_path,
        state,
        "cli-reset-001",
        "focused-cli-operator",
        reason,
    )
    request_bytes = request_path.read_bytes()

    main_alias_receipt = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            ledger,
        ],
        1,
        "reject reset receipt over ledger main file",
    )
    oracle.require(
        "refuses publication inside the SQLite ledger namespace"
        in main_alias_receipt.stderr,
        "reset receipt main-file alias did not fail before the reset effect",
    )

    sidecar_alias_receipt = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            Path(str(ledger) + "-shm"),
        ],
        1,
        "reject reset receipt over ledger SHM name",
    )
    oracle.require(
        "refuses publication inside the SQLite ledger namespace"
        in sidecar_alias_receipt.stderr,
        "reset receipt sidecar alias did not fail before the reset effect",
    )

    hardlink_receipt = root / "receipt-hardlink.sqlite"
    os.link(ledger, hardlink_receipt)
    hardlink_alias_receipt = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            hardlink_receipt,
        ],
        1,
        "reject reset receipt through ledger hardlink",
    )
    oracle.require(
        "refuses publication inside the SQLite ledger namespace"
        in hardlink_alias_receipt.stderr,
        "reset receipt hardlink alias did not fail at the object-equivalence fence",
    )
    oracle.require(
        hardlink_receipt.stat().st_ino == inode_before,
        "reset receipt hardlink alias replaced the aliased ledger object",
    )
    hardlink_receipt.unlink()

    same_request_receipt = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            request_path,
        ],
        1,
        "reject reset receipt over its request file",
    )
    oracle.require(
        "must not alias its digest-pinned request" in same_request_receipt.stderr,
        "reset receipt/request lexical alias did not fail before request read",
    )
    oracle.require(
        request_path.read_bytes() == request_bytes,
        "reset receipt/request lexical alias changed pinned request bytes",
    )

    request_hardlink = root / "request-hardlink-receipt.json"
    os.link(request_path, request_hardlink)
    request_hardlink_receipt = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            request_hardlink,
        ],
        1,
        "reject reset receipt through request hardlink",
    )
    oracle.require(
        "must not alias its digest-pinned request"
        in request_hardlink_receipt.stderr,
        "reset receipt/request hardlink alias did not fail at object equivalence",
    )
    oracle.require(
        request_hardlink.read_bytes() == request_bytes,
        "reset receipt/request hardlink alias changed pinned request bytes",
    )
    request_hardlink.unlink()

    state_after_alias_rejections = inspect(
        oracle,
        core,
        ledger,
        root / "state-after-alias-rejections.json",
        "inspect after reset publication alias rejections",
    )
    oracle.require(
        state_after_alias_rejections["expected"] == state["expected"],
        "publication alias rejection mutated exact ledger state",
    )
    oracle.require(
        ledger.stat().st_ino == inode_before,
        "publication alias rejection replaced the ledger namespace",
    )

    wrong_pin = "0" * 64
    if wrong_pin == request_sha256:
        wrong_pin = "1" * 64
    wrong_receipt = root / "wrong-pin-receipt.json"
    wrong = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            wrong_pin,
            "--ledger-reset-receipt",
            wrong_receipt,
        ],
        1,
        "reject wrong request digest",
    )
    oracle.require(
        "digest pin mismatch" in wrong.stderr,
        "wrong request pin did not fail at the digest boundary",
    )
    oracle.require(not wrong_receipt.exists(), "wrong pin published a receipt")
    state_after_wrong_pin = inspect(
        oracle,
        core,
        ledger,
        root / "state-after-wrong-pin.json",
        "inspect after wrong pin",
    )
    oracle.require(
        state_after_wrong_pin["expected"] == state["expected"],
        "wrong request pin changed ledger state",
    )

    occupied_receipt = root / "occupied-receipt.json"
    occupied_bytes = b"unrelated existing evidence must survive\n"
    occupied_receipt.write_bytes(occupied_bytes)
    occupied_inode = occupied_receipt.stat().st_ino
    occupied_denial = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            occupied_receipt,
        ],
        1,
        "reject reset before mutation when immutable receipt name is occupied",
    )
    oracle.require(
        "immutable create-new final path already exists" in occupied_denial.stderr
        and "before a durable transition was observed" in occupied_denial.stderr,
        "occupied immutable receipt did not deny before the reset effect",
    )
    oracle.require(
        occupied_receipt.read_bytes() == occupied_bytes
        and occupied_receipt.stat().st_ino == occupied_inode,
        "occupied immutable receipt bytes or inode were replaced",
    )
    state_after_occupied_denial = inspect(
        oracle,
        core,
        ledger,
        root / "state-after-occupied-denial.json",
        "inspect after occupied immutable receipt denial",
    )
    oracle.require(
        state_after_occupied_denial["expected"] == state["expected"],
        "occupied immutable receipt denial changed exact ledger state",
    )

    receipt_path = root / "receipt.json"
    oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            receipt_path,
        ],
        0,
        "commit exact reset",
    )
    receipt = load_json(receipt_path)
    identity = verify_receipt(oracle, receipt, request, request_sha256)
    receipt_bytes = receipt_path.read_bytes()
    receipt_inode = receipt_path.stat().st_ino
    oracle.require(
        ledger.stat().st_ino == inode_before,
        "reset replaced the SQLite namespace instead of mutating in place",
    )

    state_after = inspect(
        oracle, core, ledger, root / "state-after.json", "inspect committed reset"
    )
    assert_empty_state(oracle, state_after, identity, "committed reset")

    occupied_retry = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            receipt_path,
        ],
        1,
        "reject reuse of an immutable receipt name",
    )
    oracle.require(
        "immutable create-new final path already exists" in occupied_retry.stderr
        and "before a durable transition was observed" in occupied_retry.stderr,
        "immutable receipt-name reuse was not denied at preflight",
    )
    oracle.require(
        receipt_path.read_bytes() == receipt_bytes
        and receipt_path.stat().st_ino == receipt_inode,
        "immutable receipt-name reuse changed published evidence",
    )

    replay_receipt_path = root / "receipt-replay.json"
    oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            replay_receipt_path,
        ],
        0,
        "recover exact committed reset",
    )
    replay_receipt = load_json(replay_receipt_path)
    replay_identity = verify_receipt(
        oracle, replay_receipt, request, request_sha256
    )
    oracle.require(replay_identity == identity, "idempotent replay minted a new receipt")
    oracle.require(
        replay_receipt_path.read_bytes() == receipt_bytes,
        "first execution and exact recovery emitted different receipt bytes",
    )

    original_bytes = (request_path).read_bytes()
    (request_path).write_bytes(original_bytes + b" ")
    tampered_receipt = root / "tampered-receipt.json"
    oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            tampered_receipt,
        ],
        1,
        "reject request bytes changed after pin",
    )
    oracle.require(not tampered_receipt.exists(), "tampered request published receipt")
    state_after_tamper = inspect(
        oracle,
        core,
        ledger,
        root / "state-after-tamper.json",
        "inspect after tampered request",
    )
    assert_empty_state(oracle, state_after_tamper, identity, "tamper rejection")

    legacy = oracle.run([core, "--ledger-reset"], 64, "reject legacy reset flag")
    oracle.require(
        "ordinary open must not mint destructive authority" in legacy.stderr,
        "legacy reset rejection did not explain the authority boundary",
    )

    (request_path).write_bytes(original_bytes)
    isolated = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            root / "isolated-receipt.json",
            "--ledger",
            ledger,
        ],
        64,
        "reject reset combined with ordinary command state",
    )
    oracle.require(
        "accepts exactly three flag/value pairs" in isolated.stderr,
        "standalone reset isolation rejection drifted",
    )

    appended = oracle.run(
        [fixture, "--append-after-reset", ledger],
        0,
        "append legitimate state after reset",
    )
    oracle.require(
        appended.stdout.strip() == ledger.as_posix(),
        "post-reset append fixture did not report the exact ledger path",
    )
    advanced_receipt_path = root / "receipt-advanced-recovery.json"
    oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            advanced_receipt_path,
        ],
        0,
        "recover committed receipt after later state",
    )
    advanced_receipt = load_json(advanced_receipt_path)
    advanced_identity = verify_receipt(
        oracle, advanced_receipt, request, request_sha256
    )
    oracle.require(
        advanced_identity == identity,
        "advanced-state receipt recovery changed committed identity",
    )
    oracle.require(
        advanced_receipt_path.read_bytes() == receipt_bytes,
        "later-state recovery leaked attempt-local observations into receipt bytes",
    )
    advanced_state = inspect(
        oracle,
        core,
        ledger,
        root / "state-after-advanced-recovery.json",
        "inspect after advanced receipt recovery",
    )
    oracle.require(
        advanced_state["expected"].get("ledger_instance_id") == identity,
        "advanced receipt recovery lost durable receipt identity",
    )
    oracle.require(
        advanced_state["expected"].get("ledger_entry_rows") == 1
        and advanced_state["expected"].get("effect_outbox_rows") == 1
        and advanced_state["expected"].get("durable_line_count") == 1,
        "replayed old reset erased legitimate post-reset state",
    )


def exercise_lost_receipt_path(
    oracle: Oracle, core: Path, fixture: Path, root: Path
) -> None:
    ledger = (root / "preflight-symlink.sqlite").resolve()
    seed(oracle, fixture, ledger, "seed preflight-symlink ledger")
    state = inspect(
        oracle,
        core,
        ledger,
        root / "preflight-symlink-state-before.json",
        "inspect preflight-symlink path",
    )
    request_path = root / "preflight-symlink-request.json"
    request, request_sha256 = write_request(
        request_path,
        state,
        "cli-reset-002",
        "focused-cli-operator",
        "prove occupied output denial precedes destructive reset authority",
    )

    victim = root / "publication-victim.txt"
    victim.write_text("immutable victim bytes\n", encoding="utf-8")
    receipt_path = root / "preflight-symlink-receipt.json"
    receipt_path.symlink_to(victim)
    failed_preflight = oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            receipt_path,
        ],
        1,
        "deny symlink receipt before destructive reset",
    )
    oracle.require(
        "before a durable transition was observed" in failed_preflight.stderr
        and "final path must not be a symlink" in failed_preflight.stderr,
        "symlink receipt did not fail at the pre-transition publication fence",
    )
    oracle.require(
        victim.read_text(encoding="utf-8") == "immutable victim bytes\n",
        "receipt preflight followed or changed a symlink victim",
    )
    post_denial = inspect(
        oracle,
        core,
        ledger,
        root / "preflight-symlink-state-after-denial.json",
        "inspect reset state after symlink preflight denial",
    )
    oracle.require(
        post_denial["expected"] == state["expected"],
        "symlink receipt preflight denial changed exact ledger state",
    )

    receipt_path.unlink()
    fresh_receipt_path = root / "preflight-symlink-fresh-receipt.json"
    oracle.run(
        [
            core,
            "--ledger-reset-request",
            request_path,
            "--ledger-reset-request-sha256",
            request_sha256,
            "--ledger-reset-receipt",
            fresh_receipt_path,
        ],
        0,
        "commit reset after selecting a fresh absent receipt path",
    )
    recovered = load_json(fresh_receipt_path)
    recovered_identity = verify_receipt(
        oracle, recovered, request, request_sha256
    )
    post_commit = inspect(
        oracle,
        core,
        ledger,
        root / "preflight-symlink-state-after-commit.json",
        "inspect reset after fresh-path publication",
    )
    assert_empty_state(
        oracle, post_commit, recovered_identity,
        "fresh-path reset after symlink denial",
    )
    oracle.require(
        recovered_identity != state["expected"]["ledger_instance_id"],
        "fresh-path reset did not rotate durable identity",
    )
    oracle.require(
        not receipt_path.exists(),
        "fresh-path reset recreated the formerly occupied symlink name",
    )
    oracle.require(
        victim.read_text(encoding="utf-8") == "immutable victim bytes\n",
        "fresh-path recovery changed the former symlink victim",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    args = parser.parse_args()
    core = args.core.resolve()
    fixture = args.fixture.resolve()
    oracle = Oracle()
    try:
        oracle.require(core.is_file(), "core executable is missing")
        oracle.require(fixture.is_file(), "fixture executable is missing")
        with tempfile.TemporaryDirectory(prefix="anonsync-reset-cli-") as directory:
            root = Path(directory).resolve()
            exercise_committed_path(oracle, core, fixture, root)
            exercise_lost_receipt_path(oracle, core, fixture, root)
        print(f"anonsync_sqlite_replay_ledger_reset_cli_test checks={oracle.checks}")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(
            "anonsync_sqlite_replay_ledger_reset_cli_test failure after "
            f"{oracle.checks} checks: {error}",
            file=os.sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
