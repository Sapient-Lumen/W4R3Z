import hashlib, json, pathlib, re, sys, subprocess

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
errors = []
active_revision = (root / "VERSION").read_text(encoding="utf-8").strip()

sources_md = (root / "SOURCES.md").read_text(encoding="utf-8")
sources_json = json.loads((root / "SOURCES.json").read_text(encoding="utf-8"))
source_items = sources_json.get("sources", [])
source_ids = [item["id"] for item in source_items]
source_nums = [int(sid[1:]) for sid in source_ids if re.match(r"^S\d+$", sid)]
if source_nums != sorted(source_nums):
    errors.append("SOURCES.json source ids should stay sorted ascending")
cluster_pat = re.compile(r"(?:\[S\d+\]){2,}")
cluster_id_pat = re.compile(r"S\d+")
md_link_pat = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
head_pat = re.compile(r"^(#{1,6})\s+(.*)$", re.M)

def slugify(s):
    s = s.strip().lower()
    s = ''.join(ch for ch in s if ch.isalnum() or ch in '- ')
    s = re.sub(r"\s+", "-", s)
    return re.sub(r"-+", "-", s).strip('-')

anchor_map = {}
for p in root.rglob("*.md"):
    text = p.read_text(encoding="utf-8")
    anchors = set(re.findall(r'<a id="([^"]+)"></a>', text))
    seen = {}
    for m in head_pat.finditer(text):
        base = slugify(m.group(2))
        n = seen.get(base, 0)
        anchors.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1
    anchor_map[p.relative_to(root).as_posix()] = anchors

for p in root.rglob("*"):
    if p.is_file() and p.suffix.lower() == ".pdf":
        errors.append(f"pdf present: {p.relative_to(root)}")

for sid in source_ids:
    if f'<a id="{sid}"></a>' not in sources_md:
        errors.append(f"source id {sid} missing from SOURCES.md")

md_source_ids = re.findall(r'<a id="(S\d+)"></a>', sources_md)
if len(md_source_ids) != len(set(md_source_ids)):
    dupes = sorted({sid for sid in md_source_ids if md_source_ids.count(sid) > 1}, key=lambda s: int(s[1:]))
    errors.append(f"SOURCES.md has duplicate source anchors: {dupes}")
if set(md_source_ids) != set(source_ids):
    extra = sorted(set(md_source_ids) - set(source_ids), key=lambda s: int(s[1:]))
    missing = sorted(set(source_ids) - set(md_source_ids), key=lambda s: int(s[1:]))
    errors.append(f"SOURCES.md/SOURCES.json source id mismatch extra={extra} missing={missing}")

if re.search(r"^##\s+S\d+\b", sources_md, re.M):
    errors.append("SOURCES.md should stay compact and line-form; do not use heading-per-source formatting")
source_line_pat = re.compile(r'^-\s+<a id="S\d+"></a>\s+\*\*S\d+\s+—\s+.+?\*\*\s+—\s+<https?://[^>]+>\s*$', re.M)
for line in sources_md.splitlines():
    if '<a id="S' not in line:
        continue
    if not source_line_pat.match(line):
        errors.append("SOURCES.md entries should be ID + title + URL only; move explanatory notes to SOURCES.json")
        break

expected_sources_md = "# Sources\n\n" + "\n\n".join(
    f'- <a id="{item["id"]}"></a> **{item["id"]} — {item["title"]}** — <{item["url"]}>'
    for item in source_items
) + "\n"
if sources_md != expected_sources_md:
    errors.append("SOURCES.md must be generated exactly from SOURCES.json id/title/url entries")

for p in root.rglob("*.md"):
    relp = p.relative_to(root).as_posix()
    text = p.read_text(encoding="utf-8")
    for target in md_link_pat.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if target.startswith("#"):
            if target[1:] not in anchor_map.get(relp, set()):
                errors.append(f"broken local markdown anchor {target} in {relp}")
            continue
        path_part, _, frag = target.partition("#")
        dest = (p.parent / path_part).resolve()
        try:
            rel_dest = dest.relative_to(root).as_posix()
        except ValueError:
            errors.append(f"markdown link escapes archive root in {relp}: {target}")
            continue
        if not dest.exists():
            errors.append(f"broken markdown link target in {relp}: {target}")
        elif frag and dest.suffix.lower() == ".md" and frag not in anchor_map.get(rel_dest, set()):
            errors.append(f"broken markdown anchor target in {relp}: {target}")
    for sid in set(re.findall(r"\[(S\d+)\]", text)):
        if sid not in source_ids:
            errors.append(f"missing source id {sid} in SOURCES.json for {p.relative_to(root)}")
        if f'<a id="{sid}"></a>' not in sources_md:
            errors.append(f"missing source id {sid} in SOURCES.md for {p.relative_to(root)}")
    seen_defs = {}
    used_ids = set(re.findall(r"\[(S\d+)\](?!:)", text))
    for lineno, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^\[(S\d+)\]:\s+", line)
        if not m:
            continue
        sid = m.group(1)
        if sid in seen_defs:
            errors.append(f"duplicate source footnote definition {sid} in {p.relative_to(root)} at lines {seen_defs[sid]} and {lineno}")
        else:
            seen_defs[sid] = lineno
    for sid in used_ids:
        if sid not in seen_defs:
            errors.append(f"undefined local source footnote definition {sid} in {p.relative_to(root)}")
    for sid, lineno in seen_defs.items():
        if sid not in used_ids:
            errors.append(f"orphan source footnote definition {sid} in {p.relative_to(root)} at line {lineno}")
    for m in cluster_pat.finditer(text):
        ids = cluster_id_pat.findall(m.group(0))
        if len(ids) != len(set(ids)):
            errors.append(f"duplicate source id inside citation cluster in {p.relative_to(root)}: {m.group(0)}")
    if p.parts and p.parts[0] == "archive":
        sm = re.search(r"\n## Source cues\n(?P<section>[\s\S]*)$", text)
        if sm:
            section = sm.group("section")
            body = text[:sm.start()]
            body_ids = set(re.findall(r"\[(S\d+)\](?!:)", body))
            for sid in re.findall(r"^\[(S\d+)\]:\s+", section, re.M):
                if sid not in body_ids:
                    errors.append(f"archive source-cues tail carries redundant footnote definition {sid} in {p.relative_to(root)}")

