#!/usr/bin/env python3
"""tools/observer_verify_packet.py

Offline integrity checks for an evidence packet directory.

Checks:
- content-addressed objects: sha256 matches filename (sha256-<hex>.*)
- envelopes: payload_digest and tbs_digest recompute cleanly (docs/176)
- payload pointers: referenced object exists, hash/size match pointer
- attachments: referenced objects exist and hash/size match; optional receipt profile validation
- manifest: referenced digests/urls exist and hash/size match (best effort)

Signature verification is NOT performed (stdlib-only).
"""

from __future__ import annotations

import argparse
import csv
import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from jcs import dump_bytes as jcs_bytes

from envelope_common import (
    canonicalize_payload_bytes_for_digest,
    payload_digest_for_json_value,
    sha256_hex,
    tbs_digest_for_envelope,
)

from path_safety import safe_join

from verifier_problem_codes import code_of, is_known, severity as severity_for_code, all_codes_sorted, CODES

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PROFILE_REGISTRY = ROOT / "artifacts" / "registries" / "receipt-profiles.csv"
KIND_REGISTRY = ROOT / "artifacts" / "registries" / "envelope-kinds.csv"
ATTACHMENT_REQUIREMENTS = ROOT / "artifacts" / "registries" / "envelope-attachment-requirements.csv"
VERIFIER_PROBLEM_CODES_REGISTRY = ROOT / "artifacts" / "registries" / "verifier-problem-codes.csv"
ARCHIVE_VERSION_FILE = ROOT / "VERSION"

SUPPORTED_ENVELOPE_MAJORS = {1}
REPORT_VERSION = "1.1.0"  # schemas/PacketVerificationReport.json


def iso_utc_now_seconds() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_archive_version() -> str:
    try:
        return ARCHIVE_VERSION_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return "unknown"


def load_kind_registry() -> dict[str, dict[str, str]]:
    """Load artifacts/registries/envelope-kinds.csv into a kind->row map."""
    if not KIND_REGISTRY.exists():
        return {}
    out: dict[str, dict[str, str]] = {}
    with KIND_REGISTRY.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            k = (row.get("kind") or "").strip()
            if k:
                out[k] = {kk: (row.get(kk) or "").strip() for kk in (r.fieldnames or [])}
    return out


def load_attachment_requirements() -> dict[str, list[dict[str, str]]]:
    """Load required attachment rels per kind (yes-only)."""
    if not ATTACHMENT_REQUIREMENTS.exists():
        return {}
    out: dict[str, list[dict[str, str]]] = {}
    with ATTACHMENT_REQUIREMENTS.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            kind = (row.get("kind") or "").strip()
            if not kind:
                continue
            if (row.get("required") or "").strip().lower() != "yes":
                continue
            out.setdefault(kind, []).append(
                {
                    "rel": (row.get("rel") or "").strip(),
                    "media_type": (row.get("media_type") or "").strip(),
                    "attachment_schema": (row.get("attachment_schema") or "").strip(),
                }
            )
    return out


def load_receipt_profiles() -> set[str]:
    if not RECEIPT_PROFILE_REGISTRY.exists():
        return set()
    profiles = set()
    try:
        with RECEIPT_PROFILE_REGISTRY.open("r", encoding="utf-8", newline="") as f:
            r = csv.DictReader(f)
            for row in r:
                p = row.get("profile")
                if p:
                    profiles.add(p)
    except Exception:
        return set()
    return profiles


RECEIPT_PROFILES = load_receipt_profiles()
KIND_ROWS = load_kind_registry()
ATT_REQS = load_attachment_requirements()
ARCHIVE_VERSION = load_archive_version()


def parse_semver_major(v: str) -> int | None:
    try:
        parts = v.split(".")
        if len(parts) != 3:
            return None
        return int(parts[0])
    except Exception:
        return None


