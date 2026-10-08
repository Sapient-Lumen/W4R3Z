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

import json
import re
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
EXAMPLES = ROOT / "artifacts" / "examples"


def run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


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