url_to_ids = {}
title_to_ids = {}
for item in source_items:
    url_to_ids.setdefault(item["url"], []).append(item["id"])
    title_to_ids.setdefault(item["title"], []).append(item["id"])
for url, ids in url_to_ids.items():
    if len(ids) > 1:
        errors.append(f"duplicate source URL under multiple ids: {ids} -> {url}")
for title, ids in title_to_ids.items():
    if len(ids) > 1:
        errors.append(f"duplicate source title under multiple ids: {ids} -> {title}")

releases = json.loads((root / "RELEASES.json").read_text(encoding="utf-8"))
receipt = json.loads((root / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
if releases == receipt:
    errors.append("RELEASES.json duplicates REVISION-RECEIPT.json; machine-readable surfaces must have distinct jobs")
if releases.get("latest_codename") != receipt.get("codename"):
    errors.append("RELEASES.json latest_codename must match REVISION-RECEIPT.json codename")
if releases.get("source_count") != len(source_items):
    errors.append(f"RELEASES.json source_count={{releases.get('source_count')}} does not match SOURCES.json count={{len(source_items)}}")
if receipt.get("source_count") != len(source_items):
    errors.append(f"REVISION-RECEIPT.json source_count={{receipt.get('source_count')}} does not match SOURCES.json count={{len(source_items)}}")

context = json.loads((root / "context-pack.json").read_text(encoding="utf-8"))
core_claims = context.get("core_claims", [])
if len(core_claims) > 24:
    errors.append(f"context-pack.json has {len(core_claims)} core_claims; keep route-first context packets capped at 24 claims")
if len(core_claims) != len(set(core_claims)):
    errors.append("context-pack.json has duplicate core_claims; dedupe machine-readable claims")
if context.get("source_count") != len(source_items):
    errors.append(f"context-pack.json source_count={context.get('source_count')} does not match SOURCES.json count={len(source_items)}")

currentness_path = root / "docs/00-meta/source-currentness-registry.json"
currentness_ids = set()
if not currentness_path.exists():
    errors.append("docs/00-meta/source-currentness-registry.json is required for volatile current-law sources")
else:
    try:
        currentness = json.loads(currentness_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"source-currentness-registry.json is not valid JSON: {exc}")
        currentness = {"entries": []}
    required_currentness_fields = {"source_id", "jurisdiction", "source_type", "status", "effective_date", "last_checked", "review_due", "volatility", "note"}
    for entry in currentness.get("entries", []):
        sid = entry.get("source_id")
        if sid in currentness_ids:
            errors.append(f"source-currentness-registry.json duplicates source_id {sid}")
        currentness_ids.add(sid)
        if sid not in source_ids:
            errors.append(f"source-currentness-registry.json cites missing source_id {sid}")
        missing_fields = sorted(required_currentness_fields - set(entry))
        if missing_fields:
            errors.append(f"source-currentness-registry.json entry {sid} missing fields {missing_fields}")
        for date_key in ["last_checked", "review_due"]:
            if date_key in entry and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(entry.get(date_key))):
                errors.append(f"source-currentness-registry.json entry {sid} has non-ISO {date_key}: {entry.get(date_key)}")

cube_path = root / "cube-index.json"
if cube_path.exists():
    cube = json.loads(cube_path.read_text(encoding="utf-8"))
    if cube.get("revision") != active_revision:
        errors.append(f"cube-index.json revision={{cube.get('revision')}} does not match VERSION={{active_revision}}")
    axis_ids = [a.get("id") for a in cube.get("axes", [])]
    required_axes = {
        "subject", "base", "scale", "instrument", "incidence", "proof_posture", "stage",
        "floor_risk", "proceeds_route", "anti_pattern", "evidence_state", "review_trigger",
        "legal_status", "source_freshness", "market_structure", "delivery_channel",
        "burden_mechanic", "rights_affected", "remedy_type", "moral_operation",
        "severity", "confidence", "review_cadence"
    }
    if set(axis_ids) != required_axes:
        missing_axes = sorted(required_axes - set(axis_ids))
        extra_axes = sorted(set(axis_ids) - required_axes)
        errors.append(f"cube-index.json axis set drifted from required datacube axes missing={missing_axes} extra={extra_axes}")
    axis_values = {a.get("id"): set(a.get("values", [])) for a in cube.get("axes", [])}
    rec_ids = [rec.get("id") for rec in cube.get("route_records", [])]
    if len(rec_ids) != len(set(rec_ids)):
        errors.append("cube-index.json route record ids must be unique")
    for rec in cube.get("route_records", []):
        rec_path = root / rec.get("path", "")
        if not rec_path.exists():
            errors.append(f"cube-index.json route record points to missing file: {rec.get('path')}")
        if not rec.get("family"):
            errors.append(f"cube-index.json route record {rec.get('id')} missing family")
        missing_rec_axes = sorted(required_axes - set(rec.get("axes", {})))
        if missing_rec_axes:
            errors.append(f"cube-index.json route record {rec.get('id')} missing required axes: {missing_rec_axes}")
        for axis, values in rec.get("axes", {}).items():
            if axis not in axis_values:
                errors.append(f"cube-index.json route record {rec.get('id')} uses unknown axis: {axis}")
                continue
            for value in values:
                if value not in axis_values[axis]:
                    errors.append(f"cube-index.json route record {rec.get('id')} uses value {value!r} outside axis {axis}")
        if not rec.get("axes", {}).get("review_trigger"):
            errors.append(f"cube-index.json route record {rec.get('id')} should include at least one review_trigger axis value")
        if not rec.get("primary_sources"):
            errors.append(f"cube-index.json route record {rec.get('id')} should include primary_sources")
        for sid in rec.get("primary_sources", []):
            if sid not in source_ids:
                errors.append(f"cube-index.json route record {rec.get('id')} cites missing primary source {sid}")

    route_paths = {rec.get("path") for rec in cube.get("route_records", [])}
    calibration_paths = {p.relative_to(root).as_posix() for p in (root / "docs/20-calibration").glob("*.md")}
    exemption_path = root / "docs/00-meta/cube-exemptions.json"
    exemptions = set()
    if exemption_path.exists():
        try:
            exemptions = set(json.loads(exemption_path.read_text(encoding="utf-8")).get("exempt_paths", []))
        except json.JSONDecodeError as exc:
            errors.append(f"cube-exemptions.json is not valid JSON: {exc}")
    missing_calibrations = sorted(calibration_paths - route_paths - exemptions)
    if missing_calibrations:
        errors.append(f"cube-index.json missing calibration route records: {missing_calibrations}")
    dangling_exemptions = sorted(exemptions - calibration_paths)
    if dangling_exemptions:
        errors.append(f"cube-exemptions.json names non-calibration files: {dangling_exemptions}")

    for rec in cube.get("route_records", []):
        for sid in rec.get("source_currentness_refs", []):
            if sid not in currentness_ids:
                errors.append(f"cube-index.json route record {rec.get('id')} has source_currentness_ref not in registry: {sid}")
        if "proceeds_claims" in rec:
            for claim in rec.get("proceeds_claims", []):
                if not {"recipient", "route"}.issubset(claim):
                    errors.append(f"cube-index.json route record {rec.get('id')} has incomplete proceeds_claims entry")

    gp_rel = cube.get("golden_cases_path")
    golden_json_path = root / gp_rel if gp_rel else None
    if not gp_rel or not golden_json_path.exists():
        errors.append("cube-index.json golden_cases_path must point to docs/00-meta/golden-cases.json")
    else:
        golden = json.loads(golden_json_path.read_text(encoding="utf-8"))
        if golden.get("revision") != active_revision:
            errors.append("golden-cases.json revision must match VERSION")
        cases = golden.get("cases", [])
        if golden.get("case_count") != len(cases):
            errors.append("golden-cases.json case_count must equal number of cases")
        case_nums = [case.get("number") for case in cases]
        if case_nums != list(range(1, len(cases) + 1)):
            errors.append(f"golden-cases.json case numbers must be continuous from 1: {case_nums}")
        prose_path = root / golden.get("prose_path", "")
        if not prose_path.exists():
            errors.append("golden-cases.json prose_path is missing")
        else:
            prose_nums = [int(n) for n in re.findall(r"^#{2,3}\s+(\d+)\.\s+", prose_path.read_text(encoding="utf-8"), re.M)]
            if prose_nums != case_nums:
                errors.append("golden-cases.json case numbers must match prose golden-case cards")
        route_ids_set = set(rec_ids)
        for case in cases:
            if not case.get("expected_route_ids"):
                errors.append(f"golden-cases.json {case.get('case_id')} must include expected_route_ids")
            for rid in case.get("expected_route_ids", []):
                if rid not in route_ids_set:
                    errors.append(f"golden-cases.json {case.get('case_id')} cites unknown route id {rid}")
            for sid in case.get("source_ids", []):
                if sid not in source_ids:
                    errors.append(f"golden-cases.json {case.get('case_id')} cites missing source id {sid}")

scorecard = json.loads((root / "scorecard-template.json").read_text(encoding="utf-8"))
crit_ids = [c.get("id") for c in scorecard.get("criteria", [])]
if len(crit_ids) != len(set(crit_ids)):
    errors.append("scorecard criterion ids must be unique")
crit_nums = sorted(int(cid[1:]) for cid in crit_ids if isinstance(cid, str) and re.match(r"^C\d+$", cid))
if crit_nums and crit_nums != list(range(crit_nums[0], crit_nums[-1] + 1)):
    errors.append(f"scorecard criterion ids are not continuous: {crit_ids}")
if re.match(r"^rev\d{4}$", str(scorecard.get("revision", ""))):
    errors.append("scorecard-template.json should be revision-neutral; remove stale revision metadata")

scorecard_md_path = root / "docs/10-framework/proposal-scorecard.md"
if scorecard_md_path.exists():
    scorecard_md_text = scorecard_md_path.read_text(encoding="utf-8")
    expected_crit_ids = sorted(crit_ids, key=lambda cid: int(cid[1:]))
    md_crit_ids = re.findall(r"^\|\s+(C\d+)\s+\|", scorecard_md_text, re.M)
    if md_crit_ids != expected_crit_ids:
        errors.append("proposal-scorecard.md criterion ids must match scorecard-template.json exactly")
    max_expected = 2 * len(expected_crit_ids)
    m = re.search(r"Maximum score:\*\* \+(\d+); \*\*minimum score:\*\* (-?\d+)", scorecard_md_text)
    if not m or int(m.group(1)) != max_expected or int(m.group(2)) != -max_expected:
        errors.append("proposal-scorecard.md score thresholds must match current criterion count")
    try:
        rendered = subprocess.check_output([sys.executable, str(root / "tools/render_scorecard.py"), str(root)], text=True)
        if scorecard_md_text != rendered:
            errors.append("proposal-scorecard.md must be generated exactly by tools/render_scorecard.py")
    except Exception as exc:
        errors.append(f"tools/render_scorecard.py failed: {exc}")

if sources_json.get("revision") != active_revision:
    errors.append(f"SOURCES.json revision={sources_json.get('revision')} does not match VERSION={active_revision}")
if sources_json.get("source_count") != len(source_items):
    errors.append(f"SOURCES.json source_count={sources_json.get('source_count')} does not match SOURCES.json count={len(source_items)}")
if releases.get("latest_revision") != active_revision:
    errors.append(f"RELEASES.json latest_revision={releases.get('latest_revision')} does not match VERSION={active_revision}")
if receipt.get("revision") != active_revision:
    errors.append(f"REVISION-RECEIPT.json revision={receipt.get('revision')} does not match VERSION={active_revision}")
if context.get("revision") != active_revision:
    errors.append(f"context-pack.json revision={context.get('revision')} does not match VERSION={active_revision}")
if context.get("codename") != releases.get("latest_codename"):
    errors.append("context-pack.json codename must match RELEASES.json latest_codename")

if active_revision not in str(releases.get("latest_zip", "")):
    errors.append("RELEASES.json latest_zip must include active revision")

golden_path = root / "docs/00-meta/golden-case-cards.md"
if golden_path.exists():
    golden_nums = [int(n) for n in re.findall(r"^#{2,3}\s+(\d+)\.\s+", golden_path.read_text(encoding="utf-8"), re.M)]
    if golden_nums and golden_nums != list(range(golden_nums[0], golden_nums[0] + len(golden_nums))):
        errors.append(f"golden case numbering is not continuous: {golden_nums}")
for rel in releases.get("updated_files", []):
    if not (root / rel).exists():
        errors.append(f"RELEASES.json updated_files points to missing file: {rel}")
for rel in receipt.get("files_added", []) + receipt.get("files_updated", []):
    if rel != "MANIFEST.json" and not (root / rel).exists():
        errors.append(f"REVISION-RECEIPT.json file list points to missing file: {rel}")
for sid in receipt.get("sources_added", []):
    if sid not in source_ids:
        errors.append(f"REVISION-RECEIPT.json sources_added cites missing source: {sid}")
if cube_path.exists():
    try:
        rendered_audit = subprocess.check_output([sys.executable, str(root / "tools/audit_cube.py"), str(root)], text=True)
        if "cube audit ok" not in rendered_audit:
            errors.append("tools/audit_cube.py did not report success")
    except Exception as exc:
        errors.append(f"tools/audit_cube.py failed: {exc}")


if cube_path.exists():
    try:
        rendered_source_audit = subprocess.check_output([sys.executable, str(root / "tools/audit_source_currentness.py"), str(root)], text=True)
        if "source currentness audit ok" not in rendered_source_audit:
            errors.append("tools/audit_source_currentness.py did not report success")
    except Exception as exc:
        errors.append(f"tools/audit_source_currentness.py failed: {exc}")

if cube_path.exists():
    source_audit_rel = cube.get("source_currentness_audit_report_path")
    if not source_audit_rel or not (root / source_audit_rel).exists():
        errors.append("cube-index.json source_currentness_audit_report_path must point to a source-currentness audit report")
    remedy_profiles_rel = cube.get("remedy_profiles_path")
    remedy_schema_rel = cube.get("remedy_schema_path")
    remedy_audit_rel = cube.get("remedy_audit_report_path")
    case_contracts_rel = cube.get("case_contracts_path")
    case_contract_schema_rel = cube.get("case_contract_schema_path")
    case_contract_audit_rel = cube.get("case_contract_audit_report_path")
    policy_action_profiles_rel = cube.get("policy_action_profiles_path")
    policy_action_schema_rel = cube.get("policy_action_schema_path")
    policy_action_audit_rel = cube.get("policy_action_audit_report_path")
    actor_accountability_profiles_rel = cube.get("actor_accountability_profiles_path")
    actor_accountability_schema_rel = cube.get("actor_accountability_schema_path")
    actor_accountability_audit_rel = cube.get("actor_accountability_audit_report_path")
    for label, rel in [("remedy_profiles_path", remedy_profiles_rel), ("remedy_schema_path", remedy_schema_rel), ("remedy_audit_report_path", remedy_audit_rel), ("case_contracts_path", case_contracts_rel), ("case_contract_schema_path", case_contract_schema_rel), ("case_contract_audit_report_path", case_contract_audit_rel), ("policy_action_profiles_path", policy_action_profiles_rel), ("policy_action_schema_path", policy_action_schema_rel), ("policy_action_audit_report_path", policy_action_audit_rel), ("actor_accountability_profiles_path", actor_accountability_profiles_rel), ("actor_accountability_schema_path", actor_accountability_schema_rel), ("actor_accountability_audit_report_path", actor_accountability_audit_rel)]:
        if not rel or not (root / rel).exists():
            errors.append(f"cube-index.json {label} must point to an existing file")
    try:
        rendered_remedy_audit = subprocess.check_output([sys.executable, str(root / "tools/audit_remedy_profiles.py"), str(root)], text=True)
        if "remedy profile audit ok" not in rendered_remedy_audit:
            errors.append("tools/audit_remedy_profiles.py did not report success")
    except Exception as exc:
        errors.append(f"tools/audit_remedy_profiles.py failed: {exc}")
    try:
        rendered_case_audit = subprocess.check_output([sys.executable, str(root / "tools/audit_case_contracts.py"), str(root)], text=True)
        if "case contract audit ok" not in rendered_case_audit:
            errors.append("tools/audit_case_contracts.py did not report success")
    except Exception as exc:
        errors.append(f"tools/audit_case_contracts.py failed: {exc}")
    try:
        rendered_policy_action_audit = subprocess.check_output([sys.executable, str(root / "tools/audit_policy_action_profiles.py"), str(root)], text=True)
        if "policy-action profile audit ok" not in rendered_policy_action_audit:
            errors.append("tools/audit_policy_action_profiles.py did not report success")
    except Exception as exc:
        errors.append(f"tools/audit_policy_action_profiles.py failed: {exc}")

    try:
        rendered_actor_audit = subprocess.check_output([sys.executable, str(root / "tools/audit_actor_accountability_profiles.py"), str(root)], text=True)
        if "actor-accountability profile audit ok" not in rendered_actor_audit:
            errors.append("tools/audit_actor_accountability_profiles.py did not report success")
    except Exception as exc:
        errors.append(f"tools/audit_actor_accountability_profiles.py failed: {exc}")
if cube_path.exists():
    if cube.get("generated_at_utc") != receipt.get("created_at_utc"):
        errors.append("cube-index.json generated_at_utc must match REVISION-RECEIPT.json created_at_utc")
    cube_text = cube_path.read_text(encoding="utf-8")
    for sid in set(re.findall(r'"(S\d+)"', cube_text)):
        if sid not in source_ids:
            errors.append(f"cube-index.json cites missing source id: {sid}")


watched_ladders = [
    root / "docs/20-calibration/insurance-reinsurance-protection-gap-and-backstop-ladder.md",
    root / "docs/20-calibration/gambling-prediction-markets-event-contract-and-addiction-ladder.md",
    root / "docs/20-calibration/telecom-universal-service-broadband-affordability-and-surcharge-ladder.md",
    root / "docs/20-calibration/media-attention-digital-advertising-tax-and-speech-transparency-ladder.md",
    root / "docs/20-calibration/platform-worker-portable-benefits-classification-and-fringe-ladder.md",
    root / "docs/20-calibration/cumulative-burden-environmental-justice-and-siting-tax-ladder.md",
    root / "docs/20-calibration/release-integrity-source-bijection-and-regression-harness-ladder.md",
    root / "docs/20-calibration/mandatory-private-tax-rail-and-bankless-fallback-ladder.md",
    root / "docs/20-calibration/taxpayer-side-ai-preparer-agent-reliance-and-liability-ladder.md",
]
for wp in watched_ladders:
    if not wp.exists():
        errors.append(f"watched calibration ladder missing: {wp.relative_to(root)}")
        continue
    wt = wp.read_text(encoding="utf-8")
    if "How should this instrument family be calibrated so classification seams" in wt:
        errors.append(f"generic classification-seam boilerplate remains in {wp.relative_to(root)}")
def _token_shingles(path):
    text = re.sub(r"S\d+", "S", path.read_text(encoding="utf-8").lower())
    toks = re.findall(r"[a-z0-9]+", text)
    if len(toks) < 5:
        return set(toks)
    return {tuple(toks[i:i+5]) for i in range(len(toks)-4)}
_ladder_shingles = {p: _token_shingles(p) for p in watched_ladders if p.exists()}
for i, left in enumerate(watched_ladders):
    if left not in _ladder_shingles:
        continue
    lt = _ladder_shingles[left]
    for right in watched_ladders[i+1:]:
        if right not in _ladder_shingles:
            continue
        rt = _ladder_shingles[right]
        union = len(lt | rt) or 1
        ratio = len(lt & rt) / union
        if ratio > 0.72:
            errors.append(f"calibration ladders are suspiciously similar by shingle overlap ({ratio:.2f}): {left.relative_to(root)} and {right.relative_to(root)}")

compact_json_paths = [
    root / "SOURCES.json",
    root / "RELEASES.json",
    root / "REVISION-RECEIPT.json",
    root / "context-pack.json",
    root / "scorecard-template.json",
    root / "cube-index.json",
    root / "docs/00-meta/source-currentness-registry.json",
    root / "docs/00-meta/golden-cases.json",
    root / "docs/00-meta/cube-schema.json",
    root / "docs/00-meta/remedy-schema.json",
    root / "docs/00-meta/remedy-profiles.json",
    root / "docs/00-meta/case-contract-schema.json",
    root / "docs/00-meta/case-contracts.json",
    root / "docs/00-meta/policy-action-schema.json",
    root / "docs/00-meta/policy-action-profiles.json",
]
for path in compact_json_paths:
    text = path.read_text(encoding="utf-8")
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name} is not valid JSON: {exc}")
        continue
    compact = json.dumps(obj, separators=(",", ":")) + "\n"
    if text != compact:
        errors.append(f"{path.name} must stay compact on disk")