def read_payload_bytes_from_pointer(env: Dict[str, Any], packet_dir: Path) -> Tuple[bytes, str, str, List[str]]:
    """Load payload bytes and validate pointer hash/size when present."""
    problems: List[str] = []

    ptr = env.get("payload_pointer")
    if not isinstance(ptr, dict):
        return b"", "missing_payload_pointer", "", ["payload_pointer_missing"]

    uri = ptr.get("uri", "")
    if not uri:
        return b"", "missing_uri", "", ["payload_pointer_missing_uri"]

    rel = uri if uri.startswith("objects/") else f"objects/{uri}"
    p = safe_join(packet_dir, rel)
    if p is None:
        return b"", f"unsafe:{uri}", ptr.get("media_type", ""), ["payload_pointer_unsafe_uri"]
    if not p.exists():
        return b"", f"missing:{uri}", ptr.get("media_type", ""), ["payload_pointer_object_missing"]
    hardened = safe_join(packet_dir, rel, must_exist=True)
    if hardened is None:
        return b"", f"unsafe:{uri}", ptr.get("media_type", ""), ["payload_pointer_unsafe_uri"]

    b = hardened.read_bytes()

    # Pointer integrity: hash + size match the referenced object bytes.
    want_digest = ptr.get("digest")
    if isinstance(want_digest, str) and want_digest.startswith("sha256:"):
        want_hex = want_digest.split(":", 1)[1]
        got_hex = sha256_hex(b)
        if got_hex.lower() != want_hex.lower():
            problems.append(f"payload_pointer_hash_mismatch:{uri}")

    if "size_bytes" in ptr:
        try:
            if int(p.stat().st_size) != int(ptr["size_bytes"]):
                problems.append(f"payload_pointer_size_mismatch:{uri}")
        except Exception:
            pass

    return b, f"objects/{uri}", ptr.get("media_type", ""), problems


def recompute_payload_digest(env: Dict[str, Any], packet_dir: Path) -> Tuple[str, str, List[str]]:
    """Recompute payload_digest per docs/176."""
    if "payload_inline" in env:
        try:
            return payload_digest_for_json_value(env["payload_inline"]), "inline", []
        except Exception:
            # Best effort: if object can't be canonicalized, fall back to a sentinel.
            return "sha256:" + ("0" * 64), "inline", ["payload_inline_unserializable"]

    payload_bytes, where, media_type, problems = read_payload_bytes_from_pointer(env, packet_dir)
    if not payload_bytes:
        return "sha256:" + ("0" * 64), where, problems

    canon = env.get("canonicalization", "")
    bytes_to_hash, note = canonicalize_payload_bytes_for_digest(payload_bytes, media_type, canon)
    if note == "raw_non_json_media_type":
        problems.append("payload_pointer_media_type_not_json")
    elif note == "raw_json_parse_failed":
        problems.append("payload_pointer_json_parse_failed")
    return f"sha256:{sha256_hex(bytes_to_hash)}", where, problems


def verify_objects(objects_dir: Path) -> Tuple[List[str], int]:
    problems: List[str] = []
    checked = 0
    if not objects_dir.exists():
        return ["objects_dir_missing"], 0
    for p in objects_dir.iterdir():
        if not p.is_file():
            continue
        name = p.name
        if not name.startswith("sha256-"):
            continue
        checked += 1
        hexpart = name[len("sha256-") :].split(".", 1)[0]
        got = sha256_hex(p.read_bytes())
        if got.lower() != hexpart.lower():
            problems.append(f"object_hash_mismatch:{name}")
    return problems, checked


