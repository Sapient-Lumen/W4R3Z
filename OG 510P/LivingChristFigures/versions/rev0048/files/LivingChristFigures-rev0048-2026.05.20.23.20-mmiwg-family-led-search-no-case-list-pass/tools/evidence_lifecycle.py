#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re
from collections import Counter, defaultdict
from pathlib import Path

CAPACITY_WORDS = re.compile(r"(?i)\b(current|capacity|available|availability|helpline|hotline|shelter|refuge|safe house|safe-house|referral|intake|call centre|call center|frontline|service|services|bed|route|visit|visitation|outreach|street rounds|case management)\b")
BOUNDARY_TYPES = {"risk_boundary_or_caution", "capacity_or_implementation_boundary", "negative_space_or_gap", "public_export_boundary"}
INTERPRETIVE_TYPES = {"office_interpretation", "boundary_interpretation", "theological_or_metaphorical_reading"}
PRIMARYISH = {"government_or_court", "un_or_multilateral", "regional_data_or_network", "public_agency_or_cemetery_source", "public_agency_source", "academic_or_research", "academic_source", "nonprofit_or_project_self_description"}
CRITICALISH = {"critical_press", "critical_article", "investigative_or_critical_press"}


def read_csv(root: Path, rel: str) -> list[dict]:
    p = root / rel
    if not p.exists():
        return []
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, rows: list[dict]) -> None:
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, title: str, intro: str, rows: list[dict], fields: list[str], limit: int = 80) -> None:
    lines = [f"# {title}", "", intro, "", f"Rows: {len(rows)}", ""]
    if rows:
        lines.append("| " + " | ".join(fields) + " |")
        lines.append("| " + " | ".join(["---"] * len(fields)) + " |")
        for r in rows[:limit]:
            vals = []
            for field in fields:
                value = str(r.get(field, "")).replace("|", "/").replace("\n", " ")[:180]
                vals.append(value)
            lines.append("| " + " | ".join(vals) + " |")
        if len(rows) > limit:
            lines.append(f"\n_Table truncated in markdown view at {limit} rows; CSV/JSON contain all rows._")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def split_pipe(value: str) -> list[str]:
    return [x for x in (value or "").split("|") if x]


def classify_claim(claim: dict, sources: dict[str, dict], cand: dict[str, dict]) -> dict:
    ctype = claim.get("claim_type", "")
    status = claim.get("claim_status", "")
    text = " ".join([claim.get("claim_text", ""), claim.get("evidence_text", ""), claim.get("notes", "")])
    source_ids = split_pipe(claim.get("evidence_source_ids", ""))
    source_types = [sources.get(sid, {}).get("source_type", "unknown") for sid in source_ids]
    domains = [sources.get(sid, {}).get("domain", "unknown") for sid in source_ids]
    cand_row = cand.get(claim.get("candidate_id", ""), {})
    capacity_state = cand_row.get("capacity_state", "")
    source_count = len(source_ids)
    independent_domains = len(set([d for d in domains if d and d != "unknown"]))

    if ctype in BOUNDARY_TYPES or "caution" in status or "debt" in status:
        strength = "boundary_or_counterclaim"
    elif ctype in INTERPRETIVE_TYPES or "interpretive" in status:
        strength = "interpretive_not_fact_claim"
    elif any(st in CRITICALISH for st in source_types):
        strength = "critical_counterevidence_present"
    elif source_count >= 2 and independent_domains >= 2:
        strength = "multi_source_supported_shape"
    elif any(st in PRIMARYISH for st in source_types):
        strength = "single_primary_or_institutional_shape"
    elif source_count == 1:
        strength = "single_source_supported_shape"
    else:
        strength = "unsupported_or_missing_source_link"

    volatile = bool(CAPACITY_WORDS.search(text)) or "current_capacity_unverified" in capacity_state or "capacity" in ctype
    if volatile and (source_count < 2 or "unverified" in capacity_state):
        cap_risk = "high"
    elif volatile:
        cap_risk = "medium"
    else:
        cap_risk = "low"

    if strength == "unsupported_or_missing_source_link" or cap_risk == "high":
        refresh = "now_or_before_any_public_claim"
    elif strength in {"boundary_or_counterclaim", "critical_counterevidence_present"}:
        refresh = "soon_keep_near_claim"
    elif ctype in INTERPRETIVE_TYPES:
        refresh = "not_freshness_driven_but_keep_evidence_adjacent"
    else:
        refresh = "standard_refresh_cycle"

    if cap_risk == "high":
        cadence = "30_days_or_before_use"
    elif cap_risk == "medium":
        cadence = "90_days_or_before_use"
    elif strength in {"single_source_supported_shape", "single_primary_or_institutional_shape"}:
        cadence = "180_days_or_before_use"
    else:
        cadence = "365_days_or_before_major_revision"

    why_parts = []
    if cap_risk != "low":
        why_parts.append(f"capacity/current-service language risk={cap_risk}")
    if source_count < 2:
        why_parts.append("fewer_than_two_sources")
    if ctype in INTERPRETIVE_TYPES:
        why_parts.append("interpretive claim: do not let prose substitute for evidence")
    if ctype in BOUNDARY_TYPES:
        why_parts.append("boundary/caution claim must travel with underlying positive claim")
    if not why_parts:
        why_parts.append("ordinary supported-shape lifecycle")

    return {
        "claim_id": claim.get("claim_id", ""),
        "candidate_id": claim.get("candidate_id", ""),
        "candidate_name": claim.get("candidate_name", ""),
        "claim_type": ctype,
        "claim_status": status,
        "evidence_strength": strength,
        "capacity_currentness_risk": cap_risk,
        "source_count": str(source_count),
        "independent_domain_count": str(independent_domains),
        "source_type_profile": "|".join(sorted(set(source_types))) if source_types else "none",
        "refresh_priority": refresh,
        "suggested_refresh_cadence": cadence,
        "needs_human_review": "true" if refresh in {"now_or_before_any_public_claim", "soon_keep_near_claim"} else "false",
        "why": "; ".join(why_parts),
    }