start_here = root / "START_HERE.md"
if start_here.exists():
    start_text = start_here.read_text(encoding="utf-8")
    start_opening = start_text[:1200]
    stale_revs = [m.group(0).lower() for m in re.finditer(r"Rev(\d{4})", start_opening)]
    for sr in stale_revs:
        if sr != active_revision:
            errors.append("START_HERE.md opening revision is stale")
            break
    if start_here.stat().st_size > 7000:
        errors.append(f"START_HERE.md is {start_here.stat().st_size} bytes; keep reopening surfaces compact")
    if re.search(r"^##\s+Executive answer\b", start_text, re.M):
        errors.append("START_HERE.md should stay route-first; do not add a duplicate executive-summary section")
    if re.search(r"^##\s+If you only read fifteen things\b", start_text, re.M):
        errors.append("START_HERE.md should use route clusters instead of long fixed reading canons")

archive_index_path = root / "ARCHIVE_INDEX.md"
if archive_index_path.exists():
    archive_index_text = archive_index_path.read_text(encoding="utf-8")
    opening = archive_index_text.split("## Fast founding route", 1)[0]
    mrev = re.search(r"Rev(\d{4})\s+adds", opening)
    if mrev and f"rev{mrev.group(1)}" != active_revision:
        errors.append("ARCHIVE_INDEX.md opening revision is stale")
    if archive_index_path.stat().st_size > 12000:
        errors.append(f"ARCHIVE_INDEX.md is {archive_index_path.stat().st_size} bytes; keep the index compact and family-first")
    if "MANIFEST.json" not in archive_index_text:
        errors.append("ARCHIVE_INDEX.md must point to MANIFEST.json as the authoritative exhaustive inventory")
    fm = re.search(r"## Fast founding route\n(?P<section>[\s\S]*?)\n## Re-entry points", archive_index_text)
    if fm:
        nums = [int(n) for n in re.findall(r"^\s*(\d+)\.\s+", fm.group("section"), re.M)]
        if nums and nums != list(range(nums[0], nums[0] + len(nums))):
            errors.append(f"ARCHIVE_INDEX.md fast founding route numbering is not continuous: {{nums}}")
    bullet_links = len(re.findall(r"^-\s+\[`[^`]+`\]", archive_index_text, re.M))
    if bullet_links > 30:
        errors.append("ARCHIVE_INDEX.md should stay route-first and family-first rather than regrowing a long file-by-file dump")

