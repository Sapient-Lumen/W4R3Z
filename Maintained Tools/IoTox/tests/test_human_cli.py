#!/usr/bin/env python3
"""Process tests for native human-ergo IoTox commands."""

from __future__ import annotations

import json
import hashlib
import os
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path


_IOTOX_ENVIRONMENT: dict[str, str] | None = None


def iotox_environment() -> dict[str, str]:
    global _IOTOX_ENVIRONMENT
    if _IOTOX_ENVIRONMENT is not None:
        return _IOTOX_ENVIRONMENT.copy()
    environment = os.environ.copy()
    if not environment.get("IOTOX_SODIUM_LIBRARY"):
        candidates = [Path("/run/current-system/sw/lib/libsodium.so")]
        candidates.extend(sorted(Path("/nix/store").glob("*libsodium*/lib/libsodium.so")))
        for candidate in candidates:
            if candidate.is_file():
                environment["IOTOX_SODIUM_LIBRARY"] = str(candidate)
                break
    if not environment.get("IOTOX_ARGON2_LIBRARY"):
        candidates = sorted(Path("/nix/store").glob("*libargon2*/lib/libargon2.so.1"))
        candidates.append(Path("/run/current-system/sw/lib/libargon2.so.1"))
        for candidate in candidates:
            if candidate.is_file():
                environment["IOTOX_ARGON2_LIBRARY"] = str(candidate)
                break
    _IOTOX_ENVIRONMENT = environment
    return environment.copy()


def run(iotox: Path, *args: str, input_text: str | None = None) -> str:
    completed = subprocess.run(
        [str(iotox), *args],
        text=True,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=iotox_environment(),
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {iotox} {' '.join(args)}\n"
            f"{completed.stdout}"
        )
    return completed.stdout


def run_fail(iotox: Path, *args: str, input_text: str | None = None) -> str:
    completed = subprocess.run(
        [str(iotox), *args],
        text=True,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=iotox_environment(),
        check=False,
    )
    if completed.returncode == 0:
        raise AssertionError(
            f"command unexpectedly succeeded: {iotox} {' '.join(args)}\n"
            f"{completed.stdout}"
        )
    return completed.stdout


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def extract_field(output: str, name: str) -> str:
    prefix = f"{name}="
    for line in output.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):]
    raise AssertionError(f"missing field {name} in output:\n{output}")


def recovery_runbook_receipt_text() -> str:
    return (
        "iotox-sync-recovery-runbook-review-v1\n"
        "schema=iotox.sync-recovery-runbook-review.v1\n"
        "status=reviewed\n"
        "content-free=1\n"
        "operator-runbook=present\n"
        "reviewer-label=owner\n"
        f"dataset-selector-sha256={'1' * 64}\n"
        "access=read-write\n"
        "interval-seconds=30\n"
        f"runbook-sha256={'2' * 64}\n"
        "runbook-bytes=128\n"
        "covers-stop-writers-before-restore=1\n"
        "covers-restore-from-versioned-recovery-custody=1\n"
        "covers-verify-before-resuming-sync=1\n"
        "covers-retire-obsolete-writers=1\n"
        "covers-periodic-rehearsal=1\n"
        "accepted-reviewed-runbook=1\n"
        "not-content-custody=1\n"
    )


def create_identity_with_daemon(iotox: Path, root: Path, identity: Path) -> str:
    runtime = root / "identity.runtime"
    command = [
        str(iotox),
        "run",
        "--state",
        str(root / "identity.tox.save"),
        "--identity",
        str(identity),
        "--authority-ledger",
        str(root / "identity.authority.ledger"),
        "--command-store",
        str(root / "identity.commands.store"),
        "--runtime",
        str(runtime),
    ]
    environment = iotox_environment()
    mock_toxcore = environment.get("IOTOX_TEST_MOCK_TOXCORE")
    if mock_toxcore is None:
        candidate = iotox.parent / "libtoxcore-iotox-mock.so"
        mock_toxcore = str(candidate) if candidate.exists() else ""
    if mock_toxcore:
        environment["IOTOX_TOXCORE_LIBRARY"] = mock_toxcore
    else:
        environment.pop("IOTOX_TOXCORE_LIBRARY", None)
    process = subprocess.Popen(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=environment,
    )
    try:
        last_error = ""
        for _ in range(100):
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                raise AssertionError(
                    "identity daemon exited before readiness\n" + output
                )
            try:
                pong = run(iotox, "--runtime", str(runtime), "ping")
                if "pong" in pong:
                    identity_text = run(
                        iotox, "--runtime", str(runtime), "identity")
                    return extract_field(identity_text, "device-public-key")
            except AssertionError as error:
                last_error = str(error)
            time.sleep(0.05)
        raise AssertionError("identity daemon did not become ready\n" + last_error)
    finally:
        if process.poll() is None:
            try:
                run(iotox, "--runtime", str(runtime), "stop")
            except AssertionError:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: test_human_cli.py IOTOX", file=sys.stderr)
        return 2
    iotox = Path(sys.argv[1])

    root_help = run(iotox, "help")
    require("iotox help quickstart" in root_help
            and "iotox help all" in root_help
            and "iotox doctor binary" in root_help,
            "root help lost short human front door")
    require("sync-namespace-template" not in root_help
            and "witness-service-serve" not in root_help,
            "root help regressed to exhaustive command inventory")
    full_help = run(iotox, "help", "all")
    require("sync-namespace-template" in full_help
            and "witness-service-serve" in full_help
            and "completion bash|zsh|fish" in full_help,
            "help all lost exhaustive command inventory")
    binary_doctor = run(iotox, "doctor", "binary")
    require("iotox-binary-source-v1" in binary_doctor
            and "version=0.51.0" in binary_doctor
            and "revision=rev0051" in binary_doctor
            and "cwd-revision-matches-compiled=" in binary_doctor
            and "release-check-command=" in binary_doctor,
            "binary doctor lost source/provenance surface")
    version_source = run(iotox, "version", "--source")
    require("iotox-binary-source-v1" in version_source
            and "build-source-commit=" in version_source,
            "version --source lost binary provenance surface")

    for topic in ("quickstart", "sync", "terminal", "pairing", "self", "person",
                  "routes", "evidence", "shipping", "support",
                  "storage-readiness"):
        output = run(iotox, "help", topic)
        require(f"iotox help {topic}" in output, f"topic help missing {topic}")
        require("Boundary:" in output or "Current product rule:" in output,
                f"topic help lacks boundary language for {topic}")
        require("sync_subscribe" not in output and "sync_publish" not in output,
                f"topic help uses internal capability spelling for {topic}")
        require("RECALL_ROOT_PHRASE" not in output,
                f"topic help suggests RecallRoot in environment for {topic}")
    sync_help = run(iotox, "help", "sync")
    require("cat RECALLROOT.txt | iotox sync share" in sync_help,
            "sync help lost stdin RecallRoot ceremony")
    pairing_help = run(iotox, "help", "pairing")
    require("sync.subscribe,sync.publish" in pairing_help,
            "pairing help lost public sync capability spelling")
    self_help = run(iotox, "help", "self")
    require("--mode self" in self_help and "interactive.terminal" in self_help,
            "self help lost self-mode terminal authority path")
    routes_help = run(iotox, "help", "routes")
    require("route-qualification-check --scope all" in routes_help
            and "silently fall back" in routes_help,
            "routes help lost qualification/nonfallback guidance")
    evidence_help = run(iotox, "help", "evidence")
    require("evidence dossier-plan" in evidence_help
            and "evidence collect sync" in evidence_help
            and "evidence manifest" in evidence_help,
            "evidence help lost dossier/collector/manifest guidance")
    shipping_help = run(iotox, "help", "shipping")
    require("ship-check all stable" in shipping_help
            and "datacube --seed" in shipping_help
            and "datacube --upload" in shipping_help,
            "shipping help lost ship-check/datacube guidance")
    support_help = run(iotox, "help", "support")
    require("support-bundle plan" in support_help
            and "content-free, not information-free" in support_help,
            "support help lost bundle boundary guidance")
    self_swarm_help = run(iotox, "self-swarm", "help")
    require("iotox-self-swarm-help-v1" in self_swarm_help,
            "self-swarm help schema missing")
    require("create-recall-stdin" in self_swarm_help and "grant-plan" in self_swarm_help,
            "self-swarm help lost create/grant path")
    require("grant-recall-stdin" in self_swarm_help and "--expect-route" in self_swarm_help,
            "self-swarm help lost apply/route verification path")
    require("floor-commit" in self_swarm_help and "fanout-plan" in self_swarm_help
            and "readiness-command=" in self_swarm_help
            and "daily-status-command=" in self_swarm_help,
            "self-swarm help lost floor/fanout/readiness surface")
    require("route-policy=not-carried-by-self-roster" in self_swarm_help,
            "self-swarm help lost route-policy boundary")
    person_help = run(iotox, "person", "help")
    require("iotox-person-help-v1" in person_help,
            "person help schema missing")
    require("first-steps=" in person_help
            and "quickstart-command=iotox person quickstart" in person_help
            and "plain-english=" in person_help,
            "person help lost recipe-first surface")
    person_quickstart = run(iotox, "person", "quickstart")
    require("iotox-person-help-v1" in person_quickstart
            and "recipe-create-card=" in person_quickstart,
            "person quickstart alias missing")
    require("card-recall-stdin" in person_help and "message-fanout-recall-stdin" in person_help,
            "person help lost card/fanout surface")
    require("outbox-send-command=" in person_help,
            "person help lost native outbox sender")
    require("outbox-retry-plan-command=" in person_help
            and "card-refresh-plan-command=" in person_help
            and "messenger-plan-command=" in person_help
            and "background-plan-command=" in person_help
            and "graduation-check-command=" in person_help
            and "tox-bridge-graduation-check-command=" in person_help,
            "person help lost background retry/freshness porch")

    overview = run(iotox, "overview")
    require("iotox-overview-v1" in overview, "overview schema missing")
    require("precious-data=blocked" in overview, "overview lost backup boundary")
    overview_json = json.loads(run(iotox, "overview", "--json"))
    require(overview_json["schema"] == "iotox-overview-v1",
            "overview json schema mismatch")
    require(overview_json["storage"]["precious_data"] == "blocked",
            "overview json lost precious-data boundary")
    explanation = run(iotox, "explain", "storage-precious-data-blocked")
    require("iotox-explain-v1" in explanation, "explain schema missing")
    require("precious-data-ready" in explanation or "precious data" in explanation,
            "explain did not render storage boundary")
    for topic in (
        "quickstart",
        "sync",
        "terminal",
        "pairing",
        "service",
        "self",
        "person",
        "routes",
        "evidence",
        "shipping",
        "support",
        "storage-readiness",
    ):
        topic_explanation = run(iotox, "explain", topic)
        require("iotox-explain-v1" in topic_explanation
                and f"topic={topic}" in topic_explanation
                and "safe-next=" in topic_explanation
                and "boundary=" in topic_explanation,
                f"explain topic {topic} lost porch guidance")
    last = run(iotox, "explain", "last")
    require("last-error-store=not-implemented" in last,
            "explain last lost no-hidden-log boundary")

    readiness = run(iotox, "readiness")
    require("iotox-readiness-v1" in readiness, "readiness schema missing")
    require("sync-precious-data=blocked" in readiness,
            "readiness lost sync precious-data boundary")
    require("routes-policy-cards=not-carried-by-self-roster-or-person-card" in readiness,
            "readiness lost route/card policy boundary")
    readiness_privacy = run(iotox, "readiness", "privacy")
    require("routes-toxic-native=default-qualified-forced-tcp-degraded" in readiness_privacy
            and "routes-toxic-tor=evidence-gated" in readiness_privacy
            and "routes-toxic-i2p=evidence-gated" in readiness_privacy
            and "privacy-direct-tor=not-implemented" in readiness_privacy,
            "privacy readiness lost Toxic or direct-overlay route status")
    readiness_json = json.loads(run(iotox, "readiness", "storage", "--json"))
    require(readiness_json["schema"] == "iotox-readiness-v1",
            "readiness json schema mismatch")
    require(readiness_json["storage"]["media_certification"] == "not_an_iotox_goal",
            "readiness json lost storage-media boundary")
    readiness_routes_json = json.loads(run(iotox, "readiness", "routes", "--json"))
    require(readiness_routes_json["routes"]["toxic_native"] == "default-qualified-forced-tcp-degraded",
            "readiness routes json lost Toxic native qualification")
    require(readiness_routes_json["routes"]["toxic_tor"] == "evidence-gated"
            and readiness_routes_json["routes"]["toxic_i2p"] == "evidence-gated",
            "readiness routes json lost Toxic overlay evidence gates")
    route_privacy = run(iotox, "explain", "route-privacy")
    require("iotox-explain-v1" in route_privacy
            and "route-qualification-check --scope all" in route_privacy,
            "route privacy explanation missing")
    route_qualification_blocked = run_fail(
        iotox,
        "route-qualification-check",
        "--scope",
        "toxic",
    )
    require("iotox-route-qualification-check-v1" in route_qualification_blocked
            and "route-qualification=blocked" in route_qualification_blocked
            and "toxic-forced-tcp-proof-command=" in route_qualification_blocked,
            "route qualification check did not fail closed with Toxic recipe")
    route_qualification_ready = run(
        iotox,
        "route-qualification-check",
        "--scope",
        "toxic",
        "--evidence",
        "toxic-native=toxic.default",
        "--evidence",
        "toxic-forced-tcp=toxic.tcp",
        "--evidence",
        "toxic-tor=tor.route",
        "--evidence",
        "toxic-i2p=i2p.route",
        "--evidence",
        "route-nonclaims=review",
        "--evidence",
        "operator-review=owner",
    )
    require("route-qualification=operator-attested" in route_qualification_ready
            and "anonymity-certified=0" in route_qualification_ready
            and "silent-fallback-authorized=0" in route_qualification_ready,
            "route qualification check overclaimed or lost required labels")
    ship_blocked = run_fail(iotox, "ship-check")
    require("iotox-ship-check-v1" in ship_blocked
            and "stable-without-concern=blocked" in ship_blocked
            and "sync-precious-data=blocked" in ship_blocked
            and "terminal-fleet-certification=blocked" in ship_blocked,
            "ship-check stable did not fail closed with explicit blockers")
    ship_preview = run(iotox, "ship-check", "all", "founder-preview")
    require("ship-decision=allowed-with-explicit-nonclaims" in ship_preview
            and "sync-founder-preview=working-copy-with-versioned-recovery-custody" in ship_preview
            and "terminal-root-default=off" in ship_preview
            and "release-plan-command=tools/iotox-repo.sh release-plan founder-preview" in ship_preview
            and "release-check-command=tools/iotox-repo.sh release-check founder-preview" in ship_preview,
            "ship-check founder-preview lost bounded release semantics")
    ship_json = json.loads(run_fail(iotox, "ship-check", "terminal", "stable", "--json"))
    require(ship_json["schema"] == "iotox-ship-check-v1"
            and ship_json["ship_decision"] == "blocked"
            and ship_json["release_plan"] == "tools/iotox-repo.sh release-plan stable"
            and ship_json["release_check"] == "tools/iotox-repo.sh release-check stable --evidence-manifest stable-evidence.manifest"
            and ship_json["stable_evidence"] == "absent"
            and ship_json["terminal"]["fleet_certification"] == "blocked",
            "ship-check json lost stable blocked boundary")
    with tempfile.TemporaryDirectory(prefix="iotox-stable-evidence.") as raw_manifest:
        manifest_root = Path(raw_manifest)
        dossier_plan = run(
            iotox,
            "evidence",
            "dossier-plan",
            "--dataset",
            "/tmp/iotox-dataset",
            "--out",
            str(manifest_root),
            "--terminal-root",
            "/tmp/iotox-root",
            "--peer",
            "alias:self",
        )
        require("iotox-stable-dossier-plan-v1" in dossier_plan
                and "collect-sync-command=iotox evidence collect sync" in dossier_plan
                and "collect-terminal-command=iotox evidence collect terminal" in dossier_plan
                and "ship-check-command=iotox ship-check all stable" in dossier_plan,
                "stable dossier plan lost collect/ship command trail")
        first_receipt = manifest_root / "sync-local-preflight.receipt"
        first_receipt.write_text(
            "iotox-sync-doctor-v4\n"
            "decision=ready\n"
            "mutated=0\n",
            encoding="utf-8",
        )
        first_digest = hashlib.sha256(first_receipt.read_bytes()).hexdigest()
        incomplete_manifest = manifest_root / "incomplete.manifest"
        incomplete_manifest.write_text(
            "schema=iotox.stable-evidence.v1\n"
            "sync.local-preflight=accepted\n"
            "sync.local-preflight.receipt-path=" + first_receipt.name + "\n"
            "sync.local-preflight.receipt-sha256=" + first_digest + "\n",
            encoding="utf-8",
        )
        preview_with_manifest = run_fail(
            iotox,
            "ship-check",
            "all",
            "founder-preview",
            "--evidence-manifest",
            str(incomplete_manifest),
        )
        require("--evidence-manifest is only valid with stable ship-checks" in preview_with_manifest,
                "founder-preview silently accepted stable evidence manifest")
        stable_incomplete = run_fail(
            iotox,
            "ship-check",
            "sync",
            "stable",
            "--evidence-manifest",
            str(incomplete_manifest),
        )
        require("stable-evidence=blocked" in stable_incomplete
                and "stable-evidence-blocker name=sync.storage-readiness status=missing" in stable_incomplete,
                "stable evidence manifest did not fail closed on missing sync gates")
        mismatch_manifest = manifest_root / "mismatch.manifest"
        mismatch_manifest.write_text(
            "schema=iotox.stable-evidence.v1\n"
            "sync.local-preflight=accepted\n"
            "sync.local-preflight.receipt-path=" + first_receipt.name + "\n"
            "sync.local-preflight.receipt-sha256=" + "b" * 64 + "\n",
            encoding="utf-8",
        )
        stable_mismatch = run_fail(
            iotox,
            "ship-check",
            "sync",
            "stable",
            "--evidence-manifest",
            str(mismatch_manifest),
        )
        require("stable-evidence-blocker name=sync.local-preflight status=receipt-sha256-mismatch" in stable_mismatch,
                "stable evidence manifest did not verify receipt sha256")
        semantic_manifest = manifest_root / "semantic.manifest"
        semantic_gates = [
            "sync.local-preflight",
            "sync.storage-readiness",
            "sync.long-soak",
            "sync.recovery-custody",
            "sync.restore-drill",
            "sync.recovery-runbook",
        ]
        semantic_lines = ["schema=iotox.stable-evidence.v1"]
        for gate in semantic_gates:
            receipt_path = manifest_root / f"{gate.replace('.', '-')}.bad-receipt"
            receipt_path.write_text(
                f"accepted stable evidence receipt for {gate}\n",
                encoding="utf-8",
            )
            digest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            semantic_lines.append(f"{gate}=accepted")
            semantic_lines.append(f"{gate}.receipt-path={receipt_path.name}")
            semantic_lines.append(f"{gate}.receipt-sha256={digest}")
        semantic_manifest.write_text("\n".join(semantic_lines) + "\n",
                                     encoding="utf-8")
        stable_semantic_bad = run_fail(
            iotox,
            "ship-check",
            "sync",
            "stable",
            "--evidence-manifest",
            str(semantic_manifest),
        )
        require("stable-evidence-blocker name=sync.storage-readiness status=sync-storage-readiness-invalid" in stable_semantic_bad
                and "stable-evidence-blocker name=sync.recovery-runbook status=sync-recovery-runbook-invalid" in stable_semantic_bad,
                "stable evidence manifest accepted placeholder sync receipts")
        complete_manifest = manifest_root / "complete.manifest"
        gates = [
            "sync.local-preflight",
            "sync.storage-readiness",
            "sync.long-soak",
            "sync.recovery-custody",
            "sync.restore-drill",
            "sync.recovery-runbook",
            "terminal.daily-control",
            "terminal.profile-freshness",
            "terminal.service-supervision",
            "terminal.reconnect-continuity",
            "terminal.cgroup-delegation",
            "terminal.route-loss",
            "terminal.long-soak",
            "terminal.tor-route-loss",
            "terminal.i2p-route-loss",
            "terminal.sudo-policy",
            "terminal.security-review",
            "terminal.activation-decision",
        ]
        lines = ["schema=iotox.stable-evidence.v1"]
        for index, gate in enumerate(gates):
            receipt_path = manifest_root / f"{gate.replace('.', '-')}.receipt"
            if gate == "sync.local-preflight":
                receipt_path.write_text(
                    "iotox-sync-doctor-v4\n"
                    "decision=ready\n"
                    "mutated=0\n",
                    encoding="utf-8",
                )
            elif gate == "sync.storage-readiness":
                receipt_path.write_text(json.dumps({
                    "schema": "iotox.storage-readiness.v1",
                    "status": "ready",
                    "ready_for_precious_data": True,
                    "contains_secrets": False,
                    "accepted_local_storage_science": True,
                }, sort_keys=True) + "\n", encoding="utf-8")
            elif gate == "sync.long-soak":
                receipt_path.write_text(json.dumps({
                    "schema": "iotox.sync-three-writer-sandwurm-verification.v1",
                    "status": "passed",
                    "contains_secrets": False,
                    "soak_campaign": True,
                    "soak_cycles": 289,
                    "soak_elapsed_ms": 115981467,
                }, sort_keys=True) + "\n", encoding="utf-8")
            elif gate == "sync.recovery-custody":
                receipt_path.write_text(json.dumps({
                    "schema": "iotox.sync-backup-custody.v1",
                    "status": "passed",
                    "contains_secrets": False,
                    "backup_independent": False,
                    "custody_class": "same-host-versioned",
                    "immutable_or_versioned": True,
                    "restore_verified": True,
                    "operator_rehearsal_repeatable": True,
                    "recovery_comparison": {
                        "matches": True,
                        "roots_on_distinct_devices": False,
                    },
                    "nonclaims": [
                        "not-storage-media-certification",
                        "not-disk-loss-protection",
                        "not-host-compromise-protection",
                        "not-filesystem-wide-corruption-protection",
                        "not-content-custody",
                    ],
                }, sort_keys=True) + "\n", encoding="utf-8")
            elif gate == "sync.restore-drill":
                receipt_path.write_text(json.dumps({
                    "schema": "iotox.sync-retained-recovery-drill.v1",
                    "status": "passed",
                    "contains_secrets": False,
                    "decision": "match",
                    "local_requirements_satisfied": True,
                    "operator_requirement_satisfied": True,
                    "device_requirement_satisfied": True,
                }, sort_keys=True) + "\n", encoding="utf-8")
            elif gate == "sync.recovery-runbook":
                receipt_path.write_text(
                    recovery_runbook_receipt_text(),
                    encoding="utf-8",
                )
            elif gate == "terminal.service-supervision":
                run(
                    iotox,
                    "service",
                    "status-receipt",
                    "--target",
                    "all",
                    "--root",
                    "/tmp/iotox-daily",
                    "--manager",
                    "systemd-user",
                    "--unit-prefix",
                    "iotox-self",
                    "--binary",
                    str(iotox.resolve()),
                    "--service-manager-state",
                    "active",
                    "--enabled-state",
                    "enabled",
                    "--log-state",
                    "reviewed",
                    "--health-state",
                    "passed",
                    "--upgrade-state",
                    "passed",
                    "--accept-operator-responsibility",
                    "--out",
                    str(receipt_path),
                )
            elif gate == "terminal.long-soak":
                receipt_path.write_text(
                    "\n".join([
                        "iotox-terminal-long-soak-receipt-v1",
                        "schema=iotox.terminal-long-soak-receipt.v1",
                        "result=accepted",
                        "label=terminal.24h",
                        "route=native",
                        "root-sha256=" + "1" * 64,
                        "peer-sha256=" + "2" * 64,
                        "required-seconds=86400",
                        "observed-seconds=86401",
                        "samples=289",
                        "max-sample-gap-seconds=300",
                        "reconnect-attempts=3",
                        "session-generations=1",
                        "failures=0",
                        "stable-evidence-key=terminal.long-soak",
                        "content-free=1",
                        "mutated=0",
                    ]) + "\n",
                    encoding="utf-8",
                )
            else:
                receipt_path.write_text(
                    "\n".join([
                        "iotox-terminal-stable-evidence-receipt-v1",
                        "schema=iotox.terminal-stable-evidence.v1",
                        f"gate={gate}",
                        "status=operator-attested",
                        "label=" + gate.replace(".", "-"),
                        "root-sha256=" + "3" * 64,
                        "peer-sha256=" + "4" * 64,
                        "content-free=1",
                        "repo-certified=0",
                        "mutated=0",
                    ]) + "\n",
                    encoding="utf-8",
                )
            digest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            lines.append(f"{gate}=accepted")
            lines.append(f"{gate}.receipt-path={receipt_path.name}")
            lines.append(f"{gate}.receipt-sha256={digest}")
        complete_manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        stable_ready = run(
            iotox,
            "ship-check",
            "all",
            "stable",
            "--evidence-manifest",
            str(complete_manifest),
        )
        require("ship-decision=allowed-with-evidence-manifest" in stable_ready
                and "stable-without-concern=accepted" in stable_ready
                and "sync-stable=accepted" in stable_ready
                and "terminal-stable=accepted" in stable_ready
                and "terminal-fleet-certification=evidence-attested" in stable_ready,
                "complete stable evidence manifest did not graduate stable gate")
        dossier_status = run(
            iotox,
            "evidence",
            "dossier-status",
            str(manifest_root),
            "--scope",
            "all",
            "--manifest",
            str(complete_manifest),
        )
        require("iotox-stable-dossier-status-v1" in dossier_status
                and "accepted-gates=18/18" in dossier_status
                and "manifest-status=accepted" in dossier_status,
                "stable dossier status did not accept complete evidence directory")
    ship_explain = run(iotox, "explain", "ship-readiness")
    require("iotox-explain-v1" in ship_explain
            and "ship-check all stable" in ship_explain,
            "ship-readiness explanation missing release gate")

    pair_help = run(iotox, "pair-card", "help")
    require("iotox-pair-card-help-v1" in pair_help,
            "pair-card help schema missing")
    require("authority-granted=0" in pair_help,
            "pair-card help lost authority boundary")

    support_plan = run(iotox, "support-bundle", "plan", "./iotox.support")
    require("iotox-support-bundle-plan-v1" in support_plan,
            "support-bundle plan schema missing")
    require("review-before-share=1" in support_plan,
            "support-bundle plan lost review boundary")
    require("ship-check-command=iotox ship-check" in support_plan,
            "support-bundle plan lost release gate")
    require("release-plan-command=tools/iotox-repo.sh release-plan founder-preview" in support_plan,
            "support-bundle plan lost repository release trail")
    require("attestation=0" in support_plan,
            "support-bundle plan overclaimed attestation")

    conflict_summary = run(iotox, "sync-conflicts-summary", "demo")
    require("iotox-sync-conflicts-summary-v1" in conflict_summary,
            "conflict summary schema missing")
    require("agent=offline-or-unavailable" in conflict_summary,
            "conflict summary should be useful offline")
    conflict_explain = run(iotox, "sync-conflict-explain", "demo", "field.txt")
    require("iotox-sync-conflict-explain-v1" in conflict_explain,
            "conflict explain schema missing")
    require("matched=unknown" in conflict_explain,
            "conflict explain should be useful offline")

    with tempfile.TemporaryDirectory(prefix="iotox-human-cli.") as tmp:
        root = Path(tmp) / "root"
        source = Path(tmp) / "source"
        source.mkdir()
        freeze_state = root / "sync-freeze-state"
        freeze = run(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync-freeze",
            "demo",
            "--state",
            str(freeze_state),
            "--reason",
            "test.freeze",
        )
        require("iotox-sync-freeze-v1" in freeze
                and "freeze=active" in freeze
                and "native-cli-mutators-refuse-frozen-namespaces" in freeze,
                "sync freeze did not write honest local record")
        frozen_folder = run_fail(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync",
            "folder-status",
            "demo",
            str(source),
            "read-write",
            "30",
            "--state",
            str(freeze_state),
        )
        require("iotox-sync-folder-status-v1" in frozen_folder
                and "folder-state=paused" in frozen_folder
                and "safe-delete-command=iotox sync safe-delete" in frozen_folder,
                "sync folder-status did not report frozen folder ergonomics")
        freeze_status = run(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync-freeze-status",
            "demo",
            "--state",
            str(freeze_state),
        )
        require("iotox-sync-freeze-status-v1" in freeze_status
                and "freeze=active" in freeze_status,
                "sync freeze status did not see local record")
        watch = run(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync-watch",
            "demo",
            "--samples",
            "1",
            "--interval",
            "1",
            "--state",
            str(freeze_state),
        )
        require("iotox-sync-watch-v1" in watch
                and "phase=frozen-local-record" in watch
                and "status-command=iotox --runtime" in watch,
                "sync watch did not report frozen offline state")
        grouped_watch = run(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync",
            "watch",
            "demo",
            "--samples",
            "1",
            "--interval",
            "1",
            "--state",
            str(freeze_state),
        )
        require("iotox-sync-watch-v1" in grouped_watch,
                "grouped sync watch alias missing")
        unfreeze = run(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync-unfreeze",
            "demo",
            "--state",
            str(freeze_state),
            "--reason",
            "test.resume",
        )
        require("iotox-sync-unfreeze-v1" in unfreeze
                and "freeze=inactive" in unfreeze,
                "sync unfreeze did not update local record")
        folder_status = run(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync",
            "folder-status",
            "demo",
            str(source),
            "read-write",
            "30",
            "--state",
            str(freeze_state),
        )
        require("iotox-sync-folder-status-v1" in folder_status
                and "folder-state=ready" in folder_status
                and "health-command=iotox sync-health demo cached" in folder_status
                and "precious-status-command=iotox sync precious-status" in folder_status,
                "sync folder-status did not produce the daily healthy command set")
        delete_target = source / "obsolete.txt"
        delete_target.write_text("old bytes\n", encoding="utf-8")
        quarantined = run(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync",
            "safe-delete",
            "demo",
            str(delete_target),
            "--quarantine-root",
            str(root / "delete-quarantine"),
            "--reason",
            "human-cli",
        )
        require("iotox-sync-safe-delete-v1" in quarantined
                and "mutated=local-quarantine" in quarantined,
                "sync safe-delete did not quarantine the target")
        quarantine_path = Path(extract_field(quarantined, "quarantine"))
        receipt_path = Path(extract_field(quarantined, "receipt"))
        require(quarantine_path.exists()
                and not delete_target.exists()
                and receipt_path.exists(),
                "sync safe-delete did not leave recoverable quarantine evidence")
        guarded_target = source / "guarded.txt"
        guarded_target.write_text("guarded bytes\n", encoding="utf-8")
        default_frozen = run(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync-freeze",
            "guarded",
            "--reason",
            "test.guard",
        )
        require("freeze=active" in default_frozen,
                "sync freeze did not write default runtime freeze record")
        refused_delete = run_fail(
            iotox,
            "--runtime",
            str(root / "runtime"),
            "sync",
            "safe-delete",
            "guarded",
            str(guarded_target),
            "--quarantine-root",
            str(root / "delete-quarantine"),
        )
        require("is frozen; refused sync safe-delete" in refused_delete
                and guarded_target.exists(),
                "sync safe-delete did not honor the native freeze guard")
        plan = run(
            iotox,
            "init",
            "plan",
            "--root",
            str(root),
            "--mode",
            "self",
            "--enable-sync",
        )
        require("iotox-init-plan-v1" in plan, "init plan schema missing")
        require("mutated=0" in plan, "init plan should be read-only")
        require("mode=self" in plan, "init plan lost self mode")
        require("terminal-enabled=1" in plan,
                "self mode did not default terminal on")
        require("canonical-config-begin" in plan, "init plan lacks config")
        require("=--mode\n" in plan and "=self\n" in plan,
                "self mode not rendered in canonical config")
        require("--mode" in plan and "self" in plan,
                "self mode not persisted in plan")
        require("--sync-policy-root" in plan, "init plan write command incomplete")
        require("--ratox-profile-store" in plan, "init plan terminal path incomplete")
        require("--ratox-helper" in plan, "self terminal helper path missing")

        written = run(
            iotox,
            "init",
            "write-config",
            "--root",
            str(root),
            "--mode",
            "self",
            "--enable-sync",
        )
        config = root / "agent.conf"
        require(config.exists(), "init write-config did not create config")
        mode = stat.S_IMODE(config.stat().st_mode)
        require(mode == 0o600, f"config mode is {mode:o}, expected 600")
        require("iotox-init-write-config-v1" in written, "write schema missing")
        lint = run(iotox, "config-lint", str(config))
        require("decision=valid" in lint, "written config did not lint")

        recall = "abacus abdomen abdominal abide abiding ability ablaze able\n"
        roster = root / "self.swarm"
        bridge_identity = root / "bridge.device.identity"
        desktop_principal = create_identity_with_daemon(
            iotox, root, bridge_identity)
        desktop_tox = "21" * 32
        laptop_principal = "12" * 32
        laptop_tox = "22" * 32
        created = run(
            iotox,
            "self-swarm",
            "create-recall-stdin",
            str(roster),
            "desktop",
            desktop_principal,
            desktop_tox,
            "operator",
            "interactive.terminal",
            input_text=recall,
        )
        require("operation=create" in created and "generation=1" in created,
                "self-swarm create did not render generation 1")
        joined = run(
            iotox,
            "self-swarm",
            "join-recall-stdin",
            str(roster),
            "laptop",
            laptop_principal,
            laptop_tox,
            "operator",
            "interactive.terminal,sync.subscribe",
            input_text=recall,
        )
        require("operation=join" in joined and "generation=2" in joined,
                "self-swarm join did not advance generation")
        inspected = run(iotox, "self-swarm", "inspect", str(roster),
                        "--min-generation", "2",
                        "--expect-member", "laptop", laptop_principal)
        require("active-members=2" in inspected and "alias=laptop" in inspected,
                "self-swarm inspect lost active laptop")
        wrong_member = run_fail(iotox, "self-swarm", "verify", str(roster),
                                "--expect-member", "laptop", "13" * 32)
        require("principal does not match" in wrong_member,
                "self-swarm wrong-principal path did not fail closed")
        wrong_route = run_fail(iotox, "self-swarm", "verify", str(roster),
                               "--expect-route", "laptop", "23" * 32)
        require("route key does not match" in wrong_route,
                "self-swarm wrong-route path did not fail closed")
        grant_plan = run(iotox, "self-swarm", "grant-plan", str(roster),
                         "--from", "desktop")
        require("iotox-self-swarm-grant-plan-v1" in grant_plan,
                "self-swarm grant plan schema missing")
        require("alias:laptop operator interactive.terminal,sync.subscribe" in grant_plan,
                "self-swarm grant plan lost narrow laptop grant")
        require("target=desktop" not in grant_plan,
                "self-swarm grant plan did not exclude source member")
        floor = root / "self.floor"
        floor_commit = run(
            iotox,
            "self-swarm",
            "floor-commit",
            str(floor),
            str(roster),
            "--min-generation",
            "2",
        )
        require("iotox-self-swarm-floor-commit-v1" in floor_commit,
                "self-swarm floor commit schema missing")
        require("generation=2" in floor_commit and "committed=1" in floor_commit,
                "self-swarm floor commit did not record generation 2")
        floor_status = run(iotox, "self-swarm", "floor-status", str(floor))
        require("iotox-self-swarm-floor-v1" in floor_status
                and "local-high-water-floor" in floor_status,
                "self-swarm floor status missing boundary")
        floor_verify = run(iotox, "self-swarm", "verify", str(roster),
                           "--floor", str(floor), "--min-generation", "2")
        require("decision=valid" in floor_verify,
                "self-swarm floor verify did not accept current roster")
        fanout_plan = run(iotox, "self-swarm", "fanout-plan", str(roster),
                          "--from", "desktop", "--floor", str(floor))
        require("iotox-self-swarm-fanout-plan-v1" in fanout_plan,
                "self-swarm fanout plan schema missing")
        require("send-command=iotox file-send alias:laptop" in fanout_plan,
                "self-swarm fanout plan lost laptop send")
        require("receiver-floor-command=iotox self-swarm floor-commit" in fanout_plan,
                "self-swarm fanout plan lost receiver floor command")
        require("route-policy=not-carried-by-self-roster" in fanout_plan
                and "route-class=unknown" in fanout_plan,
                "self-swarm fanout plan lost route-policy boundary")
        swarm_readiness = run(iotox, "self-swarm", "readiness", str(roster),
                              "--from", "desktop", "--floor", str(floor))
        require("iotox-self-swarm-readiness-v1" in swarm_readiness,
                "self-swarm readiness schema missing")
        require("redacted=1" in swarm_readiness
                and "floor=accepted" in swarm_readiness
                and "fanout-targets=1" in swarm_readiness,
                "self-swarm readiness lost redacted floor/fanout state")
        require("route-policy=not-carried-by-self-roster" in swarm_readiness,
                "self-swarm readiness lost route-policy boundary")
        swarm_daily = run(iotox, "self-swarm", "daily-status", str(roster),
                          "--from", "desktop", "--floor", str(floor))
        require("iotox-self-swarm-daily-status-v1" in swarm_daily,
                "self-swarm daily status schema missing")
        require("floor=accepted" in swarm_daily
                and "fanout-targets=1" in swarm_daily
                and "readiness-command=iotox self-swarm readiness" in swarm_daily
                and "fanout-plan-command=iotox self-swarm fanout-plan" in swarm_daily
                and "grant-plan-command=iotox self-swarm grant-plan" in swarm_daily
                and "retire-plan-command=iotox self-swarm retire-plan" in swarm_daily,
                "self-swarm daily status lost floor/fanout/operator commands")
        person_card = root / "me.person.card"
        card_created = run(
            iotox,
            "person",
            "card-recall-stdin",
            str(roster),
            str(person_card),
            "--floor",
            str(floor),
            "--min-generation",
            "2",
            input_text=recall,
        )
        require("iotox-person-card-create-v1" in card_created,
                "person card create schema missing")
        require("generation=2" in card_created and "routes=2" in card_created,
                "person card create lost generation/routes")
        card_inspect = run(iotox, "person", "card-inspect", str(person_card))
        require("iotox-person-delivery-card-v1" in card_inspect,
                "person card inspect schema missing")
        require("routes=2" in card_inspect and "alias=" not in card_inspect,
                "person card inspect leaked aliases or lost routes")
        require("route-policy=not-carried-by-person-card" in card_inspect,
                "person card inspect lost route-policy boundary")
        self_person_key = extract_field(card_inspect, "person")
        bridge_delegation = root / "desktop.person.delegate"
        delegated = run(
            iotox,
            "person",
            "delegate-recall-stdin",
            str(roster),
            "desktop",
            str(bridge_delegation),
            "--floor",
            str(floor),
            "--min-generation",
            "2",
            input_text=recall,
        )
        require("iotox-person-sender-delegation-create-v1" in delegated,
                "person delegation create schema missing")
        external_tox = "42" * 32
        bridge_store = root / "tox.bridge"
        bridge_in_plan = run(
            iotox,
            "--identity",
            str(bridge_identity),
            "person",
            "tox-bridge-plan-in-delegated",
            "--bridge-store",
            str(bridge_store),
            str(person_card),
            str(bridge_delegation),
            external_tox,
            "message",
            "hello",
            "normal",
            "tox",
        )
        require("iotox-person-tox-bridge-plan-v1" in bridge_in_plan,
                "Tox bridge inbound plan schema missing")
        require("normal-tox-send-command=not-applicable-inbound-already-observed"
                in bridge_in_plan,
                "Tox bridge inbound plan tried to resend external text")
        require("external-tox-key=" + external_tox.upper() in bridge_in_plan,
                "Tox bridge inbound plan lost external key")
        require("local-bridge-commit-command=iotox person tox-bridge-receive"
                in bridge_in_plan,
                "Tox bridge inbound plan lost local bridge-store commit command")
        require("tox-bridge-route-qualification=default-qualified;forced-tcp-degraded;tor-i2p-open"
                in bridge_in_plan,
                "Tox bridge plan lost route qualification boundary")
        bridge_payload_hex = extract_field(bridge_in_plan, "payload-hex")
        bridge_receive = run(
            iotox,
            "person",
            "tox-bridge-receive",
            bridge_payload_hex,
            str(bridge_delegation),
            str(bridge_store),
        )
        require("iotox-person-tox-bridge-receive-v1" in bridge_receive,
                "Tox bridge receive schema missing")
        require("bridge=committed duplicate=0" in bridge_receive,
                "Tox bridge receive did not commit first observation")
        bridge_receive_duplicate = run(
            iotox,
            "person",
            "tox-bridge-receive",
            bridge_payload_hex,
            str(bridge_delegation),
            str(bridge_store),
        )
        require("duplicate=1" in bridge_receive_duplicate
                and "mutated=0" in bridge_receive_duplicate,
                "Tox bridge duplicate receive was not idempotent")
        bridge_status = run(
            iotox,
            "person",
            "tox-bridge-status",
            str(bridge_store),
        )
        require("iotox-person-tox-bridge-status-v1" in bridge_status,
                "Tox bridge status schema missing")
        require("entries=1" in bridge_status and "inbound=1" in bridge_status
                and "content-free=1" in bridge_status,
                "Tox bridge status lost content-free inbound accounting")
        person_graduation_blocked = run_fail(
            iotox,
            "person",
            "graduation-check",
            "--root",
            str(root),
        )
        require("iotox-person-graduation-check-v1" in person_graduation_blocked
                and "person-multidevice-graduation=blocked" in person_graduation_blocked
                and "background-run-command=" in person_graduation_blocked,
                "person graduation check did not fail closed")
        person_graduation_ready = run(
            iotox,
            "person",
            "graduation-check",
            "--root",
            str(root),
            "--bridge-store",
            str(bridge_store),
            "--evidence",
            "background-delivery=service.loop",
            "--evidence",
            "offline-retry-expiry=outbox.retry",
            "--evidence",
            "receipt-summary=receipts.rollup",
            "--evidence",
            "human-read-semantics=read.policy",
            "--evidence",
            "transcript-convergence=transcripts.checked",
            "--evidence",
            "group-semantics=groups.reviewed",
            "--evidence",
            "service-supervision=systemd.user",
            "--evidence",
            "route-policy=route-set.v2",
            "--evidence",
            "operator-review=owner",
        )
        require("person-multidevice-graduation=operator-attested" in person_graduation_ready
                and "messages-reach-devices=operator-attested" in person_graduation_ready
                and "repo-certified=0" in person_graduation_ready,
                "person graduation check lost operator-attested boundary")
        bridge_graduation_blocked = run_fail(
            iotox,
            "person",
            "tox-bridge-graduation-check",
            "--bridge-store",
            str(bridge_store),
        )
        require("iotox-person-tox-bridge-graduation-check-v1" in bridge_graduation_blocked
                and "toxic-bridge-graduation=blocked" in bridge_graduation_blocked
                and "toxic-multidevice-default-command=" in bridge_graduation_blocked,
                "Toxic bridge graduation check did not fail closed")
        bridge_graduation_ready = run(
            iotox,
            "person",
            "tox-bridge-graduation-check",
            "--bridge-store",
            str(bridge_store),
            "--evidence",
            "toxic-native=toxic.default",
            "--evidence",
            "toxic-forced-tcp=toxic.tcp",
            "--evidence",
            "inbound-fanout=lab.inbound",
            "--evidence",
            "outbound-send=lab.outbound",
            "--evidence",
            "identity-boundary=review",
            "--evidence",
            "bridge-store=content-free",
            "--evidence",
            "transcript-commit=transcript",
            "--evidence",
            "route-nonclaims=routes",
            "--evidence",
            "operator-review=owner",
        )
        require("toxic-bridge-graduation=operator-attested" in bridge_graduation_ready
                and "normal-tox-compatibility=operator-attested" in bridge_graduation_ready
                and "identity-claim=normal-tox-user-is-an-external-tox-key" in bridge_graduation_ready,
                "Toxic bridge graduation lost identity/nonclaim boundary")
        bridge_out_plan = run(
            iotox,
            "--identity",
            str(bridge_identity),
            "person",
            "tox-bridge-plan-out-delegated",
            str(person_card),
            str(bridge_delegation),
            external_tox,
            "action",
            "waves",
            "from",
            "iotox",
        )
        require("direction=out" in bridge_out_plan
                and "normal-tox-send-command=iotox action-hex key:" in bridge_out_plan,
                "Tox bridge outbound plan lost normal Tox action command")
        person_plan = run(
            iotox,
            "person",
            "message-plan-recall-stdin",
            str(person_card),
            "hello",
            "self",
            "swarm",
            input_text=recall,
        )
        require("iotox-person-message-fanout-plan-v1" in person_plan,
                "person fanout plan schema missing")
        require("mutated=0" in person_plan and "send-command=iotox message-hex key:" in person_plan,
                "person fanout plan lost review/mutation boundary")
        require("route-policy=not-carried-by-person-card" in person_plan,
                "person fanout plan lost route-policy boundary")
        payload_hex = None
        for line in person_plan.splitlines():
            if line.startswith("payload-hex="):
                payload_hex = line.split("=", 1)[1]
                break
        require(payload_hex is not None, "person plan did not expose payload hex")
        verified = run(iotox, "person", "message-verify-hex", payload_hex)
        require("iotox-person-message-v1" in verified
                and "signature=valid" in verified
                and "body-hex=68656C6C6F2073656C6620737761726D" in verified,
                "person message verification lost signature or body")
        seen_store = root / "person.seen"
        transcript_store = root / "person.transcript"
        received = run(
            iotox,
            "--identity",
            str(bridge_identity),
            "person",
            "receive",
            payload_hex,
            "--seen",
            str(seen_store),
            "--transcript",
            str(transcript_store),
            "--received-unix-ms",
            "123456",
        )
        require("iotox-person-receive-v1" in received,
                "person receive schema missing")
        require("transcript=" in received and "status=committed" in received,
                "person receive did not commit transcript")
        require("seen=" in received and "duplicate=0" in received,
                "person receive did not commit seen store")
        receipt_store = root / "person.receipts"
        receipt_path = root / "message.receipt"
        received_with_receipt = run(
            iotox,
            "--identity",
            str(bridge_identity),
            "person",
            "receive",
            payload_hex,
            "--seen",
            str(seen_store),
            "--transcript",
            str(transcript_store),
            "--delegation",
            str(bridge_delegation),
            "--receipt",
            str(receipt_path),
            "--receipt-store",
            str(receipt_store),
            "--received-unix-ms",
            "123457",
        )
        require("receipt=" in received_with_receipt
                and "receipt-store=" in received_with_receipt
                and "status=committed" in received_with_receipt
                and "receipt-store" in extract_field(received_with_receipt, "mutated"),
                "person receive did not create and aggregate a device receipt")
        receipt_message = extract_field(received_with_receipt, "message-id")
        receipt_status = run(
            iotox,
            "person",
            "receipts-status",
            str(receipt_store),
            "--message-id",
            receipt_message,
            "--scope",
            "person",
            "--expect-person",
            self_person_key,
            "--expect-device",
            desktop_principal,
        )
        require("iotox-person-receipts-status-v1" in receipt_status
                and "aggregate-complete=1" in receipt_status
                and "content-free=1" in receipt_status,
                "person receipt aggregate status did not prove expected device receipt")
        read_state = root / "person.read-state"
        read_mark = run(
            iotox,
            "person",
            "read-mark",
            str(read_state),
            receipt_message,
            "--reader",
            "desktop",
            "--read-unix-ms",
            "123999",
        )
        require("iotox-person-read-mark-v1" in read_mark
                and "human-read=local" in read_mark
                and "device-receipt-semantics=separate" in read_mark
                and "mutated=1" in read_mark,
                "person read-mark did not commit local human-read state")
        read_status = run(
            iotox,
            "person",
            "read-status",
            str(read_state),
            "--message-id",
            receipt_message,
            "--expect-reader",
            "desktop",
        )
        require("iotox-person-read-status-v1" in read_status
                and "matching-reads=1" in read_status
                and "reader name=desktop status=read" in read_status
                and "aggregate-human-read=complete" in read_status
                and "device-receipt-semantics=separate" in read_status,
                "person read-status did not summarize human-read state")
        read_duplicate = run(
            iotox,
            "person",
            "read-mark",
            str(read_state),
            receipt_message,
            "--reader",
            "desktop",
            "--read-unix-ms",
            "123999",
        )
        require("duplicate=1" in read_duplicate and "mutated=0" in read_duplicate,
                "person read-mark duplicate was not idempotent")
        peer_transcript = root / "person.peer.transcript"
        peer_transcript.write_bytes(transcript_store.read_bytes())
        convergence = run(
            iotox,
            "person",
            "transcript-convergence",
            str(transcript_store),
            str(peer_transcript),
        )
        require("iotox-person-transcript-convergence-v1" in convergence
                and "aggregate=converged" in convergence
                and "order-semantics=local-sequence-only" in convergence
                and "payload-mismatch=0" in convergence,
                "person transcript convergence did not recognize matching stores")
        group_path = root / "operators.group"
        group_created = run(
            iotox,
            "person",
            "group-create-recall-stdin",
            str(group_path),
            "operators",
            self_person_key,
            input_text=recall,
        )
        require("iotox-person-group-create-v1" in group_created
                and "members=1" in group_created,
                "person group create schema missing")
        group_id = extract_field(group_created, "group-id")
        group_plan = run(
            iotox,
            "person",
            "group-message-plan-recall-stdin",
            str(group_path),
            "hello",
            "group",
            input_text=recall,
        )
        require("iotox-person-group-message-plan-v1" in group_plan
                and "payload-hex=" in group_plan
                and "use-group-fanout-plan" in group_plan,
                "person group message plan lost fanout boundary")
        group_payload = extract_field(group_plan, "payload-hex")
        group_seen = root / "person.group.seen"
        group_transcript = root / "person.group.transcript"
        group_received = run(
            iotox,
            "person",
            "receive",
            group_payload,
            "--seen",
            str(group_seen),
            "--transcript",
            str(group_transcript),
        )
        require("iotox-person-receive-v1" in group_received
                and "scope=group" in group_received
                and "status=committed" in group_received,
                "person receive did not commit group transcript")
        group_read = run(
            iotox,
            "person",
            "read-mark",
            str(read_state),
            extract_field(group_received, "message-id"),
            "--scope",
            "group",
            "--group",
            group_id,
            "--reader",
            "desktop",
            "--read-unix-ms",
            "124000",
        )
        require("scope=group" in group_read and "mutated=1" in group_read,
                "person read-mark did not handle group scope")
        group_status = run(
            iotox,
            "person",
            "group-status",
            str(group_path),
            "--transcript",
            str(group_transcript),
            "--receipts",
            str(receipt_store),
            "--read-state",
            str(read_state),
        )
        require("iotox-person-group-status-v1" in group_status
                and "members=1" in group_status
                and "group-transcript-entries=1" in group_status
                and "group-human-reads=1" in group_status
                and "group-fanout-plan-command=iotox person group-fanout-plan" in group_status
                and "tox-groupchat=not-claimed" in group_status,
                "person group-status lost summary or honest group boundary")
        receipt_duplicate = run(
            iotox,
            "person",
            "receipt-commit",
            str(receipt_store),
            str(receipt_path),
            str(bridge_delegation),
        )
        require("duplicate=1" in receipt_duplicate and "mutated=0" in receipt_duplicate,
                "person receipt duplicate commit was not idempotent")
        received_duplicate = run(
            iotox,
            "person",
            "receive",
            payload_hex,
            "--seen",
            str(seen_store),
            "--transcript",
            str(transcript_store),
        )
        require("duplicate=1" in received_duplicate and "mutated=0" in received_duplicate,
                "person receive duplicate was not idempotent")
        outbox = root / "person.outbox"
        outbox_enqueued = run(
            iotox,
            "person",
            "outbox-enqueue",
            str(outbox),
            str(person_card),
            payload_hex,
        )
        require("iotox-person-outbox-enqueue-v1" in outbox_enqueued,
                "person outbox enqueue schema missing")
        outbox_dry_run = run(
            iotox,
            "person",
            "outbox-send",
            str(outbox),
            "--max-routes",
            "1",
            "--dry-run",
        )
        require("iotox-person-outbox-send-v1" in outbox_dry_run,
                "person outbox-send schema missing")
        require("dry-run=1" in outbox_dry_run and "mutated=0" in outbox_dry_run,
                "person outbox dry-run mutated or lost dry-run marker")
        require("selected-routes=1" in outbox_dry_run
                and "pending-routes-after=2" in outbox_dry_run,
                "person outbox-send did not honor max route dry-run")
        require("remote-person-receipt-is-separate" in outbox_dry_run,
                "person outbox-send lost receipt boundary")
        outbox_retry = run(
            iotox,
            "person",
            "outbox-retry-plan",
            str(outbox),
            "--max-routes",
            "1",
            "--retry-every",
            "60",
            "--expire-after",
            "3600",
        )
        require("iotox-person-outbox-retry-plan-v1" in outbox_retry,
                "person outbox retry plan schema missing")
        require("pending-routes=2" in outbox_retry
                and "one-shot-send-command=iotox person outbox-send" in outbox_retry
                and "scheduler=native-background-run-or-service-timer" in outbox_retry
                and "background-run-command=iotox person background-run" in outbox_retry,
                "person outbox retry plan lost queue/scheduler facts")
        person_floor = root / "person.card.floor"
        person_floor_commit = run(
            iotox,
            "person",
            "card-floor-commit",
            str(person_floor),
            str(person_card),
        )
        require("iotox-person-card-floor-v1" in person_floor_commit,
                "person card floor commit schema missing")
        card_refresh = run(
            iotox,
            "person",
            "card-refresh-plan",
            str(person_card),
            "--floor",
            str(person_floor),
            "--min-generation",
            "1",
        )
        require("iotox-person-card-refresh-plan-v1" in card_refresh,
                "person card refresh plan schema missing")
        require("status=ready" in card_refresh
                and "verify-command=iotox person card-verify" in card_refresh
                and "refresh-command=cat RECALLROOT.txt" in card_refresh,
                "person card refresh plan lost freshness commands")
        messenger_status = run(
            iotox,
            "person",
            "messenger-status",
            "--seen",
            str(seen_store),
            "--transcript",
            str(transcript_store),
            "--outbox",
            str(outbox),
            "--receipts",
            str(receipt_store),
        )
        require("iotox-person-messenger-status-v1" in messenger_status,
                "person messenger status schema missing")
        require("seen=" in messenger_status and "entries=1" in messenger_status,
                "person messenger status lost seen entries")
        require("transcript=" in messenger_status and "next-sequence=2" in messenger_status,
                "person messenger status lost transcript sequence")
        require("pending-routes=2" in messenger_status and "content-free=1" in messenger_status,
                "person messenger status lost outbox accounting or content-free marker")
        require("receipts=" in messenger_status and "entries=1" in messenger_status,
                "person messenger status lost receipt accounting")
        messenger_plan = run(
            iotox,
            "person",
            "messenger-plan",
            "--seen",
            str(seen_store),
            "--transcript",
            str(transcript_store),
            "--outbox",
            str(outbox),
            "--receipts",
            str(receipt_store),
            "--dead-letter",
            str(root / "person.dead-letter"),
            "--card",
            str(person_card),
            "--floor",
            str(person_floor),
            "--max-routes",
            "1",
        )
        require("iotox-person-messenger-plan-v1" in messenger_plan,
                "person messenger plan schema missing")
        require("messenger-status-command=iotox person messenger-status" in messenger_plan
                and "background-run-command=iotox person background-run" in messenger_plan
                and "outbox-retry-plan-command=iotox person outbox-retry-plan" in messenger_plan
                and "card-refresh-plan-command=iotox person card-refresh-plan" in messenger_plan
                and "device-receipt-semantics=device-received-not-human-read" in messenger_plan
                and "offline-delivery=bounded-outbox-retry-expire-dead-letter" in messenger_plan,
                "person messenger plan lost daily-driver/offline semantics")
        background_run = run(
            iotox,
            "person",
            "background-run",
            "--seen",
            str(seen_store),
            "--transcript",
            str(transcript_store),
            "--receipts",
            str(receipt_store),
            "--outbox",
            str(outbox),
            "--dead-letter",
            str(root / "person.dead-letter"),
            "--max-routes",
            "1",
            "--cycles",
            "1",
            "--interval",
            "0",
            "--dry-run",
        )
        require("iotox-person-background-run-v1" in background_run
                and "cycle=1 phase=status" in background_run
                and "dry-run=1" in background_run
                and "mutated=0" in background_run,
                "person native background-run did not execute bounded dry-run loop")
        background_plan = run(
            iotox,
            "person",
            "background-plan",
            "--seen",
            str(seen_store),
            "--transcript",
            str(transcript_store),
            "--outbox",
            str(outbox),
            "--receipts",
            str(receipt_store),
            "--dead-letter",
            str(root / "person.dead-letter"),
            "--card",
            str(person_card),
            "--floor",
            str(person_floor),
            "--max-routes",
            "1",
        )
        require("iotox-person-background-plan-v1" in background_plan,
                "person background plan schema missing")
        require("outbox-retry-plan-command=iotox person outbox-retry-plan" in background_plan
                and "card-refresh-plan-command=iotox person card-refresh-plan" in background_plan
                and "native-background-command=iotox person background-run" in background_plan
                and "outbox-expire-command=iotox person outbox-expire" in background_plan
                and "supervise-the-native-bounded-loop" in background_plan,
                "person background plan lost retry/freshness commands")
        stale = run_fail(iotox, "self-swarm", "verify", str(roster),
                         "--min-generation", "3")
        require("below the required floor" in stale,
                "self-swarm stale generation floor did not fail closed")
        stale_apply = run_fail(iotox, "self-swarm", "grant-recall-stdin",
                               str(roster), "laptop",
                               "--min-generation", "3")
        require("below the required floor" in stale_apply,
                "self-swarm stale grant apply did not fail before authority")
        wrong_route_apply = run_fail(iotox, "self-swarm", "grant-recall-stdin",
                                     str(roster), "laptop",
                                     "--expect-route", "laptop", "23" * 32)
        require("route key does not match" in wrong_route_apply,
                "self-swarm wrong-route grant apply did not fail before authority")
        retire_plan = run(iotox, "self-swarm", "retire-plan", str(roster),
                          "laptop", "--min-generation", "2")
        require("authority-revoke-remote-recall-stdin alias:laptop" in retire_plan,
                "self-swarm retire plan lost revoke command")
        retired = run(
            iotox,
            "self-swarm",
            "retire-recall-stdin",
            str(roster),
            "laptop",
            input_text=recall,
        )
        require("operation=retire" in retired and "generation=3" in retired,
                "self-swarm retire did not advance generation")
        floor_verify_after_retire = run(
            iotox, "self-swarm", "verify", str(roster), "--floor", str(floor))
        require("decision=valid" in floor_verify_after_retire,
                "self-swarm floor rejected newer roster generation")
        floor_commit_after_retire = run(
            iotox, "self-swarm", "floor-commit", str(floor), str(roster))
        require("generation=3" in floor_commit_after_retire,
                "self-swarm floor did not advance after retire")
        retired_apply = run_fail(iotox, "self-swarm", "grant-recall-stdin",
                                 str(roster), "laptop",
                                 "--min-generation", "3")
        require("grant target is retired" in retired_apply,
                "self-swarm retired grant apply did not fail closed")
        grant_after_retire = run(iotox, "self-swarm", "grant-plan", str(roster),
                                 "--from", "desktop")
        require("target=laptop" not in grant_after_retire,
                "self-swarm grant plan included retired member")

        seed = None
        for line in run(iotox, "bootstrap-seeds").splitlines():
            if line.startswith("role=bootstrap ") and " endpoint=" in line:
                seed = line.split(" endpoint=", 1)[1].split(" location=", 1)[0]
                break
        require(seed is not None, "bootstrap seed fixture unavailable")
        routed = run(
            iotox,
            "init",
            "plan",
            "--root",
            str(Path(tmp) / "routed"),
            "--network",
            "tox/tor",
            "--socks5-proxy",
            "127.0.0.1:9050",
            "--bootstrap",
            seed,
            "--tcp-relay",
            seed,
        )
        require("network=Tox/Tor" in routed, "routed init did not normalize route")
        require("bootstraps=1" in routed and "tcp-relays=1" in routed,
                "routed init did not retain explicit route endpoints")

        pair = run(
            iotox,
            "sync",
            "plan-pair",
            "demo",
            str(source),
            "alias:laptop",
            "/tmp/iotox-remote-demo",
            "read-write",
            "30",
        )
        require("iotox-sync-plan-pair-v1" in pair, "pair plan schema missing")
        require("local-share-command=cat RECALLROOT.txt | iotox sync-share" in pair,
                "pair plan lacks share command")
        require("remote-path-explicit=1" in pair, "pair plan lost remote path boundary")

        mesh = run(
            iotox,
            "sync",
            "plan-mesh",
            "demo",
            str(source),
            "alias:laptop=/tmp/iotox-laptop-demo",
            "alias:nas=/tmp/iotox-nas-demo",
            "30",
        )
        require("iotox-sync-plan-mesh-v1" in mesh, "mesh plan schema missing")
        require(mesh.count("remote-start-command=") == 2,
                "mesh plan did not emit both remote starts")
        trust_plan = run(
            iotox,
            "sync",
            "trust-plan",
            str(source),
            "read-write",
            "30",
        )
        require("iotox-sync-trust-plan-v1" in trust_plan,
                "sync trust plan schema missing")
        require("dataset-readiness-command=iotox sync-dataset-readiness" in trust_plan,
                "sync trust plan lost dataset readiness command")
        require("graduation-check-command=iotox sync graduation-check" in trust_plan,
                "sync trust plan lost graduation command")
        require("precious-data-default=blocked" in trust_plan,
                "sync trust plan overclaimed precious-data readiness")
        graduation_blocked = run_fail(
            iotox,
            "sync",
            "graduation-check",
            str(source),
            "read-write",
            "30",
        )
        require("iotox-sync-graduation-check-v1" in graduation_blocked
                and "working-copy-graduation=blocked" in graduation_blocked,
                "sync graduation check did not fail closed")
        graduation_ready = run(
            iotox,
            "sync",
            "graduation-check",
            str(source),
            "read-write",
            "30",
            "--evidence",
            "local-preflight=doctor",
            "--evidence",
            "storage-readiness=repo.storage",
            "--evidence",
            "recovery-custody=backup.receipt",
            "--evidence",
            "restore-drill=restore.drill",
            "--evidence",
            "recovery-runbook=runbook.review",
        )
        require("working-copy-graduation=operator-attested" in graduation_ready
                and "precious-data-readiness=blocked" in graduation_ready
                and "repo-certified=0" in graduation_ready,
                "sync graduation check overclaimed or lost operator boundary")

        backup = root / "backup"
        restored = root / "restored"
        backup.mkdir()
        restored.mkdir()
        (backup / "note.txt").write_text("iotox restore drill\n", encoding="utf-8")
        (restored / "note.txt").write_text("iotox restore drill\n", encoding="utf-8")
        readiness_source = run(
            iotox,
            "sync-dataset-readiness",
            str(source),
            "read-write",
            "30",
            f"backup-root={root / 'backup'}",
            f"restored-root={root / 'restored'}",
            "backup-system=borg",
            "backup-generation=gen001",
            "backup-failure-domain=external-ssd",
            "restore-provenance=drill",
            "verify-recovery=1",
        )
        require("iotox-sync-dataset-readiness-v1" in readiness_source,
                "dataset readiness schema missing")
        require("backup-custody=operator-attested" in readiness_source,
                "dataset readiness did not record backup custody labels")
        require("recovery-verify=matched" in readiness_source,
                "dataset readiness did not verify matched restore drill")
        require("precious-data-candidate=restore-verified-operator-attested" in readiness_source,
                "dataset readiness did not promote verified restore candidate")
        require("precious-data-repo-certified=0" in readiness_source,
                "dataset readiness overclaimed precious-data certification")

        backup_plan = run(
            iotox,
            "sync",
            "backup",
            "plan",
            str(source),
            "read-write",
            "30",
        )
        require("iotox-sync-backup-plan-v1" in backup_plan
                and "receipt-command=iotox sync backup receipt" in backup_plan
                and "device-rule=distinct-root-devices-recorded-not-required" in backup_plan
                and "scope-rule=not-disk-loss-host-compromise-or-filesystem-wide-corruption-protection" in backup_plan,
                "sync backup plan lost custody boundary")
        backup_verify = run(
            iotox,
            "sync",
            "backup",
            "verify",
            str(source),
            "read-write",
            "30",
            f"backup-root={backup}",
            f"restored-root={restored}",
            "backup-system=borg",
            "backup-generation=gen001",
            "backup-failure-domain=external-ssd",
            "restore-provenance=drill",
        )
        require("iotox-sync-backup-verify-v1" in backup_verify
                and "restore-drill-status=passed" in backup_verify,
                "sync backup verify did not accept matching restore drill")
        same_device_receipt = run(
            iotox,
            "sync",
            "backup",
            "receipt",
            str(source),
            "read-write",
            "30",
            f"backup-root={backup}",
            f"restored-root={restored}",
            "backup-system=borg",
            "backup-generation=gen001",
            "live-failure-domain=live.host",
            "backup-failure-domain=same-host.versioned",
            "restored-failure-domain=restore.drill",
            "restore-provenance=drill",
            "custody-class=same-host-versioned",
            "immutable-or-versioned=1",
            "operator-rehearsal-repeatable=1",
            "--out",
            str(root / "same-device-proof"),
        )
        require("status=passed" in same_device_receipt
                and "backup-custody-receipt=" in same_device_receipt,
                "sync backup receipt did not accept same-host versioned custody")

        proof = root / "proof"
        proof.mkdir()
        retention_policy = proof / "retention-policy.receipt"
        retention_set = run(
            iotox,
            "sync",
            "retention",
            "set",
            "demo",
            "--keep-days",
            "90",
            "--min-revisions",
            "8",
            "--delete-grace-days",
            "14",
            "--out",
            str(retention_policy),
        )
        require("iotox-sync-retention-policy-v1" in retention_set
                and "status=reviewed" in retention_set
                and retention_policy.is_file(),
                "sync retention set did not write reviewed policy")
        retention_status = run(
            iotox,
            "sync",
            "retention",
            "status",
            "demo",
            "--policy",
            str(retention_policy),
        )
        require("retention-policy=accepted" in retention_status,
                "sync retention status did not accept reviewed policy")

        storage_receipt = proof / "storage-readiness.json"
        storage_receipt.write_text(json.dumps({
            "schema": "iotox.storage-readiness.v1",
            "status": "ready",
            "ready_for_precious_data": True,
            "contains_secrets": False,
            "accepted_local_storage_science": True,
            "evidence": {
                "nested_status_before_top_level_status": {
                    "status": "passed",
                },
            },
        }, sort_keys=True) + "\n", encoding="utf-8")
        long_soak_receipt = proof / "long-soak.json"
        long_soak_receipt.write_text(json.dumps({
            "schema": "iotox.sync-three-writer-sandwurm-verification.v1",
            "status": "passed",
            "contains_secrets": False,
            "soak_campaign": True,
            "soak_cycles": 289,
            "soak_elapsed_ms": 86_401_000,
        }, sort_keys=True) + "\n", encoding="utf-8")
        backup_custody_receipt = proof / "backup-custody.json"
        backup_custody_receipt.write_text(json.dumps({
            "schema": "iotox.sync-backup-custody.v1",
            "status": "passed",
            "run_id": "run.TESTsync",
            "contains_secrets": False,
            "backup_independent": False,
            "custody_class": "same-host-versioned",
            "immutable_or_versioned": True,
            "restore_verified": True,
            "operator_rehearsal_repeatable": True,
            "backup_system": "borg",
            "backup_generation": "gen001",
            "live_failure_domain": "live.host",
            "backup_failure_domain": "same-host.versioned",
            "restored_failure_domain": "restore.drill",
            "restore_provenance": "restore.drill",
            "recovery_report_sha256": "a" * 64,
            "backup_inventory_sha256": "b" * 64,
            "restored_inventory_sha256": "b" * 64,
            "recovery_comparison": {
                "matches": True,
                "contains_secrets": False,
                "backup_entries": 1,
                "restored_entries": 1,
                "roots_on_distinct_devices": False,
            },
            "nonclaims": [
                "not-storage-media-certification",
                "not-disk-loss-protection",
                "not-host-compromise-protection",
                "not-filesystem-wide-corruption-protection",
                "not-content-custody",
            ],
        }, sort_keys=True) + "\n", encoding="utf-8")
        restore_drill_receipt = proof / "restore-drill.json"
        restore_drill_receipt.write_text(json.dumps({
            "schema": "iotox.sync-retained-recovery-drill.v1",
            "status": "passed",
            "contains_secrets": False,
            "decision": "match",
            "local_requirements_satisfied": True,
            "operator_requirement_satisfied": True,
            "device_requirement_satisfied": True,
        }, sort_keys=True) + "\n", encoding="utf-8")
        runbook_doc = proof / "recovery-runbook.md"
        runbook_doc.write_text(
            "# IoTox recovery runbook\n\n"
            "1. Stop all writers before restore.\n"
            "2. Restore from versioned recovery custody outside normal IoTox sync mutation.\n"
            "3. Verify the restored tree before resuming sync.\n"
            "4. Retire obsolete writers and stale devices.\n"
            "5. Rehearse this procedure periodically.\n",
            encoding="utf-8",
        )
        runbook_plan = run(
            iotox,
            "sync",
            "runbook",
            "plan",
            str(source),
            "read-write",
            "30",
        )
        require("iotox-sync-runbook-plan-v1" in runbook_plan
                and "receipt-command=iotox sync runbook receipt" in runbook_plan,
                "sync runbook plan did not compose the receipt command")
        runbook_receipt = proof / "recovery-runbook.receipt"
        runbook_missing_acceptance = run_fail(
            iotox,
            "sync",
            "runbook",
            "receipt",
            str(source),
            "read-write",
            "30",
            "--runbook",
            str(runbook_doc),
            "--reviewer",
            "owner",
            "--out",
            str(runbook_receipt),
        )
        require("--accept-reviewed-runbook" in runbook_missing_acceptance,
                "sync runbook receipt did not require explicit review acceptance")
        runbook_result = run(
            iotox,
            "sync",
            "runbook",
            "receipt",
            str(source),
            "read-write",
            "30",
            "--runbook",
            str(runbook_doc),
            "--reviewer",
            "owner",
            "--accept-reviewed-runbook",
            "--out",
            str(runbook_receipt),
        )
        require("iotox-sync-runbook-receipt-v1" in runbook_result
                and "status=reviewed" in runbook_result
                and "runbook-sha256=" in runbook_result,
                "sync runbook receipt did not write reviewed evidence")
        runbook_status = run(
            iotox,
            "sync",
            "runbook",
            "status",
            "--receipt",
            str(runbook_receipt),
        )
        require("recovery-runbook=accepted" in runbook_status,
                "sync runbook status did not accept native receipt")
        runbook_text = runbook_receipt.read_text(encoding="utf-8")
        require(f"path={source}" not in runbook_text
                and "runbook-sha256=" in runbook_text
                and "dataset-selector-sha256=" in runbook_text
                and "not-content-custody=1" in runbook_text,
                "sync runbook receipt leaked content or lost hash binding")
        minimal_runbook = proof / "minimal-recovery-runbook.receipt"
        minimal_runbook.write_text(
            "schema=iotox.sync-recovery-runbook-review.v1\n"
            "status=reviewed\n"
            "content-free=1\n"
            "operator-runbook=present\n",
            encoding="utf-8",
        )
        minimal_runbook_status = run_fail(
            iotox,
            "sync",
            "runbook",
            "status",
            "--receipt",
            str(minimal_runbook),
        )
        require("accepted-reviewed-runbook=1" in minimal_runbook_status,
                "minimal runbook receipt was not rejected with the stronger shape")
        evidence_dir = root / "evidence"
        collected = run(
            iotox,
            "evidence",
            "collect",
            "sync",
            str(source),
            "read-write",
            "30",
            "--out",
            str(evidence_dir),
            "--storage-readiness",
            str(storage_receipt),
            "--long-soak",
            str(long_soak_receipt),
            "--backup-custody",
            str(backup_custody_receipt),
            "--restore-drill",
            str(restore_drill_receipt),
            "--recovery-runbook",
            str(runbook_receipt),
            "--retention-policy",
            str(retention_policy),
        )
        require("iotox-evidence-collect-sync-v1" in collected
                and "accepted-sync-stable-gates=6/6" in collected
                and "stable-manifest=" in collected,
                "evidence collect did not gather complete sync evidence")
        manifest_path = evidence_dir / "stable-evidence.manifest"
        manifest = run(
            iotox,
            "evidence",
            "manifest",
            str(evidence_dir),
            "--out",
            str(manifest_path),
        )
        require("iotox-evidence-manifest-v1" in manifest
                and manifest_path.is_file(),
                "evidence manifest did not write stable manifest")
        precious = run(
            iotox,
            "sync",
            "precious-status",
            str(source),
            "read-write",
            "30",
            "--evidence-dir",
            str(evidence_dir),
        )
        require("precious-data=operator-signable" in precious
                and "gate name=retention-policy status=accepted" in precious
                and "precious-signoff-command=iotox sync precious-signoff" in precious
                and "stable-manifest-command=iotox evidence manifest" in precious
                and "ship-check-command=iotox ship-check sync stable" in precious
                and "repo-certified=0" in precious,
                "precious status did not become operator-signable with complete evidence")
        precious_json = json.loads(run(
            iotox,
            "sync",
            "precious-status",
            str(source),
            "read-write",
            "30",
            "--evidence-dir",
            str(evidence_dir),
            "--json",
        ))
        require(precious_json["precious_data"] == "operator_signable",
                "precious status json lost signable decision")
        signoff_without_accept = run_fail(
            iotox,
            "sync",
            "precious-signoff",
            str(source),
            "read-write",
            "30",
            "--evidence-dir",
            str(evidence_dir),
            "--reviewer",
            "owner",
            "--out",
            str(proof / "unsigned-precious-signoff.receipt"),
        )
        require("--accept-operator-responsibility" in signoff_without_accept,
                "precious signoff did not require explicit operator acceptance")
        signoff_path = proof / "precious-signoff.receipt"
        signoff = run(
            iotox,
            "sync",
            "precious-signoff",
            str(source),
            "read-write",
            "30",
            "--evidence-dir",
            str(evidence_dir),
            "--reviewer",
            "owner",
            "--accept-operator-responsibility",
            "--out",
            str(signoff_path),
        )
        signoff_text = signoff_path.read_text(encoding="utf-8")
        require("iotox-sync-precious-signoff-v1" in signoff
                and "status=accepted" in signoff
                and "precious-data=operator-signed" in signoff
                and signoff_path.is_file(),
                "precious signoff did not write accepted receipt")
        require("schema=iotox.sync-precious-data-signoff.v1" in signoff_text
                and "dataset-selector-sha256=" in signoff_text
                and "sync.retention-policy.receipt-sha256=" in signoff_text
                and "not-disk-loss-protection=1" in signoff_text
                and "not-host-compromise-protection=1" in signoff_text
                and "not-filesystem-wide-corruption-protection=1" in signoff_text
                and f"path={source}" not in signoff_text,
                "precious signoff receipt lost content-free boundary")
        sync_stable = run(
            iotox,
            "ship-check",
            "sync",
            "stable",
            "--evidence-manifest",
            str(manifest_path),
        )
        require("ship-decision=allowed-with-evidence-manifest" in sync_stable
                and "sync-precious-data=accepted" in sync_stable,
                "sync stable ship-check did not accept collected evidence")

    doctor = run(iotox, "terminal", "doctor")
    require("pidfd=" in doctor and "cgroup-v2=" in doctor,
            "terminal doctor did not expose host capability summary")
    daily = run(iotox, "terminal", "daily-plan", "--root", "/tmp/iotox-daily")
    require("iotox-terminal-daily-plan-v1" in daily,
            "terminal daily plan schema missing")
    require("reconnect-command=iotox --runtime /tmp/iotox-daily/runtime terminal alias:self --reconnect" in daily,
            "terminal daily plan lost reconnect command")
    require("service-plan-command=iotox terminal service plan" in daily
            and "service-render-command=iotox terminal service render" in daily
            and "service-receipt-command=iotox terminal service receipt" in daily
            and "activation-service-evidence=--evidence service-supervision=terminal.service.systemd-user" in daily,
            "terminal daily plan lost native service porch")
    daily_status = run(iotox, "terminal", "daily-status", "--root", "/tmp/iotox-daily")
    require("iotox-terminal-daily-status-v1" in daily_status,
            "terminal daily status schema missing")
    require("activation-check-command=iotox terminal activation-check" in daily_status
            and "graduation-check-command=iotox terminal graduation-check" in daily_status
            and "service-supervision" in daily_status
            and "long-soak-plan-command=iotox terminal soak-plan" in daily_status
            and "production-activation=requires-terminal-activation-check" in daily_status,
            "terminal daily status lost activation boundary")
    service_plan = run(
        iotox,
        "terminal",
        "service",
        "plan",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "systemd-user",
        "--unit",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
    )
    require("iotox-terminal-service-plan-v1" in service_plan
            and "render-command=iotox terminal service render" in service_plan
            and "service-file-command=iotox terminal service render" in service_plan
            and "--raw" in service_plan
            and "receipt-command=iotox terminal service receipt" in service_plan
            and "activation-evidence=--evidence service-supervision=terminal.service.systemd-user" in service_plan,
            "terminal service plan did not expose render/receipt/evidence")
    service_render = run(
        iotox,
        "terminal",
        "service",
        "render",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "systemd-user",
        "--unit",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
    )
    require("iotox-terminal-service-render-v1" in service_render
            and "[Service]" in service_render
            and "ExecStart=" in service_render
            and "run --config" in service_render
            and "NoNewPrivileges=yes" in service_render,
            "terminal service render did not emit systemd unit shape")
    service_raw = run(
        iotox,
        "terminal",
        "service",
        "render",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "systemd-user",
        "--unit",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
        "--raw",
    )
    require(service_raw.startswith("# Generated by: iotox terminal service render\n")
            and "iotox-terminal-service-render-v1" not in service_raw
            and "[Install]" in service_raw,
            "terminal service render --raw was not directly installable")
    nixos_render = run(
        iotox,
        "terminal",
        "service",
        "render",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "nixos-user",
        "--unit",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
    )
    require("systemd.user.services.\"iotox-self\"" in nixos_render
            and "ExecStart" in nixos_render
            and "PrivateTmp = true" in nixos_render,
            "terminal service render did not emit NixOS user service shape")
    with tempfile.TemporaryDirectory(prefix="iotox-terminal-service.") as raw_service:
        service_root = Path(raw_service)
        service_receipt_path = service_root / "terminal-service.receipt"
        service_receipt = run(
            iotox,
            "terminal",
            "service",
            "receipt",
            "--root",
            "/tmp/iotox-daily",
            "--manager",
            "systemd-user",
            "--unit",
            "iotox-self",
            "--binary",
            str(iotox.resolve()),
            "--accept-operator-responsibility",
            "--out",
            str(service_receipt_path),
        )
        service_receipt_text = service_receipt_path.read_text(encoding="utf-8")
        require("iotox-terminal-service-receipt-v1" in service_receipt
                and "receipt-sha256=" in service_receipt
                and service_receipt_path.is_file(),
                "terminal service receipt command did not write receipt")
        require("iotox-terminal-service-supervision-receipt-v1" in service_receipt_text
                and "activation-evidence=service-supervision=terminal.service.systemd-user" in service_receipt_text
                and "not-service-manager-state-proof=1" in service_receipt_text
                and "not-cgroup-delegation-proof=1" in service_receipt_text
                and "not-route-proof=1" in service_receipt_text,
                "terminal service receipt lost content-free honesty boundaries")
        service_receipt_blocked = run_fail(
            iotox,
            "terminal",
            "service",
            "receipt",
            "--root",
            "/tmp/iotox-daily",
            "--manager",
            "systemd-user",
            "--out",
            str(service_root / "blocked.receipt"),
        )
        require("--accept-operator-responsibility" in service_receipt_blocked,
                "terminal service receipt did not require explicit acceptance")
    resident_plan = run(
        iotox,
        "service",
        "plan",
        "--target",
        "all",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "systemd-user",
        "--unit-prefix",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
    )
    require("iotox-resident-service-plan-v1" in resident_plan
            and "agent-unit=iotox-self-agent" in resident_plan
            and "person-unit=iotox-self-person" in resident_plan
            and "enable-command=systemctl --user enable --now" in resident_plan
            and "logs-command=journalctl --user -u" in resident_plan
            and "upgrade-boundary=run-check-or-health-before-restart" in resident_plan,
            "resident service plan lost enable/log/health/upgrade commands")
    resident_status_plan = run(
        iotox,
        "service",
        "status-plan",
        "--target",
        "all",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "systemd-user",
        "--unit-prefix",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
    )
    require("iotox-resident-service-status-plan-v1" in resident_status_plan
            and "agent-active-command=systemctl --user is-active iotox-self-agent.service" in resident_status_plan
            and "person-enabled-command=systemctl --user is-enabled iotox-self-person.service" in resident_status_plan
            and "receipt-command=iotox service status-receipt" in resident_status_plan
            and "stable-evidence-key=terminal.service-supervision" in resident_status_plan,
            "resident service status plan lost status/evidence commands")
    resident_render = run(
        iotox,
        "service",
        "render",
        "--target",
        "all",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "systemd-user",
        "--unit-prefix",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
    )
    require("iotox-resident-service-render-v1" in resident_render
            and "artifact-kind=multi-file-bundle" in resident_render
            and '"person" "background-run"' in resident_render
            and '"run" "--config"' in resident_render
            and "NoNewPrivileges=yes" in resident_render,
            "resident service render did not emit agent/person units")
    resident_raw_person = run(
        iotox,
        "service",
        "render",
        "--target",
        "person",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "systemd-user",
        "--unit-prefix",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
        "--raw",
    )
    require(resident_raw_person.startswith("# Generated by: iotox service render\n")
            and "iotox-resident-service-render-v1" not in resident_raw_person
            and '"person" "background-run"' in resident_raw_person,
            "resident service render --raw was not directly installable")
    resident_mnx = run(
        iotox,
        "service",
        "render",
        "--target",
        "all",
        "--root",
        "/tmp/iotox-daily",
        "--manager",
        "monsternix",
        "--unit-prefix",
        "iotox-self",
        "--binary",
        str(iotox.resolve()),
    )
    require("MonsterNix adapter draft" in resident_mnx
            and "mnxBoundary" in resident_mnx
            and "health" in resident_mnx,
            "resident service render did not emit MonsterNix adapter shape")
    with tempfile.TemporaryDirectory(prefix="iotox-resident-service.") as raw_resident:
        resident_root = Path(raw_resident)
        resident_receipt_path = resident_root / "resident.receipt"
        resident_receipt = run(
            iotox,
            "service",
            "receipt",
            "--target",
            "all",
            "--root",
            "/tmp/iotox-daily",
            "--manager",
            "systemd-user",
            "--unit-prefix",
            "iotox-self",
            "--binary",
            str(iotox.resolve()),
            "--accept-operator-responsibility",
            "--out",
            str(resident_receipt_path),
        )
        resident_receipt_text = resident_receipt_path.read_text(encoding="utf-8")
        require("iotox-resident-service-receipt-v1" in resident_receipt
                and "receipt-sha256=" in resident_receipt
                and resident_receipt_path.is_file(),
                "resident service receipt command did not write receipt")
        require("iotox-resident-service-supervision-receipt-v1" in resident_receipt_text
                and "activation-evidence=resident-service=resident.all.systemd-user" in resident_receipt_text
                and "not-service-manager-state-proof=1" in resident_receipt_text
                and "not-sync-health-proof=1" in resident_receipt_text
                and "not-person-read-proof=1" in resident_receipt_text,
                "resident service receipt lost content-free honesty boundaries")
        resident_reality_path = resident_root / "service-reality.receipt"
        resident_reality = run(
            iotox,
            "service",
            "status-receipt",
            "--target",
            "all",
            "--root",
            "/tmp/iotox-daily",
            "--manager",
            "systemd-user",
            "--unit-prefix",
            "iotox-self",
            "--binary",
            str(iotox.resolve()),
            "--service-manager-state",
            "active",
            "--enabled-state",
            "enabled",
            "--log-state",
            "reviewed",
            "--health-state",
            "passed",
            "--upgrade-state",
            "passed",
            "--accept-operator-responsibility",
            "--out",
            str(resident_reality_path),
        )
        resident_reality_text = resident_reality_path.read_text(encoding="utf-8")
        require("iotox-service-status-receipt-v1" in resident_reality
                and "status=accepted" in resident_reality
                and "receipt-sha256=" in resident_reality
                and "iotox-service-reality-receipt-v1" in resident_reality_text
                and "schema=iotox.service-reality.v1" in resident_reality_text
                and "stable-evidence-key=terminal.service-supervision" in resident_reality_text
                and "proves-service-manager-state=1" in resident_reality_text
                and "not-sync-folder-health-proof=1" in resident_reality_text,
                "resident service status receipt lost service reality semantics")
        resident_reality_blocked = run_fail(
            iotox,
            "service",
            "status-receipt",
            "--target",
            "all",
            "--root",
            "/tmp/iotox-daily",
            "--manager",
            "systemd-user",
            "--service-manager-state",
            "inactive",
            "--enabled-state",
            "enabled",
            "--log-state",
            "reviewed",
            "--health-state",
            "passed",
            "--upgrade-state",
            "passed",
            "--accept-operator-responsibility",
            "--out",
            str(resident_root / "blocked-reality.receipt"),
        )
        require("service-manager-state=active" in resident_reality_blocked,
                "resident service status receipt did not fail closed on inactive service")
        resident_blocked = run_fail(
            iotox,
            "service",
            "receipt",
            "--target",
            "all",
            "--root",
            "/tmp/iotox-daily",
            "--manager",
            "systemd-user",
            "--out",
            str(resident_root / "blocked.receipt"),
        )
        require("--accept-operator-responsibility" in resident_blocked,
                "resident service receipt did not require explicit acceptance")
    soak_plan = run(
        iotox,
        "terminal",
        "soak-plan",
        "--root",
        "/tmp/iotox-daily",
        "--peer",
        "alias:self",
        "--seconds",
        "86400",
    )
    require("iotox-terminal-long-soak-plan-v1" in soak_plan
            and "run-command=iotox terminal soak-run" in soak_plan
            and "receipt-command=iotox terminal soak-receipt" in soak_plan
            and "stable-evidence-key=terminal.long-soak" in soak_plan,
            "terminal soak plan did not expose stable long-soak runbook")
    with tempfile.TemporaryDirectory(prefix="iotox-terminal-soak.") as raw_soak:
        soak_root = Path(raw_soak)
        run_receipt = soak_root / "terminal-soak-run.receipt"
        soak_run = run(
            iotox,
            "terminal",
            "soak-run",
            "--root",
            "/tmp/iotox-daily",
            "--peer",
            "alias:self",
            "--route",
            "native",
            "--seconds",
            "1",
            "--sample-every",
            "1",
            "--out",
            str(run_receipt),
            "--label",
            "terminal.smoke",
        )
        require("iotox-terminal-soak-run-v1" in soak_run
                and "accepted=1" in soak_run
                and run_receipt.is_file(),
                "terminal soak-run did not emit accepted verifier receipt")
        soak_run_verify = run(
            iotox,
            "terminal",
            "soak-verify",
            str(run_receipt),
            "--minimum-seconds",
            "1",
        )
        require("accepted=1" in soak_run_verify,
                "terminal soak-run receipt did not verify")
        receipt = soak_root / "terminal-soak.receipt"
        receipt.write_text(
            run(
                iotox,
                "terminal",
                "soak-receipt",
                "--root",
                "/tmp/iotox-daily",
                "--peer",
                "alias:self",
                "--route",
                "native",
                "--required-seconds",
                "60",
                "--observed-seconds",
                "61",
                "--samples",
                "2",
                "--max-sample-gap-seconds",
                "30",
                "--reconnect-attempts",
                "1",
                "--session-generations",
                "1",
                "--failures",
                "0",
                "--result",
                "accepted",
                "--label",
                "terminal.smoke",
            ),
            encoding="utf-8",
        )
        soak_verify = run(
            iotox,
            "terminal",
            "soak-verify",
            str(receipt),
            "--minimum-seconds",
            "60",
        )
        require("iotox-terminal-long-soak-verify-v1" in soak_verify
                and "accepted=1" in soak_verify,
                "terminal soak verifier did not accept valid receipt")
        soak_short = run_fail(
            iotox,
            "terminal",
            "soak-verify",
            str(receipt),
            "--minimum-seconds",
            "86400",
        )
        require("accepted=0" in soak_short
                and "shorter than required" in soak_short,
                "terminal soak verifier did not reject short receipt")
        terminal_evidence = soak_root / "terminal-evidence"
        service_reality = soak_root / "service-reality.receipt"
        run(
            iotox,
            "service",
            "status-receipt",
            "--target",
            "all",
            "--root",
            "/tmp/iotox-daily",
            "--manager",
            "systemd-user",
            "--unit-prefix",
            "iotox-self",
            "--binary",
            str(iotox.resolve()),
            "--service-manager-state",
            "active",
            "--enabled-state",
            "enabled",
            "--log-state",
            "reviewed",
            "--health-state",
            "passed",
            "--upgrade-state",
            "passed",
            "--accept-operator-responsibility",
            "--out",
            str(service_reality),
        )
        base_terminal_collect = [
            "evidence",
            "collect",
            "terminal",
            "--root",
            "/tmp/iotox-daily",
            "--peer",
            "alias:self",
            "--out",
            str(terminal_evidence),
            "--service-reality",
            str(service_reality),
            "--evidence",
            "daily-control=local.gate",
            "--evidence",
            "profile-freshness=profile.check",
            "--evidence",
            "reconnect-continuity=cli.reconnect",
            "--evidence",
            "cgroup-delegation=nixos.cgroup",
            "--evidence",
            "route-loss=tox.loss",
            "--evidence",
            "tor-route-loss=tor.operator",
            "--evidence",
            "i2p-route-loss=i2p.fronts",
            "--evidence",
            "sudo-policy=nixos.pam",
            "--evidence",
            "security-review=owner.review",
            "--evidence",
            "activation-decision=owner.decree",
        ]
        terminal_collect_incomplete = run(iotox, *base_terminal_collect)
        require("iotox-evidence-collect-terminal-v1" in terminal_collect_incomplete
                and "accepted-terminal-stable-gates=11/12" in terminal_collect_incomplete
                and "missing=long-soak" in terminal_collect_incomplete
                and "stable-manifest=blocked" in terminal_collect_incomplete,
                "terminal evidence collection did not stay blocked without long soak")
        terminal_collect_short = run_fail(
            iotox,
            *base_terminal_collect,
            "--long-soak",
            str(receipt),
        )
        require("shorter than required" in terminal_collect_short,
                "terminal evidence collection accepted short long-soak")
        receipt_24h = soak_root / "terminal-24h.receipt"
        receipt_24h.write_text(
            run(
                iotox,
                "terminal",
                "soak-receipt",
                "--root",
                "/tmp/iotox-daily",
                "--peer",
                "alias:self",
                "--route",
                "native",
                "--required-seconds",
                "86400",
                "--observed-seconds",
                "86401",
                "--samples",
                "289",
                "--max-sample-gap-seconds",
                "300",
                "--reconnect-attempts",
                "1",
                "--session-generations",
                "1",
                "--failures",
                "0",
                "--result",
                "accepted",
                "--label",
                "terminal.24h",
            ),
            encoding="utf-8",
        )
        terminal_collect_complete = run(
            iotox,
            *base_terminal_collect,
            "--long-soak",
            str(receipt_24h),
        )
        terminal_manifest = terminal_evidence / "stable-evidence.manifest"
        require("accepted-terminal-stable-gates=12/12" in terminal_collect_complete
                and terminal_manifest.is_file(),
                "terminal evidence collection did not produce complete manifest")
        terminal_manifest_output = run(
            iotox,
            "evidence",
            "manifest",
            str(terminal_evidence),
            "--out",
            str(terminal_manifest),
            "--scope",
            "terminal",
        )
        require("scope=terminal" in terminal_manifest_output,
                "terminal evidence manifest did not honor terminal scope")
        terminal_stable = run(
            iotox,
            "ship-check",
            "terminal",
            "stable",
            "--evidence-manifest",
            str(terminal_manifest),
        )
        require("ship-decision=allowed-with-evidence-manifest" in terminal_stable
                and "terminal-fleet-certification=evidence-attested" in terminal_stable,
                "terminal stable ship-check did not accept native terminal evidence")
    activation_blocked = run_fail(
        iotox,
        "terminal",
        "activation-check",
        "--root",
        "/tmp/iotox-daily",
    )
    require("iotox-terminal-activation-check-v1" in activation_blocked
            and "production-activation=blocked" in activation_blocked,
            "terminal activation check did not fail closed")
    activation_ready = run(
        iotox,
        "terminal",
        "activation-check",
        "--root",
        "/tmp/iotox-daily",
        "--evidence",
        "daily-control=local.gate",
        "--evidence",
        "profile-freshness=profile.check",
        "--evidence",
        "service-supervision=terminal.service.systemd-user",
        "--evidence",
        "reconnect-continuity=cli.reconnect",
        "--evidence",
        "cgroup-delegation=nixos.cgroup",
        "--evidence",
        "route-loss=tox.loss",
    )
    require("production-activation=operator-attested" in activation_ready
            and "repo-certified=0" in activation_ready,
            "terminal activation check lost operator-attested boundary")
    terminal_graduation_blocked = run_fail(
        iotox,
        "terminal",
        "graduation-check",
        "--root",
        "/tmp/iotox-daily",
    )
    require("iotox-terminal-graduation-check-v1" in terminal_graduation_blocked
            and "daily-driver-graduation=blocked" in terminal_graduation_blocked,
            "terminal graduation check did not fail closed")
    terminal_graduation_ready = run(
        iotox,
        "terminal",
        "graduation-check",
        "--root",
        "/tmp/iotox-daily",
        "--evidence",
        "daily-control=local.gate",
        "--evidence",
        "profile-freshness=profile.check",
        "--evidence",
        "service-supervision=terminal.service.systemd-user",
        "--evidence",
        "reconnect-continuity=cli.reconnect",
        "--evidence",
        "cgroup-delegation=nixos.cgroup",
        "--evidence",
        "route-loss=tox.loss",
        "--evidence",
        "long-soak=soak.24h",
        "--evidence",
        "tor-route-loss=tor.operator",
        "--evidence",
        "i2p-route-loss=i2p.fronts",
        "--evidence",
        "sudo-policy=nixos.pam",
        "--evidence",
        "security-review=owner.review",
        "--evidence",
        "activation-decision=owner.decree",
    )
    require("daily-driver-graduation=operator-attested" in terminal_graduation_ready
            and "production-activation=operator-attested" in terminal_graduation_ready
            and "repo-certified=0" in terminal_graduation_ready,
            "terminal graduation check lost operator-attested boundary")
    shell_plan = run(
        iotox,
        "terminal",
        "profile",
        "plan",
        "shell",
        "owner-shell",
        os.environ.get("USER", "nobody"),
        "--shell",
        "/bin/sh",
        "--store",
        "/tmp/iotox-ratox",
    )
    require("iotox-terminal-profile-plan-v1" in shell_plan,
            "terminal shell profile plan schema missing")
    require("template-command=iotox --shell /bin/sh terminal-profile-shell-template" in shell_plan,
            "terminal shell plan does not compose template command")
    profile_record = Path(tempfile.gettempdir()) / "iotox-owner-shell.profile"
    profile_record.write_text(
        run(
            iotox,
            "--shell",
            "/bin/sh",
            "terminal-profile-shell-template",
            "owner-shell",
            os.environ.get("USER", "nobody"),
        ),
        encoding="utf-8",
    )
    profile_check = run(iotox, "terminal", "profile", "check", str(profile_record))
    require("iotox-terminal-profile-check-v1" in profile_check,
            "terminal grouped profile check schema missing")
    require("executable-state=present" in profile_check
            and "payload-ready=1" in profile_check,
            "terminal profile check did not validate shell payload")
    terminal_readiness = run(
        iotox,
        "terminal",
        "readiness",
        "--root",
        "/tmp/iotox-ratox-ready",
        "--profile",
        str(profile_record),
        "--sudo-profile",
        str(profile_record),
    )
    require("iotox-terminal-readiness-v1" in terminal_readiness,
            "terminal readiness schema missing")
    require("profile label=shell" in terminal_readiness
            and "payload-ready=1" in terminal_readiness
            and "binding-service-route-and-sudo-pam-policy-remain-separate" in terminal_readiness,
            "terminal readiness lost profile payload/boundary")
    sudo_plan = run(
        iotox,
        "terminal",
        "profile",
        "plan",
        "sudo",
        "owner-sudo",
        os.environ.get("USER", "nobody"),
        "--shell",
        "/bin/sh",
    )
    require("sudo=explicit" in sudo_plan and "--allow-sudo" in sudo_plan,
            "terminal sudo plan did not make sudo explicit")
    rescue_plan = run(
        iotox,
        "terminal",
        "profile",
        "plan",
        "rescue",
        "rescue-shell",
        os.environ.get("USER", "nobody"),
        "--shell",
        "/bin/sh",
        "--toolbox-dir",
        "/tmp",
    )
    require("terminal-profile-toolbox-template" in rescue_plan,
            "terminal rescue plan did not compose toolbox template")

    print("IoTox human CLI process test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
