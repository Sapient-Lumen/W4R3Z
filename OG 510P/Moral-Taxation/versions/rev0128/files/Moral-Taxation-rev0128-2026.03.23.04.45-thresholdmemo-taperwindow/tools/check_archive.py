import json, pathlib, re, sys

root = pathlib.Path(sys.argv[1]).resolve()
errors = []
active_revision = (root / "VERSION").read_text(encoding="utf-8").strip()

sources_md = (root / "SOURCES.md").read_text(encoding="utf-8")
sources_json = json.loads((root / "SOURCES.json").read_text(encoding="utf-8"))
source_items = sources_json.get("sources", [])
source_ids = [item["id"] for item in source_items]
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

if re.search(r"^##\s+S\d+\b", sources_md, re.M):
    errors.append("SOURCES.md should stay compact and line-form; do not use heading-per-source formatting")
source_line_pat = re.compile(r'^-\s+<a id="S\d+"></a>\s+\*\*S\d+\s+—\s+.+?\*\*\s+—\s+<https?://[^>]+>\s*$', re.M)
for line in sources_md.splitlines():
    if '<a id="S' not in line:
        continue
    if not source_line_pat.match(line):
        errors.append("SOURCES.md entries should be ID + title + URL only; move explanatory notes to SOURCES.json")
        break

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

context = json.loads((root / "context-pack.json").read_text(encoding="utf-8"))
core_claims = context.get("core_claims", [])
if len(core_claims) > 24:
    errors.append(f"context-pack.json has {len(core_claims)} core_claims; keep route-first context packets capped at 24 claims")
if len(core_claims) != len(set(core_claims)):
    errors.append("context-pack.json has duplicate core_claims; dedupe machine-readable claims")
if context.get("source_count") != len(source_items):
    errors.append(f"context-pack.json source_count={context.get('source_count')} does not match SOURCES.json count={len(source_items)}")

scorecard = json.loads((root / "scorecard-template.json").read_text(encoding="utf-8"))
if re.match(r"^rev\d{4}$", str(scorecard.get("revision", ""))):
    errors.append("scorecard-template.json should be revision-neutral; remove stale revision metadata")

if sources_json.get("revision") != active_revision:
    errors.append(f"SOURCES.json revision={sources_json.get('revision')} does not match VERSION={active_revision}")
if releases.get("latest_revision") != active_revision:
    errors.append(f"RELEASES.json latest_revision={releases.get('latest_revision')} does not match VERSION={active_revision}")
if receipt.get("revision") != active_revision:
    errors.append(f"REVISION-RECEIPT.json revision={receipt.get('revision')} does not match VERSION={active_revision}")
if context.get("revision") != active_revision:
    errors.append(f"context-pack.json revision={context.get('revision')} does not match VERSION={active_revision}")

compact_json_paths = [
    root / "SOURCES.json",
    root / "RELEASES.json",
    root / "REVISION-RECEIPT.json",
    root / "context-pack.json",
    root / "scorecard-template.json",
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
    if start_here.stat().st_size > 7000:
        errors.append(f"START_HERE.md is {start_here.stat().st_size} bytes; keep reopening surfaces compact")
    if re.search(r"^##\s+Executive answer\b", start_text, re.M):
        errors.append("START_HERE.md should stay route-first; do not add a duplicate executive-summary section")
    if re.search(r"^##\s+If you only read fifteen things\b", start_text, re.M):
        errors.append("START_HERE.md should use route clusters instead of long fixed reading canons")

archive_index_path = root / "ARCHIVE_INDEX.md"
if archive_index_path.exists():
    archive_index_text = archive_index_path.read_text(encoding="utf-8")
    if archive_index_path.stat().st_size > 12000:
        errors.append(f"ARCHIVE_INDEX.md is {archive_index_path.stat().st_size} bytes; keep the index compact and family-first")
    if "MANIFEST.json" not in archive_index_text:
        errors.append("ARCHIVE_INDEX.md must point to MANIFEST.json as the authoritative exhaustive inventory")
    bullet_links = len(re.findall(r"^-\s+\[`[^`]+`\]", archive_index_text, re.M))
    if bullet_links > 30:
        errors.append("ARCHIVE_INDEX.md should stay route-first and family-first rather than regrowing a long file-by-file dump")

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
    if proposal_scorecard.stat().st_size > 15500:
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
    if open_questions.stat().st_size > 22000:
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
    if decision_procedure.stat().st_size > 24850:
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
    compact_manifest = json.dumps(manifest_obj, separators=(",", ":")) + "\n"
    if manifest_text != compact_manifest:
        errors.append("MANIFEST.json must stay compact and match the builder output shape")

if errors:
    raise SystemExit("\n".join(errors))
print("ok")
