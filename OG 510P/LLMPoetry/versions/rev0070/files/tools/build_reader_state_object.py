#!/usr/bin/env python3
"""Build a reader-facing state object for P0001-D010.

The object is deliberately derived from existing receipts. It makes the closed,
open, traversal, and patched states readable without asking the reader to inspect
seven separate JSON files first.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def md_link(label: str, path: str) -> str:
    return f"[`{label}`](../../{path.split('poems/P0001/', 1)[-1] if path.startswith('poems/P0001/') else path})" if path.startswith("poems/P0001/") else f"[`{label}`]({path})"


def local_href(from_dir: str, target: str) -> str:
    # All outputs are written under poems/P0001/reader_state/.
    if target.startswith("poems/P0001/"):
        return "../" + target.split("poems/P0001/", 1)[1]
    return "../../" + target


def extract_input_paths(packet: dict) -> dict:
    return {
        "draft": packet["draft_path"],
        "branch_packet": "poems/P0001/branches/branch_packet_010.json",
        "selector_map": packet["selector_map_path"],
        "selector_vector": packet["selector_vector_path"],
        "loss_budget": packet["loss_budget_path"],
        "state_switch": packet["state_switch_path"],
        "ergodic_traversal": packet["ergodic_traversal_path"],
        "return_diff": packet["return_diff_path"],
        "patch_application": packet["patch_application_path"],
        "cold_review": "poems/P0001/judgments/cold_review_010_on_D010.json",
    }


def build(root: Path, *, revision: str, turn: int, timestamp: str) -> dict:
    packet_path = root / "poems/P0001/branches/branch_packet_010.json"
    packet = load_json(packet_path)
    paths = extract_input_paths(packet)
    state_switch = load_json(root / paths["state_switch"])
    selector_map = load_json(root / paths["selector_map"])
    selector_vector = load_json(root / paths["selector_vector"])
    ergodic = load_json(root / paths["ergodic_traversal"])
    patch = load_json(root / paths["patch_application"])
    return_diff = load_json(root / paths["return_diff"])
    cold_review = load_json(root / paths["cold_review"])

    selector_by_cid = {s["candidate_id"]: s for s in selector_map.get("selectors", [])}
    vector_by_cid = {v["candidate_id"]: v for v in selector_vector.get("vector", [])}
    traversal_by_cid = {t["selected_candidate_id"]: t for t in ergodic.get("transitions", [])}
    operations_by_cid = {o["candidate_id"]: o for o in patch.get("operations", [])}

    layers = []
    for transition in state_switch.get("transitions", []):
        cid = transition["candidate_id"]
        selector = selector_by_cid.get(cid, {})
        vector = vector_by_cid.get(cid, {})
        route = traversal_by_cid.get(cid, {})
        op = operations_by_cid.get(cid, {})
        layers.append(
            {
                "index": transition["index"],
                "layer_id": cid[0],
                "candidate_id": cid,
                "closed_line": transition["closed_exact"],
                "open_line": transition["open_exact"],
                "shadow_phrase": transition["shadow_phrase"],
                "selector": {
                    "source": selector.get("source"),
                    "exact": selector.get("exact"),
                    "start": selector.get("start"),
                    "end": selector.get("end"),
                    "prefix": selector.get("prefix"),
                    "suffix": selector.get("suffix"),
                    "model": selector.get("selector_type"),
                },
                "shadow_slice": vector.get("shadow_slice", {}),
                "traversal": {
                    "selected_final_word": route.get("selected_final_word"),
                    "selected_final_word_length": route.get("selected_final_word_length"),
                    "omitted_candidate_count": route.get("omitted_candidate_count"),
                    "route_index": route.get("route_index"),
                    "chosen_candidate_id": route.get("chosen_candidate_id"),
                    "chosen_exact": route.get("chosen_exact"),
                    "route_word": route.get("route_word"),
                    "selector_code": route.get("selector_code"),
                },
                "patch_operation": {
                    "find": op.get("find"),
                    "replace": op.get("replace"),
                    "route_word": op.get("route_word"),
                    "before_exact": op.get("before_exact"),
                    "after_exact": op.get("after_exact"),
                    "replacement_changes_line": op.get("replacement_changes_line"),
                },
                "authorizing_receipts": {
                    "closed": [paths["branch_packet"], paths["selector_map"], paths["state_switch"]],
                    "open": [paths["state_switch"], paths["selector_vector"], paths["branch_packet"]],
                    "traversal": [paths["ergodic_traversal"], paths["branch_packet"]],
                    "patched": [paths["patch_application"], paths["ergodic_traversal"]],
                },
            }
        )

    patched_lines = patch.get("patched_state", {}).get("lines", [])
    closed_lines = state_switch.get("closed_state", {}).get("lines", [])
    open_lines = state_switch.get("open_state", {}).get("lines", [])
    route_sentence = ergodic.get("traversal_sentence")
    shadow_sentence = selector_vector.get("shadow_sentence")

    receipt_matrix = []
    for layer in layers:
        for state_name, visible in [
            ("closed", layer["closed_line"]),
            ("open", layer["open_line"]),
            ("traversal", f"{layer['traversal']['chosen_exact']} -> {layer['traversal']['route_word']}"),
            ("patched", layer["patch_operation"]["after_exact"]),
        ]:
            receipt_matrix.append(
                {
                    "state": state_name,
                    "candidate_id": layer["candidate_id"],
                    "visible_text": visible,
                    "visible_sha256": sha256_text(visible or ""),
                    "authorized_by": layer["authorizing_receipts"][state_name],
                }
            )

    input_hashes = {name: sha256_file(root / p) for name, p in paths.items() if (root / p).exists()}

    obj = {
        "schema": "llmpoetry-reader-state-object-v1",
        "object_id": "RSO-P0001-D010-001",
        "poem_id": "P0001",
        "draft_id": "P0001-D010",
        "revision": revision,
        "turn": turn,
        "built_at": timestamp,
        "title": "P0001-D010 reader-facing state object — Applied Patch / PATCHED",
        "status": "reader_state_built_from_receipts; source draft remains cold_reviewed_revise_not_promote",
        "source_paths": paths,
        "state_order": ["closed", "open", "traversal", "patched"],
        "source_status": {
            "cold_review_verdict": cold_review.get("verdict"),
            "return_diff_instruction_fulfilled": return_diff.get("previous_instruction_fulfilled"),
            "patch_application_verified": patch.get("operation_count_matches_selected_lines") is True
            and patch.get("draft_contains_patched_lines") is True,
        },
        "reader_warnings": [
            "This object is a readability layer over D010 receipts, not a new poem draft and not a promotion.",
            "The cold review remains revise_not_promote; no external reader validation has occurred.",
            "Receipts verify local construction only: selection, opening, traversal, and patch application.",
        ],
        "reader_summary": {
            "closed_surface_claim": "Seven selected lines spell PATCHED by initial letter.",
            "open_surface_claim": "Each selected line opens into a three-word loss phrase from omitted branch endings.",
            "traversal_claim": f"Selected final-word lengths route through omitted candidates to recover: {route_sentence}.",
            "patched_surface_claim": "The traversal words become seven concrete replacements against the closed surface.",
            "risk_read": "The operation is now visible to a reader; the remaining risk is aesthetic sameness and lack of external material pressure.",
        },
        "closed_state": {"lines": closed_lines, "sha256": sha256_text("\n".join(closed_lines))},
        "open_state": {"lines": open_lines, "shadow_sentence": shadow_sentence, "sha256": sha256_text("\n".join(open_lines))},
        "traversal_state": {
            "rule": ergodic.get("traversal_rule"),
            "route_algorithm": ergodic.get("route_algorithm"),
            "route_sentence": route_sentence,
            "transitions": [layer["traversal"] | {"candidate_id": layer["candidate_id"]} for layer in layers],
            "sha256": sha256_text(route_sentence or ""),
        },
        "patched_state": {
            "rule": patch.get("patch_rule"),
            "operations": [layer["patch_operation"] | {"candidate_id": layer["candidate_id"]} for layer in layers],
            "lines": patched_lines,
            "sha256": patch.get("patched_state", {}).get("sha256"),
        },
        "layer_walk": layers,
        "receipt_matrix": receipt_matrix,
        "quality_claims": [],
        "non_claim": "This reader-state object makes D010's state transitions readable. It verifies no literary quality claim and does not admit the poem.",
        "input_hashes": input_hashes,
    }
    return obj


def render_markdown(obj: dict) -> str:
    paths = obj["source_paths"]
    lines = []
    lines.append(f"# {obj['title']}")
    lines.append("")
    lines.append(f"Built: `{obj['built_at']}` / `{obj['revision']}` / turn `{obj['turn']}`")
    lines.append("")
    lines.append("## Status before reading")
    lines.append("")
    lines.append("D010 remains **cold-reviewed `revise_not_promote`**. This file is not D011 and not an admission. It is the missing reader-facing surface promised by the form notes: one place where the closed, open, traversal, and patched states can be read without spelunking seven receipts first.")
    lines.append("")
    lines.append("Core receipts: " + ", ".join(f"[`{k}`]({local_href('reader_state', v)})" for k, v in paths.items() if k in ["branch_packet", "selector_map", "selector_vector", "loss_budget", "state_switch", "ergodic_traversal", "return_diff", "patch_application", "cold_review"]))
    lines.append("")
    lines.append("## How to read the object")
    lines.append("")
    lines.append("Read downward. Each line is the same selected layer passing through four visible states: closed line, opened loss phrase, traversal route, and patched line. The poem's machine act is not hidden in a footnote; it is the transition itself.")
    lines.append("")
    lines.append("## 1. Closed state")
    lines.append("")
    for line in obj["closed_state"]["lines"]:
        lines.append(line)
    lines.append("")
    lines.append("## 2. Open state")
    lines.append("")
    for line in obj["open_state"]["lines"]:
        lines.append(line)
    lines.append("")
    lines.append("Shadow sentence: `" + obj["open_state"].get("shadow_sentence", "") + "`")
    lines.append("")
    lines.append("## 3. Traversal state")
    lines.append("")
    lines.append("Rule: final selected word length modulo three omitted candidates chooses one omitted candidate from the same layer.")
    lines.append("")
    lines.append("| Layer | Closed final word | Route | Omitted candidate | Route word |")
    lines.append("|---|---:|---|---|---|")
    for layer in obj["layer_walk"]:
        t = layer["traversal"]
        lines.append(
            f"| {layer['candidate_id']} | {t['selected_final_word']} | `{t['selector_code']}` → index `{t['route_index']}` | {t['chosen_exact']} | **{t['route_word']}** |"
        )
    lines.append("")
    lines.append("Traversal sentence: **" + obj["traversal_state"].get("route_sentence", "") + "**")
    lines.append("")
    lines.append("## 4. Patched state")
    lines.append("")
    lines.append("| Layer | Replacement | Patched line |")
    lines.append("|---|---|---|")
    for layer in obj["layer_walk"]:
        op = layer["patch_operation"]
        lines.append(f"| {layer['candidate_id']} | `{op['find']}` → **{op['replace']}** | {op['after_exact']} |")
    lines.append("")
    lines.append("Patched surface:")
    lines.append("")
    for line in obj["patched_state"]["lines"]:
        lines.append(line)
    lines.append("")
    lines.append("## One-line layer walk")
    lines.append("")
    lines.append("| Layer | Closed | Open addition | Traversal | Patch |")
    lines.append("|---|---|---|---|---|")
    for layer in obj["layer_walk"]:
        t = layer["traversal"]
        op = layer["patch_operation"]
        lines.append(
            f"| {layer['candidate_id']} | {layer['closed_line']} | ⇢ {layer['shadow_phrase']} | {t['chosen_candidate_id']} → **{t['route_word']}** | `{op['find']}` → `{op['replace']}` |"
        )
    lines.append("")
    lines.append("## Receipt matrix")
    lines.append("")
    lines.append("Every visible transition above is authorized by local receipts. These links are bookkeeping evidence only.")
    lines.append("")
    lines.append("| State | Authorizing receipts |")
    lines.append("|---|---|")
    state_to_receipts = {
        "closed": [paths["branch_packet"], paths["selector_map"], paths["state_switch"]],
        "open": [paths["state_switch"], paths["selector_vector"], paths["branch_packet"]],
        "traversal": [paths["ergodic_traversal"], paths["branch_packet"]],
        "patched": [paths["patch_application"], paths["ergodic_traversal"]],
    }
    for state, receipts in state_to_receipts.items():
        links = ", ".join(f"[`{Path(p).name}`]({local_href('reader_state', p)})" for p in receipts)
        lines.append(f"| {state} | {links} |")
    lines.append("")
    lines.append("## Risk read")
    lines.append("")
    lines.append("The earlier risk was that `patch` stayed a procedural promise. This object corrects that surface risk by showing the route words becoming replacements. The larger risk remains: the diction still leans on a narrow codework fog. If this readable state object is still inert to a human reader, the next honest move is not another receipt layer; it is freezing P0001 as a laboratory failure or forking P0002 under external material pressure.")
    lines.append("")
    lines.append("## Machine-readable non-claim")
    lines.append("")
    lines.append(obj["non_claim"])
    return "\n".join(lines) + "\n"


def render_html(obj: dict) -> str:
    paths = obj["source_paths"]
    def e(s: object) -> str:
        return html.escape(str(s))
    def receipt_link(p: str) -> str:
        return f'<a href="{e(local_href("reader_state", p))}">{e(Path(p).name)}</a>'
    body = []
    body.append(f"<h1>{e(obj['title'])}</h1>")
    body.append(f"<p><strong>Status:</strong> D010 remains <code>revise_not_promote</code>. This is a reader surface, not D011 and not a promotion.</p>")
    body.append("<p>Read the four disclosure panels in order: closed, open, traversal, patched.</p>")
    for state, label in [("closed", "1. Closed state"), ("open", "2. Open state")]:
        key = f"{state}_state"
        body.append(f"<details open><summary>{e(label)}</summary><pre>{e(chr(10).join(obj[key]['lines']))}</pre></details>")
    rows = []
    for layer in obj["layer_walk"]:
        t = layer["traversal"]
        rows.append(f"<tr><td>{e(layer['candidate_id'])}</td><td>{e(t['selected_final_word'])}</td><td><code>{e(t['selector_code'])}</code> → {e(t['route_index'])}</td><td>{e(t['chosen_exact'])}</td><td><strong>{e(t['route_word'])}</strong></td></tr>")
    body.append("<details open><summary>3. Traversal state</summary><table><thead><tr><th>Layer</th><th>Closed final word</th><th>Route</th><th>Omitted candidate</th><th>Route word</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table><p><strong>Traversal sentence:</strong> " + e(obj['traversal_state']['route_sentence']) + "</p></details>")
    rows = []
    for layer in obj["layer_walk"]:
        op = layer["patch_operation"]
        rows.append(f"<tr><td>{e(layer['candidate_id'])}</td><td><code>{e(op['find'])}</code> → <strong>{e(op['replace'])}</strong></td><td>{e(op['after_exact'])}</td></tr>")
    body.append("<details open><summary>4. Patched state</summary><table><thead><tr><th>Layer</th><th>Replacement</th><th>Patched line</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table><pre>" + e(chr(10).join(obj['patched_state']['lines'])) + "</pre></details>")
    receipts = {
        "closed": [paths["branch_packet"], paths["selector_map"], paths["state_switch"]],
        "open": [paths["state_switch"], paths["selector_vector"], paths["branch_packet"]],
        "traversal": [paths["ergodic_traversal"], paths["branch_packet"]],
        "patched": [paths["patch_application"], paths["ergodic_traversal"]],
        "loss budget": [paths["loss_budget"]],
        "return diff": [paths["return_diff"]],
        "cold review": [paths["cold_review"]],
    }
    rows = [f"<tr><td>{e(k)}</td><td>{', '.join(receipt_link(p) for p in v)}</td></tr>" for k, v in receipts.items()]
    body.append("<h2>Receipt matrix</h2><table><thead><tr><th>Visible state</th><th>Receipts</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>")
    body.append("<h2>Risk read</h2><p>The surface risk has moved from hidden mechanism to visible operation. The unresolved risk is aesthetic sameness and lack of external material pressure.</p>")
    body.append(f"<p><strong>Non-claim:</strong> {e(obj['non_claim'])}</p>")
    css = "body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.45;max-width:980px;margin:2rem auto;padding:0 1rem}pre{white-space:pre-wrap;background:#f6f6f6;padding:1rem}table{border-collapse:collapse;width:100%;margin:1rem 0}td,th{border:1px solid #bbb;padding:.4rem;vertical-align:top}summary{font-size:1.2rem;font-weight:700;cursor:pointer;margin:.8rem 0}code{font-size:.95em}"
    return "<!doctype html>\n<html lang=\"en\"><meta charset=\"utf-8\"><title>" + e(obj["title"]) + "</title><style>" + css + "</style><body>" + "\n".join(body) + "</body></html>\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--revision", required=True)
    parser.add_argument("--turn", type=int, required=True)
    parser.add_argument("--timestamp", default=None)
    parser.add_argument("--json-out", default="poems/P0001/reader_state/reader_state_object_010.json")
    parser.add_argument("--md-out", default="poems/P0001/reader_state/reader_state_object_010.md")
    parser.add_argument("--html-out", default="poems/P0001/reader_state/reader_state_object_010.html")
    args = parser.parse_args()
    root = Path(args.root)
    timestamp = args.timestamp or datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")
    obj = build(root, revision=args.revision, turn=args.turn, timestamp=timestamp)
    for target, text in [
        (Path(args.json_out), json.dumps(obj, indent=2, ensure_ascii=False) + "\n"),
        (Path(args.md_out), render_markdown(obj)),
        (Path(args.html_out), render_html(obj)),
    ]:
        path = root / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps({"ok": True, "json": args.json_out, "markdown": args.md_out, "html": args.html_out}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
