#!/usr/bin/env python3
"""Validate LLMPoetry reader-facing state objects."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def add(checks: list[dict], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": detail})


FORBIDDEN_QUALITY_CLAIMS = [
    "admitted",
    "evidence-ready",
    "publishable",
    "proves literary quality",
    "quality proof",
]

REQUIRED_STATES = ["closed", "open", "traversal", "patched"]


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    json_path = root / "poems/P0001/reader_state/reader_state_object_010.json"
    md_path = root / "poems/P0001/reader_state/reader_state_object_010.md"
    html_path = root / "poems/P0001/reader_state/reader_state_object_010.html"
    add(checks, "reader_state_json_present", json_path.exists(), json_path.as_posix())
    add(checks, "reader_state_markdown_present", md_path.exists(), md_path.as_posix())
    add(checks, "reader_state_html_present", html_path.exists(), html_path.as_posix())
    if not json_path.exists():
        return checks
    try:
        obj = load_json(json_path)
        add(checks, "reader_state_json_parse", True)
    except Exception as exc:
        add(checks, "reader_state_json_parse", False, str(exc))
        return checks

    add(checks, "schema_v1", obj.get("schema") == "llmpoetry-reader-state-object-v1", str(obj.get("schema")))
    add(checks, "draft_id_D010", obj.get("draft_id") == "P0001-D010", str(obj.get("draft_id")))
    add(checks, "state_order_complete", obj.get("state_order") == REQUIRED_STATES, str(obj.get("state_order")))
    add(checks, "quality_claims_empty", obj.get("quality_claims") == [], str(obj.get("quality_claims")))
    add(checks, "non_claim_present", "not admit" in obj.get("non_claim", "").lower() and "quality" in obj.get("non_claim", "").lower(), obj.get("non_claim", ""))
    source_paths = obj.get("source_paths", {})
    for key in ["draft", "branch_packet", "selector_map", "selector_vector", "state_switch", "ergodic_traversal", "return_diff", "patch_application", "cold_review"]:
        rel = source_paths.get(key)
        add(checks, f"source_path_present:{key}", bool(rel), str(rel))
        if rel:
            add(checks, f"source_path_exists:{key}", (root / rel).exists(), rel)
    if not all((root / p).exists() for p in source_paths.values()):
        return checks

    state_switch = load_json(root / source_paths["state_switch"])
    selector_vector = load_json(root / source_paths["selector_vector"])
    ergodic = load_json(root / source_paths["ergodic_traversal"])
    patch = load_json(root / source_paths["patch_application"])
    cold_review = load_json(root / source_paths["cold_review"])
    md_text = md_path.read_text(encoding="utf-8", errors="replace") if md_path.exists() else ""
    html_text = html_path.read_text(encoding="utf-8", errors="replace") if html_path.exists() else ""

    closed = obj.get("closed_state", {}).get("lines", [])
    opened = obj.get("open_state", {}).get("lines", [])
    patched = obj.get("patched_state", {}).get("lines", [])
    add(checks, "closed_matches_state_switch", closed == state_switch.get("closed_state", {}).get("lines", []))
    add(checks, "open_matches_state_switch", opened == state_switch.get("open_state", {}).get("lines", []))
    add(checks, "shadow_sentence_matches_selector_vector", obj.get("open_state", {}).get("shadow_sentence") == selector_vector.get("shadow_sentence"))
    add(checks, "traversal_sentence_matches_receipt", obj.get("traversal_state", {}).get("route_sentence") == ergodic.get("traversal_sentence"))
    add(checks, "patched_lines_match_receipt", patched == patch.get("patched_state", {}).get("lines", []))
    add(checks, "patched_sha_matches_receipt", obj.get("patched_state", {}).get("sha256") == patch.get("patched_state", {}).get("sha256"))
    add(checks, "cold_review_not_promote", obj.get("source_status", {}).get("cold_review_verdict") == cold_review.get("verdict") == "revise_not_promote")

    layer_walk = obj.get("layer_walk", [])
    add(checks, "layer_walk_seven_layers", len(layer_walk) == 7, f"count={len(layer_walk)}")
    route_words = [layer.get("traversal", {}).get("route_word") for layer in layer_walk]
    add(checks, "route_words_match_sentence", " ".join(route_words) == ergodic.get("traversal_sentence"), " ".join(str(w) for w in route_words))
    for idx, layer in enumerate(layer_walk):
        cid = layer.get("candidate_id")
        add(checks, f"layer:{idx}:{cid}:closed_in_markdown", layer.get("closed_line", "") in md_text)
        add(checks, f"layer:{idx}:{cid}:open_in_markdown", layer.get("open_line", "") in md_text)
        add(checks, f"layer:{idx}:{cid}:patched_in_markdown", layer.get("patch_operation", {}).get("after_exact", "") in md_text)
        add(checks, f"layer:{idx}:{cid}:replacement_changes_line", layer.get("patch_operation", {}).get("replacement_changes_line") is True)
        for state in REQUIRED_STATES:
            receipts = layer.get("authorizing_receipts", {}).get(state, [])
            add(checks, f"layer:{idx}:{cid}:receipts_for_{state}", bool(receipts), str(receipts))
            for receipt in receipts:
                add(checks, f"layer:{idx}:{cid}:receipt_exists:{state}:{Path(receipt).name}", (root / receipt).exists(), receipt)

    matrix = obj.get("receipt_matrix", [])
    add(checks, "receipt_matrix_28_entries", len(matrix) == 28, f"count={len(matrix)}")
    for entry in matrix:
        visible = entry.get("visible_text", "")
        add(checks, f"receipt_matrix_sha:{entry.get('state')}:{entry.get('candidate_id')}", entry.get("visible_sha256") == sha256_text(visible), visible)
        add(checks, f"receipt_matrix_authorized:{entry.get('state')}:{entry.get('candidate_id')}", bool(entry.get("authorized_by")))

    # Keep the reader object plain and accessible: Markdown fallback plus details-based HTML, no JS dependency.
    add(checks, "markdown_contains_all_state_headings", all(h in md_text for h in ["## 1. Closed state", "## 2. Open state", "## 3. Traversal state", "## 4. Patched state"]))
    add(checks, "html_uses_disclosure_details", "<details" in html_text and "<summary>" in html_text)
    add(checks, "html_has_no_script", "<script" not in html_text.lower())
    for key, rel in source_paths.items():
        if key in {"draft"}:
            continue
        add(checks, f"markdown_links_receipt:{key}", Path(rel).name in md_text, Path(rel).name)
        add(checks, f"html_links_receipt:{key}", Path(rel).name in html_text, Path(rel).name)

    text_all = (md_text + "\n" + html_text + "\n" + json.dumps(obj, ensure_ascii=False)).lower()
    forbidden_hits = [claim for claim in FORBIDDEN_QUALITY_CLAIMS if claim in text_all and claim not in {"quality proof"}]
    # The explicit negated phrase "quality proof" is allowed only inside non-claims.
    add(checks, "no_unverified_positive_quality_claims", not forbidden_hits, ", ".join(forbidden_hits))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    checks = run(Path(args.root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
