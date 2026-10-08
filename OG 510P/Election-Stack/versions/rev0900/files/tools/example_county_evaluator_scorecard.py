#!/usr/bin/env python3
"""Build the synthetic Example County evaluator scorecard.

The scorecard converts existing release-gated outputs into a compact rehearsal
assessment. It is synthetic-only: a perfect score is not certification, not live
deployment evidence, not proof of outcome correctness, and not legal advice.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
OUTDIR = ROOT / "artifacts" / "examples" / "example_county_2026_municipal_pilot"
REG = ROOT / "artifacts" / "registries"

BOUNDARY = "Synthetic rehearsal scorecard only; not certification, not live election evidence, not outcome proof, not proof of intent or fraud, and not legal advice."


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]


def file_text(name: str) -> str:
    return (OUTDIR / name).read_text(encoding="utf-8", errors="replace")


def _scenario_id_ok(value: object) -> bool:
    s = str(value or "")
    return s == f"EXAMPLE-COUNTY-2026-MUNI-{VERSION}" and s.endswith(VERSION)


def _json_version_ok(obj: Any) -> bool:
    return isinstance(obj, dict) and obj.get("archive_version") == VERSION and _scenario_id_ok(obj.get("scenario_id"))


def _contains_all(text: str, phrases: list[str]) -> bool:
    lower = text.lower()
    return all(p.lower() in lower for p in phrases)


def _csv_has_non_claim(path: Path) -> bool:
    rows = read_csv(path)
    return bool(rows) and all(any("non_claim" in k and (row.get(k) or "").strip() for k in row) for row in rows)


def compute_metric(metric_id: str, max_points: int, data: dict[str, Any]) -> tuple[int, str, str]:
    scenario = data["scenario"]
    evidence_map = data["evidence_map"]
    smoke = data["smoke"]
    trust = data["trust"]
    human = data["human"]
    negative = data["negative"]
    eval_rows = data["evaluation_rows"]
    crosswalk_rows = data["crosswalk_rows"]
    retention_rows = data["retention_rows"]
    component_rows = data["component_rows"]
    standards_rows = data["standards_rows"]
    pilot_rows = data["pilot_rows"]

    if metric_id == "ESR-001":
        ok = all(_json_version_ok(x) for x in [scenario, evidence_map, smoke, trust, human, negative])
        return (max_points if ok else 0, "PASS" if ok else "FAIL", "All core generated JSON outputs carry the current version and scenario id." if ok else "One or more generated outputs are stale.")

    if metric_id == "ESR-002":
        json_ok = scenario.get("synthetic_only") is True and scenario.get("no_live_deployment_claim") is True and evidence_map.get("synthetic_only") is True and trust.get("synthetic_only") is True and human.get("synthetic_only") is True and negative.get("synthetic_only") is True
        md = "\n".join(file_text(n) for n in ["public-verifier-quickstart.md", "public-failure-bulletin.md", "human-review-quickstart.md", "public-negative-control-summary.md"])
        md_ok = _contains_all(md, ["Synthetic example only", "not live election evidence"])
        return (max_points if json_ok and md_ok else 0, "PASS" if json_ok and md_ok else "FAIL", "Synthetic/live-evidence boundary is present in JSON and public markdown." if json_ok and md_ok else "Synthetic boundary is incomplete.")

    if metric_id == "ESR-003":
        results = smoke.get("results") if isinstance(smoke, dict) else []
        ok = smoke.get("status") == "PASS" and isinstance(results, list) and len(results) >= 20 and all(isinstance(r, dict) and r.get("status") == "PASS" for r in results)
        return (max_points if ok else 0, "PASS" if ok else "FAIL", f"{len(results) if isinstance(results, list) else 0} packet verifier result(s) passed." if ok else "One or more packet verifier results failed or are missing.")

    if metric_id == "ESR-004":
        packet_count = int(evidence_map.get("packet_count") or 0)
        phases = evidence_map.get("phases") if isinstance(evidence_map, dict) else []
        court_rows = read_csv(OUTDIR / "court-packet-index.csv")
        packets_ok = packet_count >= 20 and isinstance(phases, list) and all(isinstance(ph, dict) and ph.get("public_sentence") and ph.get("packets") for ph in phases)
        rows_ok = len(court_rows) == packet_count and all(r.get("manifest_sha256", "").startswith("sha256:") and r.get("verification_status") == "PASS" and r.get("non_claim") for r in court_rows)
        return (max_points if packets_ok and rows_ok else 0, "PASS" if packets_ok and rows_ok else "FAIL", "Evidence map and court index close over all scenario packets." if packets_ok and rows_ok else "Evidence map or court index is incomplete.")

    if metric_id == "ESR-005":
        eval_ids = {r.get("scenario_id") for r in eval_rows}
        cross_ids = {r.get("scenario_id") for r in crosswalk_rows}
        trp_ids = {m.get("recovery_id") for m in trust.get("failure_modes", []) if isinstance(m, dict)}
        cross_ok = eval_ids and eval_ids == cross_ids and all(r.get("recovery_ids") for r in crosswalk_rows)
        trust_ok = len(trp_ids) >= 11
        return (max_points if cross_ok and trust_ok else 0, "PASS" if cross_ok and trust_ok else "FAIL", f"{len(eval_ids)} scenario(s) crosswalked to {len(trp_ids)} recovery mode(s)." if cross_ok and trust_ok else "Scenario recovery mapping is incomplete.")

    if metric_id == "ESR-006":
        worksheet_rows = read_csv(OUTDIR / "reviewer-worksheet-index.csv")
        scenario_count = int(human.get("scenario_count") or 0)
        hr_count = int(human.get("human_review_count") or 0)
        ok = scenario_count >= 10 and hr_count >= 10 and len(worksheet_rows) >= scenario_count and all(r.get("primary_reviewer") and r.get("secondary_reviewer") and r.get("public_boundary_sentence") for r in worksheet_rows)
        return (max_points if ok else 0, "PASS" if ok else "FAIL", f"{len(worksheet_rows)} worksheet row(s) route scenarios to reviewers." if ok else "Human-review worksheet routing is incomplete.")

    if metric_id == "ESR-007":
        ok = len(retention_rows) >= 8 and all(r.get("minimum_fields_to_preserve") and r.get("redaction_floor") and r.get("non_claims") for r in retention_rows)
        return (max_points if ok else 0, "PASS" if ok else "FAIL", f"{len(retention_rows)} retention disposition(s) include preservation and redaction floors." if ok else "Retention/redaction floor is incomplete.")

    if metric_id == "ESR-008":
        texts = "\n".join(file_text(n) for n in ["public-summary.md", "public-verifier-quickstart.md", "public-failure-bulletin.md", "human-review-quickstart.md", "public-negative-control-summary.md"])
        ok = _contains_all(texts, ["not live election evidence", "not outcome", "not proof of intent or fraud"]) and "proves fraud" not in texts.lower() and "certifies the election" not in texts.lower()
        return (max_points if ok else 0, "PASS" if ok else "FAIL", "Public-facing files carry bounded non-claims and avoid prohibited inferences." if ok else "Public language boundary is incomplete or overclaiming.")

    if metric_id == "ESR-009":
        standards_ok = len(standards_rows) >= 5 and any("not a formal conformance" in (r.get("notes") or "").lower() for r in standards_rows)
        component_ok = any(r.get("component_id") == "CMP-018" and r.get("maturity") == "pilot_ready" for r in component_rows)
        return (max_points if standards_ok and component_ok else 0, "PASS" if standards_ok and component_ok else "FAIL", "External standards remain crosswalk/alignment references, and the scorecard component is maturity-labeled." if standards_ok and component_ok else "External alignment or component maturity boundary is incomplete.")

    if metric_id == "ESR-010":
        current_rows = [r for r in pilot_rows if r.get("archive_version") == VERSION]
        statuses = {r.get("status") for r in current_rows}
        ok = {"pre_pilot_empty", "synthetic_smoke_harness"}.issubset(statuses)
        return (max_points if ok else 0, "PASS" if ok else "FAIL", "Pilot-data ledger records both current pre-pilot absence and synthetic rehearsal status." if ok else "Current pre-pilot ledger rows are missing.")

    if metric_id == "ESR-011":
        results = negative.get("results") if isinstance(negative, dict) else []
        rows = read_csv(OUTDIR / "negative-control-results.csv")
        public = file_text("public-negative-control-summary.md").lower()
        fixtures_ok = (
            negative.get("status") == "PASS"
            and int(negative.get("fixture_count") or 0) >= 8
            and isinstance(results, list)
            and all(isinstance(r, dict) and r.get("expectation_status") == "PASS" and r.get("observed_status") == "FAIL" for r in results)
        )
        rows_ok = len(rows) == int(negative.get("fixture_count") or 0) and all(r.get("expectation_status") == "PASS" and r.get("non_claims") for r in rows)
        public_ok = _contains_all(public, ["synthetic example only", "not live election evidence", "expected-failure", "does not certify", "does not prove intent or fraud"]) and "certifies" not in public and "proves fraud" not in public
        ok = fixtures_ok and rows_ok and public_ok
        return (max_points if ok else 0, "PASS" if ok else "FAIL", f"{int(negative.get('fixture_count') or 0)} expected-failure fixture(s) rejected by the verifier." if ok else "Negative-control fixtures are missing, stale, or overclaiming.")

    return (0, "FAIL", f"No evaluator implemented for {metric_id}.")


def build_scorecard() -> dict[str, Any]:
    data = {
        "scenario": load_json(OUTDIR / "scenario.json"),
        "evidence_map": load_json(OUTDIR / "evidence-map.json"),
        "smoke": load_json(OUTDIR / "smoke-report.json"),
        "trust": load_json(OUTDIR / "trust-recovery-matrix.json"),
        "human": load_json(OUTDIR / "human-review-matrix.json"),
        "negative": load_json(OUTDIR / "negative-control-report.json"),
        "evaluation_rows": read_csv(REG / "evaluation-scenarios.csv"),
        "crosswalk_rows": read_csv(REG / "scenario-recovery-crosswalk.csv"),
        "retention_rows": read_csv(REG / "evidence-retention-disposition.csv"),
        "component_rows": read_csv(REG / "component-maturity.csv"),
        "standards_rows": read_csv(REG / "standards-crosswalk.csv"),
        "pilot_rows": read_csv(REG / "pilot-data-ledger.csv"),
    }
    rubric = read_csv(REG / "evaluator-scoring-rubric.csv")
    metrics: list[dict[str, Any]] = []
    total = 0
    max_total = 0
    failures: list[str] = []
    for row in rubric:
        max_points = int(row.get("max_points") or 0)
        threshold = int(row.get("pass_threshold") or 0)
        points, status, evidence = compute_metric(row["metric_id"], max_points, data)
        total += points
        max_total += max_points
        if status != "PASS" or points < threshold:
            failures.append(row["metric_id"])
        metrics.append({
            "metric_id": row["metric_id"],
            "dimension": row["dimension"],
            "points": points,
            "max_points": max_points,
            "pass_threshold": threshold,
            "status": status if points >= threshold else "FAIL",
            "evidence": evidence,
            "failure_meaning": row["failure_meaning"],
            "non_claims": row["non_claims"],
        })
    return {
        "archive_version": VERSION,
        "scenario_id": data["scenario"].get("scenario_id"),
        "synthetic_only": True,
        "no_live_deployment_claim": True,
        "scorecard_kind": "example_county_synthetic_evaluator_scorecard",
        "total_points": total,
        "max_points": max_total,
        "pass_threshold_points": max_total,
        "status": "PASS" if not failures and total == max_total else "FAIL",
        "metrics": metrics,
        "boundary": BOUNDARY,
    }


def rows_for_csv(scorecard: dict[str, Any]) -> list[dict[str, str]]:
    return [{
        "metric_id": str(m["metric_id"]),
        "dimension": str(m["dimension"]),
        "status": str(m["status"]),
        "points": str(m["points"]),
        "max_points": str(m["max_points"]),
        "evidence": str(m["evidence"]),
        "non_claims": str(m["non_claims"]),
    } for m in scorecard.get("metrics", [])]


def public_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Example County evaluator scorecard",
        "",
        "**Synthetic example only. This is not live election evidence and not certification.**",
        "",
        f"Scenario: `{scorecard['scenario_id']}`  ",
        f"Archive version: `{scorecard['archive_version']}`  ",
        f"Status: `{scorecard['status']}`  ",
        f"Score: `{scorecard['total_points']}/{scorecard['max_points']}`",
        "",
        "## Boundary",
        "",
        BOUNDARY,
        "",
        "## Metrics",
        "",
    ]
    for m in scorecard.get("metrics", []):
        lines.append(f"- `{m['metric_id']}` / `{m['dimension']}`: `{m['status']}` ({m['points']}/{m['max_points']}) — {m['evidence']}")
    lines.extend([
        "",
        "## Operator command",
        "",
        "```bash",
        "python3 tools/example_county_evaluator_scorecard.py --json",
        "```",
        "",
        "A passing scorecard means the synthetic rehearsal outputs are internally closed under the current release gates. It does not prove outcome correctness, does not replace canvass, audit, certification, recount, or court procedure, and does not turn failure evidence into proof of intent or fraud.",
        "",
    ])
    return "\n".join(lines)


def build_output() -> dict[str, Any]:
    scorecard = build_scorecard()
    return {"scorecard": scorecard, "rows": rows_for_csv(scorecard), "markdown": public_markdown(scorecard)}


def write_output_pack() -> dict[str, Any]:
    out = build_output()
    (OUTDIR / "evaluator-scorecard.json").write_text(json.dumps(out["scorecard"], sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with (OUTDIR / "evaluator-scorecard.csv").open("w", encoding="utf-8", newline="") as f:
        fields = ["metric_id", "dimension", "status", "points", "max_points", "evidence", "non_claims"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out["rows"])
    (OUTDIR / "public-evaluator-scorecard.md").write_text(out["markdown"], encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Write deterministic evaluator scorecard output files")
    ap.add_argument("--json", action="store_true", help="Print evaluator scorecard JSON")
    args = ap.parse_args()
    out = write_output_pack() if args.write else build_output()
    if args.json:
        print(json.dumps(out["scorecard"], sort_keys=True, separators=(",", ":")))
    else:
        sc = out["scorecard"]
        print(f"PASS: Example County evaluator scorecard ({sc['total_points']}/{sc['max_points']}, {sc['status']})")
    return 0 if out["scorecard"].get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
