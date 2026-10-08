#!/usr/bin/env python3
"""Validate the current candidate's calibrated disclosed-reader packet.

Rev0037 repairs two completion risks in the rev0036 gate:
1. Necessary disclosure must appear before the poem, but hostile failure labels
   must not prime the reader before first reading.
2. The response log must be allowed to move from zero responses to real,
   non-identifying responses without creating admission/evidence status.

This is still not a poem-quality validator.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

CANDIDATE_HEAD = "P0002-D010"
def is_candidate_successor_head(head: str | None) -> bool:
    if not isinstance(head, str) or not head.startswith("P0002-D"):
        return False
    try:
        return int(head.split("-D", 1)[1]) >= 11
    except ValueError:
        return False
CURRENT_PACKET = "anthology/candidates/P0002-D010_disclosed_reader_packet.json"
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)?")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)


def add(checks, name, ok, detail=""):
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def poem_body_from_draft(raw: str) -> str:
    if "## Poem" not in raw or "## Disclosure" not in raw:
        return ""
    return raw.split("## Poem", 1)[1].split("## Disclosure", 1)[0].strip("\n")


def markdown_before_poem(md: str) -> str:
    marker = "\n## Poem"
    pos = md.find(marker)
    return md[:pos] if pos >= 0 else md


def html_before_poem(h: str) -> str:
    markers = ["<h2 id=\"poem\"", "<h2 id='poem'", ">poem</h2>"]
    lows = h.lower()
    positions = [lows.find(m) for m in markers if lows.find(m) >= 0]
    return h[: min(positions)] if positions else h


def active_templates(obj):
    return [t for t in obj.get("templates", []) if t.get("active") is True or t.get("status") in {"active", "recommended_current"}]


def response_count_valid(log: dict) -> bool:
    responses = log.get("responses")
    return isinstance(responses, list) and log.get("response_count") == len(responses)


def validate_response_log(checks: list[dict], log: dict) -> None:
    responses = log.get("responses", [])
    add(checks, "candidate_reader_response_log_list", isinstance(responses, list), type(responses).__name__)
    add(checks, "candidate_reader_response_count_matches", response_count_valid(log), f"count={log.get('response_count')} len={len(responses) if isinstance(responses, list) else 'NA'}")
    add(checks, "candidate_reader_response_log_quality_claims_empty", log.get("quality_claims", []) == [], str(log.get("quality_claims")))
    non_claim = str(log.get("non_claim", "")).lower()
    add(checks, "candidate_reader_response_log_nonclaim_blocks_evidence", "not" in non_claim and "evidence" in non_claim and "admission" in non_claim, log.get("non_claim", ""))

    policy = log.get("response_policy", {})
    for key in ("no_personal_identifiers", "no_demographics", "local_editorial_pressure_only", "does_not_create_admission", "does_not_create_evidence_status"):
        add(checks, f"candidate_reader_response_policy:{key}", policy.get(key) is True, str(policy.get(key)))

    required = set(policy.get("required_response_fields", []))
    if responses:
        add(checks, "candidate_reader_response_log_nonempty_status_allowed", "response" in str(log.get("status", "")).lower(), log.get("status"))
    else:
        add(checks, "candidate_reader_response_log_zero_status_allowed", "no_external_responses_recorded" in str(log.get("status", "")).lower() or "zero" in str(log.get("status", "")).lower(), log.get("status"))

    forbidden_keys = {"name", "email", "location", "employer", "address", "phone", "demographics", "demographic", "ip_address"}
    for i, response in enumerate(responses if isinstance(responses, list) else []):
        prefix = f"candidate_reader_response_{i+1}"
        add(checks, f"{prefix}_object", isinstance(response, dict), type(response).__name__)
        if not isinstance(response, dict):
            continue
        keys = {str(k).lower() for k in response.keys()}
        add(checks, f"{prefix}_required_fields_present", required <= keys, f"missing={sorted(required - keys)}")
        bad_keys = sorted(keys & forbidden_keys)
        add(checks, f"{prefix}_no_pii_keys", not bad_keys, bad_keys)
        dumped = json.dumps(response, ensure_ascii=False).lower()
        add(checks, f"{prefix}_no_email_like_text", EMAIL_RE.search(dumped) is None, "email-like text present" if EMAIL_RE.search(dumped) else "")
        add(checks, f"{prefix}_no_admission_effect", "admitted" not in dumped and "evidence-ready" not in dumped and "evidence_candidate" not in dumped, "admission/evidence wording present" if any(s in dumped for s in ["admitted", "evidence-ready", "evidence_candidate"]) else "")


def run(root: Path):
    checks=[]
    state=load_json(root/"STATE.json")
    surface=load_json(root/"SURFACE_STATUS.json")
    rev=state.get("revision")
    current_head=surface.get("current_head")
    add(checks,"candidate_reader_global_head_allowed",current_head == CANDIDATE_HEAD or is_candidate_successor_head(current_head) or not str(current_head).startswith("P0002-D"),str(current_head))

    packet_path=root/CURRENT_PACKET
    add(checks,"candidate_reader_packet_json_present",packet_path.exists(),CURRENT_PACKET)
    if not packet_path.exists():
        return checks
    packet=load_json(packet_path)
    add(checks,"candidate_reader_packet_revision_current_or_historical", packet.get("revision") == rev or is_candidate_successor_head(current_head) or not str(current_head).startswith("P0002-D"), packet.get("revision"))
    add(checks,"candidate_reader_packet_target_draft",packet.get("draft_id")==CANDIDATE_HEAD,packet.get("draft_id"))
    status = str(packet.get("status", "")).lower()
    allowed_status = any(s in status for s in ("not_conducted", "not_run", "ready_for_real_response", "responses_logged"))
    add(checks,"candidate_reader_packet_status_allows_not_run_or_logged",allowed_status,packet.get("status"))
    add(checks,"candidate_reader_disclosed_first",packet.get("disclosure_order")=="disclosure_before_poem",packet.get("disclosure_order"))
    add(checks,"candidate_reader_no_blind_phase",packet.get("blind_phase") is False,str(packet.get("blind_phase")))
    add(checks,"candidate_reader_quality_claims_empty",packet.get("quality_claims")==[],str(packet.get("quality_claims")))
    add(checks,"candidate_reader_surface_mode_calibrated",packet.get("reader_surface_mode")=="minimal_disclosure_before_poem_failure_rubric_separated",packet.get("reader_surface_mode"))
    policy = packet.get("pre_poem_priming_policy", {})
    add(checks,"candidate_reader_prepoem_policy_present",policy.get("mode")=="necessary_disclosure_only_before_poem",str(policy.get("mode")))
    rb=packet.get("reader_boundary",{})
    for key in ("no_personal_data","no_demographic_fields","no_deception_about_machine_authorship","local_editorial_test_only","not_generalizable_research_claim"):
        add(checks,f"candidate_reader_boundary:{key}",rb.get(key) is True,str(rb.get(key)))

    paths=packet.get("paths",{})
    required_paths=("draft","candidate_packet","source_material_packet","cold_review","packet_markdown","packet_html","response_form","response_log","protocol","evaluator_rubric_markdown","evaluator_rubric_json","run_sheet","audit")
    for key in required_paths:
        rel=paths.get(key)
        add(checks,f"candidate_reader_path_declared:{key}",bool(rel),str(rel))
        if rel:
            add(checks,f"candidate_reader_path_exists:{key}",(root/rel).exists(),rel)

    draft_raw=text(root/paths.get("draft", ""))
    body=poem_body_from_draft(draft_raw)
    md_rel=paths.get("packet_markdown","")
    md=text(root/md_rel)
    html_rel=paths.get("packet_html","")
    h=text(root/html_rel)
    h_low=h.lower()
    form=text(root/paths.get("response_form", ""))
    log=load_json(root/paths.get("response_log", "")) if paths.get("response_log") and (root/paths.get("response_log")).exists() else {}
    cand=load_json(root/paths.get("candidate_packet", "")) if paths.get("candidate_packet") and (root/paths.get("candidate_packet")).exists() else {}
    rubric_md=text(root/paths.get("evaluator_rubric_markdown", ""))
    rubric_json=load_json(root/paths.get("evaluator_rubric_json", "")) if paths.get("evaluator_rubric_json") and (root/paths.get("evaluator_rubric_json")).exists() else {}
    run_sheet=text(root/paths.get("run_sheet", ""))

    add(checks,"candidate_reader_poem_body_found",bool(body),"body_chars="+str(len(body)))
    add(checks,"candidate_reader_markdown_embeds_exact_poem_body",bool(body and body in md),md_rel)
    disclosure_pos=md.lower().find("disclosure before reading")
    poem_pos=md.lower().find("## poem")
    add(checks,"candidate_reader_disclosure_precedes_poem",0 <= disclosure_pos < poem_pos,f"disclosure={disclosure_pos} poem={poem_pos}")
    required_md=["machine-drafted","not admitted","not evidence-ready","no current/live water-level value","disclosure before reading","first-response questions"]
    missing=[s for s in required_md if s not in md.lower()]
    add(checks,"candidate_reader_markdown_required_disclosures",not missing,missing)

    before_md = markdown_before_poem(md).lower()
    forbidden_before = [s.lower() for s in policy.get("forbidden_before_poem", [])] or ["hostile", "hard-fail", "graceful receipt object"]
    bad_before=[s for s in forbidden_before if s in before_md]
    add(checks,"candidate_reader_markdown_prepoem_no_failure_priming",not bad_before,bad_before)
    pre_words = WORD_RE.findall(before_md)
    add(checks,"candidate_reader_markdown_prepoem_word_cap",len(pre_words) <= 150,f"words={len(pre_words)}")
    forbidden_md=["blind-first","undisclosed", "submit or circulate machine-authored work as human-authored"]
    bad=[s for s in forbidden_md if s in md.lower()]
    add(checks,"candidate_reader_markdown_no_blind_or_deception_language",not bad,bad)

    before_html = html_before_poem(h_low)
    html_bad=[s for s in forbidden_before if s in before_html]
    add(checks,"candidate_reader_html_prepoem_no_failure_priming",not html_bad,html_bad)
    add(checks,"candidate_reader_html_lang_en","<html lang=\"en\"" in h_low or "<html lang=en" in h_low,html_rel)
    add(checks,"candidate_reader_html_no_script","<script" not in h_low,html_rel)
    add(checks,"candidate_reader_html_has_main","<main" in h_low,html_rel)
    add(checks,"candidate_reader_html_has_title","<title>" in h_low and "p0002-d010" in h_low,html_rel)
    add(checks,"candidate_reader_html_disclosure_precedes_poem",0 <= h_low.find("disclosure before reading") < h_low.find("poem"),html_rel)

    pii_terms=["name:","email:","employer:","location:","address:","phone:"]
    bad_fields=[term for term in pii_terms if term in form.lower()]
    add(checks,"candidate_reader_form_no_pii_fields",not bad_fields,bad_fields)
    add(checks,"candidate_reader_form_has_disclosure_confirmation","disclosure seen before poem" in form.lower(),paths.get("response_form"))
    add(checks,"candidate_reader_form_mentions_no_personal_identifiers","do not include name" in form.lower() or "do not include personal" in form.lower(),paths.get("response_form"))

    validate_response_log(checks, log)
    add(checks,"candidate_reader_packet_response_count_matches_log",packet.get("responses_recorded", 0)==log.get("response_count"),f"packet={packet.get('responses_recorded')} log={log.get('response_count')}")

    add(checks,"candidate_reader_rubric_separate_warning","not for reader before first response" in rubric_md.lower(),paths.get("evaluator_rubric_markdown"))
    add(checks,"candidate_reader_rubric_contains_hostile_failure_terms","graceful receipt object" in rubric_md.lower() and "hard-fail" in rubric_md.lower(),paths.get("evaluator_rubric_markdown"))
    add(checks,"candidate_reader_rubric_json_nonclaim",rubric_json.get("quality_claims", [])==[] and rubric_json.get("not_for_reader_before_first_response") is True,str(rubric_json.get("not_for_reader_before_first_response")))
    add(checks,"candidate_reader_run_sheet_blocks_rubric_preexposure","do not show" in run_sheet.lower() and "evaluator rubric" in run_sheet.lower() and "first response" in run_sheet.lower(),paths.get("run_sheet"))

    add(checks,"candidate_packet_points_to_reader_packet",cand.get("disclosed_reader_packet")==CURRENT_PACKET,str(cand.get("disclosed_reader_packet")))
    add(checks,"candidate_packet_not_admitted",cand.get("not_admitted") is True and cand.get("not_evidence_candidate") is True,str(cand.get("status")))
    add(checks,"candidate_packet_points_to_rubric",cand.get("evaluator_rubric")==paths.get("evaluator_rubric_json"),str(cand.get("evaluator_rubric")))

    templates_path=root/"registries/disclosure_test_templates.json"
    add(checks,"disclosure_templates_present",templates_path.exists(),"registries/disclosure_test_templates.json")
    if templates_path.exists():
        tmpl=load_json(templates_path)
        add(checks,"disclosure_templates_revision_current_or_historical", tmpl.get("revision") == rev or is_candidate_successor_head(current_head) or not str(current_head).startswith("P0002-D"), tmpl.get("revision"))
        active=active_templates(tmpl)
        add(checks,"disclosure_templates_active_present",len(active)>=1,f"count={len(active)}")
        bad_active=[]
        for t in active:
            hay=json.dumps(t,ensure_ascii=False).lower()
            if t.get("blind_phase") is not False or "blind-first" in hay or "present poem without authorship" in hay:
                bad_active.append(t.get("template_id"))
        add(checks,"disclosure_templates_active_disclosed_first",not bad_active,bad_active)
        add(checks,"disclosure_templates_current_points_to_candidate_packet",tmpl.get("current_packet") == CURRENT_PACKET,str(tmpl.get("current_packet")))
        add(checks,"disclosure_templates_active_uses_separate_rubric",any(t.get("evaluator_rubric") == paths.get("evaluator_rubric_markdown") for t in active),[t.get("template_id") for t in active])

    return checks


def main(root="."):
    checks=run(Path(root))
    ok=all(c.get("ok") for c in checks)
    print(json.dumps({"ok":ok,"checks":checks,"failed":[c for c in checks if not c.get("ok")]},indent=2,ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else "."))
