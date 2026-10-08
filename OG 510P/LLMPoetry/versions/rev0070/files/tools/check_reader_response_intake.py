#!/usr/bin/env python3
"""Validate practical reader handoff and response-intake path.

Rev0040 closes two remaining completion risks: the checker now exercises the
actual append path inside an isolated temporary clone, and response-log PII scans
look only at reader-supplied fields so tool-managed timestamps do not make a real
future response fail as a false phone-number match. It also verifies duplicate
content fingerprint rejection. This remains readiness/privacy/admission guarding,
not poem-quality evidence.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONEISH_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")
CURRENT_HEAD = "P0002-D010"
def is_candidate_successor_head(head: str | None) -> bool:
    if not isinstance(head, str) or not head.startswith("P0002-D"):
        return False
    try:
        return int(head.split("-D", 1)[1]) >= 11
    except ValueError:
        return False
PACKET = Path("anthology/candidates/P0002-D010_disclosed_reader_packet.json")
ONE_MD = Path("anthology/candidates/P0002-D010_reader_one_sheet.md")
ONE_HTML = Path("anthology/candidates/P0002-D010_reader_one_sheet.html")
FORM_MD = Path("anthology/candidates/P0002-D010_reader_response_form.md")
FORM_HTML = Path("anthology/candidates/P0002-D010_reader_response_form.html")
TEMPLATE = Path("anthology/candidates/P0002-D010_response_intake_template.json")
LOG = Path("anthology/candidates/P0002-D010_reader_responses.json")
TOOL = Path("tools/record_reader_response.py")
SCHEMA = Path("schemas/reader_response_intake.schema.json")
HANDOFF_DIR = Path("anthology/candidates/P0002-D010_reader_handoff")
HANDOFF_MANIFEST = HANDOFF_DIR / "HANDOFF_MANIFEST.json"
HANDOFF_BUNDLE = Path("anthology/candidates/P0002-D010_reader_handoff_bundle.zip")
HANDOFF_BUNDLE_SIDECAR = Path("anthology/candidates/P0002-D010_reader_handoff_bundle.zip.sha256")
REQUIRED_RESPONSE_FIELDS = {
    "disclosure_seen_before_poem",
    "source_packet_opened_before_first_response",
    "boundary_acknowledged",
    "keep_reject_uncertain",
    "strongest_line_or_phrase",
    "weakest_line_or_phrase",
    "disclosure_delta",
    "body_works_without_source_packet",
    "documentation_doing_poem_work",
    "revision_instruction",
}
TEXT_FIELDS = {
    "strongest_line_or_phrase",
    "weakest_line_or_phrase",
    "documentation_doing_poem_work",
    "revision_instruction",
}
FORBIDDEN_KEYS = {
    "name", "full_name", "first_name", "last_name", "email", "phone", "address",
    "location", "city", "state", "country", "zip", "postal_code", "employer",
    "organization", "school", "age", "birthdate", "gender", "race", "ethnicity",
    "demographic", "bio", "biography", "social_media", "ip", "user_agent"
}
FORBIDDEN_TEXT = [
    "hostile", "hard-fail", "graceful receipt object", "evaluator rubric",
    "source path", "email:", "name:", "location:", "employer:"
]
READER_FACE_FORBIDDEN = [
    "anthology/", "poems/", "sources/", "registries/", "reports/", "tools/",
    "evaluator rubric", "hostile", "hard-fail", "graceful receipt object"
]


def add(checks, name, ok, detail=""):
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def poem_body(raw: str) -> str:
    if "## Poem" not in raw or "## Disclosure" not in raw:
        return ""
    return raw.split("## Poem", 1)[1].split("## Disclosure", 1)[0].strip("\n")


def before_poem(raw: str) -> str:
    marker = "\n## Poem"
    pos = raw.find(marker)
    return raw[:pos] if pos >= 0 else raw


def reader_supplied_blob(response: dict) -> str:
    """Scan only reader-supplied fields, not tool timestamps/ids/fingerprints."""
    values = []
    for key in sorted(REQUIRED_RESPONSE_FIELDS | {"quality_claims"}):
        if key in response:
            values.append(str(response.get(key)))
    return "\n".join(values)


def response_log_ok(checks: list[dict], log: dict) -> None:
    responses = log.get("responses")
    add(checks, "reader_intake_log_responses_list", isinstance(responses, list), type(responses).__name__)
    if not isinstance(responses, list):
        return
    add(checks, "reader_intake_log_count_matches", log.get("response_count") == len(responses), f"count={log.get('response_count')} len={len(responses)}")
    ids = [r.get("response_id") for r in responses if isinstance(r, dict)]
    fps = [r.get("content_fingerprint") for r in responses if isinstance(r, dict) and r.get("content_fingerprint")]
    add(checks, "reader_intake_log_response_ids_unique", len(ids) == len(set(ids)), ids)
    add(checks, "reader_intake_log_content_fingerprints_unique", len(fps) == len(set(fps)), fps)
    for i, response in enumerate(responses, start=1):
        prefix = f"reader_intake_response_{i:04d}"
        if not isinstance(response, dict):
            add(checks, f"{prefix}_is_object", False, type(response).__name__)
            continue
        dumped_low = json.dumps(response, ensure_ascii=False).lower()
        supplied = reader_supplied_blob(response)
        keys = set(response)
        add(checks, f"{prefix}_required_fields_present", REQUIRED_RESPONSE_FIELDS <= keys, sorted(REQUIRED_RESPONSE_FIELDS - keys))
        bad_keys = sorted(keys & FORBIDDEN_KEYS)
        add(checks, f"{prefix}_no_personal_data_keys", not bad_keys, bad_keys)
        add(checks, f"{prefix}_boundary_acknowledged", response.get("boundary_acknowledged") is True, response.get("response_id"))
        add(checks, f"{prefix}_content_fingerprint_present", isinstance(response.get("content_fingerprint"), str) and len(response.get("content_fingerprint")) == 64, response.get("content_fingerprint"))
        add(checks, f"{prefix}_no_email_like_reader_text", EMAIL_RE.search(supplied) is None, "email-like text present" if EMAIL_RE.search(supplied) else "")
        add(checks, f"{prefix}_no_phone_like_reader_text", PHONEISH_RE.search(supplied) is None, "phone-like text present" if PHONEISH_RE.search(supplied) else "")
        bad = [s for s in ["admitted", "evidence-ready", "evidence_candidate", "human-authored"] if s in dumped_low]
        add(checks, f"{prefix}_no_admission_or_deception_leakage", not bad, bad)
        add(checks, f"{prefix}_non_claim_flags", response.get("does_not_create_admission") is True and response.get("does_not_create_evidence_status") is True, response.get("response_id"))
        for field in TEXT_FIELDS:
            value = response.get(field)
            add(checks, f"{prefix}_{field}_not_blank", isinstance(value, str) and len(value.strip()) >= 2, repr(value))


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_recorder(root: Path, payload: dict, *, dry_run: bool = True, recorded_at: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run the recorder's real append function in-process for reentrant checks.

    Rev0041 changes this from subprocess execution because doctor runs the
    intake checker after the main validator has already run it once. The
    append path is still the production recorder function and still writes to a
    temporary clone for non-dry-run tests, but the gate no longer risks a
    lingering child-process wait on repeated in-process calls.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as tmp:
        json.dump(payload, tmp, indent=2, ensure_ascii=False)
        tmp_path = Path(tmp.name)
    try:
        script_path = root / TOOL
        spec = importlib.util.spec_from_file_location(f"llmpoetry_record_reader_response_{id(tmp_path)}", script_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"could not load recorder module at {script_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.append_response(root, tmp_path, dry_run, recorded_at)
        stdout = json.dumps(report, indent=2, ensure_ascii=False)
        return subprocess.CompletedProcess(args=[str(script_path)], returncode=0 if report.get("ok") else 1, stdout=stdout, stderr="")
    except Exception as exc:
        return subprocess.CompletedProcess(args=[str(root / TOOL)], returncode=1, stdout="", stderr=str(exc))
    finally:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass


def valid_synthetic_payload() -> dict:
    return {
        "disclosure_seen_before_poem": True,
        "source_packet_opened_before_first_response": False,
        "boundary_acknowledged": True,
        "keep_reject_uncertain": "uncertain",
        "strongest_line_or_phrase": "No value came back. Water did.",
        "weakest_line_or_phrase": "Station Datum may still feel like source language.",
        "disclosure_delta": "confounded",
        "body_works_without_source_packet": True,
        "documentation_doing_poem_work": "Some pressure remains dependent on the premise, but the body can be read without the packet.",
        "revision_instruction": "Preserve the water/ruler scene and cut any line that explains the archive.",
        "quality_claims": [],
    }


def minimal_temp_root(root: Path) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="llmpoetry-intake-clone-"))
    for rel in (TOOL, LOG, PACKET):
        dst = tmp / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / rel, dst)
    return tmp


def handoff_bundle_ok(checks: list[dict], root: Path, rev: str, draft_body: str, candidate_is_current: bool) -> None:
    add(checks, "reader_handoff_dir_exists", (root / HANDOFF_DIR).is_dir(), HANDOFF_DIR.as_posix())
    payload_files = {
        "README.md",
        "reader_one_sheet.md",
        "reader_one_sheet.html",
        "reader_response_form.html",
        "response_intake_template.json",
    }
    required_files = payload_files | {"HANDOFF_MANIFEST.json"}
    for name in required_files:
        add(checks, f"reader_handoff_file_exists:{name}", (root / HANDOFF_DIR / name).exists(), name)
    if not (root / HANDOFF_MANIFEST).exists():
        return
    manifest = load_json(root / HANDOFF_MANIFEST)
    add(checks, "reader_handoff_manifest_revision_current_or_historical", manifest.get("revision") == rev or not candidate_is_current, manifest.get("revision"))
    add(checks, "reader_handoff_manifest_current_head", manifest.get("draft_id") == CURRENT_HEAD, manifest.get("draft_id"))
    add(checks, "reader_handoff_manifest_no_evaluator", manifest.get("evaluator_rubric_included") is False and manifest.get("bundle_includes_evaluator_rubric") is False, str(manifest.get("evaluator_rubric_included")))
    add(checks, "reader_handoff_manifest_bundle_declared", manifest.get("bundle_path") == HANDOFF_BUNDLE.as_posix() and manifest.get("bundle_sidecar") == HANDOFF_BUNDLE_SIDECAR.as_posix(), str(manifest.get("bundle_path")))
    files = manifest.get("files", [])
    names = {f.get("path") for f in files if isinstance(f, dict)}
    add(checks, "reader_handoff_manifest_complete", payload_files <= names, sorted(payload_files - names))
    for entry in files:
        if not isinstance(entry, dict) or not entry.get("path"):
            continue
        rel = entry["path"]
        p = root / HANDOFF_DIR / rel
        add(checks, f"reader_handoff_manifest_path_exists:{rel}", p.exists(), rel)
        if p.exists():
            add(checks, f"reader_handoff_manifest_hash:{rel}", entry.get("sha256") == sha256(p), rel)
    for rel in ["README.md", "reader_one_sheet.md", "reader_one_sheet.html", "reader_response_form.html"]:
        raw = text(root / HANDOFF_DIR / rel)
        low = raw.lower()
        bad = [s for s in READER_FACE_FORBIDDEN if s in low]
        add(checks, f"reader_handoff_no_cube_or_rubric_leak:{rel}", not bad, bad)
        add(checks, f"reader_handoff_mentions_revision_or_historical:{rel}", rev in raw or not candidate_is_current, rel)
    one_md = text(root / HANDOFF_DIR / "reader_one_sheet.md")
    one_html = text(root / HANDOFF_DIR / "reader_one_sheet.html")
    add(checks, "reader_handoff_one_sheet_exact_poem_md", bool(draft_body and draft_body in one_md), "md")
    add(checks, "reader_handoff_one_sheet_exact_poem_html", bool(draft_body and escape(draft_body.splitlines()[0]) in one_html and escape(draft_body.splitlines()[-1]) in one_html), "html")


def run(root: Path):
    checks: list[dict] = []
    state = load_json(root / "STATE.json")
    surface = load_json(root / "SURFACE_STATUS.json")
    rev = state.get("revision")
    current_head = surface.get("current_head")
    candidate_is_current = current_head == CURRENT_HEAD
    pilot_queue = load_json(root / "registries/pilot_queue.json")
    recommended = [p for p in pilot_queue.get("pilots", []) if isinstance(p, dict) and p.get("status") == "recommended_next"]
    candidate_is_active_target = bool(
        candidate_is_current
        or (
            len(recommended) == 1
            and recommended[0].get("target_draft") == CURRENT_HEAD
            and recommended[0].get("target_is_not_global_head") is True
            and recommended[0].get("current_head") == current_head
        )
    )
    add(checks, "reader_intake_evaluation_target_active", candidate_is_active_target, f"global={current_head} target={recommended[0].get('target_draft') if recommended else None}")

    for rel in (PACKET, ONE_MD, ONE_HTML, FORM_MD, FORM_HTML, TEMPLATE, LOG, TOOL, SCHEMA, HANDOFF_BUNDLE, HANDOFF_BUNDLE_SIDECAR):
        add(checks, f"reader_intake_path_exists:{rel.as_posix()}", (root / rel).exists(), rel.as_posix())

    draft_body = poem_body(text(root / "poems/P0002/draft_010.md"))
    md = text(root / ONE_MD)
    html = text(root / ONE_HTML)
    form_md = text(root / FORM_MD)
    form_html = text(root / FORM_HTML)
    html_low = html.lower()
    form_low = form_html.lower()
    add(checks, "reader_intake_one_sheet_embeds_exact_poem", bool(draft_body and draft_body in md and escape(draft_body.splitlines()[0]) in html and escape(draft_body.splitlines()[-1]) in html), f"body_chars={len(draft_body)}")
    add(checks, "reader_intake_one_sheet_revision_current_or_historical", (rev in md and rev in html) or not candidate_is_current, rev)
    add(checks, "reader_intake_one_sheet_disclosure_before_poem", 0 <= md.lower().find("disclosure before reading") < md.lower().find("## poem"), "markdown order")
    pre_words = WORD_RE.findall(before_poem(md).lower())
    add(checks, "reader_intake_one_sheet_prepoem_word_cap", len(pre_words) <= 120, f"words={len(pre_words)}")
    required = ["machine-drafted", "not admitted", "not evidence-ready", "no current/live water-level value", "do not include personal identifiers"]
    missing = [s for s in required if s not in md.lower()]
    add(checks, "reader_intake_one_sheet_required_disclosures", not missing, missing)
    add(checks, "reader_intake_one_sheet_boundary_ack_field", "boundary acknowledged" in md.lower(), ONE_MD.as_posix())
    bad = [s for s in FORBIDDEN_TEXT if s in before_poem(md).lower()]
    add(checks, "reader_intake_one_sheet_no_prepoem_priming_or_pii_fields", not bad, bad)
    add(checks, "reader_intake_one_sheet_no_cube_paths", "anthology/" not in md and "poems/" not in md and "sources/" not in md, "cube path leaked" if any(s in md for s in ["anthology/", "poems/", "sources/"]) else "")
    add(checks, "reader_intake_one_sheet_html_no_script", "<script" not in html_low, ONE_HTML.as_posix())
    add(checks, "reader_intake_one_sheet_html_lang_title_main", "<html lang=\"en\"" in html_low and "<title>" in html_low and "<main" in html_low, ONE_HTML.as_posix())

    label_count = form_low.count("<label")
    input_count = form_low.count("<textarea") + form_low.count("<select") + form_low.count("<input")
    add(checks, "reader_intake_form_md_no_cube_path", "anthology/" not in form_md and "poems/" not in form_md and "tools/" not in form_md, FORM_MD.as_posix())
    add(checks, "reader_intake_form_md_boundary_ack_field", "boundary acknowledged" in form_md.lower(), FORM_MD.as_posix())
    add(checks, "reader_intake_form_md_duplicate_note", "duplicate" in form_md.lower(), FORM_MD.as_posix())
    add(checks, "reader_intake_form_html_no_script", "<script" not in form_low, FORM_HTML.as_posix())
    add(checks, "reader_intake_form_html_labels_controls", label_count >= 9 and input_count >= 9, f"labels={label_count} controls={input_count}")
    add(checks, "reader_intake_form_html_required_controls", form_low.count("required") >= 9 and "aria-required=\"true\"" in form_low, FORM_HTML.as_posix())
    add(checks, "reader_intake_form_html_fieldset_legend", "<fieldset" in form_low and "<legend" in form_low, FORM_HTML.as_posix())
    add(checks, "reader_intake_form_html_text_error_note", "validation errors must be described in text" in form_low, FORM_HTML.as_posix())
    add(checks, "reader_intake_form_html_duplicate_note", "duplicate" in form_low, FORM_HTML.as_posix())
    bad_form = [s for s in ["name=\"name\"", "name=\"email\"", "name=\"location\"", "name=\"employer\""] if s in form_low]
    add(checks, "reader_intake_form_html_no_pii_controls", not bad_form, bad_form)

    template = load_json(root / TEMPLATE) if (root / TEMPLATE).exists() else {}
    add(checks, "reader_intake_template_current_or_historical_revision", template.get("revision") == rev or not candidate_is_current, template.get("revision"))
    add(checks, "reader_intake_template_current_head", template.get("draft_id") == CURRENT_HEAD, template.get("draft_id"))
    add(checks, "reader_intake_template_schema_v3", template.get("schema") == "llmpoetry-reader-response-intake-template-v3", template.get("schema"))
    add(checks, "reader_intake_template_required_fields", REQUIRED_RESPONSE_FIELDS <= set(template.get("response", {}).keys()), sorted(REQUIRED_RESPONSE_FIELDS - set(template.get("response", {}).keys())))
    add(checks, "reader_intake_template_boundary_null_placeholder", template.get("response", {}).get("boundary_acknowledged") is None, str(template.get("response", {}).get("boundary_acknowledged")))
    add(checks, "reader_intake_template_placeholder_not_response", template.get("template_only") is True and template.get("not_a_response") is True, str(template.get("template_only")))
    template_keys = set(template.get("response", {}).keys()) | set(template.keys())
    add(checks, "reader_intake_template_no_pii_response_keys", not (template_keys & {"name", "email", "location", "employer"}), sorted(template_keys & {"name", "email", "location", "employer"}))

    packet = load_json(root / PACKET) if (root / PACKET).exists() else {}
    paths = packet.get("paths", {})
    for key, rel in {
        "reader_one_sheet_markdown": ONE_MD.as_posix(),
        "reader_one_sheet_html": ONE_HTML.as_posix(),
        "response_form": FORM_MD.as_posix(),
        "response_form_html": FORM_HTML.as_posix(),
        "response_intake_template": TEMPLATE.as_posix(),
        "response_intake_tool": TOOL.as_posix(),
        "response_intake_checker": "tools/check_reader_response_intake.py",
        "reader_handoff_dir": HANDOFF_DIR.as_posix(),
        "reader_handoff_manifest": HANDOFF_MANIFEST.as_posix(),
        "reader_handoff_bundle": HANDOFF_BUNDLE.as_posix(),
        "reader_handoff_bundle_sidecar": HANDOFF_BUNDLE_SIDECAR.as_posix(),
        "response_intake_audit": "reports/p0002_d010_handoff_bundle_transaction_intake_audit.json",
    }.items():
        add(checks, f"reader_intake_packet_path:{key}", paths.get(key) == rel, f"{paths.get(key)} != {rel}")
    policy = packet.get("response_intake_policy", {})
    add(checks, "reader_intake_packet_policy", policy.get("mode") == "portable_handoff_bundle_plus_transactional_duplicate_guarded_json_ingest", str(policy.get("mode")))
    add(checks, "reader_intake_packet_boundary_ack_required", policy.get("boundary_acknowledgement_required") is True, str(policy.get("boundary_acknowledgement_required")))
    add(checks, "reader_intake_packet_duplicate_guard", policy.get("duplicate_content_fingerprint_rejected") is True, str(policy.get("duplicate_content_fingerprint_rejected")))

    log = load_json(root / LOG) if (root / LOG).exists() else {}
    response_log_ok(checks, log)
    response_policy = log.get("response_policy", {})
    add(checks, "reader_intake_log_duplicate_policy", response_policy.get("duplicate_content_fingerprint_rejected") is True, str(response_policy.get("duplicate_content_fingerprint_rejected")))

    if (root / TOOL).exists() and (root / TEMPLATE).exists():
        proc = run_recorder(root, load_json(root / TEMPLATE))
        add(checks, "reader_intake_recorder_rejects_template_as_response", proc.returncode != 0, proc.stdout[:300] + proc.stderr[:300])
        blank = valid_synthetic_payload()
        for field in TEXT_FIELDS:
            blank[field] = ""
        proc_blank = run_recorder(root, blank)
        add(checks, "reader_intake_recorder_rejects_blank_response", proc_blank.returncode != 0, proc_blank.stdout[:300] + proc_blank.stderr[:300])
        pii = valid_synthetic_payload()
        pii["email"] = "reader@example.com"
        pii["response_id"] = "R-P0002-D010-9999"
        proc_pii = run_recorder(root, pii)
        add(checks, "reader_intake_recorder_rejects_pii_and_reserved_keys", proc_pii.returncode != 0, proc_pii.stdout[:300] + proc_pii.stderr[:300])
        good = valid_synthetic_payload()
        proc_good = run_recorder(root, good)
        add(checks, "reader_intake_recorder_accepts_synthetic_clean_dry_run", proc_good.returncode == 0 and '"would_write": false' in proc_good.stdout.lower(), proc_good.stdout[:300] + proc_good.stderr[:300])
        tmp_root = minimal_temp_root(root)
        try:
            before_log = load_json(root / LOG)
            proc_append = run_recorder(tmp_root, good, dry_run=False, recorded_at="2026-06-16T17:36:00+00:00")
            temp_log = load_json(tmp_root / LOG)
            temp_packet = load_json(tmp_root / PACKET)
            add(checks, "reader_intake_recorder_appends_on_temp_clone", proc_append.returncode == 0 and temp_log.get("response_count") == 1 and temp_packet.get("responses_recorded") == 1, proc_append.stdout[:300] + proc_append.stderr[:300])
            response_log_ok(checks, temp_log)
            proc_dup = run_recorder(tmp_root, good, dry_run=False, recorded_at="2026-06-16T17:37:00+00:00")
            add(checks, "reader_intake_recorder_rejects_duplicate_content_on_temp_clone", proc_dup.returncode != 0 and "duplicate response content fingerprint" in (proc_dup.stdout + proc_dup.stderr).lower(), proc_dup.stdout[:300] + proc_dup.stderr[:300])
            after_log = load_json(root / LOG)
            add(checks, "reader_intake_transaction_test_does_not_modify_real_log", before_log == after_log, "real log unchanged")
        finally:
            shutil.rmtree(tmp_root, ignore_errors=True)

    validator = text(root / "tools/llmpoetry_validate.py")
    add(checks, "reader_intake_wired_into_main_validator", "('reader_response_intake', run_reader_response_intake)" in validator or '("reader_response_intake", run_reader_response_intake)' in validator, "tools/llmpoetry_validate.py")

    handoff_bundle_ok(checks, root, rev, draft_body, candidate_is_current)
    return checks


def main(root=".") -> int:
    checks = run(Path(root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
