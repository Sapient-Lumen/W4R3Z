import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from core_method_contract_lib import core_method_negative_canary_results
from core_method_contract_specs import iter_core_method_contract_specs
from external_metadata_contract_lib import external_metadata_rows
from package_preflight_lib import package_artifact_negative_canary_results, package_determinism_canary_results, package_sidecar_canary_results
from release_hygiene_lib import release_identity_canary_results
from release_integrity_lib import release_integrity_canary_results
from ledger_coldstore_contract_lib import ledger_coldstore_canary_results
from receipt_coldstore_contract_lib import receipt_coldstore_canary_results
from validation_toolchain_lib import build_validation_toolchain

NON_CLAIM = "canary-run-court, behavior-certification-board, release-legitimacy-notary, model-drift-sovereign, metadata-authority, and registry-bureaucracy-ratchet are forbidden; this surface records executable canary observations only and does not certify semantic sufficiency, public release authority, or continuation correctness."


def _load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _score(status: str) -> int:
    return 4 if status == "pass" else 0


def _row(row_id: str, expected: str, observed: str, status: str, surfaces: list[str]) -> dict[str, Any]:
    return {"id": row_id, "expected": expected, "observed": observed, "status": status, "score": _score(status), "surfaces": surfaces}


def _latest_revision_cues(root: pathlib.Path, revision: str, bundle: str) -> dict[str, Any]:
    targets = ["START_HERE.md", "README.md", "docs/README.md"]
    cue_re = re.compile(r"Latest revision `(?P<revision>rev\d{4})`")
    observations = []
    ok = True
    for rel in targets:
        text = (root / rel).read_text(encoding="utf-8")
        matches = [m.group("revision") for m in cue_re.finditer(text)]
        has_bundle = bundle in text
        observations.append({"surface": rel, "latest_revision_matches": matches, "contains_bundle": has_bundle})
        ok = ok and matches == [revision] and has_bundle
    return {"ok": ok, "observations": observations}



def _package_release_preflight_observation(root: pathlib.Path) -> dict[str, Any]:
    package_text = (root / "tools" / "package_release.py").read_text(encoding="utf-8")
    helper_text = (root / "tools" / "package_preflight_lib.py").read_text(encoding="utf-8")
    try:
        refresh_at = package_text.rindex("refresh_generated_surfaces(ROOT, include_release_integrity=True)")
        preflight_at = package_text.index("run_lint_preflight(ROOT)")
        zip_at = package_text.index("write_deterministic_zip(ROOT, bundle_path, bundle_name)")
        smoke_at = package_text.index("run_artifact_smoke(ROOT, bundle_path, bundle_name)")
        sidecar_at = package_text.index("write_verified_sha256_sidecar(bundle_path, sidecar, bundle_name)")
        order_ok = refresh_at < preflight_at < zip_at < smoke_at < sidecar_at
    except ValueError:
        order_ok = False
    helper_ok = all(needle in helper_text for needle in [
        "tools/run_lint_suite.py",
        "PYTHONDONTWRITEBYTECODE",
        "zipfile.ZipFile",
        "testzip()",
        "expected_zip_members",
        "PackagePreflightError",
        "safe_zip_member_target",
        "release-hygiene-excluded path present",
        "zip member order drifted from release paths",
        "zip member set drifted from release paths",
        "extract_zip_safely",
        "run_lint_preflight(extract_root)",
        "package_artifact_negative_canary_results",
        "package_determinism_canary_results",
        "package_sidecar_canary_results",
        "write_deterministic_zip",
        "write_verified_sha256_sidecar",
        "verify_sha256_sidecar",
        "FIXED_ZIP_DT",
        "FIXED_EXTERNAL_ATTR",
        "check=True",
    ])
    import_ok = "from package_preflight_lib import run_artifact_smoke, run_lint_preflight" in package_text
    return {
        "ok": order_ok and helper_ok and import_ok,
        "import_present": import_ok,
        "order": "refresh-before-preflight-before-zip-before-artifact-smoke-before-verified-sidecar" if order_ok else "missing-or-misordered",
        "helper_invokes_lint_suite": helper_ok,
        "artifact_smoke_present": "run_artifact_smoke" in helper_text,
        "artifact_mutation_canaries_present": "package_artifact_negative_canary_results" in helper_text,
        "deterministic_writer_canaries_present": "package_determinism_canary_results" in helper_text,
        "sidecar_canaries_present": "package_sidecar_canary_results" in helper_text,
    }

