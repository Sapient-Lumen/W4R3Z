#!/usr/bin/env python3
"""Regenerate rev0057 mission-audit data summaries.

Standard-library only. Reads rev0056 holdout files plus the current tree and writes:
  data/rev0057_cloudtainer_size_audit.csv
  data/rev0057_cloudtainer_size_audit_summary.json
  data/rev0057_claim_mechanism_profile.csv
  data/rev0057_claim_action_profile.csv
  data/rev0057_claim_mechanism_summary.json
  data/rev0057_mission_audit.json
  data/rev0057_question_bank.json

It does not change gameplay semantics.
"""
from __future__ import annotations

import csv
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REV = "rev0057"
CODENAME = "missionaudit-wastepivot"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def category(path: str) -> str:
    first = path.split("/", 1)[0]
    if first in {"data", "docs", "src", "tests", "scripts", "cpp", "build", ".pytest_cache"}:
        return first
    if "__pycache__" in path:
        return "__pycache__"
    return "root"


def waste_class(path: str) -> str:
    if path == "CHECKSUMS.json":
        return "integrity_manifest"
    if "__pycache__" in path or path.endswith(".pyc") or path.startswith(".pytest_cache/"):
        return "cache_should_not_ship"
    if path.startswith("build/"):
        return "derived_build_output_should_not_be_integrity_tracked"
    if re.search(r"_cpp_transitions\.csv$", path):
        return "large_raw_transition_evidence"
    if re.search(r"_replay_traces\.jsonl$", path):
        return "raw_trace_evidence"
    if path.startswith("data/") and path.endswith(".csv"):
        return "tabular_evidence"
    return "core_or_summary"


def build_size_audit() -> dict:
    rows = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rp = rel(path)
        size = path.stat().st_size
        ext = ".csv.gz" if path.name.endswith(".csv.gz") else (path.suffix.lower() or "<none>")
        rows.append({
            "path": rp,
            "bytes": size,
            "kib": round(size / 1024, 3),
            "mib": round(size / (1024 * 1024), 6),
            "category": category(rp),
            "extension": ext,
            "waste_class": waste_class(rp),
        })
    rows.sort(key=lambda row: (-row["bytes"], row["path"]))
    with (ROOT / "data/rev0057_cloudtainer_size_audit.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rank", "path", "bytes", "kib", "mib", "category", "extension", "waste_class"])
        writer.writeheader()
        for rank, row in enumerate(rows, 1):
            writer.writerow({"rank": rank, **row})
    by_cat = defaultdict(lambda: {"files": 0, "bytes": 0})
    by_ext = defaultdict(lambda: {"files": 0, "bytes": 0})
    by_waste = defaultdict(lambda: {"files": 0, "bytes": 0})
    for row in rows:
        for table, key in ((by_cat, row["category"]), (by_ext, row["extension"]), (by_waste, row["waste_class"])):
            table[key]["files"] += 1
            table[key]["bytes"] += row["bytes"]
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "total_files": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows),
        "total_mib": round(sum(row["bytes"] for row in rows) / (1024 * 1024), 3),
        "category_summary": dict(sorted(by_cat.items(), key=lambda kv: -kv[1]["bytes"])),
        "extension_summary_top": dict(sorted(by_ext.items(), key=lambda kv: -kv[1]["bytes"])[:20]),
        "waste_class_summary": dict(sorted(by_waste.items(), key=lambda kv: -kv[1]["bytes"])),
        "raw_transition_csv_count": sum(1 for row in rows if row["waste_class"] == "large_raw_transition_evidence"),
        "raw_transition_csv_bytes": sum(row["bytes"] for row in rows if row["waste_class"] == "large_raw_transition_evidence"),
        "cache_and_build_file_count": sum(1 for row in rows if row["waste_class"] in {"cache_should_not_ship", "derived_build_output_should_not_be_integrity_tracked"}),
        "cache_and_build_bytes": sum(row["bytes"] for row in rows if row["waste_class"] in {"cache_should_not_ship", "derived_build_output_should_not_be_integrity_tracked"}),
        "top_25_files": rows[:25],
        "recommendation": "Move bulky raw transition evidence to a compressed/archived tier and stop integrity-tracking caches/build outputs; keep compact summaries in the main linked cube.",
    }
    dump_json(ROOT / "data/rev0057_cloudtainer_size_audit_summary.json", summary)
    return summary