def verify_attachments(env: Dict[str, Any], packet_dir: Path, env_name: str) -> List[str]:
    problems: List[str] = []
    atts = env.get("attachments")
    if not atts:
        return problems
    if not isinstance(atts, list):
        return [f"attachments_not_array:{env_name}"]

    for i, att in enumerate(atts):
        if not isinstance(att, dict):
            problems.append(f"attachment_not_object:{env_name}:{i}")
            continue
        d = att.get("digest")
        if not d or not isinstance(d, str) or not d.startswith("sha256:"):
            problems.append(f"attachment_missing_digest:{env_name}:{i}")
            continue
        uri = att.get("uri", "")
        if not uri:
            problems.append(f"attachment_missing_uri:{env_name}:{i}:{d}")
            continue
        rel = uri if uri.startswith("objects/") else f"objects/{uri}"
        tgt = safe_join(packet_dir, rel)
        if tgt is None:
            problems.append(f"attachment_unsafe_uri:{env_name}:{i}:{d}")
            continue
        if not tgt.exists():
            problems.append(f"attachment_missing_object:{env_name}:{i}:{d}")
            continue
        hardened = safe_join(packet_dir, rel, must_exist=True)
        if hardened is None:
            problems.append(f"attachment_unsafe_uri:{env_name}:{i}:{d}")
            continue

        b = hardened.read_bytes()
        got = sha256_hex(b)
        want = d.split(":", 1)[1]
        if got.lower() != want.lower():
            problems.append(f"attachment_hash_mismatch:{env_name}:{i}:{tgt.relative_to(packet_dir)}")
            continue

        if "size_bytes" in att:
            try:
                if int(tgt.stat().st_size) != int(att["size_bytes"]):
                    problems.append(f"attachment_size_mismatch:{env_name}:{i}:{tgt.relative_to(packet_dir)}")
            except Exception:
                pass

        # Optional: validate receipt profile identifiers (drift firewall)
        if att.get("rel") == "transparency_receipt" and tgt.suffix == ".json":
            try:
                robj = json.loads(tgt.read_text(encoding="utf-8"))
                prof = robj.get("profile")
                if not prof:
                    problems.append(f"receipt_profile_missing:{env_name}:{i}")
                elif RECEIPT_PROFILES and prof not in RECEIPT_PROFILES:
                    problems.append(f"receipt_profile_unknown:{env_name}:{i}:{prof}")
            except Exception:
                problems.append(f"receipt_unparseable:{env_name}:{i}")

    return problems


def verify_envelopes(env_dir: Path, packet_dir: Path) -> Tuple[List[str], int, Dict[str, int]]:
    problems: List[str] = []
    checked = 0
    kinds_seen: Dict[str, int] = {}
    if not env_dir.exists():
        return ["envelopes_dir_missing"], 0, {}

    for p in env_dir.iterdir():
        if not p.is_file() or not p.name.endswith(".json"):
            continue
        checked += 1
        env = json.loads(p.read_text(encoding="utf-8"))

        kind = str(env.get("kind", "")).strip()
        if kind:
            kinds_seen[kind] = kinds_seen.get(kind, 0) + 1

        # Envelope version interop: reject unknown major versions.
        ev = str(env.get("envelope_version", "")).strip()
        maj = parse_semver_major(ev)
        if maj is None:
            problems.append(f"envelope_version_unparseable:{p.name}:{ev}")
        elif maj not in SUPPORTED_ENVELOPE_MAJORS:
            problems.append(f"envelope_version_unsupported_major:{p.name}:{ev}")

        canon = str(env.get("canonicalization", "")).strip()
        if canon != "RFC8785-JCS":
            problems.append(f"canonicalization_unsupported:{p.name}:{canon or 'missing'}")

        # Registry checks (tight verifier surface).
        row = KIND_ROWS.get(kind)
        if not row:
            if kind:
                problems.append(f"unknown_kind:{p.name}:{kind}")
        else:
            expected_schema = row.get("payload_schema", "").strip()
            got_schema = str(env.get("payload_schema", "")).strip()
            if got_schema and expected_schema and got_schema != expected_schema:
                problems.append(f"payload_schema_mismatch:{p.name}:{kind}:{got_schema}:{expected_schema}")
            expected_track = row.get("track", "").strip()
            got_track = str(env.get("track", "")).strip()
            # Track strings are sometimes human-annotated (e.g., "A (Deployable core)").
            if got_track and expected_track:
                ok_track = (
                    got_track == expected_track
                    or got_track.startswith(expected_track + " ")
                    or got_track.startswith(expected_track + "(")
                )
                if not ok_track:
                    problems.append(f"track_mismatch:{p.name}:{kind}:{got_track}:{expected_track}")

            # Required attachments per kind (anti-selective-disclosure).
            required = ATT_REQS.get(kind) or []
            if required:
                atts = env.get("attachments") or []
                rels_present: dict[str, list[dict]] = {}
                if isinstance(atts, list):
                    for a in atts:
                        if isinstance(a, dict):
                            r = str(a.get("rel", "")).strip()
                            if r:
                                rels_present.setdefault(r, []).append(a)
                for req in required:
                    rel = req.get("rel", "").strip()
                    if not rel:
                        continue
                    if rel not in rels_present:
                        problems.append(f"missing_required_attachment:{p.name}:{kind}:{rel}")
                        continue
                    # Best-effort media_type match (drift firewall).
                    exp_mt = req.get("media_type", "").strip()
                    if exp_mt:
                        for a in rels_present[rel]:
                            mt = (a.get("media_type") or a.get("content_type") or "").strip()
                            if mt and mt != exp_mt:
                                problems.append(f"attachment_media_type_mismatch:{p.name}:{kind}:{rel}:{mt}:{exp_mt}")
        problems += verify_attachments(env, packet_dir, p.name)

        recomputed, where, ptr_problems = recompute_payload_digest(env, packet_dir)
        for pp in ptr_problems:
            problems.append(f"{pp}:{p.name}")
        if recomputed != env.get("payload_digest"):
            problems.append(f"payload_digest_mismatch:{p.name}:{where}")

        # Optional: enforce payload_schema is a real file for schema-path references.
        ps = env.get("payload_schema")
        if isinstance(ps, str) and ps.startswith("schemas/"):
            if not (ROOT / ps).exists():
                problems.append(f"payload_schema_missing:{p.name}:{ps}")

        tbs_digest = tbs_digest_for_envelope(env)
        if tbs_digest != env.get("tbs_digest"):
            problems.append(f"tbs_digest_mismatch:{p.name}")

    return problems, checked, kinds_seen


