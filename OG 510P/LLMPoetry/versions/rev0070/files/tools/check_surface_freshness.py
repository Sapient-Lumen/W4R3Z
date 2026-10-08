#!/usr/bin/env python3
"""Validate current navigation surfaces without assuming a permanent poem family."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HEAD_RE = re.compile(r"^(P\d{4})-D(\d{3})$")


def add(checks: list[dict], name: str, ok: bool, detail: object = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    proof = load_json(root / "registries/proof_status.json")
    rev = state.get("revision")
    artifact = state.get("artifact")
    updated_at = state.get("updated_at") or state.get("timestamp")
    head = state.get("current_head") or surface.get("current_head")
    draft = state.get("current_draft")
    packet = state.get("current_packet")
    metrics = state.get("metrics_path")
    m = HEAD_RE.match(str(head or ""))
    add(checks, "current_head_present_and_shaped", m is not None, head)
    if not m:
        return checks
    poem_id, suffix = m.groups()
    poem_index_path = f"poems/{poem_id}/INDEX.json"
    expected_metrics = f"poems/{poem_id}/verification/metrics_draft_{suffix}.json"

    add(checks, "surface_revision_matches_state", surface.get("revision") == rev, surface.get("revision"))
    add(checks, "surface_head_matches_state", surface.get("current_head") == head, surface.get("current_head"))
    add(checks, "proof_revision_matches_state", proof.get("revision") == rev, proof.get("revision"))
    add(checks, "proof_head_matches_state", proof.get("current_head") == head and proof.get("current_draft") == head and proof.get("latest_draft") == head, f"{proof.get('current_head')} {proof.get('current_draft')}")
    for key in ("status", "current_status", "current_poem_status", "latest_poem_status", "current_summary", "poem_status_summary", "current_poem_summary", "note", "non_claim", "next_action"):
        if proof.get(key) is not None:
            add(checks, f"proof_prose_mentions_head:{key}", head in str(proof.get(key)), str(proof.get(key))[:180])

    root_current_files = [
        "START_HERE.md", "README.md", "AGENTS.md", "CONTEXT_PACK.md", "CONTEXT_PACK.json",
        "LLM_BROWSE_INDEX.json", "COMPACT_SURFACE_BUNDLE.json", "REENTRY_CONTRACT.json",
        "REPLAY_CAPSULE.json", "FRONTIER_TICKET.json", "SURFACE_STATUS.json", "DATA_CARD.json",
        "ARCHIVE_INDEX.md", "ARCHIVE_INDEX.json", "docs/00-office/BOOT_CARD.md",
        "registries/poem_index.json", "registries/proof_status.json", "registries/pilot_queue.json",
        "registries/style_firewall.json", "VALIDATION_INDEX.json", poem_index_path,
    ]
    for rel in dict.fromkeys(root_current_files):
        p = root / rel
        add(checks, f"current_surface_exists:{rel}", p.exists(), rel)
        if p.exists():
            raw = p.read_text(encoding="utf-8", errors="ignore")
            add(checks, f"current_surface_mentions_revision:{rel}", rev in raw, rev)
            add(checks, f"current_surface_mentions_head:{rel}", head in raw, head)

    surfaces = surface.get("surfaces", {})
    add(checks, "surface_status_has_surfaces", isinstance(surfaces, dict) and bool(surfaces), len(surfaces) if isinstance(surfaces, dict) else "NA")

    # A later-turn candidate review may freeze exact creation-time bytes while the
    # cube continues to a newer routing revision.  Do not force immutable poem,
    # packet, metric, or artifact files to lie about their creation revision merely
    # because a current_* pointer names them.  Instead, require their hashes to match
    # the current candidate wrapper; mutable routing/wrapper surfaces must still name
    # the current revision.
    frozen_hashes: dict[str, str] = {}
    posture = state.get("current_posture") if isinstance(state.get("current_posture"), dict) else {}
    candidate_rel = state.get("candidate_packet") or posture.get("current_status_wrapper")
    candidate = None
    if posture.get("lineage_frozen") is True and isinstance(candidate_rel, str) and (root / candidate_rel).exists():
        try:
            candidate = load_json(root / candidate_rel)
        except Exception:
            candidate = None
    if isinstance(candidate, dict):
        for rel_key, hash_key in (
            ("draft_path", "draft_sha256"),
            ("source_material_packet", "source_material_packet_sha256"),
            ("metrics_path", "metrics_sha256"),
        ):
            rel_value, hash_value = candidate.get(rel_key), candidate.get(hash_key)
            if isinstance(rel_value, str) and isinstance(hash_value, str):
                frozen_hashes[rel_value] = hash_value
        artifact_obj = candidate.get("artifact") if isinstance(candidate.get("artifact"), dict) else {}
        for rel_key, hash_key in (
            ("spec", "spec_sha256"), ("database", "database_sha256"),
            ("wal", "wal_sha256"), ("receipt", "receipt_sha256"),
            ("base_surface", "base_surface_sha256"),
            ("committed_surface", "committed_surface_sha256"),
            ("index", "index_sha256"), ("oci_layout", "oci_layout_sha256"),
            ("lower_surface", "lower_surface_sha256"),
            ("upper_surface", "upper_surface_sha256"),
            ("merged_surface", "merged_surface_sha256"),
        ):
            rel_value, hash_value = artifact_obj.get(rel_key), artifact_obj.get(hash_key)
            if isinstance(rel_value, str) and isinstance(hash_value, str):
                frozen_hashes[rel_value] = hash_value
        # Artifact families may expose a complete file inventory instead of a
        # fixed schema.  Treat each path/hash pair as an immutable surface
        # contract; this supports OCI layouts without teaching the validator
        # every future artifact-specific field name.
        for item in artifact_obj.get("file_inventory", []) if isinstance(artifact_obj.get("file_inventory"), list) else []:
            if not isinstance(item, dict):
                continue
            rel_value, hash_value = item.get("path"), item.get("sha256")
            if isinstance(rel_value, str) and isinstance(hash_value, str):
                frozen_hashes[rel_value] = hash_value
    add(checks, "frozen_current_candidate_wrapper_present", not posture.get("lineage_frozen") or isinstance(candidate, dict), candidate_rel)
    add(checks, "frozen_current_candidate_wrapper_revision", not isinstance(candidate, dict) or candidate.get("revision") == rev, candidate.get("revision") if isinstance(candidate, dict) else None)
    declared_frozen = state.get("frozen_current_surfaces") if isinstance(state.get("frozen_current_surfaces"), list) else []
    add(checks, "frozen_current_surfaces_have_hash_contract", not declared_frozen or all(rel in frozen_hashes for rel in declared_frozen), [rel for rel in declared_frozen if rel not in frozen_hashes])

    for key, rel in surfaces.items():
        if not isinstance(rel, str):
            continue
        p = root / rel
        add(checks, f"surface_map_exists:{key}", p.exists(), rel)
        if not p.exists() or not key.startswith("current_"):
            continue
        if rel in frozen_hashes:
            add(checks, f"active_frozen_surface_hash:{key}", sha256_file(p) == frozen_hashes[rel], rel)
            # The current candidate wrapper binds an immutable creation-time
            # component to the current head.  Requiring every low-level text or
            # JSON component to repeat a later routing revision/head would force
            # false provenance or mutate the artifact being frozen.
            add(
                checks,
                f"active_frozen_surface_wrapper_binds_head:{key}",
                isinstance(candidate, dict) and candidate.get("draft_id") == head,
                candidate.get("draft_id") if isinstance(candidate, dict) else None,
            )
        elif p.suffix.lower() in {".md", ".json", ".html", ".txt"}:
            raw = p.read_text(encoding="utf-8", errors="ignore")
            add(checks, f"active_surface_mentions_revision:{key}", rev in raw, rel)
            add(checks, f"active_surface_mentions_head:{key}", head in raw, rel)

    poem_index = load_json(root / "registries/poem_index.json")
    heads = [p.get("current_head") for p in poem_index.get("poems", []) if isinstance(p, dict)]
    global_rows = [p for p in poem_index.get("poems", []) if isinstance(p, dict) and p.get("global_current_head") is True]
    add(checks, "poem_index_contains_current_head", head in heads, heads)
    add(checks, "poem_index_one_global_current_head", len(global_rows) == 1, [p.get("poem_id") for p in global_rows])
    add(checks, "poem_index_global_current_head_matches_state", len(global_rows) == 1 and global_rows[0].get("current_head") == head, global_rows[0] if global_rows else None)
    add(checks, "artifact_filename_law", bool(artifact and artifact.startswith(f"LLMPoetry-{rev}-") and artifact.endswith(".zip")), artifact)
    for key in ("status", "next_action", "recommended_next_action", "non_claim"):
        if state.get(key) is not None:
            add(checks, f"state_prose_mentions_head:{key}", head in str(state.get(key)), str(state.get(key))[:180])
    for key in ("open_debts", "next_honest_actions"):
        vals = state.get(key)
        if isinstance(vals, list):
            add(checks, f"state_list_mentions_head:{key}", head in " | ".join(str(v) for v in vals), vals)
    for key in ("current_draft_id", "latest_draft_id"):
        if state.get(key) is not None:
            add(checks, f"state_id_current:{key}", state.get(key) == head, state.get(key))
    for key in ("current_draft", "latest_draft"):
        if state.get(key) is not None:
            add(checks, f"state_draft_current:{key}", state.get(key) == draft, state.get(key))
    for key in ("current_packet", "current_material_packet", "source_material_packet", "external_material_packet"):
        if state.get(key) is not None:
            add(checks, f"state_packet_current:{key}", state.get(key) == packet, state.get(key))
    add(checks, "state_metrics_current", metrics == expected_metrics, metrics)

    add(checks, "surface_updated_at_matches_state", surface.get("updated_at") == updated_at, surface.get("updated_at"))
    for key in ("status", "non_claim", "next_action"):
        add(checks, f"surface_prose_mentions_head:{key}", head in str(surface.get(key, "")), str(surface.get(key, ""))[:180])
    posture = state.get("current_posture") if isinstance(state.get("current_posture"), dict) else {}
    if posture.get("previous_head"):
        add(checks, "surface_previous_head_matches_state", surface.get("previous_head") == posture.get("previous_head"), surface.get("previous_head"))
    if posture.get("previous_head_review"):
        add(checks, "surface_previous_review_matches_state", surface.get("previous_head_review") == posture.get("previous_head_review"), surface.get("previous_head_review"))

    compact_json_files = [
        "COMPACT_SURFACE_BUNDLE.json", "CONTEXT_PACK.json", "LLM_BROWSE_INDEX.json",
        "FRONTIER_TICKET.json", "REENTRY_CONTRACT.json", "REPLAY_CAPSULE.json",
        "DATA_CARD.json", "ARCHIVE_INDEX.json", poem_index_path,
    ]
    for rel in compact_json_files:
        p = root / rel
        if not p.exists():
            continue
        obj = load_json(p)
        add(checks, f"compact_revision:{rel}", obj.get("revision") == rev, obj.get("revision"))
        if obj.get("artifact") is not None:
            add(checks, f"compact_artifact:{rel}", obj.get("artifact") == artifact, obj.get("artifact"))
        if obj.get("current_head") is not None:
            add(checks, f"compact_head:{rel}", obj.get("current_head") == head, obj.get("current_head"))
        if obj.get("current_draft") is not None:
            add(checks, f"compact_draft:{rel}", obj.get("current_draft") == draft, obj.get("current_draft"))
        if obj.get("current_packet") is not None:
            add(checks, f"compact_packet:{rel}", obj.get("current_packet") == packet, obj.get("current_packet"))
        if isinstance(obj.get("read_first"), list):
            add(checks, f"compact_read_first_current:{rel}", obj["read_first"] == state.get("read_first"), obj["read_first"][:10])
        if isinstance(obj.get("must_read"), list):
            add(checks, f"compact_must_read_current:{rel}", obj["must_read"] == state.get("read_first"), obj["must_read"][:10])
            add(checks, f"compact_must_read_paths_exist:{rel}", all((root / item).exists() for item in obj["must_read"]), [item for item in obj["must_read"] if not (root / item).exists()])
        if obj.get("web_pulse") is not None:
            add(checks, f"compact_web_pulse:{rel}", obj.get("web_pulse") == state.get("web_pulse"), obj.get("web_pulse"))
        if rel == "LLM_BROWSE_INDEX.json":
            add(checks, "compact_llm_browse_current_risk_mentions_head", head in str(obj.get("current_risk", "")), obj.get("current_risk"))
        if rel == "REPLAY_CAPSULE.json":
            add(checks, "compact_replay_note_mentions_head", head in str(obj.get("replay_note", "")), obj.get("replay_note"))
        smap = obj.get("surfaces") if isinstance(obj.get("surfaces"), dict) else {}
        if smap.get("current_draft") is not None:
            add(checks, f"compact_surface_draft:{rel}", smap.get("current_draft") == draft, smap.get("current_draft"))
        if smap.get("current_packet") is not None:
            add(checks, f"compact_surface_packet:{rel}", smap.get("current_packet") == packet, smap.get("current_packet"))

    pilot = load_json(root / "registries/pilot_queue.json")
    for key in ("status", "current_summary", "note", "default_for_p0002"):
        if pilot.get(key) is not None:
            add(checks, f"pilot_top_mentions_head:{key}", head in str(pilot.get(key)), str(pilot.get(key))[:180])

    structured = [
        "registries/poem_index.json", poem_index_path, f"poems/{poem_id}/metadata.json",
        "registries/source_registry.json", "registries/source_health.json", "registries/source_receipts.json",
        "registries/source_snapshot_registry.json", "registries/form_registry.json", "registries/open_questions.json",
        "registries/research_entropy_ledger.json", "registries/research_pulse_index.json",
        "registries/pilot_registry.json", "registries/pilot_queue.json", "registries/draft_index.json",
        "registries/proof_status.json",
    ]
    current_title = ""
    for line in (root / draft).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("# "):
            current_title = line[2:].strip()
            break
    for rel in dict.fromkeys(structured):
        obj = load_json(root / rel)
        if obj.get("revision") is not None:
            add(checks, f"structured_revision:{rel}", obj.get("revision") == rev, obj.get("revision"))
        if obj.get("current_head") is not None:
            add(checks, f"structured_head:{rel}", obj.get("current_head") == head, obj.get("current_head"))
        if obj.get("updated_at") is not None:
            add(checks, f"structured_time:{rel}", obj.get("updated_at") == updated_at, obj.get("updated_at"))
        for key in ("current_draft", "latest_draft", "current_draft_path", "latest_draft_path"):
            if obj.get(key) is not None and str(obj.get(key)).endswith(".md"):
                add(checks, f"structured_draft:{rel}:{key}", obj.get(key) == draft, obj.get(key))
        for key in ("current_packet", "current_material_packet", "external_material_packet", "source_material_packet"):
            if obj.get(key) is not None:
                add(checks, f"structured_packet:{rel}:{key}", obj.get(key) == packet, obj.get(key))
        for key in ("current_draft_id", "latest_draft_id"):
            if obj.get(key) is not None:
                add(checks, f"structured_id:{rel}:{key}", obj.get(key) == head, obj.get(key))
        if obj.get("current_title") is not None:
            add(checks, f"structured_title:{rel}", obj.get("current_title") == current_title, obj.get("current_title"))
        smap = obj.get("surfaces") if isinstance(obj.get("surfaces"), dict) else {}
        if smap.get("current_draft") is not None:
            add(checks, f"structured_surface_draft:{rel}", smap.get("current_draft") == draft, smap.get("current_draft"))
        if smap.get("current_packet") is not None:
            add(checks, f"structured_surface_packet:{rel}", smap.get("current_packet") == packet, smap.get("current_packet"))

    stale_labels = []
    for item in state.get("anthology_top_5", []) if isinstance(state.get("anthology_top_5"), list) else []:
        if isinstance(item, dict) and item.get("draft_id") != head:
            status = str(item.get("status", "")).lower()
            if "current" in status and "not_current" not in status and "non_current" not in status:
                stale_labels.append(f"{item.get('draft_id')}:{item.get('status')}")
    add(checks, "anthology_current_labels_consistent", not stale_labels, stale_labels)
    return checks


def main(root: str = ".") -> int:
    checks = run(Path(root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