archive_nums = []
for ap in (root / "archive").glob("*.md"):
    m = re.match(r"^(\d{3})-", ap.name)
    if m:
        archive_nums.append(int(m.group(1)))
if archive_nums:
    archive_nums = sorted(archive_nums)
    expected = list(range(archive_nums[0], archive_nums[-1] + 1))
    if archive_nums != expected:
        errors.append(f"archive note numbering is not continuous: missing {sorted(set(expected)-set(archive_nums))}")

runbook_path = root / "docs/00-meta/llm-runbook.md"
if runbook_path.exists():
    runbook_text = runbook_path.read_text(encoding="utf-8")
    if runbook_path.stat().st_size > 12000:
        errors.append(f"docs/00-meta/llm-runbook.md is {runbook_path.stat().st_size} bytes; keep the editor runbook compact")
    if re.search(r"^##\s+Read first\b", runbook_text, re.M):
        errors.append("docs/00-meta/llm-runbook.md should use route clusters instead of a long fixed read-first canon")
    if max((line.count(".md`") + line.count("ARCHIVE_INDEX.md")) for line in runbook_text.splitlines()) > 8:
        errors.append("docs/00-meta/llm-runbook.md should use route families and representative starts instead of giant filename sprays on one line")

proposal_scorecard = root / "docs/10-framework/proposal-scorecard.md"
if proposal_scorecard.exists():
    scorecard_text = proposal_scorecard.read_text(encoding="utf-8")
    if proposal_scorecard.stat().st_size > 24000:
        errors.append(f"docs/10-framework/proposal-scorecard.md is {proposal_scorecard.stat().st_size} bytes; keep the scorecard table-first and compact")
    if re.search(r"^##\s+Source cues\b", scorecard_text, re.M):
        errors.append("docs/10-framework/proposal-scorecard.md should not carry a redundant source-cues section when the body already cites its sources")

