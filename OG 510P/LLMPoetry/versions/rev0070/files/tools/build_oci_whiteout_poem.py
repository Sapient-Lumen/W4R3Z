#!/usr/bin/env python3
"""Build deterministic OCI image-layout poems using explicit or opaque whiteouts.

Schema v1 is preserved for P0004-D001. Schema v2 adds a bounded opaque-whiteout
form in which lower files are hidden while same-layer replacement files survive,
independent of tar-member order.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

from oci_path_safety import canonical_rel, resolve_under

JSON_MEDIA = "application/vnd.oci.image.config.v1+json"
MANIFEST_MEDIA = "application/vnd.oci.image.manifest.v1+json"
INDEX_MEDIA = "application/vnd.oci.image.index.v1+json"
LAYER_MEDIA = "application/vnd.oci.image.layer.v1.tar"
FIXED_MTIME = 0


def canonical_json(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_rel(path: str) -> str:
    return canonical_rel(path, label="OCI layer path")


def tar_bytes(entries: list[dict[str, Any]]) -> bytes:
    """Create a deterministic uncompressed USTAR archive in supplied order."""
    seen: set[str] = set()
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.USTAR_FORMAT) as tf:
        for entry in entries:
            name = safe_rel(str(entry["path"]))
            if name in seen:
                raise ValueError(f"duplicate layer path: {name}")
            seen.add(name)
            kind = entry.get("kind", "file")
            info = tarfile.TarInfo(name + ("/" if kind == "dir" and not name.endswith("/") else ""))
            info.mtime = FIXED_MTIME
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            if kind == "dir":
                info.type = tarfile.DIRTYPE
                info.mode = int(entry.get("mode", 0o755))
                info.size = 0
                tf.addfile(info)
            elif kind == "file":
                data = entry.get("content", b"")
                if isinstance(data, str):
                    data = data.encode("utf-8")
                if not isinstance(data, (bytes, bytearray)):
                    raise TypeError(f"file content must be bytes or str: {name}")
                payload = bytes(data)
                info.type = tarfile.REGTYPE
                info.mode = int(entry.get("mode", 0o644))
                info.size = len(payload)
                tf.addfile(info, io.BytesIO(payload))
            else:
                raise ValueError(f"unsupported layer entry kind {kind!r}")
    return buf.getvalue()


def write_blob(layout: Path, data: bytes) -> dict[str, Any]:
    digest = sha256_bytes(data)
    path = layout / "blobs" / "sha256" / digest
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return {"digest": f"sha256:{digest}", "size": len(data)}


def clear_layout(layout: Path) -> None:
    if not layout.exists():
        return
    for p in sorted(layout.rglob("*"), key=lambda q: len(q.parts), reverse=True):
        if p.is_symlink() or p.is_file():
            p.unlink()
        elif p.is_dir():
            p.rmdir()


def text_bytes(value: str) -> bytes:
    return (value + "\n").encode("utf-8")


def parent_dirs(paths: list[str]) -> list[str]:
    found: set[str] = set()
    for raw in paths:
        parent = PurePosixPath(raw).parent
        while str(parent) not in {"", "."}:
            found.add(parent.as_posix())
            parent = parent.parent
    return sorted(found, key=lambda p: (len(PurePosixPath(p).parts), p))


def normalize_spec(spec: dict[str, Any]) -> dict[str, Any]:
    schema = spec.get("schema")
    if schema == "llmpoetry-oci-whiteout-poem-spec-v1":
        target = safe_rel(str(spec["target_path"]))
        marker = safe_rel(str(spec["whiteout_path"]))
        expected = (PurePosixPath(target).parent / (".wh." + PurePosixPath(target).name)).as_posix()
        if marker != expected:
            raise ValueError(f"whiteout path {marker!r} does not name target {target!r}")
        statement = str(spec["statement"])
        return {
            "schema_version": 1,
            "mode": "explicit",
            "lower_files": [{"path": target, "text": statement}],
            "upper_files": [],
            "marker_path": marker,
            "marker_position": "only",
            "opaque_dir": None,
            "expected_merged_files": [],
            "expected_absent_paths": [target, marker],
            "lower_layer_title": "lower-objection-layer.tar",
            "upper_layer_title": "upper-whiteout-layer.tar",
            "description": "A non-runnable OCI image-layout poem about an objection, its whiteout, and the two required content-addressed layers.",
            "manifest_description": "Lower objection, upper zero-byte whiteout, merged absence, both blobs retained by manifest.",
        }
    if schema != "llmpoetry-oci-whiteout-poem-spec-v2":
        raise ValueError(f"unexpected OCI poem spec schema: {schema!r}")
    if spec.get("whiteout_mode") != "opaque":
        raise ValueError("v2 currently supports whiteout_mode=opaque only")
    opaque_dir = safe_rel(str(spec["opaque_dir"]))
    marker = safe_rel(str(spec.get("whiteout_path") or (PurePosixPath(opaque_dir) / ".wh..wh..opq")))
    expected_marker = (PurePosixPath(opaque_dir) / ".wh..wh..opq").as_posix()
    if marker != expected_marker:
        raise ValueError(f"opaque whiteout must be {expected_marker!r}, got {marker!r}")

    def files(key: str) -> list[dict[str, str]]:
        raw = spec.get(key)
        if not isinstance(raw, list) or not raw:
            raise ValueError(f"{key} must be a non-empty list")
        out: list[dict[str, str]] = []
        seen: set[str] = set()
        for item in raw:
            if not isinstance(item, dict):
                raise TypeError(f"{key} entries must be objects")
            path = safe_rel(str(item["path"]))
            if path in seen:
                raise ValueError(f"duplicate {key} path: {path}")
            seen.add(path)
            if not (path.startswith(opaque_dir + "/") and PurePosixPath(path).name != ".wh..wh..opq"):
                raise ValueError(f"{key} path must be a non-whiteout child of {opaque_dir}: {path}")
            out.append({"path": path, "text": str(item["text"])})
        return out

    lower_files = files("lower_files")
    upper_files = files("upper_files")
    overlap = {x["path"] for x in lower_files} & {x["path"] for x in upper_files}
    if overlap:
        raise ValueError(f"v2 lower/upper file paths must be distinct for this poem contract: {sorted(overlap)}")
    marker_position = str(spec.get("upper_marker_position", "last"))
    if marker_position not in {"first", "last"}:
        raise ValueError("upper_marker_position must be first or last")
    return {
        "schema_version": 2,
        "mode": "opaque",
        "lower_files": lower_files,
        "upper_files": upper_files,
        "marker_path": marker,
        "marker_position": marker_position,
        "opaque_dir": opaque_dir,
        "expected_merged_files": list(upper_files),
        "expected_absent_paths": [x["path"] for x in lower_files] + [marker],
        "lower_layer_title": str(spec.get("lower_layer_title", "lower-appeal-layer.tar")),
        "upper_layer_title": str(spec.get("upper_layer_title", "upper-opaque-status-layer.tar")),
        "description": str(spec.get("description", "A non-runnable OCI image-layout poem in which an opaque whiteout hides a lower appeal while a same-layer status survives.")),
        "manifest_description": str(spec.get("manifest_description", "Lower appeal records hidden by one opaque marker; same-layer status retained; both layer blobs required.")),
    }


def build(root: Path, spec_path: Path) -> dict[str, Any]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    norm = normalize_spec(spec)

    artifact_dir = resolve_under(
        root, str(spec["artifact_dir"]), label="artifact_dir", must_exist=True, expect_dir=True
    )
    if artifact_dir != spec_path.parent:
        raise ValueError(
            f"artifact_dir must be the spec parent: artifact_dir={artifact_dir.relative_to(root)} "
            f"spec_parent={spec_path.parent.relative_to(root)}"
        )
    layout = resolve_under(
        artifact_dir, str(spec["layout_dir"]), label="layout_dir", expect_dir=True
    )
    clear_layout(layout)
    layout.mkdir(parents=True, exist_ok=True)

    lower_paths = [x["path"] for x in norm["lower_files"]]
    lower_entries: list[dict[str, Any]] = [
        {"path": p, "kind": "dir", "mode": 0o755} for p in parent_dirs(lower_paths)
    ]
    lower_entries.extend(
        {"path": x["path"], "kind": "file", "mode": 0o644, "content": text_bytes(x["text"])}
        for x in norm["lower_files"]
    )

    marker_entry = {"path": norm["marker_path"], "kind": "file", "mode": 0o644, "content": b""}
    if norm["schema_version"] == 1:
        upper_entries = [marker_entry]
    else:
        upper_paths = [x["path"] for x in norm["upper_files"]] + [norm["marker_path"]]
        upper_entries = [{"path": p, "kind": "dir", "mode": 0o755} for p in parent_dirs(upper_paths)]
        upper_file_entries = [
            {"path": x["path"], "kind": "file", "mode": 0o644, "content": text_bytes(x["text"])}
            for x in norm["upper_files"]
        ]
        if norm["marker_position"] == "first":
            upper_entries.extend([marker_entry, *upper_file_entries])
        else:
            upper_entries.extend([*upper_file_entries, marker_entry])

    lower = tar_bytes(lower_entries)
    upper = tar_bytes(upper_entries)
    lower_desc = write_blob(layout, lower)
    lower_desc.update({"mediaType": LAYER_MEDIA, "annotations": {"org.opencontainers.image.title": norm["lower_layer_title"]}})
    upper_desc = write_blob(layout, upper)
    upper_desc.update({"mediaType": LAYER_MEDIA, "annotations": {"org.opencontainers.image.title": norm["upper_layer_title"]}})

    if norm["schema_version"] == 1:
        target = norm["lower_files"][0]["path"]
        history = [
            {"created": spec["created_at"], "created_by": f"ADD {target}"},
            {"created": spec["created_at"], "created_by": f"WHITEOUT {target}"},
        ]
    else:
        history = [
            {"created": spec["created_at"], "created_by": "ADD " + ", ".join(lower_paths)},
            {"created": spec["created_at"], "created_by": f"OPAQUE {norm['opaque_dir']} THEN ADD " + ", ".join(x["path"] for x in norm["upper_files"])},
        ]
    config = {
        "architecture": spec.get("architecture", "amd64"),
        "os": spec.get("os", "linux"),
        "created": spec["created_at"],
        "author": "LLMPoetry machine draft",
        "config": {
            "Labels": {
                "org.opencontainers.image.title": spec["title"],
                "org.opencontainers.image.description": norm["description"],
                "org.opencontainers.image.version": spec["revision"],
            }
        },
        "rootfs": {"type": "layers", "diff_ids": [lower_desc["digest"], upper_desc["digest"]]},
        "history": history,
    }
    config_bytes = canonical_json(config)
    config_desc = write_blob(layout, config_bytes)
    config_desc["mediaType"] = JSON_MEDIA

    manifest = {
        "schemaVersion": 2,
        "mediaType": MANIFEST_MEDIA,
        "config": config_desc,
        "layers": [lower_desc, upper_desc],
        "annotations": {
            "org.opencontainers.image.title": spec["title"],
            "org.opencontainers.image.description": norm["manifest_description"],
        },
    }
    manifest_bytes = canonical_json(manifest)
    manifest_desc = write_blob(layout, manifest_bytes)
    manifest_desc.update({
        "mediaType": MANIFEST_MEDIA,
        "platform": {"architecture": config["architecture"], "os": config["os"]},
        "annotations": {"org.opencontainers.image.ref.name": spec["ref_name"]},
    })
    index = {
        "schemaVersion": 2,
        "mediaType": INDEX_MEDIA,
        "manifests": [manifest_desc],
        "annotations": {
            "org.opencontainers.image.title": spec["title"],
            "org.opencontainers.image.version": spec["revision"],
            "org.llmpoetry.draft.id": spec["draft_id"],
        },
    }
    (layout / "index.json").write_bytes(canonical_json(index))
    (layout / "oci-layout").write_bytes(canonical_json({"imageLayoutVersion": "1.0.0"}))

    lower_surface = "LOWER LAYER\n" + "".join(f"{x['path']} | {x['text']}\n" for x in norm["lower_files"])
    upper_surface = "UPPER LAYER\n" + "".join(f"{x['path']} | {x['text']}\n" for x in norm["upper_files"])
    upper_surface += f"{norm['marker_path']} | 0 BYTES\n"
    merged_surface = "MERGED FILESYSTEM\n"
    merged_surface += "".join(f"{x['path']} | {x['text']}\n" for x in norm["expected_merged_files"])
    merged_surface += "".join(f"{p} | NOT FOUND\n" for p in norm["expected_absent_paths"])
    merged_surface += "\nIMAGE MANIFEST\nlower layer | REQUIRED\nupper layer | REQUIRED\n"
    (artifact_dir / "lower_surface.txt").write_text(lower_surface, encoding="utf-8")
    (artifact_dir / "upper_surface.txt").write_text(upper_surface, encoding="utf-8")
    (artifact_dir / "merged_surface.txt").write_text(merged_surface, encoding="utf-8")

    state_contract: dict[str, Any]
    if norm["schema_version"] == 1:
        state_contract = {
            "lower_contains_target": True,
            "upper_contains_empty_whiteout": True,
            "upper_does_not_readd_target": True,
            "merged_contains_target": False,
            "merged_contains_whiteout": False,
            "manifest_references_both_layers": True,
        }
        receipt_schema = "llmpoetry-oci-whiteout-receipt-v1"
    else:
        state_contract = {
            "lower_files_exact": True,
            "upper_same_layer_files_exact": True,
            "upper_contains_one_empty_opaque_whiteout": True,
            "opaque_whiteout_applies_only_to_lower_layer": True,
            "same_layer_files_survive_regardless_of_marker_order": True,
            "merged_lower_files_absent": True,
            "merged_upper_files_present": True,
            "merged_whiteout_absent": True,
            "manifest_references_both_layers": True,
            "closed_world_blob_set": True,
        }
        receipt_schema = "llmpoetry-oci-whiteout-receipt-v2"

    receipt: dict[str, Any] = {
        "schema": receipt_schema,
        "revision": spec["revision"],
        "turn": spec["turn"],
        "created_at": spec["created_at"],
        "poem_id": spec["poem_id"],
        "draft_id": spec["draft_id"],
        "title": spec["title"],
        "spec_path": spec_path.relative_to(root).as_posix(),
        "layout_path": layout.relative_to(root).as_posix(),
        "whiteout_mode": norm["mode"],
        "whiteout_path": norm["marker_path"],
        "whiteout_size": 0,
        "upper_marker_position": norm["marker_position"],
        "lower_files": norm["lower_files"],
        "upper_files": norm["upper_files"],
        "expected_absent_paths": norm["expected_absent_paths"],
        "layer_order": ["lower", "upper"],
        "descriptors": {
            "config": config_desc,
            "manifest": manifest_desc,
            "lower_layer": lower_desc,
            "upper_layer": upper_desc,
        },
        "state_contract": state_contract,
        "surface_paths": {
            "lower": (artifact_dir / "lower_surface.txt").relative_to(root).as_posix(),
            "upper": (artifact_dir / "upper_surface.txt").relative_to(root).as_posix(),
            "merged": (artifact_dir / "merged_surface.txt").relative_to(root).as_posix(),
        },
        "quality_claims": [],
        "non_claim": "This receipt proves a bounded OCI layout, descriptor, layer-order, whiteout, and merged-state contract only. It is not a literary judgment, reader response, admission, or evidence of quality.",
    }
    if norm["schema_version"] == 1:
        target_item = norm["lower_files"][0]
        receipt.update({
            "target_path": target_item["path"],
            "statement": target_item["text"],
            "statement_utf8_size": len(text_bytes(target_item["text"])),
        })
    else:
        receipt["opaque_dir"] = norm["opaque_dir"]
        receipt["blob_closure"] = sorted(
            d["digest"] for d in (config_desc, manifest_desc, lower_desc, upper_desc)
        )
    receipt_path = artifact_dir / "OCI_RECEIPT.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--spec", required=True)
    args = ap.parse_args()
    root = Path(args.root).resolve()
    spec_path = resolve_under(
        root, args.spec, label="spec path", must_exist=True, expect_dir=False
    )
    receipt = build(root, spec_path)
    print(json.dumps({"ok": True, "draft_id": receipt["draft_id"], "layout": receipt["layout_path"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