def aggregate_queue(claim_rows: list[dict], debt_rows: list[dict], cand_rows: list[dict]) -> list[dict]:
    by_cand = defaultdict(list)
    for r in claim_rows:
        by_cand[r["candidate_id"]].append(r)
    high_debt = Counter()
    debt_types = defaultdict(set)
    for d in debt_rows:
        cid = d.get("candidate_id", "")
        if d.get("priority") in {"high", "urgent"}:
            high_debt[cid] += 1
        if d.get("debt_type"):
            debt_types[cid].add(d.get("debt_type"))
    priority_rank = {
        "now_or_before_any_public_claim": 0,
        "soon_keep_near_claim": 1,
        "not_freshness_driven_but_keep_evidence_adjacent": 2,
        "standard_refresh_cycle": 3,
    }
    cadence_rank = {
        "30_days_or_before_use": 0,
        "90_days_or_before_use": 1,
        "180_days_or_before_use": 2,
        "365_days_or_before_major_revision": 3,
    }
    out = []
    for c in cand_rows:
        cid = c.get("candidate_id", "")
        claims = by_cand.get(cid, [])
        if not claims:
            best_priority = "now_or_before_any_public_claim"
            best_cadence = "30_days_or_before_use"
        else:
            best_priority = sorted((r["refresh_priority"] for r in claims), key=lambda x: priority_rank.get(x, 9))[0]
            best_cadence = sorted((r["suggested_refresh_cadence"] for r in claims), key=lambda x: cadence_rank.get(x, 9))[0]
        cap_high = sum(1 for r in claims if r.get("capacity_currentness_risk") == "high")
        boundary = sum(1 for r in claims if r.get("evidence_strength") in {"boundary_or_counterclaim", "critical_counterevidence_present"})
        weak = sum(1 for r in claims if r.get("evidence_strength") in {"unsupported_or_missing_source_link", "single_source_supported_shape", "single_primary_or_institutional_shape"})
        reasons = []
        if cap_high:
            reasons.append(f"{cap_high} high current-capacity-risk claim(s)")
        if high_debt[cid]:
            reasons.append(f"{high_debt[cid]} high-priority evidence-debt row(s)")
        if weak:
            reasons.append(f"{weak} single/weakly sourced claim(s)")
        if boundary:
            reasons.append(f"{boundary} boundary/counterevidence claim(s) must remain adjacent")
        if not reasons:
            reasons.append("standard lifecycle; no urgent lifecycle signal derived")
        out.append({
            "candidate_id": cid,
            "candidate_name": c.get("name", ""),
            "status_current": c.get("status_current", ""),
            "capacity_state": c.get("capacity_state", ""),
            "highest_refresh_priority": best_priority,
            "shortest_suggested_cadence": best_cadence,
            "claim_rows": str(len(claims)),
            "high_capacity_risk_claims": str(cap_high),
            "high_priority_evidence_debts": str(high_debt[cid]),
            "weak_or_single_source_claims": str(weak),
            "debt_type_profile": "|".join(sorted(debt_types[cid])),
            "why": "; ".join(reasons),
        })
    out.sort(key=lambda r: (priority_rank.get(r["highest_refresh_priority"], 9), cadence_rank.get(r["shortest_suggested_cadence"], 9), r["candidate_name"]))
    return out