cal_frontier = root / "docs/00-meta/calibration-frontier-map.md"
if cal_frontier.exists():
    cal_text = cal_frontier.read_text(encoding="utf-8")
    if cal_frontier.stat().st_size > 17000:
        errors.append(f"docs/00-meta/calibration-frontier-map.md is {cal_frontier.stat().st_size} bytes; keep the frontier map compact and cluster-first")
    if cal_text.count("Use when | Main questions | Start files | Default outputs") < 3:
        errors.append("docs/00-meta/calibration-frontier-map.md should stay table-first across its frontier clusters")
    if cal_text.count("Use this cluster when the issue is") > 2:
        errors.append("docs/00-meta/calibration-frontier-map.md should stay cluster-first and table-first rather than repeating per-cluster boilerplate")
    if cal_text.count("Default outputs:") > 2:
        errors.append("docs/00-meta/calibration-frontier-map.md should collapse repeated per-cluster output boilerplate into a tighter route map")

open_questions = root / "docs/10-framework/open-questions.md"
if open_questions.exists():
    open_text = open_questions.read_text(encoding="utf-8")
    if open_questions.stat().st_size > 30000:
        errors.append(f"docs/10-framework/open-questions.md is {open_questions.stat().st_size} bytes; keep frontier prompts compact")
    if "after the narrow waist" in open_text:
        errors.append("docs/10-framework/open-questions.md should drop repeated 'after the narrow waist' scaffolding")
    if open_text.count("given the archive's compact") > 3:
        errors.append("docs/10-framework/open-questions.md should point frontier questions straight to their first calibration memo instead of repeating compact-rule boilerplate")
    if "rather than reopening the rule itself" in open_text:
        errors.append("docs/10-framework/open-questions.md should use compact start-memo pointers rather than repeating reopening boilerplate")


