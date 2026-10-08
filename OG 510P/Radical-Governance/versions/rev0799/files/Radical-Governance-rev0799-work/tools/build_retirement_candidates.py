#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from archive_meta import GENERATED, METADATA_DIR, current_notes_from_index, current_revision, generated_at_utc

ARCHIVE_INDEX = GENERATED / "ARCHIVE_INDEX.json"
NOTE_METADATA = METADATA_DIR / "note_metadata.json"
CASE_PACKET_MATRIX = GENERATED / "CASE_PACKET_MATRIX.json"
ROUTE_MERGE_PACKETS = METADATA_DIR / "route_merge_packets.json"
ROUTE_REDIRECT_LEDGER = METADATA_DIR / "route_redirect_ledger.json"
OUT_JSON = GENERATED / "RETIREMENT_CANDIDATES.json"
OUT_MD = GENERATED / "RETIREMENT_CANDIDATES.md"

STOP = set(
    "the and for with without from into onto before after when while where whose that this these those public governance no by of in to a an as is are be or and on via across through under over not should do can has have its it".split()
)


def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(t) > 2 and t not in STOP}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def overlap_score(left: dict, right: dict) -> tuple[float, int, float, float]:
    lexical = jaccard(left["tokens"], right["tokens"])
    tag_overlap = len(left["tags"] & right["tags"])
    tag_union = len(left["tags"] | right["tags"])
    tag_score = (tag_overlap / tag_union) if tag_union else 0.0
    score = 0.65 * lexical + 0.35 * tag_score
    return score, tag_overlap, lexical, tag_score


def load_route_merge_packets() -> dict:
    if not ROUTE_MERGE_PACKETS.exists():
        return {"packets": {}}
    return json.loads(ROUTE_MERGE_PACKETS.read_text(encoding="utf-8"))


def load_route_redirect_ledger() -> dict:
    if not ROUTE_REDIRECT_LEDGER.exists():
        return {"ledgers": {}}
    return json.loads(ROUTE_REDIRECT_LEDGER.read_text(encoding="utf-8"))


def reviewed_packet_rows(packet_data: dict, redirect_data: dict | None = None) -> list[dict]:
    rows: list[dict] = []
    redirect_ledgers = (redirect_data or {}).get("ledgers", {})
    for packet_id, packet in sorted(packet_data.get("packets", {}).items()):
        redirect_id = packet.get("redirect_ledger_id")
        redirect = redirect_ledgers.get(redirect_id, {}) if redirect_id else {}
        rows.append(
            {
                "packet_id": packet_id,
                "source_note": packet.get("source_note"),
                "source_file": packet.get("source_file"),
                "candidate_status": packet.get("candidate_status"),
                "reviewed_in_revision": packet.get("reviewed_in_revision"),
                "review_packet_file": packet.get("review_packet_file"),
                "review_packet_note": packet.get("review_packet_note"),
                "target_files": packet.get("target_files", []),
                "protected_elements": packet.get("protected_elements", []),
                "absorption_requirements": packet.get("absorption_requirements", []),
                "partial_absorption_patch_file": packet.get("partial_absorption_patch_file"),
                "partial_absorption_patch_note": packet.get("partial_absorption_patch_note"),
                "successor_route_file": packet.get("successor_route_file"),
                "successor_route_note": packet.get("successor_route_note"),
                "successor_absorption_status": packet.get("successor_absorption_status"),
                "redirect_ledger_id": redirect_id,
                "redirect_ledger_status": packet.get("redirect_ledger_status"),
                "reader_redirect_status": packet.get("reader_redirect_status") or redirect.get("reader_redirect_status"),
                "reader_redirect_surfaces": packet.get("reader_redirect_surfaces") or [s.get('surface') if isinstance(s, dict) else s for s in redirect.get("reader_redirect_surfaces", [])],
                "redirect_row_count": len(redirect.get("redirect_rows", [])) if redirect else 0,
                "deletion_authorization": redirect.get("deletion_authorization") if redirect else None,
                "final_preservation_review_file": packet.get("final_preservation_review_file") or redirect.get("final_preservation_review_file"),
                "final_preservation_review_note": packet.get("final_preservation_review_note") or redirect.get("final_preservation_review_note"),
                "final_preservation_review_status": packet.get("final_preservation_review_status") or redirect.get("final_preservation_review_status"),
                "retirement_blockers": packet.get("retirement_blockers", []),
                "absorption_progress": packet.get("absorption_progress", []),
                "next_action": packet.get("next_action", ""),
            }
        )
    return rows


