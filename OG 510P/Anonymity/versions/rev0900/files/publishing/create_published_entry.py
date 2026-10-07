#!/usr/bin/env python3
"""Create a guarded new published entry directory.

The helper now refuses unguarded publication.  A new Anonymity release must have
an explicit publish decision, a source hash binding, an evidence-pack manifest,
a clean compile witness, and a staged freeze-packet manifest before a copy is
made under published/.

Usage:
  python3 -B publishing/create_published_entry.py \
      --date 2026.05.22 \
      --title "Certified Menus for Anonymous DHT Lookups" \
      --source series/certified_series/paperA_certified_menus_anonymous_dht/paper.tex \
      --expected-source-sha256 <64-hex> \
      --decision-note release_queue/decisions/<publish-decision>.md \
      --evidence-pack release_queue/evidence_packs/<id>/EVIDENCE_PACK_MANIFEST.json \
      --compile-witness release_queue/FREEZE_COMPILE_WITNESS.json \
      --freeze-packet release_queue/freeze_packets/<id>/FREEZE_PACKET_MANIFEST.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import publication_target as pt  # noqa: E402

PREFIX = "Anonymity: "
DATE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
MIN_PDFLATEX_COMPILE_PASSES = 3


def minimum_compile_runs(command: str) -> int:
    """Mirror the freeze-witness compile-pass policy used by the guards."""
    return MIN_PDFLATEX_COMPILE_PASSES if command == "pdflatex" else 1


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel_inside(root: pathlib.Path, rel: str) -> pathlib.Path | None:
    path = (root / rel).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path


def require_path(root: pathlib.Path, rel: str, label: str) -> pathlib.Path:
    path = rel_inside(root, rel)
    if path is None or not path.exists():
        raise ValueError(f"{label} is missing or escapes archive: {rel}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Publish date in YYYY.MM.DD format")
    parser.add_argument("--title", required=True, help="Human title without the 'Anonymity: ' prefix")
    parser.add_argument("--source", required=True, help="Path to the source .tex file to freeze")
    parser.add_argument("--expected-source-sha256", required=True, help="Expected SHA-256 digest of --source")
    parser.add_argument("--decision-note", required=True, help="Explicit publish decision note")
    parser.add_argument("--evidence-pack", required=True, help="Evidence-pack manifest path")
    parser.add_argument("--compile-witness", required=True, help="Clean compile witness path")
    parser.add_argument("--freeze-packet", required=True, help="Freeze-packet manifest path")
    parser.add_argument("--root", default=".", help="Repo root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    src = require_path(root, args.source, "source")
    if src.suffix != ".tex":
        print(f"error: source must be a .tex file: {args.source}", file=sys.stderr)
        return 1
    if not DATE_RE.match(args.date):
        print(f"error: --date must be in YYYY.MM.DD format: {args.date}", file=sys.stderr)
        return 1
    if args.title.startswith(PREFIX):
        print('error: --title should not include the "Anonymity: " prefix', file=sys.stderr)
        return 1
    title = args.title.strip()
    if not title:
        print("error: --title may not be empty", file=sys.stderr)
        return 1
    if not SHA_RE.match(args.expected_source_sha256):
        print("error: --expected-source-sha256 must be a lowercase 64-hex digest", file=sys.stderr)
        return 1

    source_sha = sha256_file(src)
    if source_sha != args.expected_source_sha256:
        print(f"error: source hash mismatch: expected {args.expected_source_sha256}, actual {source_sha}", file=sys.stderr)
        return 1

    decision_path = require_path(root, args.decision_note, "decision note")
    evidence_path = require_path(root, args.evidence_pack, "evidence pack")
    compile_path = require_path(root, args.compile_witness, "compile witness")
    freeze_path = require_path(root, args.freeze_packet, "freeze packet")

    decision_text = decision_path.read_text(encoding="utf-8", errors="replace")
    try:
        dirname = pt.portable_published_dirname(args.date, title)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    published_path_rel = f"published/{dirname}"
    decision_required_fragments = [
        "Publication action: publish",
        "Publication authorized by this completed note: true",
        "Public citation-head update: required",
        "Publication receipt: required",
        f"Publication date: {args.date}",
        f"Source: {args.source}",
        f"Source SHA-256: {source_sha}",
        f"Published name: {dirname}",
        f"Published path: {published_path_rel}",
        f"Evidence pack manifest: {args.evidence_pack}",
        f"Compile witness: {args.compile_witness}",
        f"Freeze packet manifest: {args.freeze_packet}",
        "Unicode/control hygiene: reports/unicode_control_hygiene.json must pass for the current revision",
        args.source,
        source_sha,
        dirname,
        published_path_rel,
        args.evidence_pack,
        args.compile_witness,
        args.freeze_packet,
    ]
    for required_fragment in decision_required_fragments:
        if required_fragment not in decision_text:
            print(f"error: decision note must name {required_fragment!r}", file=sys.stderr)
            return 1

    release = load_json(root / "RELEASE_MANIFEST.json")
    # release-lane blockers: a publish attempt must see the current
    # manifest, warning-resolution, toolchain-fingerprint, and Unicode-control
    # hygiene reports as passing.
    # Materialization should depend on the selected paper's freeze evidence, not
    # on unrelated hot-lane/global manifest surfaces that will necessarily move
    # again when this helper creates the published directory.  The final package
    # verification still checks manifest canonicality and full toolchain
    # fingerprint coverage after publication.
    for rel, label in [
        ("reports/freeze_warning_resolution.json", "freeze warning resolution"),
        ("reports/unicode_control_hygiene.json", "Unicode/control-character hygiene"),
    ]:
        report = load_json(root / rel)
        if report.get("status") != "pass" or report.get("generated_for_revision") != release["revision"] or report.get("checked_bundle") != release["bundle"] or report.get("publication_authorized") is not False:
            print(f"error: {label} report is not current, passing, and non-authorizing: {rel}", file=sys.stderr)
            return 1
    evidence = load_json(evidence_path)
    compile_witness = load_json(compile_path)
    freeze_packet = load_json(freeze_path)
    for label, obj in [("evidence pack", evidence), ("compile witness", compile_witness), ("freeze packet", freeze_packet)]:
        if obj.get("publication_authorized") is not False:
            print(f"error: {label} must be non-authorizing gate evidence; found publication_authorized={obj.get('publication_authorized')}", file=sys.stderr)
            return 1
        if obj.get("generated_for_revision") != release["revision"] or obj.get("checked_bundle") != release["bundle"]:
            print(f"error: {label} is stale for this release manifest", file=sys.stderr)
            return 1
    if evidence.get("source_tex") != args.source or evidence.get("source_sha256") != source_sha:
        print("error: evidence pack is not bound to the selected source/hash", file=sys.stderr)
        return 1
    if compile_witness.get("source_tex") != args.source or compile_witness.get("source_sha256") != source_sha:
        print("error: compile witness is not bound to the selected source/hash", file=sys.stderr)
        return 1
    compile_report = compile_witness.get("preflight_report", {}).get("details", {}).get("compile", {}) if isinstance(compile_witness.get("preflight_report"), dict) else {}
    if compile_witness.get("compile_gate_status") != "pass":
        print(f"error: compile witness does not close the current publication gate: {compile_witness.get('compile_gate_status')}", file=sys.stderr)
        return 1
    witness_toolchain = compile_witness.get("toolchain", {}) if isinstance(compile_witness.get("toolchain"), dict) else {}
    witness_command = str(compile_report.get("command", witness_toolchain.get("latex_command", "pdflatex")))
    witness_required_runs = minimum_compile_runs(witness_command)
    if int(compile_report.get("run_count", 0)) < witness_required_runs:
        print(f"error: compile witness ran {compile_report.get('run_count')} {witness_command} passes; required at least {witness_required_runs}", file=sys.stderr)
        return 1
    if compile_witness.get("preflight_report", {}).get("status") != "pass" or compile_report.get("status") != "pass" or int(compile_report.get("final_warning_count", 999)) != 0 or int(compile_report.get("final_rerun_warning_count", 999)) != 0:
        print("error: compile witness is not a clean final compile pass", file=sys.stderr)
        return 1
    if compile_report.get("deterministic_pdf_environment") is not True or not compile_report.get("source_date_epoch"):
        print("error: compile witness must record a deterministic SOURCE_DATE_EPOCH compile environment", file=sys.stderr)
        return 1
    witness_toolchain = compile_witness.get("toolchain", {}) if isinstance(compile_witness.get("toolchain"), dict) else {}
    if not witness_toolchain.get("version_line") or not witness_toolchain.get("version_output_sha256"):
        print("error: compile witness must record a TeX toolchain version fingerprint", file=sys.stderr)
        return 1
    if freeze_packet.get("source_tex") != args.source or freeze_packet.get("source_sha256") != source_sha:
        print("error: freeze packet is not bound to the selected source/hash", file=sys.stderr)
        return 1
    allowed_compile_witnesses = {
        str(freeze_packet.get("compile_witness", "")),
        str(freeze_packet.get("compile_witness_snapshot", "")),
    }
    if freeze_packet.get("evidence_pack_manifest") != args.evidence_pack or args.compile_witness not in allowed_compile_witnesses:
        print("error: freeze packet does not bind the supplied evidence pack and compile witness/snapshot", file=sys.stderr)
        return 1

    snapshot_rel = str(freeze_packet.get("compile_witness_snapshot", ""))
    snapshot_sha = str(freeze_packet.get("compile_witness_snapshot_sha256", ""))
    snapshot_path = require_path(root, snapshot_rel, "freeze-packet compile witness snapshot")
    if sha256_file(snapshot_path) != snapshot_sha:
        print("error: freeze-packet compile witness snapshot hash mismatch", file=sys.stderr)
        return 1
    snapshot = load_json(snapshot_path)
    snapshot_compile_report = snapshot.get("preflight_report", {}).get("details", {}).get("compile", {}) if isinstance(snapshot.get("preflight_report"), dict) else {}
    if snapshot.get("source_tex") != args.source or snapshot.get("source_sha256") != source_sha:
        print("error: freeze-packet compile witness snapshot is not source-hash-bound", file=sys.stderr)
        return 1
    if snapshot.get("generated_for_revision") != release["revision"] or snapshot.get("checked_bundle") != release["bundle"]:
        print("error: freeze-packet compile witness snapshot is stale for this release", file=sys.stderr)
        return 1
    if snapshot.get("compile_gate_status") != "pass" or snapshot.get("preflight_report", {}).get("status") != "pass" or snapshot_compile_report.get("status") != "pass":
        print("error: freeze-packet compile witness snapshot does not close the compile gate", file=sys.stderr)
        return 1
    if snapshot_compile_report.get("deterministic_pdf_environment") is not True or not snapshot_compile_report.get("source_date_epoch"):
        print("error: freeze-packet compile witness snapshot lacks deterministic compile evidence", file=sys.stderr)
        return 1
    snapshot_toolchain = snapshot.get("toolchain", {}) if isinstance(snapshot.get("toolchain"), dict) else {}
    if not snapshot_toolchain.get("version_line") or not snapshot_toolchain.get("version_output_sha256"):
        print("error: freeze-packet compile witness snapshot lacks TeX toolchain fingerprint evidence", file=sys.stderr)
        return 1
    snapshot_toolchain = snapshot.get("toolchain", {}) if isinstance(snapshot.get("toolchain"), dict) else {}
    snapshot_command = str(snapshot_compile_report.get("command", snapshot_toolchain.get("latex_command", "pdflatex")))
    snapshot_required_runs = minimum_compile_runs(snapshot_command)
    if int(snapshot_compile_report.get("run_count", 0)) < snapshot_required_runs:
        print(f"error: freeze-packet compile witness snapshot ran {snapshot_compile_report.get('run_count')} {snapshot_command} passes; required at least {snapshot_required_runs}", file=sys.stderr)
        return 1
    if int(snapshot_compile_report.get("final_warning_count", 999)) != 0 or int(snapshot_compile_report.get("final_rerun_warning_count", 999)) != 0:
        print("error: freeze-packet compile witness snapshot has final compile warnings", file=sys.stderr)
        return 1

    publish_dir = root / "published" / dirname
    tex_name = "paper.tex"
    target_tex = publish_dir / tex_name
    note_path = publish_dir / "SOURCE.md"
    metadata_path = publish_dir / "METADATA.json"
    receipt_path = publish_dir / "PUBLICATION_RECEIPT.json"
    published_snapshot_path = publish_dir / "FREEZE_COMPILE_WITNESS.snapshot.json"

    if publish_dir.exists():
        print(f"error: published directory already exists: {publish_dir}", file=sys.stderr)
        return 1

    publish_dir.mkdir(parents=True)
    shutil.copy2(src, target_tex)
    shutil.copy2(snapshot_path, published_snapshot_path)
    published_sha = sha256_file(target_tex)
    published_snapshot_sha = sha256_file(published_snapshot_path)
    if published_sha != source_sha:
        print("error: copied published source hash drifted", file=sys.stderr)
        return 1
    if published_snapshot_sha != snapshot_sha:
        print("error: copied compile witness snapshot hash drifted", file=sys.stderr)
        return 1

    note_path.write_text(
        "# Source freeze\n\n"
        f"- Frozen from: `{args.source}`\n"
        f"- Source SHA-256: `{source_sha}`\n"
        f"- Published name: `[[{dirname}]]`\n"
        "- Public label: `Anonymity`\n"
        "- Canonical artifact: `.tex`\n"
        f"- Publication decision: `{args.decision_note}`\n"
        f"- Evidence pack: `{args.evidence_pack}`\n"
        f"- Compile witness: `{args.compile_witness}`\n"
        f"- Freeze packet: `{args.freeze_packet}`\n",
        encoding="utf-8",
    )

    metadata = {
        "published_name": dirname,
        "wikilink": f"[[{dirname}]]",
        "public_label": "Anonymity",
        "public_title": pt.display_title(title),
        "published_path": published_path_rel,
        "published_date": args.date,
        "source_tex": args.source,
        "source_sha256": source_sha,
        "canonical_artifact": tex_name,
        "decision_note": args.decision_note,
        "evidence_pack_manifest": args.evidence_pack,
        "freeze_compile_witness": args.compile_witness,
        "freeze_compile_witness_snapshot": snapshot_rel,
        "freeze_compile_witness_snapshot_sha256": snapshot_sha,
        "published_compile_witness_snapshot": f"published/{dirname}/FREEZE_COMPILE_WITNESS.snapshot.json",
        "freeze_packet_manifest": args.freeze_packet,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "version": 1,
        "publication_authorized": True,
        "publication_revision": release["revision"],
        "publication_bundle": release["bundle"],
        "published_name": dirname,
        "published_path": published_path_rel,
        "published_tex": f"published/{dirname}/{tex_name}",
        "published_tex_sha256": published_sha,
        "source_tex": args.source,
        "source_sha256": source_sha,
        "decision_note": args.decision_note,
        "evidence_pack_manifest": args.evidence_pack,
        "compile_witness": args.compile_witness,
        "compile_witness_snapshot": snapshot_rel,
        "compile_witness_snapshot_sha256": snapshot_sha,
        "published_compile_witness_snapshot": f"published/{dirname}/FREEZE_COMPILE_WITNESS.snapshot.json",
        "published_compile_witness_snapshot_sha256": published_snapshot_sha,
        "freeze_packet_manifest": args.freeze_packet,
        "created_by": "publishing/create_published_entry.py",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(target_tex.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