ideal_answer = root / "docs/10-framework/ideal-taxation-by-class-context-and-species.md"
if ideal_answer.exists():
    ia_text = ideal_answer.read_text(encoding="utf-8")
    if ideal_answer.stat().st_size > 31000:
        errors.append(f"docs/10-framework/ideal-taxation-by-class-context-and-species.md is {ideal_answer.stat().st_size} bytes; keep the founding answer compact and answer-first")
    if 'one-screen-schedule' not in anchor_map.get('docs/10-framework/ideal-taxation-by-class-context-and-species.md', set()):
        errors.append('docs/10-framework/ideal-taxation-by-class-context-and-species.md must keep an explicit or heading anchor for one-screen-schedule')
    if ia_text.count("The archive also treats") > 2:
        errors.append("docs/10-framework/ideal-taxation-by-class-context-and-species.md should use short rule intros rather than repeating 'The archive also treats...' scaffolding")
    if ia_text.count("For the archive's compact routing answer") + ia_text.count("For the compact routing answer") > 1:
        errors.append("docs/10-framework/ideal-taxation-by-class-context-and-species.md should use compact Route: callouts instead of repeated routing sentences")
    intro_text = ia_text.split('<a id="one-screen-schedule"></a>', 1)[0]
    intro_lines = [line for line in intro_text.splitlines() if line.strip()]
    if len(intro_lines) > 4:
        errors.append("docs/10-framework/ideal-taxation-by-class-context-and-species.md should reach the one-screen schedule quickly; keep the pre-schedule intro to a short direct answer plus one route line")
    if intro_text.count('\n- ') > 0:
        errors.append("docs/10-framework/ideal-taxation-by-class-context-and-species.md should not add a second summary-bullet layer above the one-screen schedule")


