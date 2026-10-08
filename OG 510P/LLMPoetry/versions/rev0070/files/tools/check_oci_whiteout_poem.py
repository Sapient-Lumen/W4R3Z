#!/usr/bin/env python3
"""Validate all LLMPoetry OCI whiteout-poem artifacts without host extraction.

The layer simulator is deliberately phase-based: whiteouts are applied to the
pre-layer state first, then non-whiteout entries from the same layer are added.
That models OCI's lower-layer-only rule and makes opaque marker behavior
independent of tar-member order.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import posixpath
import shutil
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

from build_oci_whiteout_poem import build as build_oci_poem
from oci_path_safety import canonical_rel, descriptor_blob_path, parse_sha256_digest, resolve_under

MANIFEST_MEDIA = "application/vnd.oci.image.manifest.v1+json"
INDEX_MEDIA = "application/vnd.oci.image.index.v1+json"
CONFIG_MEDIA = "application/vnd.oci.image.config.v1+json"
LAYER_MEDIA = "application/vnd.oci.image.layer.v1.tar"
MAX_PROJECT_BLOB_BYTES = 64 * 1024 * 1024


def add(checks: list[dict[str, Any]], name: str, ok: bool, detail: Any = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_path(name: str) -> bool:
    try:
        canonical_rel(name, label="OCI tar path")
    except ValueError:
        return False
    return True


def read_descriptor(layout: Path, desc: dict[str, Any], checks: list[dict[str, Any]], prefix: str) -> bytes:
    """Validate descriptor grammar and containment before any blob I/O."""
    digest = str(desc.get("digest", ""))
    try:
        hexdigest = parse_sha256_digest(digest)
        path = descriptor_blob_path(layout, digest)
    except Exception as exc:
        add(checks, prefix + ":digest_shape", False, str(exc))
        add(checks, prefix + ":descriptor_path_rejected_before_io", True, digest)
        return b""
    add(checks, prefix + ":digest_shape", True, digest)
    add(checks, prefix + ":descriptor_path_contained", True, path.as_posix())
    regular = path.is_file() and not path.is_symlink()
    add(checks, prefix + ":blob_exists", regular, path.as_posix())
    if not regular:
        return b""
    declared_size = desc.get("size")
    stat_size = path.stat().st_size
    size_type_ok = isinstance(declared_size, int) and not isinstance(declared_size, bool) and declared_size >= 0
    add(checks, prefix + ":size_type", size_type_ok, declared_size)
    add(checks, prefix + ":size", size_type_ok and declared_size == stat_size, f"declared={declared_size} actual={stat_size}")
    within_bound = stat_size <= MAX_PROJECT_BLOB_BYTES
    add(checks, prefix + ":project_blob_size_bound", within_bound, f"actual={stat_size} max={MAX_PROJECT_BLOB_BYTES}")
    if not size_type_ok or declared_size != stat_size or not within_bound:
        return b""
    data = path.read_bytes()
    add(checks, prefix + ":digest", sha(data) == hexdigest, hexdigest)
    return data


def parse_layer(data: bytes, checks: list[dict[str, Any]], prefix: str) -> dict[str, Any]:
    order: list[str] = []
    entries: dict[str, tuple[str, bytes]] = {}
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as tf:
            names = [m.name.rstrip("/") for m in tf.getmembers()]
            add(checks, prefix + ":no_duplicate_members", len(names) == len(set(names)), names)
            casefolded = [n.casefold() for n in names]
            add(checks, prefix + ":no_casefold_collisions", len(casefolded) == len(set(casefolded)), names)
            for member, name in zip(tf.getmembers(), names):
                order.append(name)
                add(checks, prefix + f":safe_path:{name}", safe_path(name), name)
                add(checks, prefix + f":portable_type:{name}", member.isdir() or member.isreg(), member.type)
                add(checks, prefix + f":root_owned:{name}", member.uid == 0 and member.gid == 0, f"{member.uid}:{member.gid}")
                add(checks, prefix + f":fixed_mtime:{name}", member.mtime == 0, member.mtime)
                if member.isdir():
                    entries[name] = ("dir", b"")
                elif member.isreg():
                    fh = tf.extractfile(member)
                    entries[name] = ("file", fh.read() if fh else b"")
            file_paths = {name for name, (kind, _data) in entries.items() if kind == "file"}
            conflicts = []
            for name in entries:
                parent = PurePosixPath(name).parent
                while str(parent) not in {"", "."}:
                    if parent.as_posix() in file_paths:
                        conflicts.append((parent.as_posix(), name))
                    parent = parent.parent
            add(checks, prefix + ":path_tree_consistent", not conflicts, conflicts)
    except Exception as exc:
        add(checks, prefix + ":tar_parse", False, str(exc))
    else:
        add(checks, prefix + ":tar_parse", True, len(entries))
    return {"order": order, "entries": entries}


def whiteout_kind(name: str) -> str | None:
    base = PurePosixPath(name).name
    if base == ".wh..wh..opq":
        return "opaque"
    if base.startswith(".wh."):
        return "explicit"
    return None


def apply_layers(layers: list[dict[str, Any]], checks: list[dict[str, Any]] | None = None, prefix: str = "apply") -> dict[str, tuple[str, bytes]]:
    """Apply deletions to prior state, then add same-layer non-whiteout entries."""
    state: dict[str, tuple[str, bytes]] = {}
    for layer_no, layer in enumerate(layers):
        entries: dict[str, tuple[str, bytes]] = layer["entries"]
        order: list[str] = layer["order"]
        prior = dict(state)
        markers = [name for name in order if whiteout_kind(name)]
        nonmarkers = [name for name in order if not whiteout_kind(name)]

        # Phase one: every whiteout affects only the lower/prior state. This is
        # intentionally independent of where the marker occurs in the tar.
        for name in markers:
            kind = whiteout_kind(name)
            parent = PurePosixPath(name).parent
            parent_s = "" if str(parent) == "." else parent.as_posix()
            if kind == "opaque":
                victims = [p for p in prior if (not parent_s or p.startswith(parent_s + "/")) and p != parent_s]
                for victim in victims:
                    prior.pop(victim, None)
            else:
                target = (parent / PurePosixPath(name).name[4:]).as_posix()
                victims = [p for p in prior if p == target or p.startswith(target + "/")]
                for victim in victims:
                    prior.pop(victim, None)
            if checks is not None:
                add(checks, f"{prefix}:marker_phase:{layer_no}:{name}", True, kind)

        # Phase two: additions/modifications from this layer survive its own
        # whiteouts, even when their tar entries precede the markers.
        state = prior
        for name in nonmarkers:
            kind, data = entries[name]
            parent = PurePosixPath(name).parent
            ancestors: list[str] = []
            while str(parent) not in {"", "."}:
                ancestors.append(parent.as_posix())
                parent = parent.parent
            for ancestor in ancestors:
                if state.get(ancestor, (None,))[0] == "file":
                    state.pop(ancestor, None)
            if kind == "file":
                for victim in [p for p in state if p == name or p.startswith(name + "/")]:
                    state.pop(victim, None)
            state[name] = (kind, data)
    return state


def normalized_contract(spec: dict[str, Any]) -> dict[str, Any]:
    schema = spec.get("schema")
    if schema == "llmpoetry-oci-whiteout-poem-spec-v1":
        target = str(spec.get("target_path", ""))
        marker = str(spec.get("whiteout_path", ""))
        return {
            "schema_version": 1,
            "mode": "explicit",
            "lower_files": [{"path": target, "text": str(spec.get("statement", ""))}],
            "upper_files": [],
            "marker": marker,
            "marker_position": "only",
            "opaque_dir": None,
            "expected_contract": {
                "lower_contains_target": True,
                "upper_contains_empty_whiteout": True,
                "upper_does_not_readd_target": True,
                "merged_contains_target": False,
                "merged_contains_whiteout": False,
                "manifest_references_both_layers": True,
            },
            "receipt_schema": "llmpoetry-oci-whiteout-receipt-v1",
        }
    if schema != "llmpoetry-oci-whiteout-poem-spec-v2":
        raise ValueError(f"unsupported schema {schema!r}")
    lower = spec.get("lower_files") if isinstance(spec.get("lower_files"), list) else []
    upper = spec.get("upper_files") if isinstance(spec.get("upper_files"), list) else []
    opaque_dir = str(spec.get("opaque_dir", ""))
    marker = str(spec.get("whiteout_path") or (PurePosixPath(opaque_dir) / ".wh..wh..opq"))
    return {
        "schema_version": 2,
        "mode": "opaque",
        "lower_files": [{"path": str(x.get("path", "")), "text": str(x.get("text", ""))} for x in lower if isinstance(x, dict)],
        "upper_files": [{"path": str(x.get("path", "")), "text": str(x.get("text", ""))} for x in upper if isinstance(x, dict)],
        "marker": marker,
        "marker_position": str(spec.get("upper_marker_position", "last")),
        "opaque_dir": opaque_dir,
        "expected_contract": {
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
        },
        "receipt_schema": "llmpoetry-oci-whiteout-receipt-v2",
    }


def expected_surfaces(contract: dict[str, Any]) -> dict[str, str]:
    lower = "LOWER LAYER\n" + "".join(f"{x['path']} | {x['text']}\n" for x in contract["lower_files"])
    upper = "UPPER LAYER\n" + "".join(f"{x['path']} | {x['text']}\n" for x in contract["upper_files"])
    upper += f"{contract['marker']} | 0 BYTES\n"
    merged = "MERGED FILESYSTEM\n"
    merged += "".join(f"{x['path']} | {x['text']}\n" for x in contract["upper_files"])
    merged += "".join(f"{x['path']} | NOT FOUND\n" for x in contract["lower_files"])
    merged += f"{contract['marker']} | NOT FOUND\n"
    merged += "\nIMAGE MANIFEST\nlower layer | REQUIRED\nupper layer | REQUIRED\n"
    return {"lower": lower, "upper": upper, "merged": merged}


def check_spec(root: Path, spec_path: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    rel = spec_path.relative_to(root).as_posix()
    prefix = rel.replace("/", ":")
    try:
        spec = load_json(spec_path)
        contract = normalized_contract(spec)
    except Exception as exc:
        add(checks, prefix + ":spec_parse", False, str(exc))
        return checks
    add(checks, prefix + ":spec_parse", True)
    add(checks, prefix + ":spec_schema", spec.get("schema") in {"llmpoetry-oci-whiteout-poem-spec-v1", "llmpoetry-oci-whiteout-poem-spec-v2"}, spec.get("schema"))
    add(checks, prefix + ":whiteout_mode", contract["mode"] in {"explicit", "opaque"}, contract["mode"])

    lower_paths = [x["path"] for x in contract["lower_files"]]
    upper_paths = [x["path"] for x in contract["upper_files"]]
    add(checks, prefix + ":lower_paths_safe_unique", bool(lower_paths) and len(lower_paths) == len(set(lower_paths)) and all(safe_path(p) for p in lower_paths), lower_paths)
    add(checks, prefix + ":upper_paths_safe_unique", len(upper_paths) == len(set(upper_paths)) and all(safe_path(p) for p in upper_paths), upper_paths)
    add(checks, prefix + ":marker_safe", safe_path(contract["marker"]), contract["marker"])
    if contract["mode"] == "explicit":
        expected = (PurePosixPath(lower_paths[0]).parent / (".wh." + PurePosixPath(lower_paths[0]).name)).as_posix() if lower_paths else ""
        add(checks, prefix + ":explicit_marker_names_target", contract["marker"] == expected, f"expected={expected} actual={contract['marker']}")
    else:
        expected = (PurePosixPath(contract["opaque_dir"]) / ".wh..wh..opq").as_posix()
        add(checks, prefix + ":opaque_marker_exact", contract["marker"] == expected, f"expected={expected} actual={contract['marker']}")
        add(checks, prefix + ":opaque_children_bounded", bool(lower_paths) and bool(upper_paths) and all(p.startswith(contract["opaque_dir"] + "/") for p in lower_paths + upper_paths), lower_paths + upper_paths)
        add(checks, prefix + ":lower_upper_paths_disjoint", not (set(lower_paths) & set(upper_paths)), sorted(set(lower_paths) & set(upper_paths)))

    try:
        artifact = resolve_under(root, str(spec.get("artifact_dir", "")), label="artifact_dir", must_exist=True, expect_dir=True)
        declared_matches_spec = artifact == spec_path.parent.resolve()
        add(checks, prefix + ":artifact_dir_contained", True, artifact.as_posix())
        add(checks, prefix + ":artifact_dir_matches_spec_parent", declared_matches_spec, f"declared={artifact} spec_parent={spec_path.parent.resolve()}")
        if not declared_matches_spec:
            return checks
        layout = resolve_under(artifact, str(spec.get("layout_dir", "")), label="layout_dir", must_exist=True, expect_dir=True)
    except Exception as exc:
        add(checks, prefix + ":artifact_layout_path_containment", False, str(exc))
        return checks
    add(checks, prefix + ":artifact_layout_path_containment", True, layout.as_posix())
    add(checks, prefix + ":layout_exists", layout.is_dir() and not layout.is_symlink(), layout.as_posix())
    if not layout.is_dir() or layout.is_symlink():
        return checks

    oci_layout = load_json(layout / "oci-layout") if (layout / "oci-layout").is_file() else {}
    add(checks, prefix + ":oci_layout_version", oci_layout.get("imageLayoutVersion") == "1.0.0", oci_layout)
    index = load_json(layout / "index.json") if (layout / "index.json").is_file() else {}
    add(checks, prefix + ":index_media", index.get("mediaType") == INDEX_MEDIA and index.get("schemaVersion") == 2, index.get("mediaType"))
    manifests = index.get("manifests") if isinstance(index.get("manifests"), list) else []
    add(checks, prefix + ":one_manifest", len(manifests) == 1, len(manifests))
    if len(manifests) != 1:
        return checks
    manifest_desc = manifests[0]
    manifest_bytes = read_descriptor(layout, manifest_desc, checks, prefix + ":manifest")
    try:
        manifest = json.loads(manifest_bytes)
    except Exception as exc:
        add(checks, prefix + ":manifest_parse", False, str(exc))
        return checks
    add(checks, prefix + ":manifest_parse", True)
    add(checks, prefix + ":manifest_media", manifest.get("mediaType") == MANIFEST_MEDIA and manifest.get("schemaVersion") == 2, manifest.get("mediaType"))
    layers = manifest.get("layers") if isinstance(manifest.get("layers"), list) else []
    add(checks, prefix + ":two_layers", len(layers) == 2, len(layers))
    add(checks, prefix + ":layer_media", len(layers) == 2 and all(d.get("mediaType") == LAYER_MEDIA for d in layers), [d.get("mediaType") for d in layers])
    if len(layers) != 2:
        return checks
    config_desc = manifest.get("config") if isinstance(manifest.get("config"), dict) else {}
    add(checks, prefix + ":config_media", config_desc.get("mediaType") == CONFIG_MEDIA, config_desc.get("mediaType"))
    config_bytes = read_descriptor(layout, config_desc, checks, prefix + ":config")
    try:
        config = json.loads(config_bytes)
    except Exception as exc:
        add(checks, prefix + ":config_parse", False, str(exc))
        config = {}
    else:
        add(checks, prefix + ":config_parse", True)
    diff_ids = ((config.get("rootfs") or {}).get("diff_ids") if isinstance(config.get("rootfs"), dict) else []) or []
    add(checks, prefix + ":diff_ids_match_layers", diff_ids == [d.get("digest") for d in layers], diff_ids)

    parsed_layers: list[dict[str, Any]] = []
    for i, desc in enumerate(layers):
        data = read_descriptor(layout, desc, checks, prefix + f":layer{i}")
        parsed_layers.append(parse_layer(data, checks, prefix + f":layer{i}"))
    lower, upper = parsed_layers
    lower_files_actual = {p: data for p, (kind, data) in lower["entries"].items() if kind == "file"}
    upper_files_actual = {p: data for p, (kind, data) in upper["entries"].items() if kind == "file" and not whiteout_kind(p)}
    expected_lower = {x["path"]: (x["text"] + "\n").encode("utf-8") for x in contract["lower_files"]}
    expected_upper = {x["path"]: (x["text"] + "\n").encode("utf-8") for x in contract["upper_files"]}
    add(checks, prefix + ":lower_regular_files_exact", lower_files_actual == expected_lower, sorted(lower_files_actual))
    add(checks, prefix + ":upper_regular_files_exact", upper_files_actual == expected_upper, sorted(upper_files_actual))
    markers = [p for p, (kind, data) in upper["entries"].items() if kind == "file" and whiteout_kind(p)]
    add(checks, prefix + ":one_expected_empty_marker", markers == [contract["marker"]] and upper["entries"].get(contract["marker"]) == ("file", b""), markers)
    if contract["marker_position"] == "last":
        add(checks, prefix + ":marker_last_in_tar", bool(upper["order"]) and upper["order"][-1] == contract["marker"], upper["order"])
    elif contract["marker_position"] == "first":
        marker_positions = [i for i, name in enumerate(upper["order"]) if name == contract["marker"]]
        non_dir_positions = [i for i, name in enumerate(upper["order"]) if upper["entries"].get(name, (None,))[0] == "file"]
        add(checks, prefix + ":marker_first_file_in_tar", bool(marker_positions) and marker_positions[0] == min(non_dir_positions), upper["order"])
    else:
        add(checks, prefix + ":marker_only_file", list(upper_files_actual) == [] and markers == [contract["marker"]], upper["order"])

    merged = apply_layers(parsed_layers, checks, prefix)
    for item in contract["lower_files"]:
        add(checks, prefix + f":merged_lower_absent:{item['path']}", item["path"] not in merged, sorted(merged))
    for item in contract["upper_files"]:
        expected_value = ("file", (item["text"] + "\n").encode("utf-8"))
        add(checks, prefix + f":merged_upper_present:{item['path']}", merged.get(item["path"]) == expected_value, merged.get(item["path"]))
    add(checks, prefix + ":merged_marker_absent", contract["marker"] not in merged, sorted(merged))

    # Project-specific closed-world constraint: unlike general OCI layouts, poem
    # artifacts may not conceal unreferenced blobs beside the committed image.
    expected_blob_names = {
        str(d.get("digest", "")).split(":", 1)[1]
        for d in [manifest_desc, config_desc, *layers]
        if str(d.get("digest", "")).startswith("sha256:")
    }
    blob_root = layout / "blobs" / "sha256"
    actual_blob_names = {p.name for p in blob_root.iterdir() if p.is_file()} if blob_root.is_dir() else set()
    nonfiles = [p.relative_to(layout).as_posix() for p in blob_root.rglob("*") if not p.is_file()] if blob_root.is_dir() else []
    add(checks, prefix + ":closed_world_blob_set", actual_blob_names == expected_blob_names, f"expected={sorted(expected_blob_names)} actual={sorted(actual_blob_names)}")
    add(checks, prefix + ":blob_tree_flat", not nonfiles, nonfiles)

    receipt_path = artifact / "OCI_RECEIPT.json"
    add(checks, prefix + ":receipt_exists", receipt_path.is_file(), receipt_path.as_posix())
    receipt = load_json(receipt_path) if receipt_path.is_file() else {}
    add(checks, prefix + ":receipt_schema", receipt.get("schema") == contract["receipt_schema"], receipt.get("schema"))
    add(checks, prefix + ":receipt_identity", receipt.get("draft_id") == spec.get("draft_id") and receipt.get("revision") == spec.get("revision"), receipt.get("draft_id"))
    add(checks, prefix + ":receipt_mode_marker", (receipt.get("whiteout_mode", "explicit") == contract["mode"] and receipt.get("whiteout_path") == contract["marker"]), f"{receipt.get('whiteout_mode')} {receipt.get('whiteout_path')}")
    add(checks, prefix + ":receipt_contract_exact", receipt.get("state_contract") == contract["expected_contract"], receipt.get("state_contract"))
    expected_descs = {"config": config_desc, "manifest": manifest_desc, "lower_layer": layers[0], "upper_layer": layers[1]}
    add(checks, prefix + ":receipt_descriptors_exact", receipt.get("descriptors") == expected_descs, receipt.get("descriptors"))
    if contract["schema_version"] == 2:
        add(checks, prefix + ":receipt_file_lists_exact", receipt.get("lower_files") == contract["lower_files"] and receipt.get("upper_files") == contract["upper_files"], f"lower={receipt.get('lower_files')} upper={receipt.get('upper_files')}")
        add(checks, prefix + ":receipt_blob_closure_exact", receipt.get("blob_closure") == sorted(f"sha256:{x}" for x in expected_blob_names), receipt.get("blob_closure"))

    surfaces = expected_surfaces(contract)
    for key, filename in (("lower", "lower_surface.txt"), ("upper", "upper_surface.txt"), ("merged", "merged_surface.txt")):
        p = artifact / filename
        add(checks, prefix + f":surface_exists:{key}", p.is_file(), p.as_posix())
        if p.is_file():
            add(checks, prefix + f":surface_exact:{key}", p.read_text(encoding="utf-8") == surfaces[key], p.as_posix())
    return checks


def semantic_self_tests(root: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    lower = {"order": ["appeal", "appeal/old.txt"], "entries": {"appeal": ("dir", b""), "appeal/old.txt": ("file", b"old\n")}}
    upper_marker_last = {
        "order": ["appeal", "appeal/status.txt", "appeal/.wh..wh..opq"],
        "entries": {
            "appeal": ("dir", b""),
            "appeal/status.txt": ("file", b"new\n"),
            "appeal/.wh..wh..opq": ("file", b""),
        },
    }
    merged = apply_layers([lower, upper_marker_last])
    add(checks, "oci_semantics:opaque_removes_lower", "appeal/old.txt" not in merged, merged)
    add(checks, "oci_semantics:opaque_preserves_same_layer_before_marker", merged.get("appeal/status.txt") == ("file", b"new\n"), merged)
    upper_explicit_readd = {
        "order": ["x.txt", ".wh.x.txt"],
        "entries": {"x.txt": ("file", b"replacement\n"), ".wh.x.txt": ("file", b"")},
    }
    merged2 = apply_layers([{"order": ["x.txt"], "entries": {"x.txt": ("file", b"old\n")}}, upper_explicit_readd])
    add(checks, "oci_semantics:explicit_preserves_same_layer_before_marker", merged2.get("x.txt") == ("file", b"replacement\n"), merged2)
    ancestor_collision = apply_layers([
        {"order": ["appeal"], "entries": {"appeal": ("file", b"old\n")}},
        {"order": ["appeal", "appeal/status.txt"], "entries": {"appeal": ("dir", b""), "appeal/status.txt": ("file", b"new\n")}},
    ])
    add(checks, "oci_semantics:file_ancestor_replaced_by_directory", ancestor_collision.get("appeal") == ("dir", b"") and ancestor_collision.get("appeal/status.txt") == ("file", b"new\n"), ancestor_collision)
    add(checks, "oci_semantics:whiteout_markers_never_surface", all(not whiteout_kind(p) for p in merged) and all(not whiteout_kind(p) for p in merged2), [merged, merged2])
    add(checks, "oci_paths:canonical_accept", safe_path("appeal/status.txt"), "appeal/status.txt")
    for bad in ["../escape", "/absolute", "a//b", "a/./b", "a\\b", "a/../b", "a\x00b"]:
        add(checks, f"oci_paths:canonical_reject:{bad!r}", not safe_path(bad), bad)
    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        layout = temp / "layout"
        (layout / "blobs" / "sha256").mkdir(parents=True)
        sentinel = temp / "outside"
        sentinel.write_bytes(b"must-not-be-read")
        local: list[dict[str, Any]] = []
        data = read_descriptor(layout, {"digest": "../outside:deadbeef", "size": sentinel.stat().st_size}, local, "selftest:descriptor")
        add(checks, "oci_paths:malformed_digest_returns_no_bytes", data == b"", len(data))
        add(checks, "oci_paths:malformed_digest_rejected_before_io", any(c["name"].endswith(":descriptor_path_rejected_before_io") and c["ok"] for c in local), local)
        try:
            resolve_under(layout, "../outside", label="self-test escape")
        except ValueError:
            escaped = False
        else:
            escaped = True
        add(checks, "oci_paths:declared_path_escape_rejected", not escaped, escaped)

    # The generator must obey the same containment contract as the checker.
    # Rebuild the current v2 artifact only in a temporary cube, compare every
    # byte, then exercise malicious spec-declared paths without touching the
    # real artifact or any path outside the temporary root.
    source_artifact = root / "poems/P0004/artifact/d002"
    if source_artifact.is_dir():
        with tempfile.TemporaryDirectory() as td:
            temp_root = Path(td) / "cube"
            temp_artifact = temp_root / "poems/P0004/artifact/d002"
            temp_artifact.parent.mkdir(parents=True)
            shutil.copytree(source_artifact, temp_artifact)

            def tree_hashes(base: Path) -> dict[str, str]:
                return {
                    p.relative_to(base).as_posix(): sha(p.read_bytes())
                    for p in sorted(base.rglob("*"))
                    if p.is_file() and not p.is_symlink()
                }

            before = tree_hashes(temp_artifact)
            temp_spec = temp_artifact / "OCI_POEM_SPEC.json"
            try:
                build_oci_poem(temp_root, temp_spec)
            except Exception as exc:
                add(checks, "oci_builder:deterministic_temp_rebuild", False, str(exc))
            else:
                after = tree_hashes(temp_artifact)
                add(checks, "oci_builder:deterministic_temp_rebuild", before == after, f"before={len(before)} after={len(after)}")

            original_spec = load_json(temp_spec)
            outside = Path(td) / "outside-sentinel"
            outside.write_bytes(b"unchanged")
            for label, field, value in [
                ("artifact_dir_escape", "artifact_dir", "../outside-artifact"),
                ("layout_dir_escape", "layout_dir", "../../outside-layout"),
            ]:
                malicious = dict(original_spec)
                malicious[field] = value
                temp_spec.write_text(json.dumps(malicious), encoding="utf-8")
                try:
                    build_oci_poem(temp_root, temp_spec)
                except ValueError:
                    rejected = True
                except Exception as exc:
                    rejected = False
                    add(checks, f"oci_builder:{label}:error_type", False, repr(exc))
                else:
                    rejected = False
                add(checks, f"oci_builder:{label}_rejected", rejected, value)
                add(checks, f"oci_builder:{label}_outside_unchanged", outside.read_bytes() == b"unchanged", outside)
            temp_spec.write_text(json.dumps(original_spec, indent=2) + "\n", encoding="utf-8")

            symlink_target = Path(td) / "symlink-target"
            symlink_target.mkdir()
            symlink_layout = temp_artifact / "image-link"
            try:
                symlink_layout.symlink_to(symlink_target, target_is_directory=True)
            except (OSError, NotImplementedError) as exc:
                add(checks, "oci_builder:layout_symlink_test_available", True, f"skipped:{exc}")
            else:
                malicious = dict(original_spec)
                malicious["layout_dir"] = "image-link"
                temp_spec.write_text(json.dumps(malicious), encoding="utf-8")
                try:
                    build_oci_poem(temp_root, temp_spec)
                except ValueError:
                    rejected = True
                else:
                    rejected = False
                add(checks, "oci_builder:layout_symlink_rejected", rejected, symlink_layout)
                add(checks, "oci_builder:layout_symlink_target_unchanged", list(symlink_target.iterdir()) == [], symlink_target)
    else:
        add(checks, "oci_builder:current_v2_artifact_available_for_selftest", False, source_artifact)
    return checks


def run(root: Path) -> list[dict[str, Any]]:
    specs = sorted(root.glob("poems/P*/artifact/d*/OCI_POEM_SPEC.json"))
    checks: list[dict[str, Any]] = []
    add(checks, "oci_whiteout_specs_present", bool(specs), [p.relative_to(root).as_posix() for p in specs])
    checks.extend(semantic_self_tests(root))
    for spec in specs:
        checks.extend(check_spec(root, spec))
    return checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    args = ap.parse_args()
    checks = run(Path(args.root).resolve())
    ok = all(c["ok"] for c in checks)
    print(json.dumps({"ok": ok, "check_count": len(checks), "failed": [c for c in checks if not c["ok"]], "checks": checks}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