def loss_loser(loss_reason: str):
    match = re.search(r"player_([01])_", loss_reason or "")
    return int(match.group(1)) if match else None


def mechanism(loss_reason: str) -> str:
    lr = loss_reason or ""
    if "draw_from_empty_library" in lr:
        return "library_out"
    if "life_total_zero_or_less" in lr or "zero_or_less" in lr:
        return "life_total"
    if "truncation" in lr:
        return "truncation"
    return "other"


def normalize_action(kind: str, action: str) -> str:
    if kind == "CAST":
        card = re.search(r"card=([^,\)]+)", action)
        mode = re.search(r"mode=([^,\)]+)", action)
        payment = re.search(r"payment=([^,\)]+)", action)
        pitch = re.search(r"pitch_card=([^,\)]+)", action)
        target = re.search(r"target_card=([^,\)]+)", action)
        bits = [f"CAST:{card.group(1) if card else 'unknown'}"]
        if mode:
            bits.append(f"mode={mode.group(1)}")
        if payment:
            bits.append(f"payment={payment.group(1)}")
        if pitch:
            bits.append(f"pitch={pitch.group(1)}")
        if target:
            bits.append(f"target={target.group(1)}")
        return " ".join(bits)
    if kind == "ACTIVATE_JACE":
        mode = re.search(r"mode=([^,\)]+)", action)
        return f"ACTIVATE_JACE:{mode.group(1) if mode else 'unknown'}"
    if kind == "CHOOSE_FOR_EFFECT":
        effect = re.search(r"effect=([^,\)]+)", action)
        discard = re.search(r"discard=([^,\)]+)", action)
        if effect and discard:
            return f"CHOOSE:{effect.group(1)} discard={discard.group(1)}"
        if effect:
            return f"CHOOSE:{effect.group(1)}"
        return "CHOOSE:unknown"
    if kind in {"PLAY_ISLAND", "PASS", "ATTACK", "BLOCK"}:
        return kind
    return kind