ai_exceptional = root / "docs/10-framework/ai-exceptional-levy-trigger-routing.md"
if ai_exceptional.exists():
    ai_text = ai_exceptional.read_text(encoding="utf-8")
    if ai_exceptional.stat().st_size > 12650:
        errors.append(f"docs/10-framework/ai-exceptional-levy-trigger-routing.md is {ai_exceptional.stat().st_size} bytes; keep it compact and trigger-first")
    if re.search(r"^##\s+Use this note with", ai_text, re.M):
        errors.append("docs/10-framework/ai-exceptional-levy-trigger-routing.md should use route clusters, not a long companion-file tail")
    if "## Route clusters" not in ai_text:
        errors.append("docs/10-framework/ai-exceptional-levy-trigger-routing.md should keep a route-clusters block")

decision_procedure = root / "docs/10-framework/decision-procedure.md"
if decision_procedure.exists():
    dp_text = decision_procedure.read_text(encoding="utf-8")
    if decision_procedure.stat().st_size > 30000:
        errors.append(f"docs/10-framework/decision-procedure.md is {decision_procedure.stat().st_size} bytes; keep it checklist-first and compact even with local source definitions")
    if "## Companion routes" not in dp_text:
        errors.append("docs/10-framework/decision-procedure.md should keep a short companion-routes block near the top")
    if dp_text.count("For the clearest") > 3:
        errors.append("docs/10-framework/decision-procedure.md should collapse repeated route-preamble boilerplate into a short route pack")

default_stack = root / "docs/10-framework/default-tax-stack-by-scale.md"
if default_stack.exists():
    ds_text = default_stack.read_text(encoding="utf-8")
    ds_size = default_stack.stat().st_size
    if ds_size > 10250:
        errors.append(f"default-tax-stack-by-scale.md is {ds_size} bytes; keep it compact")
    if "## Companion routes" not in ds_text:
        errors.append("default-tax-stack-by-scale.md needs companion routes")
    if "## Route clusters" not in ds_text or "## Use this document with" in ds_text:
        errors.append("default-tax-stack-by-scale.md should end with route clusters")

timing_ladder = root / "docs/20-calibration/timing-cashflow-liquidity-deferral-and-prefunding-ladder.md"
if timing_ladder.exists():
    tl_text = timing_ladder.read_text(encoding="utf-8")
    if timing_ladder.stat().st_size > 10650:
        errors.append(f"docs/20-calibration/timing-cashflow-liquidity-deferral-and-prefunding-ladder.md is {timing_ladder.stat().st_size} bytes; keep it ladder-first and compact")
    if "## Companion routes" not in tl_text or "## Option scan" not in tl_text:
        errors.append("docs/20-calibration/timing-cashflow-liquidity-deferral-and-prefunding-ladder.md should keep companion routes and a compact option scan")
    if "## Closed rules invoked" in tl_text or "## Small option set" in tl_text:
        errors.append("docs/20-calibration/timing-cashflow-liquidity-deferral-and-prefunding-ladder.md should use the newer ladder-first memo shape, not the older long calibration scaffold")