def render_md(data: dict) -> str:
    lines = [
        "# Retirement / merge candidates audit",
        "",
        f"Generated for `{data['revision']}` from `generated/ARCHIVE_INDEX.json`, `metadata/note_metadata.json`, and `generated/CASE_PACKET_MATRIX.json`.",
        "",
        "## Holding",
        "",
        data["holding"],
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Archive notes | {data['archive_note_count']} |",
        f"| Current revision notes excluded | {data['current_note_count']} |",
        f"| Deletion-ready candidates | {data['deletion_ready_count']} |",
        f"| Merge-reviewed candidates | {len(data.get('merge_packet_reviewed_candidates', []))} |",
        f"| Partial absorption patches recorded | {data.get('partial_absorption_patch_count', 0)} |",
        f"| Successor routes recorded | {data.get('successor_route_count', 0)} |",
        f"| Redirect ledgers recorded | {data.get('redirect_ledger_count', 0)} |",
        f"| Redirect rows recorded | {data.get('redirect_row_count', 0)} |",
        f"| Reader redirect surfaces recorded | {data.get('reader_redirect_surface_count', 0)} |",
        f"| Final preservation reviews recorded | {data.get('final_preservation_review_count', 0)} |",
        f"| Retirement blockers recorded | {data.get('retirement_blocker_count', 0)} |",
        f"| Merge-packet priority candidates | {len(data.get('merge_packet_priority_candidates', []))} |",
        f"| Review-only candidates | {len(data['review_only_candidates'])} |",
        "",
        "## Merge-reviewed candidates",
        "",
        "These have already been converted from similarity-score pressure into explicit preservation instructions. A reviewed packet is still not deletion authorization.",
        "",
        "| Packet | Source note | Status | Review packet | Targets | Patch | Successor | Reader redirect | Redirect rows | Reader surfaces | Final review | Blockers | Absorption requirements | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    if not data.get("merge_packet_reviewed_candidates"):
        lines.append("| — | — | — | — | — | — | — | — | 0 | 0 | — | 0 | 0 | No merge packets have been reviewed yet. |")
    for row in data.get("merge_packet_reviewed_candidates", []):
        targets = ", ".join(f"`{Path(t).name}`" for t in row.get("target_files", [])[:3]) or "—"
        req_count = len(row.get("absorption_requirements", []))
        patch = f"note `{row.get('partial_absorption_patch_note')}`" if row.get("partial_absorption_patch_note") else "—"
        successor = f"note `{row.get('successor_route_note')}`" if row.get("successor_route_note") else "—"
        redirect_rows = row.get("redirect_row_count", 0)
        reader_surfaces = len(row.get("reader_redirect_surfaces", []) or [])
        reader_status = row.get("reader_redirect_status") or "—"
        final_review = f"note `{row.get('final_preservation_review_note')}`" if row.get("final_preservation_review_note") else "—"
        review_packet = f"note `{row.get('review_packet_note')}`" if row.get("review_packet_note") else "—"
        blockers = len(row.get("retirement_blockers", []) or [])
        lines.append(
            f"| `{row['packet_id']}` | `{row.get('source_note')}` | {row.get('candidate_status', '—')} | {review_packet} | {targets} | {patch} | {successor} | {reader_status} | {redirect_rows} | {reader_surfaces} | {final_review} | {blockers} | {req_count} | {row.get('next_action', '—')} |"
        )
    lines.extend([
        "",
        "## Merge-packet priority candidates",
        "",
        "These are still not deletion instructions. They are the smallest zero-dependency review queue where a future merge packet is most likely to reduce route mass without breaking dispatch, source posture, or test coverage. Rows that already have a merge packet are removed from this raw priority queue.",
        "",
        "| Note | Score | Nearest newer/current surface | Why prioritized |",
        "| --- | ---: | --- | --- |",
    ])
    if not data.get("merge_packet_priority_candidates"):
        lines.append("| — | — | — | No priority candidates met the bounded threshold after reviewed packets were excluded. |")
    for row in data.get("merge_packet_priority_candidates", []):
        near = row.get("nearest_surface") or {}
        near_text = f"`{near.get('number')}` {near.get('title','')}" if near else "—"
        lines.append(f"| `{row['number']}` {row['title']} | {row['review_score']:.3f} | {near_text} | {row['priority_reason']} |")
    lines.extend([
        "",
        "## Review-only candidates",
        "",
        "These are not deletion instructions. They are places where a future human merge packet should check whether an older note has been absorbed without losing a test, source posture, affected-party tail, dispatch role, or opposition brief.",
        "",
        "| Note | Score | Dependency count | Nearest newer/current surface | Reason |",
        "| --- | ---: | ---: | --- | --- |",
    ])
    if not data["review_only_candidates"]:
        lines.append("| — | — | — | — | No review-only candidates met the audit threshold. |")
    for row in data["review_only_candidates"][:50]:
        near = row.get("nearest_surface") or {}
        near_text = f"`{near.get('number')}` {near.get('title','')}" if near else "—"
        lines.append(
            f"| `{row['number']}` {row['title']} | {row['review_score']:.3f} | {row['dependency_count']} | {near_text} | {row['reason']} |"
        )
    lines.extend(["", "## Protected classes", ""])
    for item in data.get("protected_classes", []):
        lines.append(f"- **{item['class']}**: {item['instruction']}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    index = json.loads(ARCHIVE_INDEX.read_text(encoding="utf-8"))
    metadata = json.loads(NOTE_METADATA.read_text(encoding="utf-8"))
    matrix = json.loads(CASE_PACKET_MATRIX.read_text(encoding="utf-8"))
    current_notes = set(current_notes_from_index())
    meta_notes = metadata.get("notes", {})
    packet_data = load_route_merge_packets()
    redirect_data = load_route_redirect_ledger()
    merge_reviewed_candidates = reviewed_packet_rows(packet_data, redirect_data)
    reviewed_note_numbers = {int(row["source_note"]) for row in merge_reviewed_candidates if row.get("source_note") is not None}

    dependents: Counter[int] = Counter()
    for _file, meta in meta_notes.items():
        for n in meta.get("depends_on", []) + meta.get("reserved_notes", []):
            dependents[int(n)] += 1
        dispatcher = meta.get("dispatcher")
        if dispatcher is not None:
            dependents[int(dispatcher)] += 1
    for case in matrix.get("cases", []):
        for n in case.get("live_chain_notes", []) + case.get("reserved_notes", []):
            dependents[int(n)] += 1

    notes: list[dict] = []
    for entry in index.get("notes", []):
        file = entry.get("file", "")
        meta = meta_notes.get(file, {})
        number = int(entry.get("number", meta.get("number", 0)))
        tag_set = set(entry.get("tags", [])) | set(meta.get("tags", []))
        text_tokens = tokens(" ".join([entry.get("title", ""), entry.get("thesis", ""), " ".join(tag_set), meta.get("canon_role", "")]))
        notes.append(
            {
                "file": file,
                "number": number,
                "title": entry.get("title", ""),
                "tokens": text_tokens,
                "tags": tag_set,
                "meta": meta,
                "dependency_count": dependents[number],
            }
        )

    # Newer/current surfaces are the possible absorption surfaces. They are deliberately broad enough
    # to identify merge-review pressure, not deletion readiness.
    newer_surfaces = [
        n
        for n in notes
        if n["number"] >= 848
        or n["file"] in current_notes
        or n["meta"].get("note_class") in {"policy_docket", "applied_case_packet"}
    ]

    candidates: list[dict] = []
    for n in notes:
        meta = n["meta"]
        if n["file"] in current_notes:
            continue
        if n["number"] >= 848:
            continue
        if meta.get("first_citation") or meta.get("note_class") in {"applied_case_packet", "policy_docket"}:
            continue

        best = None
        best_tuple = (0.0, 0, 0.0, 0.0)
        for other in newer_surfaces:
            if other["number"] <= n["number"]:
                continue
            score_tuple = overlap_score(n, other)
            if score_tuple[0] > best_tuple[0]:
                best_tuple = score_tuple
                best = other

        best_score, tag_overlap, lexical, tag_score = best_tuple
        if best_score < 0.10:
            continue
        if tag_overlap < 2 and lexical < 0.09:
            continue

        dep = n["dependency_count"]
        review_score = best_score / (1 + min(dep, 8) * 0.12)
        if tag_overlap >= 2 and lexical >= 0.06:
            reason = f"lexical plus tag overlap with newer surface; {tag_overlap} shared tag(s); review only"
        elif tag_overlap >= 2:
            reason = f"tag-family overlap with newer surface; {tag_overlap} shared tag(s); review only"
        else:
            reason = "lexical overlap with newer surface; review only"
        if dep > 2:
            reason += "; dependencies require preservation check"
        else:
            reason += "; low dependency"

        candidates.append(
            {
                "file": n["file"],
                "number": n["number"],
                "title": n["title"],
                "dependency_count": dep,
                "review_score": round(review_score, 4),
                "nearest_surface": {
                    "file": best["file"],
                    "number": best["number"],
                    "title": best["title"],
                    "combined_overlap": round(best_score, 4),
                    "lexical_overlap": round(lexical, 4),
                    "tag_overlap": tag_overlap,
                    "tag_score": round(tag_score, 4),
                    "shared_tags": sorted(list(n["tags"] & best["tags"]))[:12],
                }
                if best
                else None,
                "reason": reason,
                "instruction": "Do not delete. Review only if a future merge packet proves the newer surface preserves the older note's test, source posture, affected-party tail, opposition brief, and dispatch function.",
            }
        )

    candidates.sort(key=lambda row: (-row["review_score"], row["dependency_count"], row["number"]))
    merge_packet_priority_candidates = []
    for row in candidates:
        if int(row.get("number", -1)) in reviewed_note_numbers:
            continue
        near = row.get("nearest_surface") or {}
        shared = near.get("shared_tags", [])
        if row.get("dependency_count", 0) != 0:
            continue
        if row.get("review_score", 0) < 0.18:
            continue
        if near.get("tag_overlap", 0) < 4:
            continue
        priority = dict(row)
        priority["priority_reason"] = (
            f"zero recorded dependencies; {near.get('tag_overlap', 0)} shared tag(s); "
            f"requires human proof that the newer surface preserves: {', '.join(shared[:5]) or 'overlap fields'}"
        )
        merge_packet_priority_candidates.append(priority)
        if len(merge_packet_priority_candidates) >= 12:
            break

    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "generated_from": ["generated/ARCHIVE_INDEX.json", "metadata/note_metadata.json", "generated/CASE_PACKET_MATRIX.json", "metadata/route_merge_packets.json", "metadata/route_redirect_ledger.json"],
        "route_merge_packets_source": "metadata/route_merge_packets.json" if ROUTE_MERGE_PACKETS.exists() else None,
        "route_redirect_ledger_source": "metadata/route_redirect_ledger.json" if ROUTE_REDIRECT_LEDGER.exists() else None,
        "route_merge_packet_count": len(packet_data.get("packets", {})),
        "redirect_ledger_count": len(redirect_data.get("ledgers", {})),
        "redirect_row_count": sum(len(ledger.get("redirect_rows", [])) for ledger in redirect_data.get("ledgers", {}).values()),
        "reader_redirect_surface_count": sum(len(ledger.get("reader_redirect_surfaces", [])) for ledger in redirect_data.get("ledgers", {}).values()),
        "final_preservation_review_count": sum(1 for row in merge_reviewed_candidates if row.get("final_preservation_review_note")),
        "retirement_blocker_count": sum(len(row.get("retirement_blockers", []) or []) for row in merge_reviewed_candidates),
        "partial_absorption_patch_count": sum(1 for row in merge_reviewed_candidates if row.get("partial_absorption_patch_note")),
        "successor_route_count": sum(1 for row in merge_reviewed_candidates if row.get("successor_route_note")),
        "holding": "No archive note is deletion-ready from metadata alone. This audit turns merge pressure into a bounded review-only queue using lexical and tag overlap, and every possible merge must preserve tests, source posture, affected-party tails, opposition briefs, dispatch function, successor-route parity, and protected-element redirect evidence. Merge-reviewed packets and redirect ledgers are preservation instructions, not deletion authorization.",
        "archive_note_count": len(notes),
        "current_note_count": len(current_notes),
        "deletion_ready_count": 0,
        "merge_packet_reviewed_candidates": merge_reviewed_candidates,
        "merge_packet_priority_candidates": merge_packet_priority_candidates,
        "review_only_candidates": [row for row in candidates if int(row.get("number", -1)) not in reviewed_note_numbers][:80],
        "protected_classes": [
            {"class": "current revision notes", "instruction": "never retire in the same revision that adds them"},
            {"class": "first-citation notes", "instruction": "do not retire unless the canon front door and source posture are explicitly reassigned"},
            {"class": "applied case packets", "instruction": "merge only by preserving affected-party tail, lower-form result, source keys, and anti-theater core"},
            {"class": "dispatcher and test matrices", "instruction": "do not collapse into prose summaries; they route future work"},
            {"class": "high-dependency notes", "instruction": "use overlap as a review signal only; dependencies must be traced before any merge"},
        ],
    }
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_md(data), encoding="utf-8")
    print("OK: wrote generated/RETIREMENT_CANDIDATES.json and generated/RETIREMENT_CANDIDATES.md")


if __name__ == "__main__":
    main()