def build_claim_mechanism() -> dict:
    games_path = ROOT / "data/rev0056_life_cell_replication_games.csv"
    transitions_path = ROOT / "data/rev0056_life_cell_replication_cpp_transitions.csv"
    if not games_path.exists() or not transitions_path.exists():
        raise SystemExit("rev0056 life-cell source files are missing")
    games = []
    by_game = {}
    with games_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            row["starting_life"] = int(row["starting_life"])
            row["focus_target_seat"] = int(row["focus_target_seat"])
            row["focus_target_score"] = float(row["focus_target_score"])
            row["decisions"] = int(row["decisions"])
            row["turn_number"] = int(row["turn_number"])
            row["loser"] = loss_loser(row.get("loss_reason", ""))
            row["mechanism"] = mechanism(row.get("loss_reason", ""))
            row["target_result"] = "target_win" if row["focus_target_score"] == 1.0 else ("target_draw" if row["focus_target_score"] == 0.5 else "target_loss")
            row["loser_role"] = "unknown" if row["loser"] is None else ("target" if row["loser"] == row["focus_target_seat"] else "opponent")
            games.append(row)
            by_game[row["cpp_shadow_game_id"]] = row
    mechanism_counts = Counter()
    scores_by_life = defaultdict(list)
    decisions_by_life_mechanism = defaultdict(list)
    turns_by_life_mechanism = defaultdict(list)
    loss_reason_counts = Counter()
    for game in games:
        key = (game["starting_life"], game["target_result"], game["mechanism"], game["loser_role"])
        mechanism_counts[key] += 1
        scores_by_life[game["starting_life"]].append(game["focus_target_score"])
        decisions_by_life_mechanism[(game["starting_life"], game["mechanism"])].append(game["decisions"])
        turns_by_life_mechanism[(game["starting_life"], game["mechanism"])].append(game["turn_number"])
        loss_reason_counts[game.get("loss_reason", "")] += 1
    profile_rows = []
    for (life, result, mech, loser_role), count in sorted(mechanism_counts.items()):
        total = sum(v for (l, *_), v in mechanism_counts.items() if l == life)
        profile_rows.append({
            "starting_life": life,
            "target_result": result,
            "terminal_mechanism": mech,
            "loser_role": loser_role,
            "games": count,
            "share_of_life_cell": round(count / total, 6) if total else 0,
        })
    with (ROOT / "data/rev0057_claim_mechanism_profile.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["starting_life", "target_result", "terminal_mechanism", "loser_role", "games", "share_of_life_cell"])
        writer.writeheader()
        writer.writerows(profile_rows)
    action_kind_counts = Counter()
    action_signature_counts = Counter()
    role_rows = Counter()
    examples = defaultdict(list)
    transition_rows = 0
    with transitions_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            transition_rows += 1
            game = by_game.get(row["game_id"])
            if not game:
                continue
            player = int(row["player"])
            role = "target" if player == game["focus_target_seat"] else "opponent"
            kind = row["action_kind"]
            sig = normalize_action(kind, row["action"])
            action_kind_counts[(role, kind)] += 1
            action_signature_counts[(role, sig)] += 1
            role_rows[role] += 1
            if len(examples[(role, sig)]) < 3:
                examples[(role, sig)].append(row["action"])
    action_rows = []
    for (role, kind), count in action_kind_counts.items():
        action_rows.append({
            "profile": "action_kind",
            "role": role,
            "label": kind,
            "count": count,
            "share_within_role": round(count / role_rows[role], 6) if role_rows[role] else 0,
            "example_actions": "",
        })
    for (role, sig), count in action_signature_counts.items():
        action_rows.append({
            "profile": "action_signature",
            "role": role,
            "label": sig,
            "count": count,
            "share_within_role": round(count / role_rows[role], 6) if role_rows[role] else 0,
            "example_actions": " | ".join(examples[(role, sig)]),
        })
    action_rows.sort(key=lambda row: (row["profile"], row["role"], -row["count"], row["label"]))
    with (ROOT / "data/rev0057_claim_action_profile.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["profile", "role", "label", "count", "share_within_role", "example_actions"])
        writer.writeheader()
        writer.writerows(action_rows)
    def median(values):
        return statistics.median(values) if values else None
    summary = {
        "revision": REV,
        "codename": CODENAME,
        "source_revision": "rev0056",
        "focused_matchup": "cf34_counter_wall vs pub_threat_overlord",
        "total_games": len(games),
        "life_cell_scores": {str(life): {"games": len(vals), "score": sum(vals) / len(vals)} for life, vals in sorted(scores_by_life.items())},
        "loss_reason_counts": dict(loss_reason_counts.most_common()),
        "mechanism_counts": profile_rows,
        "key_inference": "The replicated claim is primarily an endurance/decking claim, not a direct damage/life-race claim: most target wins end when the opponent attempts to draw from an empty library.",
        "target_wins_by_opponent_library_out": sum(r["games"] for r in profile_rows if r["target_result"] == "target_win" and r["terminal_mechanism"] == "library_out" and r["loser_role"] == "opponent"),
        "target_wins_by_opponent_life_total": sum(r["games"] for r in profile_rows if r["target_result"] == "target_win" and r["terminal_mechanism"] == "life_total" and r["loser_role"] == "opponent"),
        "target_losses_by_target_library_out": sum(r["games"] for r in profile_rows if r["target_result"] == "target_loss" and r["terminal_mechanism"] == "library_out" and r["loser_role"] == "target"),
        "target_losses_by_target_life_total": sum(r["games"] for r in profile_rows if r["target_result"] == "target_loss" and r["terminal_mechanism"] == "life_total" and r["loser_role"] == "target"),
        "median_decisions_by_life_and_mechanism": {f"{life}_{mech}": median(vals) for (life, mech), vals in sorted(decisions_by_life_mechanism.items())},
        "median_turns_by_life_and_mechanism": {f"{life}_{mech}": median(vals) for (life, mech), vals in sorted(turns_by_life_mechanism.items())},
        "transition_rows": transition_rows,
        "role_transition_rows": dict(role_rows),
        "top_action_kinds_by_role": {
            role: [
                {"action_kind": kind, "count": count, "share": round(count / role_rows[role], 6) if role_rows[role] else 0}
                for (r, kind), count in action_kind_counts.most_common() if r == role
            ][:12]
            for role in ["target", "opponent"]
        },
        "top_action_signatures_by_role": {
            role: [
                {"action_signature": sig, "count": count, "share": round(count / role_rows[role], 6) if role_rows[role] else 0}
                for (r, sig), count in action_signature_counts.most_common() if r == role
            ][:20]
            for role in ["target", "opponent"]
        },
        "recommended_next_ablation": "Separate pilot, deck-size, mulligan, and Jace draw/decking effects before calling this a general life-total result.",
    }
    dump_json(ROOT / "data/rev0057_claim_mechanism_summary.json", summary)
    return summary


def write_mission_json(size_summary: dict, claim_summary: dict) -> None:
    mission = {
        "revision": REV,
        "codename": CODENAME,
        "heart_of_mission": "A closed-world, reproducible imperfect-information Magic microgame for exact legal actions, public-safe observations, replayable evidence, and local strategic theory discovery.",
        "missing": [
            "one-page mission charter",
            "compact claim cards",
            "terminal mechanism labels in claim tables",
            "causal decomposition experiments",
            "retention/archive policy",
            "experiment registry with stop conditions",
            "human-readable dashboard/report surface",
        ],
        "should_change": [
            "shift from claim mining to explaining the first replicated claim",
            "run pilot/deck/deck-size/mulligan/Jace ablations",
            "separate core summaries from raw evidence archives",
            "stop tracking caches and derived build outputs by default",
            "derive audit revision/focus from manifest over time",
        ],
        "possible_wrong_or_wasteful": [
            "the life-cell claim is mostly a library-out/endurance mechanism rather than a direct damage/life-race mechanism",
            "raw transition CSVs dominate uncompressed working size",
            "caches and build outputs are included in the integrity-tracked tree",
            "audit output/focus has become large and revision-specific instead of structured",
        ],
        "speculation": "The cf34 edge is probably a 60-card counter/Jace endurance shell exploiting the 40-card Overlord shell's draw pressure; life 40 increases survival time and reduces target life losses.",
        "size_summary_ref": "data/rev0057_cloudtainer_size_audit_summary.json",
        "claim_summary_ref": "data/rev0057_claim_mechanism_summary.json",
    }
    dump_json(ROOT / "data/rev0057_mission_audit.json", mission)
    qbank = {
        "revision": REV,
        "questions": [
            {"id": "Q57-01", "question": "Does the replicated edge remain when both shells have equal deck size?", "first_experiment": "E57-C"},
            {"id": "Q57-02", "question": "Does cf34 pilot skill transfer to the opponent deck shell?", "first_experiment": "E57-A"},
            {"id": "Q57-03", "question": "Is Jace zero activation a self-decking accelerant or a defensive selection engine?", "first_experiment": "E57-D"},
            {"id": "Q57-04", "question": "How much of the result comes from mulligan policy rather than play policy?", "first_experiment": "E57-E"},
            {"id": "Q57-05", "question": "Which raw evidence files can be compressed without reducing claim auditability?", "first_experiment": "maintenance include-list"},
        ],
    }
    dump_json(ROOT / "data/rev0057_question_bank.json", qbank)


def main() -> None:
    size_summary = build_size_audit()
    claim_summary = build_claim_mechanism()
    # Rebuild size after claim CSV/JSON updates so the summary includes these files.
    size_summary = build_size_audit()
    write_mission_json(size_summary, claim_summary)
    print(json.dumps({
        "revision": REV,
        "total_mib": size_summary["total_mib"],
        "target_wins_by_opponent_library_out": claim_summary["target_wins_by_opponent_library_out"],
        "target_wins_by_opponent_life_total": claim_summary["target_wins_by_opponent_life_total"],
        "recommendation": claim_summary["recommended_next_ablation"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
