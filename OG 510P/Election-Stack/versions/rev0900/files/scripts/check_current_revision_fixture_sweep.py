#!/usr/bin/env python3
"""Check that current-revision fixtures move with VERSION.

Several recent releases had the same failure mode: the main VERSION advanced,
but a rev-specific trust-policy fixture, source-byte batch report, or verifier
example still carried the previous revision.  This gate is intentionally narrow
and mechanical.  It does not create new authority or source-byte evidence; it
only prevents the current synthetic release surface from presenting stale bytes
as if they belonged to the current revision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_context import release_date as _release_date  # noqa: E402

VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
REPORT = ROOT / "artifacts" / "reports" / f"current-revision-fixture-sweep-rev{REV}.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_pin(path: Path) -> str:
    return "sha256:" + sha256_file(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except Exception:
        return str(path)


def sidecar_ok(path: Path) -> tuple[bool, str]:
    sidecar = Path(str(path) + ".sha256")
    if not sidecar.exists():
        return False, f"missing sidecar {rel(sidecar)}"
    expected = f"sha256:{sha256_file(path)}  {path.name}"
    got = sidecar.read_text(encoding="utf-8").strip()
    return got == expected, "" if got == expected else f"sidecar mismatch for {rel(path)}"


def read_packet_report_payload(packet_dir: Path) -> dict[str, Any]:
    env_dir = packet_dir / "envelopes"
    for env_path in sorted(env_dir.glob("*.json")):
        env = load_json(env_path)
        if not isinstance(env, dict) or env.get("kind") != "hfv.verifier.packet_verification_report":
            continue
        ptr = env.get("payload_pointer")
        if not isinstance(ptr, dict):
            continue
        uri = str(ptr.get("uri") or "")
        target = packet_dir / (uri if uri.startswith("objects/") else f"objects/{uri}")
        obj = load_json(target)
        return obj if isinstance(obj, dict) else {}
    return {}


def add(rows: list[dict[str, Any]], *, check_id: str, path: Path, ok: bool, detail: str) -> None:
    rows.append({"check_id": check_id, "path": rel(path), "ok": bool(ok), "detail": detail})


def build_report() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    rev_token = f"rev{REV}"

    # Source-byte batch ingest report: current file name and archive_version must match.
    batch = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-ingest-rev{REV}.json"
    if batch.exists():
        obj = load_json(batch)
        add(rows, check_id="current_source_byte_batch_report", path=batch, ok=obj.get("archive_version") == VERSION, detail=f"archive_version={obj.get('archive_version')!r}")
    else:
        add(rows, check_id="current_source_byte_batch_report", path=batch, ok=False, detail="missing current source-byte batch ingest report")

    # Source-byte cache intake manifest: current JSON and sha256sum handoff file must move with VERSION.
    intake = ROOT / "artifacts" / "reports" / f"source-byte-cache-intake-manifest-rev{REV}.json"
    intake_sha = ROOT / "artifacts" / "source_byte_cache_intake" / f"source-byte-cache-missing-receipts-rev{REV}.sha256"
    if intake.exists():
        iobj = load_json(intake)
        ok = (
            iobj.get("archive_version") == VERSION
            and str(iobj.get("sha256sum_path") or "") == rel(intake_sha)
            and int(iobj.get("manifest_entry_count") or -1) == int(iobj.get("receipt_missing_count") or -2)
            and iobj.get("queue_next_batch_matches") is True
        )
        add(rows, check_id="current_source_byte_intake_manifest", path=intake, ok=ok, detail=f"archive_version={iobj.get('archive_version')!r}; entries={iobj.get('manifest_entry_count')!r}")
    else:
        add(rows, check_id="current_source_byte_intake_manifest", path=intake, ok=False, detail="missing current source-byte cache intake manifest")
    if intake_sha.exists():
        line_count = len([ln for ln in intake_sha.read_text(encoding="utf-8").splitlines() if ln.strip()])
        expected = load_json(intake).get("manifest_entry_count") if intake.exists() else None
        ok = expected == line_count and line_count >= 0
        add(rows, check_id="current_source_byte_intake_sha256sum", path=intake_sha, ok=ok, detail=f"lines={line_count}; expected={expected!r}")
    else:
        add(rows, check_id="current_source_byte_intake_sha256sum", path=intake_sha, ok=False, detail="missing current source-byte cache intake sha256sum file")

    # Selected-batch resume report should also move with VERSION so operators do
    # not run a stale first-batch receipt scan after a version bump.
    resume = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-resume-rev{REV}.json"
    if resume.exists():
        robj = load_json(resume)
        batch01 = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
        ok = (
            robj.get("archive_version") == VERSION
            and robj.get("batch_file") == rel(batch01)
            and robj.get("assume_empty_cache") is True
            and robj.get("third_party_bytes_bundled") is False
            and int(robj.get("matched_cache_file_count", -1)) == 0
        )
        add(rows, check_id="current_source_byte_batch_resume", path=resume, ok=ok, detail=f"archive_version={robj.get('archive_version')!r}; batch_file={robj.get('batch_file')!r}; candidates={robj.get('candidate_source_count')!r}")
    else:
        add(rows, check_id="current_source_byte_batch_resume", path=resume, ok=False, detail="missing current source-byte batch resume report")

    # Source-byte batch status report should move with VERSION and agree with the
    # current receipt-missing batch handoff set.
    status = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-status-rev{REV}.json"
    if status.exists():
        sobj = load_json(status)
        ok = (
            sobj.get("archive_version") == VERSION
            and sobj.get("third_party_bytes_bundled") is False
            and int(sobj.get("error_count", -1)) == 0
            and int(sobj.get("batched_source_count") or -1) == int(sobj.get("receipt_missing_count") or -2)
            and int(sobj.get("first_incomplete_batch_index", 0)) > 0
        )
        add(rows, check_id="current_source_byte_batch_status", path=status, ok=ok, detail=f"archive_version={sobj.get('archive_version')!r}; missing={sobj.get('receipt_missing_count')!r}; first_batch={sobj.get('first_incomplete_batch_index')!r}")
    else:
        add(rows, check_id="current_source_byte_batch_status", path=status, ok=False, detail="missing current source-byte batch status report")

    # Per-batch sha256sum handoff files should move with VERSION and reconstruct
    # the current intake manifest without stale rev-specific paths.
    batch_manifest = ROOT / "artifacts" / "reports" / f"source-byte-cache-batch-manifests-rev{REV}.json"
    if batch_manifest.exists():
        bobj = load_json(batch_manifest)
        batch_files = bobj.get("batch_files") or []
        expected_entries = load_json(intake).get("manifest_entry_count") if intake.exists() else None
        ok = (
            bobj.get("archive_version") == VERSION
            and bobj.get("master_sha256sum_path") == rel(intake_sha)
            and int(bobj.get("manifest_entry_count") or -1) == int(expected_entries or -2)
            and int(bobj.get("batch_count") or -1) == len(batch_files)
            and int(bobj.get("error_count", -1)) == 0
        )
        add(rows, check_id="current_source_byte_batch_manifests", path=batch_manifest, ok=ok, detail=f"archive_version={bobj.get('archive_version')!r}; batches={bobj.get('batch_count')!r}; entries={bobj.get('manifest_entry_count')!r}")
        missing_batches = []
        for row in batch_files:
            if not isinstance(row, dict):
                continue
            bpath = ROOT / str(row.get("path") or "")
            if not bpath.exists():
                missing_batches.append(str(row.get("path") or ""))
        ok_files = not missing_batches and len(batch_files) == int(bobj.get("batch_count") or -1)
        add(rows, check_id="current_source_byte_batch_manifest_files", path=ROOT / "artifacts" / "source_byte_cache_intake" / "batches", ok=ok_files, detail="missing=" + ",".join(missing_batches) if missing_batches else f"files={len(batch_files)}")
    else:
        add(rows, check_id="current_source_byte_batch_manifests", path=batch_manifest, ok=False, detail="missing current source-byte cache batch-manifests report")

    # Source-byte batch host slices should move with VERSION and reconstruct current batch01.
    host_slice = ROOT / "artifacts" / "reports" / f"source-byte-batch-host-slices-rev{REV}.json"
    batch01 = ROOT / "artifacts" / "source_byte_cache_intake" / "batches" / f"source-byte-cache-missing-receipts-rev{REV}-batch01.sha256"
    if host_slice.exists():
        hobj = load_json(host_slice)
        hfiles = hobj.get("host_slices") or []
        missing_host_slices = []
        for row in hfiles:
            if not isinstance(row, dict):
                continue
            hpath = ROOT / str(row.get("path") or "")
            if not hpath.exists():
                missing_host_slices.append(str(row.get("path") or ""))
        ok = (
            hobj.get("archive_version") == VERSION
            and hobj.get("batch_file") == rel(batch01)
            and hobj.get("third_party_bytes_bundled") is False
            and int(hobj.get("error_count", -1)) == 0
            and int(hobj.get("host_slice_count") or -1) == len(hfiles)
            and not missing_host_slices
        )
        detail = "missing=" + ",".join(missing_host_slices) if missing_host_slices else f"slices={hobj.get('host_slice_count')!r}; dominant={hobj.get('dominant_host')!r}"
        add(rows, check_id="current_source_byte_batch_host_slices", path=host_slice, ok=ok, detail=detail)
    else:
        add(rows, check_id="current_source_byte_batch_host_slices", path=host_slice, ok=False, detail="missing current source-byte batch host-slices report")

    # DNS preflight and classified attempt workpacks should move with VERSION, but
    # they remain environment/retry evidence rather than completion claims.
    dns = ROOT / "artifacts" / "reports" / f"source-byte-dns-preflight-rev{REV}.json"
    if dns.exists():
        dobj = load_json(dns)
        ok = (
            dobj.get("archive_version") == VERSION
            and dobj.get("http_fetch_io") is False
            and dobj.get("write_receipts") is False
            and dobj.get("third_party_bytes_bundled") is False
            and int(dobj.get("selected_missing_source_count") or -1) == len([ln for ln in batch01.read_text(encoding="utf-8").splitlines() if ln.strip()])
        )
        add(rows, check_id="current_source_byte_dns_preflight", path=dns, ok=ok, detail=f"hosts={dobj.get('selected_unique_host_count')!r}; statuses={dobj.get('status_counts')!r}")
    else:
        add(rows, check_id="current_source_byte_dns_preflight", path=dns, ok=False, detail="missing current DNS preflight report")

    attempt_workpacks = ROOT / "artifacts" / "reports" / f"source-byte-batch-attempt-workpacks-rev{REV}.json"
    if attempt_workpacks.exists():
        aobj = load_json(attempt_workpacks)
        workpacks = aobj.get("workpacks") or []
        missing_workpacks = []
        for row in workpacks:
            if not isinstance(row, dict):
                continue
            wpath = ROOT / str(row.get("path") or "")
            if not wpath.exists():
                missing_workpacks.append(str(row.get("path") or ""))
        ok = (
            aobj.get("archive_version") == VERSION
            and aobj.get("batch_file") == rel(batch01)
            and aobj.get("network_io") is False
            and aobj.get("third_party_bytes_bundled") is False
            and int(aobj.get("batch_file_entry_count") or -1) == len([ln for ln in batch01.read_text(encoding="utf-8").splitlines() if ln.strip()])
            and int(aobj.get("workpack_count") or -1) == len(workpacks)
            and not missing_workpacks
        )
        detail = "missing=" + ",".join(missing_workpacks) if missing_workpacks else f"workpacks={aobj.get('workpack_count')!r}; classes={aobj.get('action_class_counts')!r}"
        add(rows, check_id="current_source_byte_batch_attempt_workpacks", path=attempt_workpacks, ok=ok, detail=detail)
    else:
        add(rows, check_id="current_source_byte_batch_attempt_workpacks", path=attempt_workpacks, ok=False, detail="missing current source-byte attempt-workpack report")

    # Source-byte operator workplan should move with VERSION so the newest finite
    # completion plan cannot point at stale batch/workpack artifacts.
    workplan = ROOT / "artifacts" / "reports" / f"source-byte-operator-workplan-rev{REV}.json"
    if workplan.exists():
        wobj = load_json(workplan)
        ok = (
            wobj.get("archive_version") == VERSION
            and wobj.get("network_io") is False
            and wobj.get("third_party_bytes_bundled") is False
            and wobj.get("first_incomplete_batch_file") == rel(batch01)
            and int(wobj.get("batch01_source_count") or -1) == len([ln for ln in batch01.read_text(encoding="utf-8").splitlines() if ln.strip()])
            and bool(wobj.get("operator_command_plan"))
        )
        add(rows, check_id="current_source_byte_operator_workplan", path=workplan, ok=ok, detail=f"archive_version={wobj.get('archive_version')!r}; commands={len(wobj.get('operator_command_plan') or [])}; missing={(wobj.get('receipt_summary') or {}).get('receipt_missing_count')!r}")
    else:
        add(rows, check_id="current_source_byte_operator_workplan", path=workplan, ok=False, detail="missing current source-byte operator workplan")

    # Strict policy lockfile and publication receipt: current filenames, ids, digest sidecars.
    policy = ROOT / "artifacts" / "examples" / "trust_policies" / f"verification-policy-lockfile-ed25519-authorized-threshold2-rev{REV}.json"
    receipt = ROOT / "artifacts" / "examples" / "trust_policies" / f"verification-policy-lockfile-ed25519-authorized-threshold2-rev{REV}.publication-receipt.json"
    if policy.exists():
        pobj = load_json(policy)
        policy_id = str(pobj.get("policy_id") or "")
        policy_version_ok = (
            REV in policy_id
            and pobj.get("release_context", {}).get("archive_version") == VERSION
            and pobj.get("verifier_requirements", {}).get("archive_version") == VERSION
        )
        add(rows, check_id="current_policy_lockfile_identity", path=policy, ok=policy_version_ok, detail=f"policy_id={policy_id!r}")
        ok, detail = sidecar_ok(policy)
        add(rows, check_id="current_policy_lockfile_sidecar", path=Path(str(policy) + ".sha256"), ok=ok, detail=detail or "sidecar matches raw policy bytes")
    else:
        add(rows, check_id="current_policy_lockfile_identity", path=policy, ok=False, detail="missing current policy lockfile")
        policy_id = ""

    if receipt.exists() and policy.exists():
        robj = load_json(receipt)
        actual_pin = sha_pin(policy)
        channel_details = []
        channel_ok = True
        for idx, ch in enumerate(robj.get("publication_channels") or []):
            if not isinstance(ch, dict):
                channel_ok = False
                channel_details.append(f"channel {idx} non-object")
                continue
            cids = [str(ch.get(k) or "") for k in ("channel_id", "locator_ref")]
            if not any(rev_token in v for v in cids):
                channel_ok = False
                channel_details.append(f"channel {idx} missing {rev_token}")
            digests = {str(ch.get(k) or "") for k in ch if k.startswith("observed_") and k.endswith("sha256")}
            if digests != {actual_pin}:
                channel_ok = False
                channel_details.append(f"channel {idx} digest drift")
        receipt_id_ok = (
            REV in str(robj.get("receipt_id") or "")
            and robj.get("policy_lockfile_id") == policy_id
            and robj.get("verification_policy_lockfile_id") == policy_id
            and robj.get("policy_lockfile_sha256") == actual_pin
            and robj.get("verification_policy_lockfile_sha256") == actual_pin
        )
        add(rows, check_id="current_policy_receipt_identity", path=receipt, ok=receipt_id_ok and channel_ok, detail="; ".join(channel_details) if channel_details else "receipt ids, channels, and policy digest match current lockfile")
        ok, detail = sidecar_ok(receipt)
        add(rows, check_id="current_policy_receipt_sidecar", path=Path(str(receipt) + ".sha256"), ok=ok, detail=detail or "sidecar matches raw receipt bytes")
    else:
        add(rows, check_id="current_policy_receipt_identity", path=receipt, ok=False, detail="missing current policy receipt or policy lockfile")

    # PacketVerificationReport examples: template and packet payload should not lag behind VERSION.
    template = ROOT / "artifacts" / "templates" / "packet-verification-report-example.json"
    if template.exists():
        tobj = load_json(template)
        tool = tobj.get("tool") if isinstance(tobj, dict) else {}
        ok = isinstance(tool, dict) and tool.get("version") == VERSION and tool.get("archive_version") == VERSION
        add(rows, check_id="current_packet_verification_report_template", path=template, ok=ok, detail=f"tool={tool!r}")
    else:
        add(rows, check_id="current_packet_verification_report_template", path=template, ok=False, detail="missing template")

    packet = ROOT / "artifacts" / "examples" / "evidence_packet_packet_verification_report_minimal"
    payload = read_packet_report_payload(packet) if packet.exists() else {}
    tool = payload.get("tool") if isinstance(payload, dict) else {}
    ok = isinstance(tool, dict) and tool.get("version") == VERSION and tool.get("archive_version") == VERSION
    add(rows, check_id="current_packet_verification_report_packet", path=packet, ok=ok, detail=f"tool={tool!r}")

    # Example County synthetic outputs are current-version smoke evidence; stale scenario ids caused repeated churn.
    ex = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
    for name in ("scenario.json", "smoke-report.json", "evidence-map.json", "evaluator-scorecard.json"):
        path = ex / name
        if not path.exists():
            add(rows, check_id="current_example_county_output", path=path, ok=False, detail="missing")
            continue
        obj = load_json(path)
        scenario_id = str(obj.get("scenario_id") or "")
        ok = obj.get("archive_version") == VERSION and VERSION in scenario_id
        add(rows, check_id=f"current_example_county_{name.replace('.', '_')}", path=path, ok=ok, detail=f"archive_version={obj.get('archive_version')!r}; scenario_id={scenario_id!r}")



    # Non-rev-named gate packs must still move with VERSION.  v896 exposed why
    # this belongs in the sweep: several no-go matrices were stale at v895 while
    # root navigation and the go/no-go packet had advanced.
    for check_id, rel_path, field, expected in [
        ("current_local_pilot_intake_pack", "artifacts/reports/local-pilot-intake-matrix.json", "archive_version", VERSION),
        ("current_redaction_publication_pack", "artifacts/reports/redaction-publication-matrix.json", "archive_version", VERSION),
        ("current_accessibility_language_pack", "artifacts/reports/accessibility-language-matrix.json", "archive_version", VERSION),
        ("current_custody_provenance_pack", "artifacts/reports/evidence-custody-provenance-matrix.json", "archive_version", VERSION),
        ("current_independent_review_pack", "artifacts/reports/independent-review-matrix.json", "archive_version", VERSION),
        ("current_adopter_authority_capture_pack", "artifacts/reports/adopter-authority-capture-matrix.json", "archive_version", VERSION),
        ("current_adopter_capture_validator", "artifacts/reports/adopter-capture-record-validation-report.json", "archive_version", VERSION),
        ("current_release_maintainer_handoff", "artifacts/reports/release-maintainer-handoff.json", "archive_version", VERSION),
        ("current_release_go_no_go_decision", "artifacts/reports/release-go-no-go-decision.json", "archive_version", VERSION),
    ]:
        path = ROOT / rel_path
        if not path.exists():
            add(rows, check_id=check_id, path=path, ok=False, detail="missing")
            continue
        obj = load_json(path)
        ok = obj.get(field) == expected
        add(rows, check_id=check_id, path=path, ok=ok, detail=f"{field}={obj.get(field)!r}; expected={expected!r}")

    # Current executable CDF/ballot-accounting reports are rev-named, but their
    # internal archive_version and decisions must also be current and bounded.
    for check_id, path, want_decision in [
        ("current_cdf_export_replay_report", ROOT / "artifacts" / "reports" / f"cdf-export-replay-report-rev{REV}.json", "SYNTHETIC_CDF_REPLAY_PASS_NOT_CONFORMANCE"),
        ("current_cdf_independent_replay_report", ROOT / "artifacts" / "reports" / f"cdf-independent-replay-verifier-rev{REV}.json", "INDEPENDENT_SYNTHETIC_CDF_REPLAY_AGREES_NOT_CONFORMANCE"),
        ("current_ballot_accounting_reconciliation_report", ROOT / "artifacts" / "reports" / f"ballot-accounting-reconciliation-rev{REV}.json", "SYNTHETIC_BALLOT_ACCOUNTING_RECONCILIATION_PASS_NOT_CUSTODY_EVIDENCE"),
        ("current_election_event_log_reconciliation_report", ROOT / "artifacts" / "reports" / f"election-event-log-reconciliation-rev{REV}.json", "SYNTHETIC_EVENT_LOG_CHAIN_PASS_NOT_LIVE_EEL"),
    ]:
        if not path.exists():
            add(rows, check_id=check_id, path=path, ok=False, detail="missing")
            continue
        obj = load_json(path)
        ok = obj.get("archive_version") == VERSION and obj.get("decision") == want_decision and (obj.get("counts") or {}).get("error_count") == 0
        add(rows, check_id=check_id, path=path, ok=ok, detail=f"archive_version={obj.get('archive_version')!r}; decision={obj.get('decision')!r}; errors={(obj.get('counts') or {}).get('error_count')!r}")

    failed = [r for r in rows if r.get("ok") is not True]
    return {
        "archive_version": VERSION,
        "release_date": _release_date(ROOT),
        "synthetic_only": True,
        "boundary": "Current-revision fixture sweep prevents stale synthetic fixtures from masquerading as current; it is not current voter instruction, not legal advice, not source-byte cache completeness, not public-release authorization, and not live-pilot approval.",
        "check_count": len(rows),
        "failed_count": len(failed),
        "status": "PASS" if not failed else "FAIL",
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write deterministic current-revision fixture sweep report")
    ap.add_argument("--json", action="store_true", help="print report JSON")
    args = ap.parse_args()

    report = build_report()
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(payload, encoding="utf-8")
    if args.json:
        sys.stdout.write(payload)

    if not args.write:
        if not REPORT.exists():
            print(f"ERROR: missing current-revision fixture sweep report: {rel(REPORT)}", file=sys.stderr)
            return 2
        shipped = load_json(REPORT)
        if shipped != report:
            print("ERROR: current-revision fixture sweep report is stale; run scripts/check_current_revision_fixture_sweep.py --write", file=sys.stderr)
            return 2
    if report["failed_count"]:
        for row in report["rows"]:
            if row.get("ok") is not True:
                print(f"ERROR: {row['check_id']}: {row['path']}: {row['detail']}", file=sys.stderr)
        return 2
    print(f"PASS: current-revision fixture sweep ({VERSION}, checks={report['check_count']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