def run(root: Path) -> tuple[list[dict], list[dict]]:
    claims = read_csv(root, "Claim-Ledger-current.csv")
    sources = {r.get("source_id", ""): r for r in read_csv(root, "Source-Registry-current.csv")}
    cands = {r.get("candidate_id", ""): r for r in read_csv(root, "Candidate-Ledger-current.csv")}
    explicit_quarantine = {r.get("claim_id", "") for r in read_csv(root, "META/Public-Claim-Quarantine-current.csv")}
    claim_strength = [classify_claim(c, sources, cands) for c in claims]
    # rev0041: an explicit public-claim quarantine is a safety override, not merely
    # a derived lifecycle label. Keep quarantined claims in the public-claim review
    # lane even when added sources would otherwise lower the derived freshness risk.
    for row in claim_strength:
        if row.get("claim_id") in explicit_quarantine:
            row["refresh_priority"] = "now_or_before_any_public_claim"
            row["suggested_refresh_cadence"] = "30_days_or_before_use"
            row["needs_human_review"] = "true"
            why = row.get("why", "")
            if "explicit_public_claim_quarantine" not in why:
                row["why"] = (why + "; " if why else "") + "explicit_public_claim_quarantine"
    queue = aggregate_queue(claim_strength, read_csv(root, "Evidence-Debt-current.csv"), list(cands.values()))
    return claim_strength, queue


def write_reports(root: Path) -> None:
    claim_strength, queue = run(root)
    claim_fields = ["claim_id","candidate_id","candidate_name","claim_type","claim_status","evidence_strength","capacity_currentness_risk","source_count","independent_domain_count","source_type_profile","refresh_priority","suggested_refresh_cadence","needs_human_review","why"]
    queue_fields = ["candidate_id","candidate_name","status_current","capacity_state","highest_refresh_priority","shortest_suggested_cadence","claim_rows","high_capacity_risk_claims","high_priority_evidence_debts","weak_or_single_source_claims","debt_type_profile","why"]
    write_csv(root / "META/Claim-Evidence-Strength-current.csv", claim_strength, claim_fields)
    write_json(root / "META/Claim-Evidence-Strength-current.json", claim_strength)
    write_md(root / "META/Claim-Evidence-Strength-current.md", "Claim Evidence Strength — current", "Derived lifecycle labels. These are not truth verdicts; they are refresh and caution routing labels.", claim_strength, ["claim_id","candidate_id","evidence_strength","capacity_currentness_risk","refresh_priority","why"])
    write_csv(root / "META/Refresh-Priority-Queue-current.csv", queue, queue_fields)
    write_json(root / "META/Refresh-Priority-Queue-current.json", queue)
    write_md(root / "META/Refresh-Priority-Queue-current.md", "Refresh Priority Queue — current", "Candidate-level work queue derived from claim evidence strength, current-capacity language, and evidence-debt pressure.", queue, ["candidate_id","highest_refresh_priority","shortest_suggested_cadence","high_capacity_risk_claims","high_priority_evidence_debts","why"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--write-report", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if args.write_report:
        write_reports(root)
    claim_strength, queue = run(root)
    high = sum(1 for r in claim_strength if r["capacity_currentness_risk"] == "high")
    now = sum(1 for r in claim_strength if r["refresh_priority"] == "now_or_before_any_public_claim")
    print(f"claims={len(claim_strength)} high_capacity_risk_claims={high} now_or_before_public_claim={now} candidates={len(queue)}")

if __name__ == "__main__":
    main()
