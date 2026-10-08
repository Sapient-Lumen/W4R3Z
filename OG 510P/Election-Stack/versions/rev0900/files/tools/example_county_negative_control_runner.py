#!/usr/bin/env python3
"""Run synthetic Example County negative-control verifier fixtures.

The scorecard happy path proves that known-good packets verify. This helper adds
expected-failure coverage: it mutates temporary copies of selected Example County
packets, runs the same public verifier primitives, and checks that each mutated
copy fails with stable publishable problem codes.

No tampered packet is shipped as evidence. Temporary mutated packets are deleted
at process exit. Passing negative controls mean the verifier rejected the
fixture as expected; they are not live deployment evidence, certification,
outcome proof, proof of intent/fraud, or legal advice.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
SCENARIO = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot" / "scenario.json"
OUTDIR = SCENARIO.parent
REG = ROOT / "artifacts" / "registries" / "negative-control-fixtures.csv"
BOUNDARY = (
    "Synthetic expected-failure rehearsal only; not live election evidence, not certification, "
    "not proof of outcome correctness, not proof of intent or fraud, and not legal advice."
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def first_envelope(packet: Path) -> Path:
    envs = sorted((packet / "envelopes").glob("*.json"))
    if not envs:
        raise RuntimeError("fixture source packet has no envelopes")
    return envs[0]


def first_object(packet: Path) -> Path:
    objs = sorted((packet / "objects").glob("sha256-*.json"))
    if not objs:
        raise RuntimeError("fixture source packet has no content-addressed JSON objects")
    return objs[0]


def payload_object_from_first_envelope(packet: Path) -> Path:
    env = load_json(first_envelope(packet))
    pp = env.get("payload_pointer") if isinstance(env, dict) else None
    if not isinstance(pp, dict):
        return first_object(packet)
    uri = str(pp.get("uri") or "").strip()
    if not uri:
        return first_object(packet)
    rel = uri if uri.startswith("objects/") else f"objects/{uri}"
    p = packet / rel
    if not p.exists():
        return first_object(packet)
    return p


def mutate_append_payload_object(packet: Path) -> None:
    p = payload_object_from_first_envelope(packet)
    p.write_bytes(p.read_bytes() + b"\n{\"tampered\":true}\n")


def mutate_payload_pointer_digest(packet: Path) -> None:
    p = first_envelope(packet)
    env = load_json(p)
    if not isinstance(env.get("payload_pointer"), dict):
        raise RuntimeError("fixture source envelope has no payload_pointer")
    env["payload_pointer"]["digest"] = "sha256:" + ("1" * 64)
    write_json(p, env)


def mutate_payload_digest(packet: Path) -> None:
    p = first_envelope(packet)
    env = load_json(p)
    env["payload_digest"] = "sha256:" + ("2" * 64)
    write_json(p, env)


def mutate_tbs_digest(packet: Path) -> None:
    p = first_envelope(packet)
    env = load_json(p)
    env["tbs_digest"] = "sha256:" + ("3" * 64)
    write_json(p, env)


def mutate_manifest_digest(packet: Path) -> None:
    p = packet / "manifest.json"
    man = load_json(p)
    arts = man.get("artifacts") if isinstance(man, dict) else None
    if not isinstance(arts, list) or not arts:
        raise RuntimeError("fixture source manifest has no artifacts")
    if not isinstance(arts[0], dict):
        raise RuntimeError("fixture source manifest artifact is not an object")
    arts[0]["digest"] = "sha256:" + ("4" * 64)
    write_json(p, man)


def mutate_remove_manifest(packet: Path) -> None:
    (packet / "manifest.json").unlink()


def mutate_unsupported_envelope_version(packet: Path) -> None:
    p = first_envelope(packet)
    env = load_json(p)
    env["envelope_version"] = "2.0.0"
    write_json(p, env)


def mutate_missing_payload_object(packet: Path) -> None:
    payload_object_from_first_envelope(packet).unlink()


MUTATORS = {
    "append_payload_object": mutate_append_payload_object,
    "tamper_payload_pointer_digest": mutate_payload_pointer_digest,
    "tamper_payload_digest": mutate_payload_digest,
    "tamper_tbs_digest": mutate_tbs_digest,
    "tamper_manifest_digest": mutate_manifest_digest,
    "remove_manifest": mutate_remove_manifest,
    "unsupported_envelope_version": mutate_unsupported_envelope_version,
    "missing_payload_object": mutate_missing_payload_object,
}


def verify_packet(packet_dir: Path) -> dict[str, Any]:
    tools_dir = str(ROOT / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    from observer_verify_packet import build_report, verify_envelopes, verify_manifest, verify_objects  # type: ignore

    problems: list[str] = []
    obj_problems, objects_checked = verify_objects(packet_dir / "objects")
    problems += obj_problems
    env_problems, envelopes_checked, kinds_seen = verify_envelopes(packet_dir / "envelopes", packet_dir)
    problems += env_problems
    problems += verify_manifest(packet_dir)
    report = build_report(packet_dir, problems, envelopes_checked, objects_checked, kinds_seen, public=True)
    return {
        "status": str(report.get("status") or "ERROR"),
        "problem_codes": list(report.get("problems") or []),
        "envelopes_checked": int(report.get("envelopes_checked") or 0),
        "objects_checked": int(report.get("objects_checked") or 0),
    }


def split_codes(cell: str) -> list[str]:
    return [x.strip() for x in (cell or "").split(";") if x.strip()]


def run_fixture(row: dict[str, str], tmp_root: Path) -> dict[str, Any]:
    fid = row["fixture_id"]
    source_rel = row["source_packet"]
    source = ROOT / source_rel
    work = tmp_root / fid
    shutil.copytree(source, work)
    mutation = row["mutation"]
    mutator = MUTATORS.get(mutation)
    if mutator is None:
        raise RuntimeError(f"unknown mutation {mutation!r}")
    mutator(work)
    observed = verify_packet(work)
    expected_status = row.get("expected_status", "FAIL")
    expected_codes = split_codes(row.get("expected_problem_codes", ""))
    observed_codes = [str(x) for x in observed.get("problem_codes") or []]
    missing_codes = [c for c in expected_codes if c not in observed_codes]
    expectation_ok = observed.get("status") == expected_status and not missing_codes
    return {
        "fixture_id": fid,
        "track": row.get("track"),
        "source_packet": source_rel,
        "mutation": mutation,
        "expected_status": expected_status,
        "expected_problem_codes": expected_codes,
        "observed_status": observed.get("status"),
        "observed_problem_codes": observed_codes,
        "missing_expected_codes": missing_codes,
        "expectation_status": "PASS" if expectation_ok else "FAIL",
        "public_interpretation": row.get("public_interpretation", ""),
        "non_claims": row.get("non_claims", ""),
    }


def build_report() -> dict[str, Any]:
    scenario = load_json(SCENARIO)
    rows = read_csv(REG)
    with tempfile.TemporaryDirectory(prefix="tes_negative_controls_") as td:
        results = [run_fixture(row, Path(td)) for row in rows]
    failed = [r for r in results if r["expectation_status"] != "PASS"]
    return {
        "archive_version": VERSION,
        "scenario_id": scenario.get("scenario_id"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "fixture_count": len(results),
        "status": "PASS" if not failed else "FAIL",
        "results": results,
        "boundary": BOUNDARY,
        "non_claim": BOUNDARY,
    }


def public_summary(report: dict[str, Any]) -> str:
    lines = [
        "# Example County negative-control verifier summary",
        "",
        "**Synthetic example only. This is not live election evidence.**",
        "",
        f"Scenario: `{report['scenario_id']}`  ",
        f"Archive version: `{report['archive_version']}`  ",
        f"Negative controls: `{report['fixture_count']}`  ",
        f"Expected-failure status: `{report['status']}`",
        "",
        "## What this checks",
        "",
        "These fixtures deliberately mutate temporary copies of otherwise valid synthetic packets. A PASS means the verifier rejected the tampered temporary packet with the expected publishable problem code. It does not certify any election, does not prove an outcome, and does not prove intent or fraud.",
        "",
        "## Expected failures",
        "",
    ]
    for r in report.get("results", []):
        if not isinstance(r, dict):
            continue
        codes = ", ".join(str(c) for c in r.get("observed_problem_codes") or [])
        lines.append(f"- `{r.get('fixture_id')}` / `{r.get('mutation')}`: {r.get('expectation_status')} ({codes})")
    lines.extend([
        "",
        "## Operator command",
        "",
        "```bash",
        "python3 tools/example_county_negative_control_runner.py --json",
        "```",
        "",
        "## Boundary",
        "",
        BOUNDARY,
        "",
    ])
    return "\n".join(lines)


def csv_rows(report: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for r in report.get("results", []):
        if not isinstance(r, dict):
            continue
        out.append({
            "fixture_id": str(r.get("fixture_id") or ""),
            "mutation": str(r.get("mutation") or ""),
            "source_packet": str(r.get("source_packet") or ""),
            "expected_status": str(r.get("expected_status") or ""),
            "expected_problem_codes": "; ".join(str(c) for c in r.get("expected_problem_codes") or []),
            "observed_status": str(r.get("observed_status") or ""),
            "observed_problem_codes": "; ".join(str(c) for c in r.get("observed_problem_codes") or []),
            "expectation_status": str(r.get("expectation_status") or ""),
            "public_interpretation": str(r.get("public_interpretation") or ""),
            "non_claims": str(r.get("non_claims") or ""),
        })
    return out


def write_outputs(report: dict[str, Any]) -> None:
    write_json(OUTDIR / "negative-control-report.json", report)
    (OUTDIR / "public-negative-control-summary.md").write_text(public_summary(report), encoding="utf-8")
    fields = [
        "fixture_id",
        "mutation",
        "source_packet",
        "expected_status",
        "expected_problem_codes",
        "observed_status",
        "observed_problem_codes",
        "expectation_status",
        "public_interpretation",
        "non_claims",
    ]
    with (OUTDIR / "negative-control-results.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(csv_rows(report))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic negative-control output files")
    ap.add_argument("--json", action="store_true", help="Print negative-control report JSON")
    args = ap.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    if args.json:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    else:
        print(f"{report['status']}: negative controls ({report['fixture_count']} fixture(s))")
        print(BOUNDARY)
    return 0 if report.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
