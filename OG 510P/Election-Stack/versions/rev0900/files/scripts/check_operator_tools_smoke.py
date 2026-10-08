#!/usr/bin/env python3
"""scripts/check_operator_tools_smoke.py

Release-gate smoke tests for operator-facing helper tools.

Rationale:
The archive includes small “card” tools intended for copy/paste publication.
These tools have a narrow, user-visible contract: given a canonical example packet,
they must recompute digests cleanly and exit 0.

This keeps the operator UX from silently rotting under refactors.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import re
import runpy
import sys
import tempfile
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
EXAMPLES = ROOT / "artifacts" / "examples"


def _coerce_exit_code(code: object) -> int:
    if code is None:
        return 0
    if isinstance(code, int):
        return code
    return 1


def run(cmd: list[str]) -> tuple[int, str, str]:
    """Run repository Python CLI tools in-process for a bounded smoke gate.

    The previous implementation spawned a new interpreter for every tool-card
    assertion. In this archive, interpreter startup dominates the check and can
    make the release gate look hung in constrained offline environments. Running
    the small repository-local CLIs with an isolated argv/stdout/stderr frame
    preserves their command-line contract while keeping the smoke test fast and
    deterministic.
    """

    if len(cmd) < 2 or cmd[0] != sys.executable:
        return 127, "", f"unsupported smoke command: {cmd!r}\n"

    script = Path(cmd[1])
    if not script.is_file() or script.suffix != ".py":
        return 127, "", f"unsupported smoke command: {cmd!r}\n"

    old_argv = sys.argv[:]
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    old_path = sys.path[:]
    old_cwd = Path.cwd()
    old_dont_write = sys.dont_write_bytecode

    out = io.StringIO()
    err = io.StringIO()
    rc = 0

    try:
        sys.argv = [str(script)] + cmd[2:]
        sys.stdout = out
        sys.stderr = err
        sys.dont_write_bytecode = True
        for entry in [str(TOOLS), str(ROOT)]:
            if entry not in sys.path:
                sys.path.insert(0, entry)
        try:
            runpy.run_path(str(script), run_name="__main__")
            rc = 0
        except SystemExit as exc:
            rc = _coerce_exit_code(exc.code)
            if not isinstance(exc.code, (None.__class__, int)):
                print(exc.code, file=sys.stderr)
        except Exception:
            rc = 1
            traceback.print_exc()
    finally:
        try:
            os.chdir(old_cwd)
        except Exception:
            pass
        sys.argv = old_argv
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        sys.path = old_path
        sys.dont_write_bytecode = old_dont_write

    return rc, out.getvalue(), err.getvalue()


def main() -> int:
    failures: list[str] = []

    # 1) PublicNotice digest card
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "public_notice_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_public_notice"),
        ]
    )
    if code != 0:
        failures.append("public_notice_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)


    # 1b) PublicNoticeFeed digest card
    code, out, err = run([
            sys.executable,
            str(TOOLS / "public_notice_feed_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_public_notice_feed"),
        ])
    if code != 0:
        failures.append("public_notice_feed_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 1c) OfficialChannelDirectory digest card
    code, out, err = run([
            sys.executable,
            str(TOOLS / "official_channel_directory_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_official_channel_directory"),
        ])
    if code != 0:
        failures.append("official_channel_directory_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 1d) WellKnownElectionStackDiscovery digest card
    code, out, err = run([
            sys.executable,
            str(TOOLS / "well_known_discovery_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_well_known_discovery"),
        ])
    if code != 0:
        failures.append("well_known_discovery_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)


    # 1e) LivenessBeacon digest card
    code, out, err = run([
            sys.executable,
            str(TOOLS / "liveness_beacon_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_liveness_beacon_minimal"),
        ])
    if code != 0:
        failures.append("liveness_beacon_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 1eb) PublicationCoverageReport digest card
    code, out, err = run([
            sys.executable,
            str(TOOLS / "publication_coverage_report_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_publication_compliance_minimal"),
        ])
    if code != 0:
        failures.append("publication_coverage_report_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 1ea) PublicSurfaceParitySnapshot digest card
    code, out, err = run([
            sys.executable,
            str(TOOLS / "public_surface_parity_snapshot_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_public_surface_parity_snapshot_minimal"),
        ])
    if code != 0:
        failures.append("public_surface_parity_snapshot_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        # Contract: must render a bounded parity summary line.
        if "PublicSurfaceParitySnapshot digest card" not in out:
            failures.append("public_surface_parity_snapshot_card missing header")
        if "parity:" not in out or "PARITY_" not in out:
            failures.append("public_surface_parity_snapshot_card missing parity status")

    # 1ea2) compare_public_surface_parity_snapshots: comparing a packet to itself must yield no diffs (exit 0).
    code, out, err = run([
            sys.executable,
            str(TOOLS / "compare_public_surface_parity_snapshots.py"),
            "--a",
            str(EXAMPLES / "evidence_packet_public_surface_parity_snapshot_minimal"),
            "--b",
            str(EXAMPLES / "evidence_packet_public_surface_parity_snapshot_minimal"),
        ])
    if code != 0:
        failures.append("compare_public_surface_parity_snapshots self-compare failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        if "diff: none" not in out:
            failures.append("compare_public_surface_parity_snapshots expected diff: none")

    # 1ea3) compare_public_surface_parity_snapshots: synthetic diff vectors must yield diffs (exit 3).
    a = EXAMPLES.parent / "test-vectors" / "parity_snapshot_diff_a.json"
    b = EXAMPLES.parent / "test-vectors" / "parity_snapshot_diff_b.json"
    code, out, err = run([
            sys.executable,
            str(TOOLS / "compare_public_surface_parity_snapshots.py"),
            "--a",
            str(a),
            "--b",
            str(b),
        ])
    if code != 3:
        failures.append("compare_public_surface_parity_snapshots diff-compare did not return exit 3")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        if "channels:" not in out or "changed=1" not in out:
            failures.append("compare_public_surface_parity_snapshots diff summary unexpected")



    # 1e2) compare_liveness_beacons: comparing a packet to itself must yield no diffs (exit 0).
    code, out, err = run([
            sys.executable,
            str(TOOLS / "compare_liveness_beacons.py"),
            "--a",
            str(EXAMPLES / "evidence_packet_liveness_beacon_minimal"),
            "--b",
            str(EXAMPLES / "evidence_packet_liveness_beacon_minimal"),
        ])
    if code != 0:
        failures.append("compare_liveness_beacons self-compare failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        if "diff: none" not in out:
            failures.append("compare_liveness_beacons expected diff: none")

    # 1e3) compare_liveness_beacons: synthetic diff vectors must yield diffs (exit 3).
    a = EXAMPLES.parent / "test-vectors" / "liveness_beacon_diff_a.json"
    b = EXAMPLES.parent / "test-vectors" / "liveness_beacon_diff_b.json"
    code, out, err = run([
            sys.executable,
            str(TOOLS / "compare_liveness_beacons.py"),
            "--a",
            str(a),
            "--b",
            str(b),
        ])
    if code != 3:
        failures.append("compare_liveness_beacons diff-compare did not return exit 3")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        if "surfaces:" not in out or "changed=1" not in out:
            failures.append("compare_liveness_beacons diff summary unexpected")


    # 1e3b) compare_public_fingerprints: comparing a packet to itself must match (exit 0).
    code, out, err = run([
            sys.executable,
            str(TOOLS / "compare_public_fingerprints.py"),
            str(EXAMPLES / "evidence_packet_public_notice"),
            str(EXAMPLES / "evidence_packet_public_notice"),
        ])
    if code != 0:
        failures.append("compare_public_fingerprints self-compare failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        if ("public_fingerprint_sha256=sha256:" not in out) and ("OK" not in out):
            failures.append("compare_public_fingerprints missing OK/fingerprint output")
    # 1e4) surface_anomaly_rollup: roll up codes from synthetic liveness vectors.
    a = EXAMPLES.parent / "test-vectors" / "liveness_beacon_diff_a.json"
    b = EXAMPLES.parent / "test-vectors" / "liveness_beacon_diff_b.json"
    code, out, err = run([
            sys.executable,
            str(TOOLS / "surface_anomaly_rollup.py"),
            "--json",
            str(a),
            str(b),
        ])
    if code != 0:
        failures.append("surface_anomaly_rollup failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            res = o.get("result") or {}
            codes = res.get("codes") or []
            # Expect at least these two codes (from the test vectors).
            have = {c.get("code") for c in codes if isinstance(c, dict)}
            for want in ["surface_fetch_failed", "surface_stale_pointer_suspected"]:
                if want not in have:
                    failures.append(f"surface_anomaly_rollup missing expected code: {want}")
        except Exception as e:
            failures.append(f"surface_anomaly_rollup JSON parse failed: {e}")

    # 1f) http_capture_to_observation: parse a small synthetic capture into an observation snippet.
    cap = EXAMPLES.parent / "test-vectors" / "http_capture_well_known_example.txt"
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "http_capture_to_observation.py"),
            "--capture",
            str(cap),
            "--surface",
            "well_known_discovery",
            "--observed-at",
            "2026-02-25T12:00:07Z",
        ]
    )
    if code not in (0, 1):
        failures.append("http_capture_to_observation failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            for k in ["surface", "observed_at", "result", "payload_sha256"]:
                if k not in o:
                    failures.append(f"http_capture_to_observation missing key: {k}")
            if "http_status" not in o:
                failures.append("http_capture_to_observation missing key: http_status")
            if o.get("surface") != "well_known_discovery":
                failures.append("http_capture_to_observation wrong surface")
            if o.get("observed_at") != "2026-02-25T12:00:07Z":
                failures.append("http_capture_to_observation wrong observed_at")
            if o.get("http_status") != 200:
                failures.append("http_capture_to_observation wrong http_status")
            ps = str(o.get("payload_sha256") or "")
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", ps):
                failures.append("http_capture_to_observation payload_sha256 not sha256:<hex>")
            h = o.get("headers") or {}
            if isinstance(h, dict):
                # Ensure we're extracting the bounded freshness headers.
                for k in ["etag", "cache_control", "last_modified", "age_seconds"]:
                    if k not in h:
                        failures.append(f"http_capture_to_observation missing header key: {k}")
        except Exception as e:
            failures.append(f"http_capture_to_observation JSON parse failed: {e}")

    # 1f2) http_capture_to_observation: redirect / multi-response capture MUST use the last response block.
    cap = EXAMPLES.parent / "test-vectors" / "http_capture_redirect_chain_example.txt"
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "http_capture_to_observation.py"),
            "--capture",
            str(cap),
            "--surface",
            "well_known_discovery",
            "--observed-at",
            "2026-02-25T12:00:09Z",
        ]
    )
    if code not in (0, 1):
        failures.append("http_capture_to_observation (redirect chain) failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("http_status") != 200:
                failures.append("http_capture_to_observation did not select last response (want http_status=200)")
            h = o.get("headers") or {}
            if not (isinstance(h, dict) and h.get("etag") == '"second"'):
                failures.append("http_capture_to_observation did not select last response (etag mismatch)")
            if isinstance(h, dict) and h.get("age_seconds") != 5:
                failures.append("http_capture_to_observation did not select last response (age_seconds mismatch)")
            if str(o.get("payload_sha256") or "") != "sha256:c3ec8f8f237bdd77a9253598015d897634a4dd57bac21eb3344dc02022d11074":
                failures.append("http_capture_to_observation payload_sha256 mismatch for redirect chain vector")
        except Exception as e:
            failures.append(f"http_capture_to_observation (redirect chain) JSON parse failed: {e}")
    # 1f3) http_capture_to_observation: HTTP/2 + LF-only capture must parse correctly.
    cap = EXAMPLES.parent / "test-vectors" / "http_capture_http2_lf_example.txt"
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "http_capture_to_observation.py"),
            "--capture",
            str(cap),
            "--surface",
            "well_known_discovery",
            "--observed-at",
            "2026-02-25T12:00:10Z",
        ]
    )
    if code not in (0, 1):
        failures.append("http_capture_to_observation (http2 lf) failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("http_status") != 200:
                failures.append("http_capture_to_observation (http2 lf) wrong http_status")
            if o.get("observed_at") != "2026-02-25T12:00:10Z":
                failures.append("http_capture_to_observation (http2 lf) wrong observed_at")
            h = o.get("headers") or {}
            if not (isinstance(h, dict) and h.get("etag") == "\"h2\""):
                failures.append("http_capture_to_observation (http2 lf) missing etag")
            if isinstance(h, dict) and h.get("age_seconds") != 2:
                failures.append("http_capture_to_observation (http2 lf) wrong age_seconds")
        except Exception as e:
            failures.append(f"http_capture_to_observation (http2 lf) JSON parse failed: {e}")



    # 1g) http_capture_to_parity_observation: parse a small synthetic envelope capture into a parity observation snippet.
    cap = EXAMPLES.parent / "test-vectors" / "http_capture_public_notice_feed_example.txt"
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "http_capture_to_parity_observation.py"),
            "--capture",
            str(cap),
            "--channel-id",
            "web_primary",
            "--url",
            "https://elections.example/notices/feed/latest.json",
            "--fetched-at",
            "2026-02-25T12:00:08Z",
        ]
    )
    if code not in (0, 1):
        failures.append("http_capture_to_parity_observation failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            for k in ["channel_id", "url", "fetched_at", "body_sha256"]:
                if k not in o:
                    failures.append(f"http_capture_to_parity_observation missing key: {k}")
            if o.get("channel_id") != "web_primary":
                failures.append("http_capture_to_parity_observation wrong channel_id")
            if o.get("fetched_at") != "2026-02-25T12:00:08Z":
                failures.append("http_capture_to_parity_observation wrong fetched_at")
            bs = str(o.get("body_sha256") or "")
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", bs):
                failures.append("http_capture_to_parity_observation body_sha256 not sha256:<hex>")
            if o.get("http_status") != 200:
                failures.append("http_capture_to_parity_observation wrong http_status")
            if o.get("content_type") != "application/json":
                failures.append("http_capture_to_parity_observation wrong content_type")
            # Envelope fields should be parseable from the synthetic body.
            if str(o.get("envelope_kind") or "").strip() != "hfv.public.notice_feed":
                failures.append("http_capture_to_parity_observation wrong envelope_kind")
            for k in ["envelope_payload_sha256", "envelope_tbs_sha256"]:
                v = str(o.get(k) or "")
                if not re.fullmatch(r"sha256:[0-9a-f]{64}", v):
                    failures.append(f"http_capture_to_parity_observation {k} not sha256:<hex>")
            if "parse_error" in o and str(o.get("parse_error") or ""):
                failures.append("http_capture_to_parity_observation unexpectedly emitted parse_error")
        except Exception as e:
            failures.append(f"http_capture_to_parity_observation JSON parse failed: {e}")

    # 2) Implementation-scoped verifier report card
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "verifier_report_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_verifier_report_minimal"),
        ]
    )
    if code != 0:
        failures.append("verifier_report_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 3) Packet-scoped verifier output card
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "packet_verification_report_card.py"),
            "--packet",
            str(EXAMPLES / "evidence_packet_packet_verification_report_minimal"),
        ]
    )
    if code != 0:
        failures.append("packet_verification_report_card failed")
        sys.stderr.write(out)
        sys.stderr.write(err)

    # 4) observer_verify_packet: ensure --public --json path remains usable.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "observer_verify_packet.py"),
            str(EXAMPLES / "evidence_packet_minimal"),
            "--public",
            "--json",
        ]
    )
    if code != 0:
        failures.append("observer_verify_packet --public --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            json.loads(out)
        except Exception as e:
            failures.append(f"observer_verify_packet JSON parse failed: {e}")

    # 4b) public_surface_pins: should emit JSON and include the verifier comparability pins.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "public_surface_pins.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("public_surface_pins --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            for k in [
                "envelope_kinds_sha256",
                "verifier_problem_codes_sha256",
                "verifier_profiles_sha256",
                "surface_anomaly_codes_sha256",
            ]:
                if k not in o:
                    failures.append(f"public_surface_pins missing key: {k}")
        except Exception as e:
            failures.append(f"public_surface_pins JSON parse failed: {e}")

    # 4c) public_artifact_lint: conservative redaction lint must exit 0 on core publishable example packets.
    for pkt in [
        "evidence_packet_public_surface_parity_snapshot_minimal",
        "evidence_packet_liveness_beacon_minimal",
        "evidence_packet_public_notice_feed",
    ]:
        code, out, err = run(
            [
                sys.executable,
                str(TOOLS / "public_artifact_lint.py"),
                "--packet",
                str(EXAMPLES / pkt),
                "--json",
            ]
        )
        if code != 0:
            failures.append(f"public_artifact_lint failed for {pkt}")
            sys.stderr.write(out)
            sys.stderr.write(err)
        else:
            try:
                o = json.loads(out)
                s = o.get("summary") or {}
                if int(s.get("fail") or 0) != 0:
                    failures.append(f"public_artifact_lint reported failures for {pkt}")
            except Exception as e:
                failures.append(f"public_artifact_lint JSON parse failed: {e}")

    # 5) evidence_object_card: dispatch should work for operator-facing example packets.
    for pkt in [
        "evidence_packet_public_notice",
        "evidence_packet_public_notice_feed",
        "evidence_packet_official_channel_directory",
        "evidence_packet_well_known_discovery",
        "evidence_packet_public_surface_parity_snapshot_minimal",
        "evidence_packet_verifier_report_minimal",
        "evidence_packet_packet_verification_report_minimal",
        "evidence_packet_liveness_beacon_minimal",
        "evidence_packet_publication_compliance_minimal",
    ]:
        code, out, err = run(
            [
                sys.executable,
                str(TOOLS / "evidence_object_card.py"),
                "--packet",
                str(EXAMPLES / pkt),
            ]
        )
        if code != 0:
            failures.append(f"evidence_object_card failed for {pkt}")
            sys.stderr.write(out)
            sys.stderr.write(err)

    # 5b) example_county_pilot_smoke: synthetic scenario harness must verify all referenced packets.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "example_county_pilot_smoke.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("example_county_pilot_smoke --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("status") != "PASS":
                failures.append("example_county_pilot_smoke did not report PASS")
            if int(o.get("packets_checked") or 0) < 12:
                failures.append("example_county_pilot_smoke checked too few packets")
            if o.get("synthetic_only") is not True:
                failures.append("example_county_pilot_smoke missing synthetic_only=true")
        except Exception as e:
            failures.append(f"example_county_pilot_smoke JSON parse failed: {e}")

    # 5c) example_county_output_pack: derived output map must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "example_county_output_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("example_county_output_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("smoke_status") != "PASS":
                failures.append("example_county_output_pack did not report PASS smoke_status")
            if int(o.get("packet_count") or 0) < 12:
                failures.append("example_county_output_pack checked too few packets")
            if o.get("synthetic_only") is not True:
                failures.append("example_county_output_pack missing synthetic_only=true")
        except Exception as e:
            failures.append(f"example_county_output_pack JSON parse failed: {e}")


    # 5c2) mission_kernel_closeout: seven-element mission kernel must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "mission_kernel_closeout.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("mission_kernel_closeout --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("mission_kernel_closeout archive_version mismatch")
            if o.get("readiness_verdict") != "SYNTHETIC_REPLAY_PASS_LIVE_NO_GO":
                failures.append("mission_kernel_closeout verdict not live no-go")
            if len(o.get("kernel_elements") or []) != 7:
                failures.append("mission_kernel_closeout did not emit seven kernel elements")
            if (o.get("refactor_audit") or {}).get("status") != "PASS":
                failures.append("mission_kernel_closeout refactor audit did not pass")
        except Exception as e:
            failures.append(f"mission_kernel_closeout JSON parse failed: {e}")


    # 5c3) mission_kernel_live_evidence_intake: live-evidence intake must fail closed without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "mission_kernel_live_evidence_intake.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("mission_kernel_live_evidence_intake --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            report = o.get("report") if isinstance(o.get("report"), dict) else o
            if report.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("mission_kernel_live_evidence_intake archive_version mismatch")
            if report.get("decision") != "NO_GO_NO_LIVE_EVIDENCE_SUBMITTED":
                failures.append("mission_kernel_live_evidence_intake decision did not fail closed")
            if int(report.get("live_evidence_object_count", -1)) != 0:
                failures.append("mission_kernel_live_evidence_intake found unexpected live evidence objects")
            if int(report.get("valid_live_evidence_object_count", -1)) != 0:
                failures.append("mission_kernel_live_evidence_intake found unexpected valid live evidence objects")
            if report.get("synthetic_archive_report") is not True or report.get("no_live_deployment_claim") is not True:
                failures.append("mission_kernel_live_evidence_intake missing boundary flags")
            if len(report.get("rows") or []) != 7:
                failures.append("mission_kernel_live_evidence_intake did not evaluate seven workqueue items")
        except Exception as e:
            failures.append(f"mission_kernel_live_evidence_intake JSON parse failed: {e}")


    # 5d) trust_recovery_output_pack: failure handoff matrix must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "trust_recovery_output_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("trust_recovery_output_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("trust_recovery_output_pack archive_version mismatch")
            if int(o.get("row_count") or 0) < 10:
                failures.append("trust_recovery_output_pack checked too few failure modes")
            if o.get("synthetic_only") is not True:
                failures.append("trust_recovery_output_pack missing synthetic_only=true")
        except Exception as e:
            failures.append(f"trust_recovery_output_pack JSON parse failed: {e}")

    # 5e) human_review_handoff_pack: reviewer handoff matrix must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "human_review_handoff_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("human_review_handoff_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("human_review_handoff_pack archive_version mismatch")
            if int(o.get("scenario_count") or 0) < 10:
                failures.append("human_review_handoff_pack checked too few scenarios")
            if o.get("synthetic_only") is not True:
                failures.append("human_review_handoff_pack missing synthetic_only=true")
        except Exception as e:
            failures.append(f"human_review_handoff_pack JSON parse failed: {e}")


    # 5f) example_county_evaluator_scorecard: evaluator scorecard must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "example_county_evaluator_scorecard.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("example_county_evaluator_scorecard --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("example_county_evaluator_scorecard archive_version mismatch")
            if o.get("status") != "PASS":
                failures.append("example_county_evaluator_scorecard did not report PASS")
            if int(o.get("total_points") or 0) != int(o.get("max_points") or -1):
                failures.append("example_county_evaluator_scorecard did not earn full synthetic points")
            if o.get("synthetic_only") is not True:
                failures.append("example_county_evaluator_scorecard missing synthetic_only=true")
        except Exception as e:
            failures.append(f"example_county_evaluator_scorecard JSON parse failed: {e}")



    # 5g) example_county_negative_control_runner: expected-failure fixtures must reject tampered temp packets.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "example_county_negative_control_runner.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("example_county_negative_control_runner --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("example_county_negative_control_runner archive_version mismatch")
            if o.get("status") != "PASS":
                failures.append("example_county_negative_control_runner did not report PASS")
            if int(o.get("fixture_count") or 0) < 8:
                failures.append("example_county_negative_control_runner checked too few fixtures")
            if not all(isinstance(r, dict) and r.get("observed_status") == "FAIL" and r.get("expectation_status") == "PASS" for r in (o.get("results") or [])):
                failures.append("example_county_negative_control_runner did not observe expected failures")
            if o.get("synthetic_only") is not True:
                failures.append("example_county_negative_control_runner missing synthetic_only=true")
        except Exception as e:
            failures.append(f"example_county_negative_control_runner JSON parse failed: {e}")


    # 5h) release_maintainer_handoff_pack: maintainer summary must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "release_maintainer_handoff_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("release_maintainer_handoff_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            if o.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("release_maintainer_handoff_pack archive_version mismatch")
            if o.get("synthetic_only") is not True or o.get("no_live_deployment_claim") is not True:
                failures.append("release_maintainer_handoff_pack missing boundary flags")
            source = o.get("source_review_triage") or {}
            if int(source.get("expired_review_count") or 0) != 0:
                failures.append("release_maintainer_handoff_pack found expired source reviews")
            outputs = o.get("current_outputs") or {}
            if outputs.get("smoke_status") != "PASS" or outputs.get("negative_control_status") != "PASS":
                failures.append("release_maintainer_handoff_pack current outputs not PASS")
        except Exception as e:
            failures.append(f"release_maintainer_handoff_pack JSON parse failed: {e}")


    # 5i) release_go_no_go_pack: synthetic release decision and source burn-down must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "release_go_no_go_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("release_go_no_go_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            d = o.get("decision") or {}
            s = o.get("source_burndown") or {}
            if d.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("release_go_no_go_pack archive_version mismatch")
            if d.get("synthetic_only") is not True or d.get("no_live_deployment_claim") is not True:
                failures.append("release_go_no_go_pack missing boundary flags")
            if d.get("topline_decision") != "GO_SYNTHETIC_RELEASE_ONLY":
                failures.append("release_go_no_go_pack topline did not remain synthetic-only")
            if not str(d.get("live_pilot_decision") or "").startswith("NO_GO_LIVE_PILOT"):
                failures.append("release_go_no_go_pack live pilot decision not NO_GO")
            if "expired_review_count" not in s or int(s.get("expired_review_count")) != 0:
                failures.append("release_go_no_go_pack found expired source reviews")
            if "due_within_30_days_count" not in s or int(s.get("due_within_30_days_count") or 0) < 0:
                failures.append("release_go_no_go_pack missing or invalid source-review queue count")
        except Exception as e:
            failures.append(f"release_go_no_go_pack JSON parse failed: {e}")



    # 5j) local_pilot_intake_pack: local-pilot no-go matrix must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "local_pilot_intake_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("local_pilot_intake_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            m = o.get("intake_matrix") or {}
            if m.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("local_pilot_intake_pack archive_version mismatch")
            if m.get("synthetic_only") is not True or m.get("no_live_deployment_claim") is not True:
                failures.append("local_pilot_intake_pack missing boundary flags")
            if not str(m.get("decision") or "").startswith("NO_GO_LIVE_PILOT"):
                failures.append("local_pilot_intake_pack decision not NO_GO_LIVE_PILOT")
            if int(m.get("requirement_count") or 0) < 14:
                failures.append("local_pilot_intake_pack checked too few requirements")
        except Exception as e:
            failures.append(f"local_pilot_intake_pack JSON parse failed: {e}")

    # 5k) redaction_publication_pack: public-release redaction no-go matrix must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "redaction_publication_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("redaction_publication_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            m = o.get("redaction_matrix") or {}
            if m.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("redaction_publication_pack archive_version mismatch")
            if m.get("synthetic_only") is not True or m.get("no_live_deployment_claim") is not True:
                failures.append("redaction_publication_pack missing boundary flags")
            if m.get("no_public_release_authorization") is not True:
                failures.append("redaction_publication_pack missing no-public-release flag")
            if not str(m.get("decision") or "").startswith("NO_GO_PUBLIC_RELEASE"):
                failures.append("redaction_publication_pack decision not NO_GO_PUBLIC_RELEASE")
            if int(m.get("policy_count") or 0) < 14:
                failures.append("redaction_publication_pack checked too few policies")
        except Exception as e:
            failures.append(f"redaction_publication_pack JSON parse failed: {e}")


    # 5l) accessibility_language_pack: accessibility/language no-go matrix must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "accessibility_language_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("accessibility_language_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            m = o.get("accessibility_language_matrix") or {}
            if m.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("accessibility_language_pack archive_version mismatch")
            if m.get("synthetic_only") is not True or m.get("no_live_deployment_claim") is not True:
                failures.append("accessibility_language_pack missing boundary flags")
            if m.get("no_public_release_authorization") is not True:
                failures.append("accessibility_language_pack missing no-public-release flag")
            if m.get("no_accessibility_conformance_certification") is not True:
                failures.append("accessibility_language_pack missing accessibility non-certification flag")
            if not str(m.get("decision") or "").startswith("NO_GO_PUBLIC_RELEASE_ACCESSIBILITY_LANGUAGE"):
                failures.append("accessibility_language_pack decision not NO_GO_PUBLIC_RELEASE_ACCESSIBILITY_LANGUAGE")
            if int(m.get("policy_count") or 0) < 14:
                failures.append("accessibility_language_pack checked too few policies")
        except Exception as e:
            failures.append(f"accessibility_language_pack JSON parse failed: {e}")


    # 5m) evidence_custody_provenance_pack: custody/provenance no-go matrix must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "evidence_custody_provenance_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("evidence_custody_provenance_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            m = o.get("custody_matrix") or {}
            if m.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("evidence_custody_provenance_pack archive_version mismatch")
            if m.get("synthetic_only") is not True or m.get("no_live_deployment_claim") is not True:
                failures.append("evidence_custody_provenance_pack missing boundary flags")
            if m.get("no_chain_of_custody_certification") is not True:
                failures.append("evidence_custody_provenance_pack missing chain-of-custody non-certification flag")
            if not str(m.get("decision") or "").startswith("NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE"):
                failures.append("evidence_custody_provenance_pack decision not NO_GO_LIVE_PILOT_CUSTODY_PROVENANCE")
            if int(m.get("policy_count") or 0) < 14:
                failures.append("evidence_custody_provenance_pack checked too few policies")
        except Exception as e:
            failures.append(f"evidence_custody_provenance_pack JSON parse failed: {e}")



    # 5n) independent_review_conflict_pack: independent-review/conflict no-go matrix must be buildable without mutating release files.
    code, out, err = run(
        [
            sys.executable,
            str(TOOLS / "independent_review_conflict_pack.py"),
            "--json",
        ]
    )
    if code != 0:
        failures.append("independent_review_conflict_pack --json failed")
        sys.stderr.write(out)
        sys.stderr.write(err)
    else:
        try:
            o = json.loads(out)
            m = o.get("review_matrix") or {}
            if m.get("archive_version") != (ROOT / "VERSION").read_text(encoding="utf-8").strip():
                failures.append("independent_review_conflict_pack archive_version mismatch")
            if m.get("synthetic_only") is not True or m.get("no_live_deployment_claim") is not True:
                failures.append("independent_review_conflict_pack missing boundary flags")
            if m.get("no_third_party_validation_claim") is not True:
                failures.append("independent_review_conflict_pack missing third-party-validation non-claim flag")
            if not str(m.get("decision") or "").startswith("NO_GO_INDEPENDENT_REVIEW_CONFLICT"):
                failures.append("independent_review_conflict_pack decision not NO_GO_INDEPENDENT_REVIEW_CONFLICT")
            if int(m.get("policy_count") or 0) < 14:
                failures.append("independent_review_conflict_pack checked too few policies")
        except Exception as e:
            failures.append(f"independent_review_conflict_pack JSON parse failed: {e}")


    # 5o) retrieve_compacted_history: recover one exact historical payload and verify its bound bytes.
    with tempfile.TemporaryDirectory() as td:
        rel = "artifacts/reports/source-byte-cache-batch-ingest-rev0893.json"
        recovered = Path(td) / "recovered.json"
        code, out, err = run([
            sys.executable,
            str(TOOLS / "retrieve_compacted_history.py"),
            "--path",
            rel,
            "--output",
            str(recovered),
        ])
        if code != 0:
            failures.append("retrieve_compacted_history recovery failed")
            sys.stderr.write(out)
            sys.stderr.write(err)
        else:
            try:
                stub = json.loads((ROOT / rel).read_text(encoding="utf-8"))
                data = recovered.read_bytes()
                actual = "sha256:" + hashlib.sha256(data).hexdigest()
                if len(data) != stub.get("original_size_bytes") or actual != stub.get("original_sha256"):
                    failures.append("retrieve_compacted_history recovered bytes do not match stub bindings")
            except Exception as e:
                failures.append(f"retrieve_compacted_history verification failed: {e}")


    # 6) Path traversal hardening: packet_common MUST reject unsafe payload_pointer.uri.
    try:
        sys.path.insert(0, str(TOOLS))
        from packet_common import recompute_payload_digest  # type: ignore

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "objects").mkdir(parents=True, exist_ok=True)
            unsafe_uris = [
                "../secrets.txt",
                "%2e%2e%2fsecrets.txt",
                "..%2Fsecrets.txt",
                "%2e%2e%5csecrets.txt",
            ]
            for u in unsafe_uris:
                env = {
                    "canonicalization": "RFC8785-JCS",
                    "payload_pointer": {"uri": u, "media_type": "application/json"},
                }
                try:
                    recompute_payload_digest(env, tmp / "objects")
                    failures.append(f"packet_common did not reject unsafe payload_pointer.uri: {u!r}")
                except SystemExit:
                    pass

            # Symlink escape hardening: reject packets where objects/ is a symlink out of the packet root.
            pkt = tmp / "pkt_symlink_escape"
            pkt.mkdir(parents=True, exist_ok=True)
            outside = tmp / "outside_objects"
            outside.mkdir(parents=True, exist_ok=True)
            fname = "sha256-" + ("a" * 64) + ".json"
            (outside / fname).write_text("{\"x\": 1}\n", encoding="utf-8")
            try:
                os.symlink(outside, pkt / "objects")
            except Exception:
                # If symlinks are unavailable in this environment, skip the test.
                pass
            else:
                env = {
                    "canonicalization": "RFC8785-JCS",
                    "payload_pointer": {"uri": fname, "media_type": "application/json"},
                }
                try:
                    recompute_payload_digest(env, pkt / "objects")
                    failures.append("packet_common did not reject objects/ symlink escape")
                except SystemExit:
                    pass
    except Exception as e:
        failures.append(f"packet_common import/smoke failed: {e}")

    if failures:
        for f in failures:
            print("ERROR:", f, file=sys.stderr)
        return 2

    print("PASS: operator tools smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
