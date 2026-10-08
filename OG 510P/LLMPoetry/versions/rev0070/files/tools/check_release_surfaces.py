#!/usr/bin/env python3
"""Validate release-facing descriptors against the dynamically resolved head."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HEAD_RE = re.compile(r"^(P\d{4})-D(\d{3})$")


def add(checks: list[dict], name: str, ok: bool, detail: object = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def resource_paths(obj: dict) -> set[str]:
    return {r.get("path") for r in obj.get("resources", []) if isinstance(r, dict) and r.get("path")}


def title_from_draft(raw: str) -> str:
    return next((line[2:].strip() for line in raw.splitlines() if line.startswith("# ")), "")


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    proof = load_json(root / "registries/proof_status.json")
    poem_index = load_json(root / "registries/poem_index.json")
    rev = state.get("revision")
    artifact = state.get("artifact")
    updated_at = state.get("updated_at") or state.get("timestamp")
    head = state.get("current_head") or surface.get("current_head")
    draft = state.get("current_draft")
    packet = state.get("current_packet")
    m = HEAD_RE.match(str(head or ""))
    add(checks, "release_current_head_shape", m is not None, head)
    if not m:
        return checks
    poem_id, suffix = m.groups()
    poem_dir = Path("poems") / poem_id
    add(checks, "release_expected_state_present", all([rev, artifact, updated_at, head, draft, packet]), f"rev={rev} head={head}")
    add(checks, "release_surface_matches_state", surface.get("revision") == rev and surface.get("artifact") == artifact and surface.get("current_head") == head, surface.get("current_head"))
    add(checks, "release_current_paths_exist", (root / draft).exists() and (root / packet).exists(), f"{draft} {packet}")

    for key, obj in (("state", state), ("surface", surface), ("proof", proof)):
        if obj.get("current_head") is not None:
            add(checks, f"release_{key}_head", obj.get("current_head") == head, obj.get("current_head"))
        for prose_key in ("status", "current_summary", "note", "next_action", "non_claim"):
            if obj.get(prose_key) is not None:
                add(checks, f"release_{key}_{prose_key}_mentions_head", head in str(obj.get(prose_key)), str(obj.get(prose_key))[:180])

    add(checks, "version_file_matches_state", text(root / "VERSION").strip() == rev, text(root / "VERSION").strip())
    for rel in ("REVISION_RECEIPT.json", "RELEASE_MANIFEST.json"):
        p = root / rel
        add(checks, f"release_descriptor_present:{rel}", p.exists(), rel)
        if not p.exists():
            continue
        obj = load_json(p)
        add(checks, f"release_descriptor_revision:{rel}", obj.get("revision") == rev, obj.get("revision"))
        add(checks, f"release_descriptor_artifact:{rel}", obj.get("artifact") == artifact, obj.get("artifact"))
        add(checks, f"release_descriptor_head:{rel}", obj.get("current_head") == head, obj.get("current_head"))
        if obj.get("updated_at") is not None:
            add(checks, f"release_descriptor_time:{rel}", obj.get("updated_at") == updated_at, obj.get("updated_at"))
        if obj.get("current_draft") is not None:
            add(checks, f"release_descriptor_draft:{rel}", obj.get("current_draft") == draft, obj.get("current_draft"))
        if obj.get("current_packet") is not None:
            add(checks, f"release_descriptor_packet:{rel}", obj.get("current_packet") == packet, obj.get("current_packet"))
        files = set(obj.get("current_files", []) or [])
        if files:
            add(checks, f"release_descriptor_lists_current:{rel}", draft in files and packet in files, sorted(files))
            for f in files:
                add(checks, f"release_descriptor_file_exists:{rel}:{f}", (root / f).exists(), f)
    receipt_md = text(root / "REVISION_RECEIPT.md")
    add(checks, "release_receipt_md_current", rev in receipt_md and head in receipt_md, "REVISION_RECEIPT.md")

    cff = text(root / "CITATION.cff")
    add(checks, "citation_present", bool(cff), "CITATION.cff")
    add(checks, "citation_current", f"version: {rev}" in cff and head in cff, "CITATION.cff")
    message_match = re.search(r'^message:\s*["\']?(.*?)["\']?$', cff, re.MULTILINE)
    message = message_match.group(1) if message_match else ""
    add(checks, "citation_message_current", rev in message and head in message, message)

    makefile = text(root / "Makefile")
    def make_var(name: str) -> str | None:
        mm = re.search(rf"^{re.escape(name)} \?= (.+)$", makefile, re.MULTILINE)
        return mm.group(1).strip() if mm else None
    current_var = make_var("CURRENT_DRAFT") or make_var("P0002_DRAFT")
    add(checks, "makefile_current_draft", current_var == draft, current_var)
    add(checks, "makefile_current_packet", make_var("EXTERNAL_MATERIAL_PACKET") == packet, make_var("EXTERNAL_MATERIAL_PACKET"))
    add(checks, "makefile_output_current", artifact in str(make_var("OUT")), make_var("OUT"))
    stamp = make_var("STAMP")
    add(checks, "makefile_stamp_current", bool(stamp and stamp.replace(".", "") in artifact.replace(".", "")), stamp)

    current_title = title_from_draft(text(root / draft))
    add(checks, "release_current_title_found", bool(current_title), draft)
    meta_path = root / poem_dir / "metadata.json"
    idx_path = root / poem_dir / "INDEX.json"
    for label, p in (("metadata", meta_path), ("index", idx_path)):
        add(checks, f"release_current_poem_{label}_present", p.exists(), p)
    if meta_path.exists():
        meta = load_json(meta_path)
        add(checks, "release_metadata_title", meta.get("title") == current_title, meta.get("title"))
        add(checks, "release_metadata_head", meta.get("current_head") == head, meta.get("current_head"))
        add(checks, "release_metadata_paths", meta.get("current_draft") == draft and meta.get("source_material_packet") == packet and meta.get("external_material_packet") == packet, poem_id)
        add(checks, "release_metadata_revision", meta.get("current_revision") == rev and meta.get("last_updated_revision") == rev, f"{meta.get('current_revision')} {meta.get('last_updated_revision')}")
        gen = meta.get("generation_context") if isinstance(meta.get("generation_context"), dict) else {}
        if gen:
            add(checks, "release_metadata_prompt", gen.get("prompt_path") == (poem_dir / f"prompt_{suffix}.md").as_posix(), gen.get("prompt_path"))
            add(checks, "release_metadata_generation_packet", gen.get("source_material_packet") == packet, gen.get("source_material_packet"))
    if idx_path.exists():
        idx = load_json(idx_path)
        add(checks, "release_index_title", idx.get("title") == current_title and idx.get("current_title", current_title) == current_title, idx.get("title"))
        add(checks, "release_index_head", idx.get("current_head") == head and idx.get("current_draft_id") == head, idx.get("current_head"))
        add(checks, "release_index_paths", idx.get("current_draft") == draft and idx.get("current_packet") == packet, poem_id)

    rows = [p for p in poem_index.get("poems", []) if p.get("poem_id") == poem_id]
    add(checks, "release_poem_index_row_unique", len(rows) == 1, f"{poem_id}:{len(rows)}")
    add(checks, "release_poem_index_top_current", poem_index.get("revision") == rev and poem_index.get("current_head") == head and poem_index.get("updated_at") == updated_at, f"{poem_index.get('revision')} {poem_index.get('current_head')}")
    if rows:
        row = rows[0]
        add(checks, "release_poem_index_row_title", row.get("title") == current_title, row.get("title"))
        add(checks, "release_poem_index_row_head", row.get("current_head") == head and row.get("current_draft_id") == head, row.get("current_head"))
        add(checks, "release_poem_index_row_paths", row.get("current_draft") == draft and row.get("source_material_packet") == packet and row.get("external_material_packet") == packet, poem_id)
        add(checks, "release_poem_index_row_revision", row.get("current_revision") == rev and row.get("last_updated_revision") == rev, f"{row.get('current_revision')} {row.get('last_updated_revision')}")

    dp = load_json(root / "datapackage.json")
    paths = resource_paths(dp)
    add(checks, "datapackage_current", dp.get("revision") == rev and dp.get("current_head") == head, f"{dp.get('revision')} {dp.get('current_head')}")
    add(checks, "datapackage_modified", dp.get("dateModified") == updated_at or dp.get("updated") == updated_at, f"{dp.get('dateModified')} {dp.get('updated')}")
    add(checks, "datapackage_current_resources", draft in paths and packet in paths, f"{draft} {packet}")
    expected_names = {f"{poem_id.lower()}_draft_{suffix.lower()}": draft, f"{poem_id.lower()}_source_material_packet_{suffix.lower()}": packet}
    names = {r.get("name"): r.get("path") for r in dp.get("resources", []) if isinstance(r, dict)}
    add(checks, "datapackage_current_resource_names", all(names.get(k) == v for k, v in expected_names.items()), {k: names.get(k) for k in expected_names})

    vi = load_json(root / "VALIDATION_INDEX.json")
    raw_vi = text(root / "VALIDATION_INDEX.json")
    add(checks, "validation_index_current", (vi.get("revision") == rev or vi.get("current_revision") == rev) and vi.get("current_head") == head, f"{vi.get('revision')} {vi.get('current_head')}")
    add(checks, "validation_index_description_current", head in str(vi.get("description", "")), vi.get("description"))
    add(checks, "validation_index_paths_current", draft in raw_vi and packet in raw_vi, f"{draft} {packet}")

    for rel in ("croissant-lite.json", "ro-crate-metadata.json", "codemeta.json", "VALIDATION_TOOLCHAIN_MANIFEST.json", "sbom-lite.json"):
        p = root / rel
        add(checks, f"descriptor_present:{rel}", p.exists(), rel)
        if p.exists():
            obj = load_json(p)
            raw = text(p)
            add(checks, f"descriptor_revision:{rel}", obj.get("revision") == rev or obj.get("version") == rev, f"{obj.get('revision')} {obj.get('version')}")
            add(checks, f"descriptor_head:{rel}", head in raw and (obj.get("current_head") in {None, head}), obj.get("current_head"))
            if obj.get("dateModified") is not None:
                add(checks, f"descriptor_modified:{rel}", obj.get("dateModified") == updated_at, obj.get("dateModified"))
    return checks


def main(root: str = ".") -> int:
    checks = run(Path(root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