def verify_manifest(packet_dir: Path) -> List[str]:
    problems: List[str] = []

    mpath = packet_dir / "manifest.json"
    if not mpath.exists():
        return ["manifest_missing"]

    m = json.loads(mpath.read_text(encoding="utf-8"))
    arts = m.get("artifacts", [])
    for a in arts:
        if not isinstance(a, dict):
            continue

        d = a.get("digest") or (("sha256:" + a["sha256"]) if "sha256" in a else "")
        if not isinstance(d, str) or not d.startswith("sha256:"):
            continue
        want_hex = d.split(":", 1)[1]

        # Prefer url field when present.
        url = a.get("url")
        if isinstance(url, str) and url:
            fp = safe_join(packet_dir, url)
            if fp is None:
                problems.append(f"manifest_url_unsafe:{a.get('name','?')}:{url}")
                continue
            if not fp.exists():
                problems.append(f"manifest_url_missing:{a.get('name','?')}:{url}")
                continue
            hardened = safe_join(packet_dir, url, must_exist=True)
            if hardened is None:
                problems.append(f"manifest_url_unsafe:{a.get('name','?')}:{url}")
                continue
            got_hex = sha256_hex(hardened.read_bytes())
            if got_hex.lower() != want_hex.lower():
                problems.append(f"manifest_url_hash_mismatch:{a.get('name','?')}:{url}")
                continue
            if "size_bytes" in a:
                try:
                    if int(fp.stat().st_size) != int(a["size_bytes"]):
                        problems.append(f"manifest_url_size_mismatch:{a.get('name','?')}:{url}")
                except Exception:
                    pass
            continue

        # Fallback: locate by digest in common locations.
        found = False
        for root in [packet_dir / "objects", packet_dir]:
            for ext in [".json", ".bin", ".txt", ".md", ".csv", ".toml", ""]:
                pp = root / f"sha256-{want_hex}{ext}"
                if pp.exists():
                    found = True
                    break
            if found:
                break
        if not found:
            problems.append(f"missing_artifact_object:{a.get('name','?')}:{d}")

    return problems