def build_canary_runs(root: pathlib.Path) -> dict[str, Any]:
    receipt = _load_json(root, "REVISION-RECEIPT.json")
    manifest = _load_json(root, "RELEASE-MANIFEST.json")
    status = _load_json(root, "SURFACE-STATUS.json")
    context = _load_json(root, "context-pack.json")
    frontier = _load_json(root, "frontier-ticket.json")
    replay = _load_json(root, "replay-capsule.json")
    compact = _load_json(root, "compact-surface-bundle.json")
    protocol = _load_json(root, "CANARY-PROTOCOL.json")
    self_suff = _load_json(root, "SELF-SUFFICIENCY-LEDGER.json")

    revision = receipt["revision"]
    bundle = manifest["bundle"]
    next_q = receipt["next_open_question"]
    resolved = receipt["resolved_question"]

    positive_runs: list[dict[str, Any]] = []
    identity_ok = (
        manifest.get("revision") == revision
        and receipt.get("packaged_bundle_filename") == bundle
        and status.get("latest_revision") == revision
        and status.get("latest_bundle") == bundle
        and status.get("current_head") == revision
    )
    positive_runs.append(_row(
        "release-identity-current",
        "manifest, receipt, and status all name the same current revision and bundle",
        f"manifest={manifest.get('revision')} bundle={bundle} status={status.get('latest_revision')} latest_bundle={status.get('latest_bundle')}",
        "pass" if identity_ok else "fail",
        ["REVISION-RECEIPT.json", "RELEASE-MANIFEST.json", "SURFACE-STATUS.json"],
    ))

    focus_ids = [
        context.get("open_questions", [{}])[-1].get("id"),
        frontier.get("primary_focus", {}).get("id"),
        replay.get("current_projection", {}).get("selected_focus_id"),
    ]
    compact_members = [row.get("surface") for row in compact.get("members", [])]
    focus_ok = all(item == next_q for item in focus_ids) and compact.get("revision") == revision and "frontier-ticket.json" in compact_members
    positive_runs.append(_row(
        "compact-frontier-current",
        "compact reentry surfaces are current and focus-carrying surfaces point to the receipt successor question",
        f"focus_ids={focus_ids}, expected={next_q}, compact_revision={compact.get('revision')}, compact_members={len(compact_members)}",
        "pass" if focus_ok else "fail",
        ["context-pack.json", "frontier-ticket.json", "replay-capsule.json", "compact-surface-bundle.json"],
    ))

    landing = _latest_revision_cues(root, revision, bundle)
    positive_runs.append(_row(
        "landing-current-cues",
        "landing pages each contain exactly one current Latest revision cue and the current bundle",
        json.dumps(landing["observations"], ensure_ascii=False, sort_keys=True),
        "pass" if landing["ok"] else "fail",
        ["START_HERE.md", "README.md", "docs/README.md"],
    ))

    latest_self = self_suff.get("items", [])[-1]
    latest_scorecard = latest_self.get("scorecard", {}) if isinstance(latest_self.get("scorecard"), dict) else {}
    packet_tests = latest_self.get("packet_tests", []) if isinstance(latest_self.get("packet_tests"), list) else []
    packet_score = sum(row.get("score", 0) for row in packet_tests if isinstance(row, dict))
    packet_max = sum(row.get("max", 0) for row in packet_tests if isinstance(row, dict))
    self_ok = (
        latest_self.get("revision") == revision
        and latest_self.get("assay_state") == "scored-canary"
        and latest_self.get("frontier_id") == next_q
        and resolved in latest_self.get("question_set", [])
        and next_q in latest_self.get("question_set", [])
        and latest_scorecard.get("state") == "scored-canary"
        and latest_scorecard.get("observed_score") == packet_score
        and latest_scorecard.get("max_score") == packet_max
        and packet_max > 0
        and 0 <= packet_score <= packet_max
    )
    positive_runs.append(_row(
        "self-sufficiency-tail-scored",
        "latest self-sufficiency item is scored, current, aligned to resolved/successor questions, and internally sums its packet-test scores without requiring a perfect result",
        f"id={latest_self.get('id')} revision={latest_self.get('revision')} frontier={latest_self.get('frontier_id')} score={latest_scorecard.get('observed_score')}/{latest_scorecard.get('max_score')} packet_sum={packet_score}/{packet_max}",
        "pass" if self_ok else "fail",
        ["SELF-SUFFICIENCY-LEDGER.json", "REVISION-RECEIPT.json"],
    ))

    protocol_ok = (
        protocol.get("revision") == revision
        and len(protocol.get("negative_canaries", [])) >= 8
        and "continuation authority" in protocol.get("forbidden_conclusions", [])
        and "review court" in protocol.get("non_claim", "")
    )
    positive_runs.append(_row(
        "canary-protocol-boundary",
        "protocol is current and names negative canaries plus forbidden authority claims",
        f"revision={protocol.get('revision')} negative_count={len(protocol.get('negative_canaries', []))}",
        "pass" if protocol_ok else "fail",
        ["CANARY-PROTOCOL.json"],
    ))

    metadata_rows = external_metadata_rows(root)
    metadata_failures = [row for row in metadata_rows if row.get("status") != "pass"]
    positive_runs.append(_row(
        "external-metadata-date-contract",
        "external metadata tokens and release dates match the current bundle and receipt timestamp",
        f"rows={len(metadata_rows)} failures={len(metadata_failures)}",
        "pass" if not metadata_failures else "fail",
        ["LICENSE", "CITATION.cff", "codemeta.json", "ro-crate-metadata.json", "SBOM.spdx.json", "tools/check_external_metadata_contract.py"],
    ))

    release_identity_rows = release_identity_canary_results()
    release_identity_status = "pass" if release_identity_rows and all(row.get("status") == "pass" for row in release_identity_rows) else "fail"
    positive_runs.append(_row(
        "release-filename-identity-canaries",
        "release filename components reject path-like, malformed, uppercase, empty, and impossible-date values while accepting the canonical Project-rev####-YYYY.MM.DD.HH.MM-slug.zip structure",
        f"identity_canaries={len(release_identity_rows)} failures={sum(1 for row in release_identity_rows if row.get('status') != 'pass')}",
        release_identity_status,
        ["tools/release_hygiene_lib.py", "tools/check_release_identity_canaries.py", "tools/package_release.py"],
    ))

    core_negative_runs = core_method_negative_canary_results(root, list(iter_core_method_contract_specs()))
    core_negative_status = "pass" if core_negative_runs and all(row.get("status") == "pass" for row in core_negative_runs) else "fail"
    positive_runs.append(_row(
        "core-method-mutation-canaries",
        "core-method checker fails loudly on doc, source-size, auxiliary-surface, wrapper-regrowth, and duplicate-source mutations",
        f"mutation_canaries={len(core_negative_runs)} failed_canary_failures={sum(1 for row in core_negative_runs if row.get('status') != 'pass')}",
        core_negative_status,
        ["tools/check_core_method_batch_contract.py", "tools/core_method_contract_lib.py", "tools/check_core_method_batch_negative_canaries.py"],
    ))

    artifact_negative_runs = package_artifact_negative_canary_results()
    artifact_negative_status = "pass" if artifact_negative_runs and all(row.get("status") == "pass" for row in artifact_negative_runs) else "fail"
    positive_runs.append(_row(
        "package-artifact-smoke-mutation-canaries",
        "artifact-smoke guards fail loudly on missing members, excluded extras, traversal paths, duplicate members, order drift, and direct unsafe extraction",
        f"mutation_canaries={len(artifact_negative_runs)} failed_canary_failures={sum(1 for row in artifact_negative_runs if row.get('status') != 'pass')}",
        artifact_negative_status,
        ["tools/package_preflight_lib.py", "tools/check_package_artifact_smoke_negative_canaries.py", "tools/check_package_release_preflight_contract.py"],
    ))


    determinism_runs = package_determinism_canary_results()
    determinism_status = "pass" if determinism_runs and all(row.get("status") == "pass" for row in determinism_runs) else "fail"
    positive_runs.append(_row(
        "package-deterministic-zip-writer-canaries",
        "deterministic zip writer produces stable bytes, fixed metadata, release-hygiene ordering, and artifact-smoke-compatible output without full double packaging",
        f"writer_canaries={len(determinism_runs)} failures={sum(1 for row in determinism_runs if row.get('status') != 'pass')}",
        determinism_status,
        ["tools/package_preflight_lib.py", "tools/package_release.py", "tools/check_package_deterministic_zip_canaries.py"],
    ))


    release_integrity_rows = release_integrity_canary_results()
    release_integrity_status = "pass" if release_integrity_rows and all(row.get("status") == "pass" for row in release_integrity_rows) else "fail"
    positive_runs.append(_row(
        "release-integrity-mutation-canaries",
        "release integrity validator rejects content-hash drift, checksum drift, manifest row omissions, path-count drift, and provenance command/policy drift without full package release",
        f"integrity_canaries={len(release_integrity_rows)} failures={sum(1 for row in release_integrity_rows if row.get('status') != 'pass')}",
        release_integrity_status,
        ["tools/release_integrity_lib.py", "tools/release_integrity_contract_lib.py", "tools/check_release_integrity_negative_canaries.py", "tools/check_release_integrity_contract.py"],
    ))

    sidecar_runs = package_sidecar_canary_results()
    sidecar_status = "pass" if sidecar_runs and all(row.get("status") == "pass" for row in sidecar_runs) else "fail"
    positive_runs.append(_row(
        "package-sha256-sidecar-canaries",
        "package sidecar helper writes and verifies the exact sha256sum-compatible line after artifact smoke, and rejects stale digest, spacing, bundle-name, and sidecar-name drift",
        f"sidecar_canaries={len(sidecar_runs)} failures={sum(1 for row in sidecar_runs if row.get('status') != 'pass')}",
        sidecar_status,
        ["tools/package_preflight_lib.py", "tools/package_release.py", "tools/check_package_sidecar_canaries.py"],
    ))

    ledger_coldstore_rows = ledger_coldstore_canary_results(root)
    ledger_coldstore_status = "pass" if ledger_coldstore_rows and all(row.get("status") == "pass" for row in ledger_coldstore_rows) else "fail"
    positive_runs.append(_row(
        "ledger-coldstore-mutation-canaries",
        "ledger coldstore checker rejects payload hash drift, row hash drift, payload row omission, hot-ref mismatch, current-tail compaction, and savings arithmetic drift without relying on prose audit",
        f"coldstore_canaries={len(ledger_coldstore_rows)} failures={sum(1 for row in ledger_coldstore_rows if row.get('status') != 'pass')}",
        ledger_coldstore_status,
        ["LEDGER-COLDSTORE.json", "tools/ledger_coldstore_contract_lib.py", "tools/check_ledger_coldstore_roundtrip_contract.py", "tools/check_ledger_coldstore_mutation_canaries.py"],
    ))

    receipt_coldstore_rows = receipt_coldstore_canary_results(root)
    receipt_coldstore_status = "pass" if receipt_coldstore_rows and all(row.get("status") == "pass" for row in receipt_coldstore_rows) else "fail"
    positive_runs.append(_row(
        "receipt-coldstore-mutation-canaries",
        "receipt coldstore checker rejects payload hash drift, key hash drift, key omission, hot-overlap, current-key compaction, and savings arithmetic drift without relying on receipt prose",
        f"receipt_coldstore_canaries={len(receipt_coldstore_rows)} failures={sum(1 for row in receipt_coldstore_rows if row.get('status') != 'pass')}",
        receipt_coldstore_status,
        ["RECEIPT-COLDSTORE.json", "tools/receipt_coldstore_contract_lib.py", "tools/check_receipt_coldstore_roundtrip_contract.py", "tools/check_receipt_coldstore_mutation_canaries.py"],
    ))

    toolchain = build_validation_toolchain(root)
    gen_tools = [tool for tool in toolchain if tool.startswith("gen_")]
    lint_drift_ok = "check_generated_surface_drift.py" in toolchain and not gen_tools
    positive_runs.append(_row(
        "lint-generated-surface-drift-gate",
        "lint fails on stale generated surfaces before any generator can rewrite them",
        f"drift_checker={'present' if 'check_generated_surface_drift.py' in toolchain else 'absent'} generator_tools_in_lint={gen_tools}",
        "pass" if lint_drift_ok else "fail",
        ["tools/check_generated_surface_drift.py", "tools/generated_surface_lib.py", "tools/validation_toolchain_lib.py", "Makefile"],
    ))

    package_preflight = _package_release_preflight_observation(root)
    positive_runs.append(_row(
        "package-release-admission-preflight",
        "package release refreshes generated surfaces, runs non-mutating lint preflight, writes the deterministic zip, smoke-tests the emitted artifact in a clean extraction, and only then writes and verifies the SHA256 sidecar",
        json.dumps(package_preflight, ensure_ascii=False, sort_keys=True),
        "pass" if package_preflight["ok"] else "fail",
        ["tools/package_release.py", "tools/package_preflight_lib.py", "tools/check_package_release_preflight_contract.py"],
    ))

    max_score = len(positive_runs) * 4
    observed_score = sum(row["score"] for row in positive_runs)
    return {
        "project": "DelayBasin",
        "revision": revision,
        "surface": "CANARY-RUNS.json",
        "state": "generated-executable-canary-runs",
        "generated_from": [
            "REVISION-RECEIPT.json",
            "RELEASE-MANIFEST.json",
            "SURFACE-STATUS.json",
            "CANARY-PROTOCOL.json",
            "SELF-SUFFICIENCY-LEDGER.json",
            "tools/core_method_contract_lib.py",
            "tools/external_metadata_contract_lib.py",
            "tools/package_preflight_lib.py",
            "tools/release_hygiene_lib.py",
            "tools/release_integrity_lib.py",
            "tools/release_integrity_contract_lib.py",
            "tools/ledger_coldstore_contract_lib.py",
            "tools/receipt_coldstore_contract_lib.py",
            "tools/check_release_integrity_negative_canaries.py",
            "tools/check_release_identity_canaries.py",
            "tools/check_package_artifact_smoke_negative_canaries.py",
            "tools/check_package_deterministic_zip_canaries.py",
            "tools/check_package_sidecar_canaries.py",
            "tools/check_ledger_coldstore_mutation_canaries.py",
            "tools/check_receipt_coldstore_mutation_canaries.py",
        ],
        "non_claim": NON_CLAIM,
        "scorecard": {
            "max_score": max_score,
            "observed_score": observed_score,
            "passing": observed_score == max_score,
            "interpretation": "executable, archive-local canary evidence only",
        },
        "positive_runs": positive_runs,
        "negative_mutation_runs": [*core_negative_runs, *artifact_negative_runs, *release_integrity_rows, *ledger_coldstore_rows, *receipt_coldstore_rows],
        "release_identity_rows": release_identity_rows,
        "release_integrity_rows": release_integrity_rows,
        "deterministic_writer_rows": determinism_runs,
        "sidecar_rows": sidecar_runs,
        "ledger_coldstore_rows": ledger_coldstore_rows,
        "receipt_coldstore_rows": receipt_coldstore_rows,
        "external_metadata_rows": metadata_rows,
    }


def write_canary_runs(root: pathlib.Path) -> dict[str, Any]:
    payload = build_canary_runs(root)
    (root / "CANARY-RUNS.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload
