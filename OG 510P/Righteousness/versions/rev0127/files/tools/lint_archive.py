import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "START_HERE.md",
    "ARCHIVE_INDEX.md",
    "CHANGELOG.md",
    "SOURCES.md",
    "SOURCES.json",
    "CLAIM_REGISTRY.json",
    "OPEN_QUESTIONS.json",
    "ASSUMPTION_LEDGER.json",
    "DATACUBE_TRANSFER_LEDGER.json",
    "SURFACE_STATUS.json",
    "REVISION_RECEIPT.json",
    "RELEASE_MANIFEST.json",
    "docs/00-meta/charter.md",
    "docs/00-meta/method.md",
    "docs/90-quarantine/900-live-speculations.md",
]
REQUIRED.extend(sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "docs/10-canon").glob("*.md")))

for rel in REQUIRED:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing required file: {rel}")

# validate source ids used in markdown
source_ids = {item["id"] for item in json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))}

# source parity between SOURCES.md and SOURCES.json
source_urls = [item["url"] for item in json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))]
if len(source_urls) != len(set(source_urls)):
    raise SystemExit("duplicate source urls in SOURCES.json")
source_titles = [item["title"] for item in json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))]
if len(source_titles) != len(set(source_titles)):
    raise SystemExit("duplicate source titles in SOURCES.json")
sources_md = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
md_ids = set(re.findall(r"`\[(S\d{2,3})\]`", sources_md))
if md_ids != source_ids:
    raise SystemExit(f"source registry drift between SOURCES.md and SOURCES.json: md={sorted(md_ids)}, json={sorted(source_ids)}")
markdown_files = [p for p in ROOT.rglob("*.md") if ".git" not in p.parts]
used = set()
for path in markdown_files:
    text = path.read_text(encoding="utf-8")
    used.update(re.findall(r"\[(S\d{2,3})\]", text))
    for sid in re.findall(r"\[(S\d{2,3})\]", text):
        if sid not in source_ids:
            raise SystemExit(f"unknown source id {sid} in {path.relative_to(ROOT)}")

if not used:
    raise SystemExit("no source ids referenced in markdown")
unused = sorted(source_ids - used)
if unused:
    raise SystemExit(f"unused source ids in SOURCES.json: {unused}")

# canon numbering hygiene
canon_numbers = sorted(int(re.match(r"(\d+)-", p.name).group(1)) for p in (ROOT / "docs/10-canon").glob("*.md"))
if len(canon_numbers) != len(set(canon_numbers)):
    raise SystemExit("duplicate canon numbering in docs/10-canon")
if canon_numbers != sorted(canon_numbers):
    raise SystemExit(f"canon numbering order drift in docs/10-canon: {canon_numbers}")
if any(n % 5 != 0 for n in canon_numbers):
    raise SystemExit(f"canon numbering must stay on 5-step boundaries: {canon_numbers}")

# validate claim/open question ids unique
claims = json.loads((ROOT / "CLAIM_REGISTRY.json").read_text(encoding="utf-8"))["claims"]
claim_ids = [c["id"] for c in claims]
if len(claim_ids) != len(set(claim_ids)):
    raise SystemExit("duplicate claim ids")

if claim_ids != sorted(claim_ids):
    raise SystemExit(f"claim ids out of order: {claim_ids}")

questions = json.loads((ROOT / "OPEN_QUESTIONS.json").read_text(encoding="utf-8"))["questions"]
question_ids = [q["id"] for q in questions]
if len(question_ids) != len(set(question_ids)):
    raise SystemExit("duplicate open question ids")
allowed_priorities = {"high", "medium", "low"}
for q in questions:
    if q.get("priority") not in allowed_priorities:
        raise SystemExit(f"invalid open question priority for {q.get('id')}: {q.get('priority')}")
if question_ids != sorted(question_ids):
    raise SystemExit(f"open question ids out of order: {question_ids}")

assumptions = json.loads((ROOT / "ASSUMPTION_LEDGER.json").read_text(encoding="utf-8"))["assumptions"]
assumption_ids = [a.get("id") for a in assumptions]
if len(assumption_ids) != len(set(assumption_ids)):
    raise SystemExit("duplicate assumption ids")
if any(not re.fullmatch(r"AS-\d{4}", aid or "") for aid in assumption_ids):
    raise SystemExit(f"invalid assumption id format: {assumption_ids}")
if assumption_ids != sorted(assumption_ids):
    raise SystemExit(f"assumption ids out of order: {assumption_ids}")

allowed_assumption_states = {"active", "quarantined", "retired"}
for a in assumptions:
    if a.get("state") not in allowed_assumption_states:
        raise SystemExit(f"invalid or missing assumption state for {a.get('id')}: {a.get('state')}")

# validate claim support paths exist
for claim in claims:
    for rel in claim.get("support", []):
        if not (ROOT / rel).exists():
            raise SystemExit(f"claim support path missing for {claim['id']}: {rel}")

# validate archive index referenced paths exist
index_text = (ROOT / "ARCHIVE_INDEX.md").read_text(encoding="utf-8")
for rel in re.findall(r"`([^`]+)`", index_text):
    if rel.endswith((".md", ".json", ".py")):
        if not (ROOT / rel).exists():
            raise SystemExit(f"ARCHIVE_INDEX missing path: {rel}")


# validate ARCHIVE_INDEX includes every canon markdown surface
index_listed = set(re.findall(r"`([^`]+)`", index_text))
canon_docs = {p.relative_to(ROOT).as_posix() for p in (ROOT / "docs/10-canon").glob("*.md")}
claim_support_paths = {rel for claim in claims for rel in claim.get("support", []) if rel.endswith(".md")}
missing_support_from_index = sorted(claim_support_paths - index_listed)
if missing_support_from_index:
    raise SystemExit(f"ARCHIVE_INDEX missing claim-support markdown surfaces: {missing_support_from_index}")
missing_from_index = sorted(canon_docs - index_listed)
if missing_from_index:
    raise SystemExit(f"ARCHIVE_INDEX missing canon surfaces: {missing_from_index}")
canon_index_order = [rel for rel in re.findall(r"`([^`]+)`", index_text) if rel.startswith("docs/10-canon/") and rel.endswith(".md")]
canon_index_nums = [int(pathlib.Path(rel).name.split("-", 1)[0]) for rel in canon_index_order]
if canon_index_nums != sorted(canon_index_nums):
    raise SystemExit(f"ARCHIVE_INDEX canon order drift: {canon_index_order}")

# validate README listed paths and explicit revision if present
readme = (ROOT / "README.md").read_text(encoding="utf-8")
for rel in re.findall(r"`([^`]+)`", readme):
    if rel.endswith((".md", ".json")):
        if not (ROOT / rel).exists():
            raise SystemExit(f"README missing path: {rel}")

receipt = json.loads((ROOT / "REVISION_RECEIPT.json").read_text(encoding="utf-8"))
revision = receipt.get("revision")
m = re.search(r"Revision:\s*`(rev\d{4})`", readme)
if m and m.group(1) != revision:
    raise SystemExit(f"README revision mismatch: expected {revision}, got {m.group(1)}")

# validate start-here paths and route
start = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
for rel in re.findall(r"`([^`]+)`", start):
    if rel.endswith((".md", ".json")):
        if not (ROOT / rel).exists():
            raise SystemExit(f"START_HERE missing path: {rel}")
start_route = [
    re.match(r"\d+\. `([^`]+)`", line.strip()).group(1)
    for line in start.splitlines()
    if re.match(r"\d+\. `([^`]+)`", line.strip())
]

# startup-surface coverage for canon docs
readme_listed = set(re.findall(r"`([^`]+)`", readme))
start_listed = set(start_route)
missing_from_readme = sorted(canon_docs - readme_listed)
if missing_from_readme:
    raise SystemExit(f"README missing canon surfaces: {missing_from_readme}")
missing_from_start = sorted(canon_docs - start_listed)
if missing_from_start:
    raise SystemExit(f"START_HERE missing canon surfaces: {missing_from_start}")

# startup-route hygiene
readme_route = [
    re.match(r"\d+\. `([^`]+)`", line.strip()).group(1)
    for line in readme.splitlines()
    if re.match(r"\d+\. `([^`]+)`", line.strip())
]
for name, route_text, route in [("README", readme, readme_route), ("START_HERE", start, start_route)]:
    nums = [int(re.match(r"(\d+)\.", line.strip()).group(1)) for line in route_text.splitlines() if re.match(r"\d+\. `([^`]+)`", line.strip())]
    if nums != list(range(1, len(nums)+1)):
        raise SystemExit(f"{name} route numbering is not contiguous from 1")
    if len(route) != len(set(route)):
        raise SystemExit(f"{name} route contains duplicate entries")
    canon_in_route = [rel for rel in route if rel.startswith("docs/10-canon/") and rel.endswith(".md")]
    canon_nums = [int(pathlib.Path(rel).name.split("-", 1)[0]) for rel in canon_in_route]
    if canon_nums != sorted(canon_nums):
        raise SystemExit(f"{name} canon route is not in ascending numeric order")

# validate revision receipt references resolve
transfer_ids = [t["id"] for t in json.loads((ROOT / "DATACUBE_TRANSFER_LEDGER.json").read_text(encoding="utf-8"))["transfers"]]
for qid in receipt.get("open_questions", []):
    if qid not in question_ids:
        raise SystemExit(f"REVISION_RECEIPT references unknown open question: {qid}")
for tid in receipt.get("transfer_witness", []):
    if tid not in transfer_ids:
        raise SystemExit(f"REVISION_RECEIPT references unknown transfer witness: {tid}")

# revision consistency across machine-readable files
for rel in [
    "CLAIM_REGISTRY.json",
    "OPEN_QUESTIONS.json",
    "ASSUMPTION_LEDGER.json",
    "DATACUBE_TRANSFER_LEDGER.json",
    "SURFACE_STATUS.json",
    "RELEASE_MANIFEST.json",
]:
    data = json.loads((ROOT / rel).read_text(encoding="utf-8"))
    if data.get("revision") != revision:
        raise SystemExit(f"revision mismatch in {rel}: expected {revision}, got {data.get('revision')}")

# context-pack freshness and consistency
ctx = ROOT / "context-pack.json"
if not ctx.exists():
    raise SystemExit("context-pack.json missing; run make context-pack")
pack = json.loads(ctx.read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE_STATUS.json").read_text(encoding="utf-8"))
if manifest.get("bundle") != status["citation_head"]["surface"]:
    raise SystemExit("RELEASE_MANIFEST bundle drift from SURFACE_STATUS citation_head")
if pack.get("project") != "Righteousness":
    raise SystemExit("context-pack project mismatch")
if pack.get("revision") != revision:
    raise SystemExit(f"context-pack revision mismatch: expected {revision}, got {pack.get('revision')}")
if pack.get("must_read") != start_route:
    raise SystemExit("context-pack must_read drift from START_HERE route")
if pack.get("bundle") != manifest.get("bundle"):
    raise SystemExit("context-pack bundle mismatch with RELEASE_MANIFEST")
current = pack.get("current_posture", {})
if current.get("citation_head") != status["citation_head"]["surface"]:
    raise SystemExit("context-pack citation_head drift from SURFACE_STATUS")
if current.get("operational_head") != status["operational_head"]["surface"]:
    raise SystemExit("context-pack operational_head drift from SURFACE_STATUS")

# changelog hygiene
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
if changelog.count("# CHANGELOG") != 1:
    raise SystemExit("CHANGELOG should contain exactly one top-level '# CHANGELOG' heading")
if changelog.count(f"## {revision} ") != 1:
    raise SystemExit(f"CHANGELOG should mention {revision} exactly once as a revision heading")
head_match = re.search(r"^## (rev\d{4}) ", changelog, flags=re.MULTILINE)
if not head_match:
    raise SystemExit("CHANGELOG missing revision headings")
if head_match.group(1) != revision:
    raise SystemExit(f"CHANGELOG head drift: expected first revision heading {revision}, got {head_match.group(1)}")

print("lint_archive: OK")