def build_report(packet_dir: Path, problems: List[str], envelopes_checked: int, objects_checked: int, kinds_seen: Dict[str, int], public: bool, verifier_report_tbs_digest: str | None = None) -> Dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    # Public mode: avoid leaking absolute paths and keep outputs comparable.
    packet_id = packet_dir.name if public else str(packet_dir)
    notes: List[str] = ["Signature verification not performed by this stdlib-only tool."]

    # Drift firewall: if the verifier emits an unknown code, add a stable sentinel.
    # Keep the original problem strings (they may contain useful local context).
    if not public:
        codes = sorted(set([code_of(x) for x in problems if isinstance(x, str) and x.strip()]))
        unknown = [c for c in codes if c and not is_known(c)]
        if unknown:
            for c in unknown:
                problems.append(f"unknown_problem_code:{c}")
            notes.append(f"Detected {len(unknown)} unrecognized problem code(s); emitted unknown_problem_code sentinel(s).")
    if public:
        codes = sorted(set([code_of(x) for x in problems if isinstance(x, str) and x.strip()]))
        unknown = [c for c in codes if c and not is_known(c)]
        codes = [c for c in codes if c and is_known(c)]
        if unknown:
            # Public mode only publishes stable codes; collapse any unrecognized codes.
            codes.append("unknown_problem_code")
            codes = sorted(set(codes))
            notes.append(f"Suppressed {len(unknown)} unknown problem code(s) in public output.")
        problems = codes
    report: Dict[str, Any] = {
        "report_version": REPORT_VERSION,
        "generated_at": generated_at,
        "packet_dir": packet_id,
        "tool": {
            "name": "observer_verify_packet",
            "version": ARCHIVE_VERSION,
            "archive_version": ARCHIVE_VERSION,
        },
        "status": (
            "PASS"
            if not problems
            else ("FAIL" if any(severity_for_code(code_of(p)) == "FAIL" for p in problems) else "PASS_WITH_WARNINGS")
        ),
        "problems": list(problems),
        "envelopes_checked": int(envelopes_checked),
        "objects_checked": int(objects_checked),
        "kinds_seen": dict(sorted(kinds_seen.items())),
        "notes": notes,
    }

    # Optional: link packet-scoped results to an implementation-scoped verifier identity report.
    # This is publishable and enables comparison across verifier identities.
    if verifier_report_tbs_digest:
        report["verifier_report_tbs_digest"] = verifier_report_tbs_digest


    # Optional comparability pins: include sha256 of key public-surface registries when available.
    try:
        if VERIFIER_PROBLEM_CODES_REGISTRY.exists():
            report["verifier_problem_codes_sha256"] = "sha256:" + sha256_hex_bytes(VERIFIER_PROBLEM_CODES_REGISTRY.read_bytes())
    except Exception:
        pass

    try:
        if KIND_REGISTRY.exists():
            report["envelope_kinds_sha256"] = "sha256:" + sha256_hex_bytes(KIND_REGISTRY.read_bytes())
    except Exception:
        pass

    mpath = packet_dir / "manifest.json"
    if mpath.exists():
        try:
            report["manifest_sha256"] = "sha256:" + sha256_hex_bytes(mpath.read_bytes())
        except Exception:
            pass

    return report


def _best_effort_election_id(packet_dir: Path) -> str:
    """Pull election_id from a packet manifest when available."""
    try:
        m = json.loads((packet_dir / "manifest.json").read_text(encoding="utf-8"))
        eid = (m.get("election_id") or "").strip()
        return eid or "ELECTION_UNKNOWN"
    except Exception:
        return "ELECTION_UNKNOWN"


