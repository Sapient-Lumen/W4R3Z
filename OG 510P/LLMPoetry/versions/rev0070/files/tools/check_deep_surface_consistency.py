#!/usr/bin/env python3
"""Validate that current-facing surfaces follow whichever poem owns the head.

Historical poem families may retain their own terminal heads. This gate resolves the
active poem from STATE.current_head instead of assuming that P0002 is permanently
current. It checks navigation/release truth, not poem quality.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HEAD_RE = re.compile(r"^(P\d{4})-D(\d{3})$")
CURRENT_CLAIM_RE = re.compile(
    r"(?:current(?: provenance)? head|resume at|active head|is current)\s*[:=]?\s*`?(P\d{4}-D\d{3})`?",
    re.I,
)


def add(checks: list[dict], name: str, ok: bool, detail: object = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def stale_claims(raw: str, current_head: str) -> list[str]:
    return sorted({m.group(0) for m in CURRENT_CLAIM_RE.finditer(raw) if m.group(1) != current_head})


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    rev = state.get("revision")
    artifact = state.get("artifact")
    updated_at = state.get("updated_at") or state.get("timestamp")
    head = state.get("current_head") or surface.get("current_head")
    draft = state.get("current_draft")
    packet = state.get("current_packet")
    metrics = state.get("metrics_path")
    turn = state.get("turn", {}).get("last_completed") or state.get("last_completed_turn")
    m = HEAD_RE.match(str(head or ""))
    add(checks, "deep_current_head_shape", m is not None, head)
    if not m:
        return checks
    poem_id, suffix = m.groups()
    poem_dir = Path("poems") / poem_id
    expected_draft = (poem_dir / f"draft_{suffix}.md").as_posix()
    expected_packet = (poem_dir / "material" / f"source_material_packet_{suffix}.json").as_posix()
    expected_metrics = (poem_dir / "verification" / f"metrics_draft_{suffix}.json").as_posix()

    add(checks, "deep_state_basics_present", all([rev, artifact, updated_at, head, draft, packet, metrics]), f"rev={rev} head={head}")
    add(checks, "deep_state_paths_derived_from_head", draft == expected_draft and packet == expected_packet and metrics == expected_metrics, f"draft={draft} packet={packet} metrics={metrics}")
    canonical_status = state.get("status")
    summary_values = [state.get(key) for key in ("status", "current_status", "current_summary", "summary")]
    add(checks, "deep_state_summary_fields_canonical", bool(canonical_status) and all(value == canonical_status for value in summary_values), summary_values)
    read_first = state.get("read_first") or []
    add(checks, "deep_state_read_first_current", draft in read_first and packet in read_first, read_first)
    add(checks, "deep_state_read_first_paths_exist", bool(read_first) and all((root / rel).exists() for rel in read_first), [rel for rel in read_first if not (root / rel).exists()])
    add(checks, "deep_state_raw_no_stale_claim", not stale_claims(json.dumps(state, ensure_ascii=False), head), stale_claims(json.dumps(state, ensure_ascii=False), head)[:5])
    add(checks, "deep_surface_matches_state", surface.get("revision") == rev and surface.get("current_head") == head and surface.get("artifact") == artifact, f"surface_rev={surface.get('revision')} head={surface.get('current_head')}")

    root_cards = [
        "START_HERE.md", "README.md", "AGENTS.md", "ARCHIVE_INDEX.md", "CONTEXT_PACK.md",
        "docs/00-office/BOOT_CARD.md", "HUMAN_QUESTIONS.md", "docs/10-method/DATACUBE_DATA_CARD.md",
        (poem_dir / "README.md").as_posix(), "poems/P0002/README.md",
    ]
    for rel in dict.fromkeys(root_cards):
        p = root / rel
        raw = text(p)
        add(checks, f"deep_card_present:{rel}", p.exists(), rel)
        add(checks, f"deep_card_mentions_revision:{rel}", rev in raw, rel)
        add(checks, f"deep_card_mentions_current_head:{rel}", head in raw, rel)
        add(checks, f"deep_card_no_stale_current_claim:{rel}", not stale_claims(raw, head), stale_claims(raw, head))

    compact_jsons = [
        "SURFACE_STATUS.json", "FRONTIER_TICKET.json", "DATA_CARD.json", "REENTRY_CONTRACT.json",
        "CONTEXT_PACK.json", "COMPACT_SURFACE_BUNDLE.json", "LLM_BROWSE_INDEX.json",
        "VALIDATION_INDEX.json", "REPLAY_CAPSULE.json", "ARCHIVE_INDEX.json", "RELEASE_MANIFEST.json",
        "REVISION_RECEIPT.json", "VALIDATION_TOOLCHAIN_MANIFEST.json", "croissant-lite.json",
        "codemeta.json", "ro-crate-metadata.json", "datapackage.json",
    ]
    for rel in compact_jsons:
        p = root / rel
        add(checks, f"deep_json_present:{rel}", p.exists(), rel)
        if not p.exists():
            continue
        obj = load_json(p)
        raw = json.dumps(obj, ensure_ascii=False)
        if obj.get("revision") is not None:
            add(checks, f"deep_json_revision:{rel}", obj.get("revision") == rev, obj.get("revision"))
        if obj.get("current_revision") is not None:
            add(checks, f"deep_json_current_revision:{rel}", obj.get("current_revision") == rev, obj.get("current_revision"))
        if obj.get("version") is not None:
            add(checks, f"deep_json_version:{rel}", obj.get("version") == rev, obj.get("version"))
        if obj.get("current_head") is not None:
            add(checks, f"deep_json_head:{rel}", obj.get("current_head") == head, obj.get("current_head"))
        if obj.get("artifact") is not None:
            add(checks, f"deep_json_artifact:{rel}", obj.get("artifact") == artifact, obj.get("artifact"))
        for key in ("updated_at", "generated_at", "dateModified", "updated"):
            if obj.get(key) is not None:
                add(checks, f"deep_json_time:{rel}:{key}", obj.get(key) == updated_at, obj.get(key))
        for key in ("current_draft", "latest_draft"):
            if obj.get(key) is not None:
                add(checks, f"deep_json_draft:{rel}:{key}", obj.get(key) == draft, obj.get(key))
        for key in ("current_packet", "source_material_packet", "external_material_packet", "current_material_packet"):
            if obj.get(key) is not None:
                add(checks, f"deep_json_packet:{rel}:{key}", obj.get(key) == packet, obj.get(key))
        for key in ("frontier", "contract", "description", "current_summary", "status", "summary", "note"):
            if obj.get(key) is not None:
                prose = str(obj.get(key))
                add(checks, f"deep_json_prose_mentions_head:{rel}:{key}", head in prose, prose[:180])
                add(checks, f"deep_json_prose_no_stale_claim:{rel}:{key}", not stale_claims(prose, head), stale_claims(prose, head))
        if isinstance(obj.get("read_first"), list):
            add(checks, f"deep_json_read_first_canonical:{rel}", obj.get("read_first") == read_first, obj.get("read_first"))
        if isinstance(obj.get("must_read"), list):
            add(checks, f"deep_json_must_read_canonical:{rel}", obj.get("must_read") == read_first, obj.get("must_read"))
            add(checks, f"deep_json_must_read_paths_exist:{rel}", all((root / item).exists() for item in obj.get("must_read")), [item for item in obj.get("must_read") if not (root / item).exists()])
        if obj.get("web_pulse") is not None:
            add(checks, f"deep_json_web_pulse:{rel}", obj.get("web_pulse") == state.get("web_pulse"), obj.get("web_pulse"))
        if rel == "LLM_BROWSE_INDEX.json":
            add(checks, "deep_llm_browse_current_risk_mentions_head", head in str(obj.get("current_risk", "")), obj.get("current_risk"))
        if rel == "REPLAY_CAPSULE.json":
            add(checks, "deep_replay_note_mentions_head", head in str(obj.get("replay_note", "")), obj.get("replay_note"))
        smap = obj.get("surfaces") if isinstance(obj.get("surfaces"), dict) else {}
        expected_surface_paths = {
            "current_draft": draft,
            "current_packet": packet,
            "current_material_packet": packet,
            "current_metrics": metrics,
            "current_audit": state.get("current_audit"),
        }
        for skey, expected in expected_surface_paths.items():
            if skey in smap:
                add(checks, f"deep_json_surface_canonical:{rel}:{skey}", smap.get(skey) == expected, smap.get(skey))
        for skey, value in smap.items():
            if skey.startswith("current_") and isinstance(value, str):
                add(checks, f"deep_json_surface_path_exists:{rel}:{skey}", (root / value).exists(), value)
        add(checks, f"deep_json_raw_no_stale_claim:{rel}", not stale_claims(raw, head), stale_claims(raw, head)[:5])

    add(checks, "deep_version_file", text(root / "VERSION").strip() == rev, text(root / "VERSION").strip())
    pyproject = text(root / "pyproject.toml")
    add(checks, "deep_pyproject_revision", f'revision = "{rev}"' in pyproject, "pyproject.toml")
    add(checks, "deep_pyproject_head", f'current_head = "{head}"' in pyproject, "pyproject.toml")
    add(checks, "deep_pyproject_artifact", artifact in pyproject, "pyproject.toml")
    cff = text(root / "CITATION.cff")
    add(checks, "deep_citation_revision", f"version: {rev}" in cff, "CITATION.cff")
    add(checks, "deep_citation_head", head in cff, "CITATION.cff")
    sbom = load_json(root / "sbom-lite.json")
    add(checks, "deep_sbom_revision", sbom.get("revision") == rev and sbom.get("version") == rev, f"{sbom.get('revision')} {sbom.get('version')}")
    add(checks, "deep_sbom_current_poem", poem_id in json.dumps(sbom, ensure_ascii=False), poem_id)

    meta_path = root / poem_dir / "metadata.json"
    idx_path = root / poem_dir / "INDEX.json"
    for label, p in (("metadata", meta_path), ("index", idx_path)):
        add(checks, f"deep_current_poem_{label}_present", p.exists(), p)
    if meta_path.exists():
        meta = load_json(meta_path)
        add(checks, "deep_current_metadata_head", meta.get("current_head") == head and meta.get("latest_draft_id") == head, f"{meta.get('current_head')} {meta.get('latest_draft_id')}")
        add(checks, "deep_current_metadata_revision", meta.get("current_revision") == rev and meta.get("last_updated_revision") == rev, f"{meta.get('current_revision')} {meta.get('last_updated_revision')}")
        add(checks, "deep_current_metadata_turn", meta.get("current_turn") == turn and meta.get("last_updated_turn") == turn, f"{meta.get('current_turn')} {turn}")
        add(checks, "deep_current_metadata_paths", meta.get("current_draft") == draft and meta.get("source_material_packet") == packet and meta.get("external_material_packet") == packet, poem_id)
        add(checks, "deep_current_metadata_metrics", meta.get("current_metrics") == metrics or meta.get("metrics_path") == metrics, metrics)
        add(checks, "deep_current_metadata_drafts_contains_head", any(isinstance(d, dict) and d.get("draft_id") == head for d in meta.get("drafts", [])), head)
    if idx_path.exists():
        idx = load_json(idx_path)
        add(checks, "deep_current_index_head", idx.get("current_head") == head and idx.get("current_draft_id") == head and idx.get("latest_draft_id") == head, idx.get("current_head"))
        add(checks, "deep_current_index_revision", idx.get("revision") == rev and idx.get("current_revision") == rev and idx.get("last_updated_revision") == rev, f"{idx.get('revision')} {idx.get('current_revision')}")
        add(checks, "deep_current_index_paths", idx.get("current_draft") == draft and idx.get("current_packet") == packet and idx.get("source_material_packet") == packet, poem_id)
        add(checks, "deep_current_index_metrics", idx.get("metrics_path") == metrics or idx.get("current_metrics") == metrics, metrics)

    poem_index = load_json(root / "registries/poem_index.json")
    rows = [p for p in poem_index.get("poems", []) if p.get("poem_id") == poem_id]
    global_rows = [p for p in poem_index.get("poems", []) if isinstance(p, dict) and p.get("global_current_head") is True]
    add(checks, "deep_poem_index_one_global_head", len(global_rows) == 1, [p.get("poem_id") for p in global_rows])
    add(checks, "deep_poem_index_global_head_owner", len(global_rows) == 1 and global_rows[0].get("poem_id") == poem_id and global_rows[0].get("current_head") == head, global_rows[0] if global_rows else None)
    add(checks, "deep_current_poem_index_row_unique", len(rows) == 1, f"poem={poem_id} count={len(rows)}")
    if rows:
        row = rows[0]
        add(checks, "deep_current_poem_index_row_head", row.get("current_head") == head and row.get("current_draft_id") == head, row.get("current_head"))
        add(checks, "deep_current_poem_index_row_paths", row.get("current_draft") == draft and row.get("source_material_packet") == packet, poem_id)
        add(
            checks,
            "deep_current_poem_index_row_revision",
            row.get("revision") == rev and row.get("current_revision") == rev and row.get("last_updated_revision") == rev,
            f"{row.get('revision')} {row.get('current_revision')} {row.get('last_updated_revision')}",
        )
        add(
            checks,
            "deep_current_poem_index_row_turn",
            row.get("turn") == turn and row.get("current_turn") == turn and row.get("last_updated_turn") == turn,
            f"{row.get('turn')} {row.get('current_turn')} {row.get('last_updated_turn')}",
        )

    # All poem-family rows can carry current-named aliases even when they do not own
    # the global head. Validate those aliases against each row's own head so a stale
    # historical family cannot silently route readers to a superseded draft/packet.
    all_row_faults = []
    for prow in poem_index.get("poems", []):
        if not isinstance(prow, dict):
            continue
        phead = prow.get("current_head") or prow.get("current_draft_id") or prow.get("latest_draft_id")
        pm = HEAD_RE.match(str(phead or ""))
        if not pm:
            continue
        ppid, psuffix = pm.groups()
        expected_pdraft = f"poems/{ppid}/draft_{psuffix}.md"
        expected_ppacket = f"poems/{ppid}/material/source_material_packet_{psuffix}.json"
        expected_pmetrics = f"poems/{ppid}/verification/metrics_draft_{psuffix}.json"
        for key in ("current_head", "current_draft_id", "latest_draft_id"):
            if prow.get(key) is not None and prow.get(key) != phead:
                all_row_faults.append(f"{ppid}:{key}={prow.get(key)} expected={phead}")
        for key in ("draft_path", "current_draft", "latest_draft", "current_draft_path", "latest_draft_path"):
            if prow.get(key) is not None and prow.get(key) != expected_pdraft:
                all_row_faults.append(f"{ppid}:{key}={prow.get(key)} expected={expected_pdraft}")
        for key in ("source_material_packet", "external_material_packet", "current_packet", "current_material_packet"):
            if prow.get(key) is not None and prow.get(key) != expected_ppacket:
                all_row_faults.append(f"{ppid}:{key}={prow.get(key)} expected={expected_ppacket}")
        for key in ("metrics_path", "current_metrics"):
            if prow.get(key) is not None and prow.get(key) != expected_pmetrics:
                all_row_faults.append(f"{ppid}:{key}={prow.get(key)} expected={expected_pmetrics}")
        if prow.get("non_claim") is not None and phead not in str(prow.get("non_claim")):
            all_row_faults.append(f"{ppid}:non_claim_missing_head={phead}")
    add(checks, "deep_poem_index_all_rows_head_aliases", not all_row_faults, all_row_faults[:20])

    # Proof status is current-facing routing state, not a historical scrapbook. In
    # rev0068 its top-level head had moved to P0004 while nested family entries and
    # current_context still routed to superseded P0002/P0003 states. Validate both
    # the global aliases and each live family entry against poem_index so that kind
    # of split-brain proof surface cannot pass again.
    proof_path = root / "registries/proof_status.json"
    add(checks, "deep_proof_status_present", proof_path.exists(), proof_path)
    if proof_path.exists():
        proof = load_json(proof_path)
        add(
            checks,
            "deep_proof_status_global_identity",
            proof.get("revision") == rev
            and proof.get("current_revision") == rev
            and proof.get("current_head") == head
            and proof.get("current_draft_id") == head
            and proof.get("latest_draft_id") == head,
            f"rev={proof.get('revision')} current_rev={proof.get('current_revision')} head={proof.get('current_head')}",
        )
        add(
            checks,
            "deep_proof_status_global_paths",
            proof.get("current_draft_path") == draft
            and proof.get("latest_draft_path") == draft
            and proof.get("current_packet") == packet
            and proof.get("source_material_packet") == packet
            and proof.get("metrics_path") == metrics,
            f"draft={proof.get('current_draft_path')} packet={proof.get('current_packet')} metrics={proof.get('metrics_path')}",
        )
        pctx = proof.get("current_context")
        add(
            checks,
            "deep_proof_status_current_context",
            isinstance(pctx, dict)
            and pctx.get("current_head") == head
            and pctx.get("current_draft") == draft
            and pctx.get("current_packet") == packet,
            pctx,
        )
        pmap = proof.get("poems")
        add(checks, "deep_proof_status_poems_mapping", isinstance(pmap, dict), type(pmap).__name__)
        row_map = {
            item.get("poem_id"): item
            for item in poem_index.get("poems", [])
            if isinstance(item, dict) and item.get("poem_id")
        }
        proof_faults = []
        if isinstance(pmap, dict):
            for family in ("P0002", "P0003", "P0004", "P0005"):
                row = row_map.get(family)
                entry = pmap.get(family)
                if not row:
                    proof_faults.append(f"{family}:poem_index_row_missing")
                    continue
                if not isinstance(entry, dict):
                    proof_faults.append(f"{family}:proof_entry_not_object")
                    continue
                family_head = row.get("current_head")
                family_draft = row.get("current_draft") or row.get("draft_path")
                family_packet = row.get("current_packet") or row.get("source_material_packet")
                if entry.get("current_head") != family_head:
                    proof_faults.append(f"{family}:current_head={entry.get('current_head')} expected={family_head}")
                if entry.get("current_draft") != family_draft:
                    proof_faults.append(f"{family}:current_draft={entry.get('current_draft')} expected={family_draft}")
                if entry.get("current_packet") != family_packet:
                    proof_faults.append(f"{family}:current_packet={entry.get('current_packet')} expected={family_packet}")
                expected_candidate = bool(row.get("anthology_candidate"))
                if entry.get("anthology_candidate") is not expected_candidate:
                    proof_faults.append(
                        f"{family}:anthology_candidate={entry.get('anthology_candidate')} expected={expected_candidate}"
                    )
                expected_frozen = bool(row.get("lineage_frozen"))
                if entry.get("lineage_frozen") is not expected_frozen:
                    proof_faults.append(
                        f"{family}:lineage_frozen={entry.get('lineage_frozen')} expected={expected_frozen}"
                    )
                for key in ("current_judgment", "candidate_packet", "reader_edition"):
                    if entry.get(key) is not None and not (root / str(entry.get(key))).exists():
                        proof_faults.append(f"{family}:{key}_missing={entry.get(key)}")
        add(checks, "deep_proof_status_family_truth", not proof_faults, proof_faults[:30])
        p2 = pmap.get("P0002") if isinstance(pmap, dict) else None
        add(
            checks,
            "deep_proof_status_p0002_reader_target",
            isinstance(p2, dict)
            and p2.get("reader_target") == "P0002-D010"
            and p2.get("reader_response_count") == 0,
            p2,
        )

    draft_registry = load_json(root / "registries/draft_index.json")
    draft_by_id = {d.get("draft_id"): d for d in draft_registry.get("drafts", []) if isinstance(d, dict) and d.get("draft_id")}
    anthology = state.get("anthology_top_5") or []
    ranks = [item.get("rank") for item in anthology if isinstance(item, dict)]
    add(checks, "deep_anthology_ranks_unique_ordered", ranks == list(range(1, len(ranks) + 1)), ranks)
    anthology_faults = []
    for item in anthology:
        if not isinstance(item, dict):
            anthology_faults.append("non-dict anthology entry")
            continue
        did = item.get("draft_id")
        record = draft_by_id.get(did)
        if not record or record.get("anthology_candidate") is not True:
            anthology_faults.append(f"{did}:not_anthology_candidate")
            continue
        cpacket = record.get("candidate_packet")
        if not cpacket or not (root / cpacket).exists():
            anthology_faults.append(f"{did}:candidate_packet_missing={cpacket}")
        if item.get("path") != record.get("path"):
            anthology_faults.append(f"{did}:path={item.get('path')} expected={record.get('path')}")
    add(checks, "deep_anthology_entries_are_real_candidates", not anthology_faults, anthology_faults[:20])

    dp = load_json(root / "datapackage.json")
    paths = {r.get("path") for r in dp.get("resources", []) if isinstance(r, dict)}
    add(checks, "deep_datapackage_current_draft", draft in paths, draft)
    add(checks, "deep_datapackage_current_packet", packet in paths, packet)

    oq = load_json(root / "registries/open_questions.json")
    live = [q for q in oq.get("open_questions", []) if q.get("status") in {"live", "open", "pending"}]
    add(checks, "deep_open_questions_current", oq.get("revision") == rev and oq.get("current_head") == head, f"{oq.get('revision')} {oq.get('current_head')}")
    add(checks, "deep_open_question_mentions_head", any(head in str(q) for q in live), f"live_count={len(live)}")
    return checks


def main(root: str = ".") -> int:
    checks = run(Path(root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "check_count": len(checks), "failed": [c for c in checks if not c.get("ok")], "checks": checks}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