collection_ladder = root / "docs/20-calibration/collection-anchor-choice-and-remittance-chain-ladder.md"
if collection_ladder.exists():
    cl_text = collection_ladder.read_text(encoding="utf-8")
    if collection_ladder.stat().st_size > 10650:
        errors.append(f"docs/20-calibration/collection-anchor-choice-and-remittance-chain-ladder.md is {collection_ladder.stat().st_size} bytes; keep it ladder-first and compact")
    if "## Companion routes" not in cl_text or "## Option scan" not in cl_text:
        errors.append("docs/20-calibration/collection-anchor-choice-and-remittance-chain-ladder.md should keep companion routes and a compact option scan")
    if "## Closed rules invoked" in cl_text or "## Small option set" in cl_text:
        errors.append("docs/20-calibration/collection-anchor-choice-and-remittance-chain-ladder.md should use the newer ladder-first memo shape, not the older long calibration scaffold")

proceeds_ladder = root / "docs/20-calibration/proceeds-visibility-local-share-and-earmarking-ladder.md"
if proceeds_ladder.exists():
    pl_text = proceeds_ladder.read_text(encoding="utf-8")
    if proceeds_ladder.stat().st_size > 10650:
        errors.append(f"docs/20-calibration/proceeds-visibility-local-share-and-earmarking-ladder.md is {proceeds_ladder.stat().st_size} bytes; keep it ladder-first and compact")
    if "## Companion routes" not in pl_text or "## Option scan" not in pl_text:
        errors.append("docs/20-calibration/proceeds-visibility-local-share-and-earmarking-ladder.md should keep companion routes and a compact option scan")
    if "## Closed rules invoked" in pl_text or "## Small option set" in pl_text:
        errors.append("docs/20-calibration/proceeds-visibility-local-share-and-earmarking-ladder.md should use the newer ladder-first memo shape, not the older long calibration scaffold")


docs_readme_path = root / "docs/README.md"
if docs_readme_path.exists():
    docs_readme_text = docs_readme_path.read_text(encoding="utf-8")
    docs_readme_opening = docs_readme_text[:1200]
    stale_revs = [m.group(0).lower() for m in re.finditer(r"Rev(\d{4})", docs_readme_opening)]
    for sr in stale_revs:
        if sr != active_revision:
            errors.append("docs/README.md opening revision is stale")
            break

makefile_path = root / "Makefile"
if makefile_path.exists():
    makefile_text = makefile_path.read_text(encoding="utf-8")
    if not re.search(r"^package:\s+scorecard\s+manifest\s+check\b", makefile_text, re.M):
        errors.append("Makefile package target should rebuild manifest before check")
    if not re.search(r"^package:.*\bzip\b", makefile_text, re.M) or not re.search(r"^zip:\n\tpython3 tools/package_release.py \.\s*$", makefile_text, re.M):
        errors.append("Makefile package target should create the release zip through tools/package_release.py")
    if not (root / "tools/package_release.py").exists():
        errors.append("tools/package_release.py is required for repeatable release zipping")

readme_path = root / "README.md"
if readme_path.exists():
    readme_text = readme_path.read_text(encoding="utf-8")
    opening = readme_text[:2500]
    stale_revs = [m.group(0).lower() for m in re.finditer(r"Rev(\d{4})", opening)]
    for sr in stale_revs:
        if sr != active_revision:
            errors.append("README.md opening revision is stale")
            break
if active_revision not in root.name:
    errors.append("archive root folder name should include active revision")

changelog_path = root / "CHANGELOG.md"
if changelog_path.exists():
    changelog_text = changelog_path.read_text(encoding="utf-8")
    if changelog_path.stat().st_size > 15000:
        errors.append(f"CHANGELOG.md is {changelog_path.stat().st_size} bytes; keep archive history compact")
    if len(re.findall(r"^##\s+rev\d{4}\b", changelog_text, re.M)) > 1:
        errors.append("CHANGELOG.md should keep only the current detailed revision section above the compact ledger")
    if "## Compact revision ledger" not in changelog_text:
        errors.append("CHANGELOG.md must include a compact revision ledger")
    if changelog_text.count("| Revision | Date | Codename | Summary |") != 1 or changelog_text.count("|---|---|---|---|") != 1:
        errors.append("CHANGELOG.md should keep exactly one compact-ledger header row and one separator row")

manifest_path = root / "MANIFEST.json"
manifest_text = manifest_path.read_text(encoding="utf-8")
try:
    manifest_obj = json.loads(manifest_text)
except json.JSONDecodeError as exc:
    errors.append(f"MANIFEST.json is not valid JSON: {exc}")
else:
    expected_items = []
    for mp in sorted(root.rglob("*")):
        if mp.is_file() and mp.name != "MANIFEST.json":
            data = mp.read_bytes()
            expected_items.append({
                "file": mp.relative_to(root).as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
    expected_manifest = {"root": root.name, "files": expected_items}
    expected_manifest_text = json.dumps(expected_manifest, separators=(",", ":")) + "\n"
    if manifest_text != expected_manifest_text:
        errors.append("MANIFEST.json must be generated exactly from the live file inventory and hashes; run tools/build_manifest.py after edits")

if errors:
    raise SystemExit("\n".join(errors))
print("ok")