def emit_report_as_packet(out_dir: Path, report_public: Dict[str, Any], issuer_id: str, subject_extra: Dict[str, Any] | None = None) -> Path:
    """Emit a minimal evidence packet containing a publishable PacketVerificationReport.

    Returns the written envelope path.
    """

    out_dir = out_dir.resolve()
    (out_dir / "objects").mkdir(parents=True, exist_ok=True)
    (out_dir / "envelopes").mkdir(parents=True, exist_ok=True)
    (out_dir / "notes").mkdir(parents=True, exist_ok=True)

    payload_bytes = jcs_bytes(report_public)
    payload_hex = sha256_hex(payload_bytes)
    payload_digest = f"sha256:{payload_hex}"

    obj_name = f"sha256-{payload_hex}.json"
    obj_path = out_dir / "objects" / obj_name
    if not obj_path.exists():
        obj_path.write_bytes(payload_bytes)

    issued_at = iso_utc_now_seconds()
    subject: Dict[str, Any] = {
        "packet_dir": report_public.get("packet_dir", ""),
    }
    if isinstance(report_public.get("manifest_sha256"), str) and report_public.get("manifest_sha256"):
        subject["packet_manifest_sha256"] = report_public["manifest_sha256"]
    if subject_extra:
        for k, v in subject_extra.items():
            if k not in subject:
                subject[k] = v

    env: Dict[str, Any] = {
        "envelope_version": "1.1.0",
        "kind": "hfv.verifier.packet_verification_report",
        "track": "A",
        "issued_at": issued_at,
        "issuer": {"issuer_id": issuer_id},
        "subject": subject,
        "payload_schema": "schemas/PacketVerificationReport.json",
        "canonicalization": "RFC8785-JCS",
        "payload_digest": payload_digest,
        "payload_pointer": {
            "digest": payload_digest,
            "media_type": "application/json",
            "size_bytes": int(len(payload_bytes)),
            "uri": obj_name,
        },
    }
    env["tbs_digest"] = tbs_digest_for_envelope(env)
    env["signatures"] = [
        {
            "signer_id": issuer_id,
            "alg": "none",
            "sig": "UNSIGNED",
            "sig_encoding": "base64",
        }
    ]

    env_path = out_dir / "envelopes" / f"packet_verification_report_{payload_hex[:16]}.json"
    env_path.write_text(json.dumps(env, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Minimal manifest (so this packet can be re-verified offline).
    created_at = issued_at
    election_id = (subject_extra or {}).get("election_id") or "ELECTION_UNKNOWN"
    manifest = {
        "election_id": election_id,
        "created_at": created_at,
        "crypto_policy": {
            "election_id": election_id,
            "allowed_crypto_suites": ["hfv.placeholder.suite"],
            "default_crypto_suite": "hfv.placeholder.suite",
            "deprecation": [],
            "notes": "Placeholder crypto policy for verifier report packets; replace in production bundles.",
        },
        "artifacts": [
            {
                "name": "PacketVerificationReport envelope",
                "media_type": "application/json",
                "digest": f"sha256:{sha256_hex(env_path.read_bytes())}",
                "size_bytes": int(env_path.stat().st_size),
                "url": str(env_path.relative_to(out_dir)).replace("\\\\", "/"),
                "kind": "hfv.envelope",
                "schema": "schemas/EvidenceEnvelope.json",
            },
            {
                "name": "PacketVerificationReport payload (detached)",
                "media_type": "application/json",
                "digest": payload_digest,
                "size_bytes": int(obj_path.stat().st_size),
                "url": str(obj_path.relative_to(out_dir)).replace("\\\\", "/"),
                "kind": "hfv.verifier.packet_verification_report",
                "schema": "schemas/PacketVerificationReport.json",
            },
        ],
        "signatures": [
            {
                "signer_id": issuer_id,
                "alg": "none",
                "sig": "UNSIGNED",
            }
        ],
        "bundle_version": "0.1",
        "created_by": "tools/observer_verify_packet.py --emit-evidence-object",
        "notes": "This packet is a minimal verifier-report bundle. Replace placeholder signatures/crypto policy.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    readme = out_dir / "notes" / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Verifier report packet\n\n"
            "This is a minimal evidence packet containing a publishable `PacketVerificationReport` as an `EvidenceEnvelope`.\n\n"
            "Generated by `tools/observer_verify_packet.py --emit-evidence-object`.\n",
            encoding="utf-8",
            newline="\n",
        )

    return env_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packet_dir", nargs="?", default="", help="Packet directory")
    ap.add_argument("--list-codes", action="store_true", help="List publishable verifier problem codes and exit")
    ap.add_argument("--explain", default="", help="Explain one verifier problem code (or problem string) and exit")
    ap.add_argument("--json", action="store_true", help="Emit PacketVerificationReport JSON to stdout")
    ap.add_argument("--public", action="store_true", help="Public-safe output: codes only; sanitize packet_dir")
    ap.add_argument("--out", help="Write PacketVerificationReport JSON to this path")
    ap.add_argument(
        "--emit-evidence-object",
        dest="emit_packet_dir",
        default="",
        help="Emit a minimal verifier-report evidence packet to this directory (always uses public-safe payload)",
    )
    ap.add_argument(
        "--verifier-report-envelope",
        default="",
        help="Optional: path to an EvidenceEnvelope JSON of kind hfv.verifier.report; include its tbs_digest in the PacketVerificationReport as verifier_report_tbs_digest",
    )
    ap.add_argument(
        "--verifier-report-tbs-digest",
        default="",
        help="Optional: set verifier_report_tbs_digest directly (sha256:<hex>)",
    )

    ap.add_argument(
        "--issuer-id",
        default="verifier:observer_verify_packet",
        help="issuer_id to place in the emitted EvidenceEnvelope/manifest (for --emit-evidence-object)",
    )
    args = ap.parse_args()
    if args.list_codes:
        print("Verifier problem codes (publishable surface)")
        for pc in all_codes_sorted():
            print(f"{pc.code}	{pc.severity}	{pc.summary}")
        return 0

    if args.explain:
        code = code_of(args.explain)
        pc = CODES.get(code)
        if not pc:
            # Fail closed: unknown codes should not be normalized into publication without review.
            print(f"UNKNOWN	{code}")
            print(CODES["unknown_problem_code"].summary)
            return 2
        print(f"{pc.code}	{pc.severity}	{pc.summary}")
        return 0

    if not args.packet_dir:
        ap.error("packet_dir is required unless --list-codes or --explain is used")

    packet_dir = Path(args.packet_dir)

    verifier_report_tbs_digest: str | None = None
    # Optional linkage: allow packet reports to point at an implementation-scoped verifier report envelope.
    if args.verifier_report_tbs_digest:
        v = args.verifier_report_tbs_digest.strip()
        if re.fullmatch(r"sha256:[0-9a-f]{64}", v):
            verifier_report_tbs_digest = v
        else:
            # Do not treat as a packet failure; just ignore and keep the report publishable.
            # Avoid leaking full paths in public notes.
            pass
    elif args.verifier_report_envelope:
        p = Path(args.verifier_report_envelope)
        try:
            env_obj = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(env_obj, dict) and env_obj.get("kind") == "hfv.verifier.report":
                computed = tbs_digest_for_envelope(env_obj)
                # If the envelope includes a tbs_digest field and it disagrees, ignore the linkage.
                existing = env_obj.get("tbs_digest")
                if isinstance(existing, str) and existing and existing != computed:
                    # Don't fail the packet; just avoid publishing a confusing pointer.
                    pass
                else:
                    verifier_report_tbs_digest = computed
        except Exception:
            pass

    problems: List[str] = []
    obj_problems, objects_checked = verify_objects(packet_dir / "objects")
    problems += obj_problems
    env_problems, envelopes_checked, kinds_seen = verify_envelopes(packet_dir / "envelopes", packet_dir)
    problems += env_problems
    problems += verify_manifest(packet_dir)

    report = build_report(packet_dir, problems, envelopes_checked, objects_checked, kinds_seen, args.public, verifier_report_tbs_digest=verifier_report_tbs_digest)

    # Optional: emit a publishable evidence object as its own minimal packet.
    if args.emit_packet_dir:
        report_public = build_report(packet_dir, problems, envelopes_checked, objects_checked, kinds_seen, True, verifier_report_tbs_digest=verifier_report_tbs_digest)
        subject_extra = {"election_id": _best_effort_election_id(packet_dir)}
        emit_report_as_packet(Path(args.emit_packet_dir), report_public, issuer_id=args.issuer_id, subject_extra=subject_extra)

    if args.out:
        try:
            Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except Exception as e:
            # If we can't write the report, fail closed.
            problems.append(f"report_write_failed:{args.out}:{e}")
            report = build_report(packet_dir, problems, envelopes_checked, objects_checked, kinds_seen, args.public, verifier_report_tbs_digest=verifier_report_tbs_digest)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if not problems else 2

    if problems:
        for p in problems:
            print("PROBLEM", p)
        return 2
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
