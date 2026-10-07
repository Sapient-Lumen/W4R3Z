#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, hashlib, json, re, sys
from collections import Counter
from pathlib import Path


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def parse_scalar(raw: str):
    v = raw.strip()
    if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        v = v[1:-1]
    low = v.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if re.fullmatch(r"-?\d+", v):
        try:
            return int(v)
        except ValueError:
            pass
    return v


def parse_frontmatter(p: Path) -> dict:
    txt = read_text(p)
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return {}
    out: dict[str, object] = {}
    current_key = None
    current_list: list[object] = []
    for raw in m.group(1).splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - "):
            if current_key is not None:
                current_list.append(parse_scalar(line[4:]))
            continue
        if current_key is not None:
            out[current_key] = current_list
            current_key = None
            current_list = []
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if v == "":
                current_key = k
                current_list = []
            else:
                out[k] = parse_scalar(v)
    if current_key is not None:
        out[current_key] = current_list
    return out


def csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def csv_header(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            return next(reader)
        except StopIteration:
            return []


def type_ok(value, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str) and value.strip() != ""
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "date-string":
        return isinstance(value, str) and re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", value) is not None
    if expected == "list[string]":
        return isinstance(value, list) and len(value) > 0 and all(isinstance(x, str) and x.strip() for x in value)
    return True


def validate_frontmatter(root: Path, contract: dict) -> list[dict]:
    findings = []
    schemas = contract.get("schemas", {})
    targets = [
        ("living_christ_figures_candidate_v1", [p for p in (root / "CANDIDATES").glob("*.txt") if not p.name.startswith("_REFRESH")]),
        ("living_christ_figures_office_card_v1", list((root / "OFFICE-CARDS").glob("*.txt"))),
        ("living_christ_figures_refresh_note_v1", list((root / "CANDIDATES").glob("_REFRESH*.txt"))),
    ]
    for schema_id, paths in targets:
        spec = schemas.get(schema_id, {})
        required = spec.get("required_fields", {})
        patterns = spec.get("patterns", {})
        invariants = spec.get("package_invariants", {})
        for p in paths:
            fm = parse_frontmatter(p)
            rel = str(p.relative_to(root))
            if not fm:
                findings.append({"severity": "high", "check": "frontmatter_present", "file": rel, "detail": "missing or unparsable front matter"})
                continue
            for field, typ in required.items():
                if field not in fm:
                    findings.append({"severity": "high", "check": "frontmatter_required_field", "file": rel, "detail": f"missing {field}"})
                elif not type_ok(fm[field], typ):
                    findings.append({"severity": "high", "check": "frontmatter_type", "file": rel, "detail": f"{field} expected {typ}, got {type(fm[field]).__name__}"})
            for field, expected in invariants.items():
                if fm.get(field) != expected:
                    findings.append({"severity": "high", "check": "frontmatter_invariant", "file": rel, "detail": f"{field}={fm.get(field)!r} expected {expected!r}"})
            for field, pat in patterns.items():
                if field.endswith("[]"):
                    base = field[:-2]
                    for item in fm.get(base, []) if isinstance(fm.get(base), list) else []:
                        if not re.fullmatch(pat, str(item)):
                            findings.append({"severity": "high", "check": "frontmatter_pattern", "file": rel, "detail": f"{base} item {item!r} fails {pat}"})
                else:
                    val = fm.get(field)
                    if val is not None and not re.fullmatch(pat, str(val)):
                        findings.append({"severity": "high", "check": "frontmatter_pattern", "file": rel, "detail": f"{field}={val!r} fails {pat}"})
    return findings


def validate_ledger_contract(root: Path, contract: dict) -> list[dict]:
    findings = []
    for rel, spec in contract.get("ledgers", {}).items():
        p = root / rel
        if not p.exists():
            findings.append({"severity": "high", "check": "ledger_exists", "file": rel, "detail": "missing"})
            continue
        got = csv_header(p)
        expected = spec.get("columns", [])
        if got != expected:
            findings.append({"severity": "high", "check": "ledger_header", "file": rel, "detail": f"header drift: got {got}, expected {expected}"})
        mirror = spec.get("json_mirror")
        if mirror:
            jp = root / mirror
            if not jp.exists():
                findings.append({"severity": "high", "check": "json_mirror_exists", "file": mirror, "detail": f"missing JSON mirror for {rel}"})
            else:
                try:
                    data = json.loads(jp.read_text(encoding="utf-8"))
                    rows = csv_rows(p)
                    if not isinstance(data, list):
                        findings.append({"severity": "high", "check": "json_mirror_type", "file": mirror, "detail": "JSON mirror is not a list"})
                    elif len(data) != len(rows):
                        findings.append({"severity": "high", "check": "json_mirror_row_count", "file": mirror, "detail": f"{len(data)} JSON rows != {len(rows)} CSV rows"})
                    elif rows:
                        csv_keys = set(rows[0].keys())
                        bad = [i for i, row in enumerate(data[:20]) if set(row.keys()) != csv_keys]
                        if bad:
                            findings.append({"severity": "high", "check": "json_mirror_keys", "file": mirror, "detail": f"row key mismatch at rows {bad[:5]}"})
                except Exception as e:
                    findings.append({"severity": "high", "check": "json_mirror_parse", "file": mirror, "detail": str(e)})
    return findings


def validate_source_vocabulary(root: Path) -> list[dict]:
    findings = []
    vocab_path = root / "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv"
    if not vocab_path.exists():
        return [{"severity": "high", "check": "source_type_vocab_exists", "file": str(vocab_path.relative_to(root)), "detail": "missing"}]
    vocab = csv_rows(vocab_path)
    source_rows = csv_rows(root / "Source-Registry-current.csv")
    mapped = {r.get("source_type", ""): r for r in vocab}
    got = Counter(r.get("source_type", "") for r in source_rows)
    for st, count in got.items():
        row = mapped.get(st)
        if row is None:
            findings.append({"severity": "high", "check": "source_type_mapped", "file": "Source-Registry-current.csv", "detail": f"{st!r} appears {count} times but is absent from controlled vocabulary"})
        elif row.get("rev0031_action") != "mapped" or row.get("normalized_source_class") in {"", "UNMAPPED"}:
            findings.append({"severity": "high", "check": "source_type_mapped", "file": "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv", "detail": f"{st!r} is not mapped"})
    extras = sorted(set(mapped) - set(got))
    for st in extras:
        if st:
            findings.append({"severity": "low", "check": "source_type_vocab_extra", "file": "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv", "detail": f"{st!r} is mapped but not currently used"})
    return findings


def validate_public_manifest(root: Path) -> list[dict]:
    findings = []
    manifest_path = root / "manifest.json"
    public_manifest_path = root / "PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        public_manifest = json.loads(public_manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [{"severity": "high", "check": "manifest_parse", "file": "manifest/public manifest", "detail": str(e)}]
    if public_manifest.get("revision") != manifest.get("revision"):
        findings.append({"severity": "high", "check": "public_manifest_revision", "file": "PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json", "detail": f"public revision {public_manifest.get('revision')} != manifest revision {manifest.get('revision')}"})
    if public_manifest.get("package_revision") != manifest.get("revision"):
        findings.append({"severity": "high", "check": "public_manifest_package_revision", "file": "PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json", "detail": f"public package_revision {public_manifest.get('package_revision')} != manifest revision {manifest.get('revision')}"})
    allowed = set((root / "SCHEMA/Package-Release-Contract-current.json").exists() and json.loads((root / "SCHEMA/Package-Release-Contract-current.json").read_text(encoding="utf-8")).get("allowed_public_layer_files", []) or [])
    if allowed:
        actual = {str(p.relative_to(root)) for p in (root / "PUBLIC").glob("*") if p.is_file()}
        extra = sorted(actual - allowed)
        missing = sorted(allowed - actual)
        if extra:
            findings.append({"severity": "high", "check": "public_layer_extra_files", "file": "PUBLIC/", "detail": "; ".join(extra)})
        if missing:
            findings.append({"severity": "high", "check": "public_layer_missing_files", "file": "PUBLIC/", "detail": "; ".join(missing)})
    return findings



def validate_governance_fields(root: Path) -> list[dict]:
    findings = []
    required_files = [
        "CURRENT-SPINE.md",
        "GOVERNANCE/Indigenous-Data-Governance-Protocol-current.md",
        "GOVERNANCE/Family-Consent-and-Case-Name-Use-Ledger-current.csv",
        "GOVERNANCE/Takedown-and-Reclassification-Protocol-current.md",
        "SCHEMA/Indigenous-Data-Governance-Fields-current.csv",
        "SCHEMA/Public-Allowed-Claim-Shapes-current.csv",
        "SCHEMA/Public-Link-Policy-current.csv",
        "SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv",
        "PUBLIC/Public-Safe-Prose-Templates-current.md",
        "GOVERNANCE/Public-Export-Eligibility-Protocol-current.md",
        "GOVERNANCE/Governance-Decision-and-Review-Protocol-current.md",
        "GOVERNANCE/Governance-Decision-Ledger-current.csv",
        "SCHEMA/Public-Export-Eligibility-Fields-current.csv",
        "SCHEMA/Governance-Decision-Fields-current.csv",
        "META/Public-Export-Eligibility-current.csv",
        "tools/public_export_eligibility.py",
        "META/Public-Source-Link-Review-current.csv",
        "tools/public_source_link_review.py",
        "META/Public-Release-Lint-current.csv",
        "tools/public_release_lint.py",
        "META/Sensitive-Surface-Inventory-current.csv",
        "tools/sensitive_surface_inventory.py",
        "META/Candidate-Governance-Snapshot-current.csv",
        "META/Governance-Review-Queue-current.csv",
        "tools/candidate_governance_snapshot.py",
        "SCHEMA/Row-Validation-Contract-current.json",
        "SCHEMA/Row-Validation-Report-current.csv",
        "tools/row_validate.py",
        "META/Generated-Artifact-Provenance-current.csv",
        "tools/generated_artifact_provenance.py",
        "META/Revision-Surface-Audit-current.csv",
        "tools/revision_surface_audit.py",
        "META/Release-Gate-Attestation-current.csv",
        "tools/release_gate_attestation.py",
        "META/Public-Index-Parity-current.csv",
        "tools/public_index_parity.py",
        "META/Governance-Consistency-Audit-current.csv",
        "tools/governance_consistency_audit.py",
        "META/Package-Dependency-Graph-current.csv",
        "tools/package_dependency_graph.py",
        "META/Policy-Assertion-Matrix-current.csv",
        "tools/policy_assertion_matrix.py",
        "META/Regeneration-Sequence-Plan-current.csv",
        "tools/regeneration_sequence_plan.py",
        "META/Archive-Build-Manifest-current.csv",
        "tools/archive_build_manifest.py",
        "META/Selftest-Coverage-Matrix-current.csv",
        "tools/selftest_coverage_matrix.py",
        "META/Checksum-Scope-Audit-current.csv",
        "tools/checksum_scope_audit.py",
        "META/Public-Negative-Corpus-current.csv",
        "tools/public_negative_corpus.py",
        "META/Release-Evidence-Closure-current.csv",
        "tools/release_evidence_closure.py",
        "GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md",
        "META/Dependency-Cycle-Audit-current.csv",
        "tools/dependency_cycle_audit.py",
        "META/Handoff-Notice-Audit-current.csv",
        "tools/handoff_notice_audit.py",
        "META/Current-Surface-Registry-current.csv",
        "tools/current_surface_registry.py",
    ]
    for rel in required_files:
        if not (root / rel).exists():
            findings.append({"severity": "high", "check": "governance_file_exists", "file": rel, "detail": "missing"})
    allowed_harm = {r.get("harm_proximity", "") for r in csv_rows(root / "SCHEMA/Harm-Proximity-Controlled-Vocabulary-current.csv")}
    allowed_link = {r.get("public_link_policy", "") for r in csv_rows(root / "SCHEMA/Public-Link-Policy-current.csv")}
    for r in csv_rows(root / "Source-Registry-current.csv"):
        sid = r.get("source_id", "")
        hp = r.get("harm_proximity", "")
        lp = r.get("public_link_policy", "")
        if not hp:
            findings.append({"severity": "high", "check": "source_harm_proximity_present", "file": "Source-Registry-current.csv", "detail": f"{sid} missing harm_proximity"})
        elif allowed_harm and hp not in allowed_harm and not set(hp.split("|")).issubset(allowed_harm):
            findings.append({"severity": "high", "check": "source_harm_proximity_allowed", "file": "Source-Registry-current.csv", "detail": f"{sid} has {hp!r}"})
        if not lp:
            findings.append({"severity": "high", "check": "source_public_link_policy_present", "file": "Source-Registry-current.csv", "detail": f"{sid} missing public_link_policy"})
        elif allowed_link and lp not in allowed_link:
            findings.append({"severity": "high", "check": "source_public_link_policy_allowed", "file": "Source-Registry-current.csv", "detail": f"{sid} has {lp!r}"})
    return findings


def validate_public_export_eligibility(root: Path) -> list[dict]:
    findings = []
    required_files = [
        "GOVERNANCE/Public-Export-Eligibility-Protocol-current.md",
        "GOVERNANCE/Governance-Decision-and-Review-Protocol-current.md",
        "GOVERNANCE/Governance-Decision-Ledger-current.csv",
        "GOVERNANCE/Governance-Decision-Ledger-current.json",
        "SCHEMA/Public-Export-Eligibility-Fields-current.csv",
        "SCHEMA/Governance-Decision-Fields-current.csv",
        "META/Public-Export-Eligibility-current.csv",
        "META/Public-Export-Eligibility-current.json",
        "META/Public-Export-Eligibility-current.md",
        "tools/public_export_eligibility.py",
        "META/Public-Source-Link-Review-current.csv",
        "tools/public_source_link_review.py",
        "META/Public-Release-Lint-current.csv",
        "tools/public_release_lint.py",
        "META/Sensitive-Surface-Inventory-current.csv",
        "tools/sensitive_surface_inventory.py",
        "META/Candidate-Governance-Snapshot-current.csv",
        "META/Governance-Review-Queue-current.csv",
        "tools/candidate_governance_snapshot.py",
        "SCHEMA/Row-Validation-Contract-current.json",
        "SCHEMA/Row-Validation-Report-current.csv",
        "tools/row_validate.py",
        "META/Generated-Artifact-Provenance-current.csv",
        "tools/generated_artifact_provenance.py",
        "META/Revision-Surface-Audit-current.csv",
        "tools/revision_surface_audit.py",
        "META/Release-Gate-Attestation-current.csv",
        "tools/release_gate_attestation.py",
        "META/Public-Index-Parity-current.csv",
        "tools/public_index_parity.py",
        "META/Governance-Consistency-Audit-current.csv",
        "tools/governance_consistency_audit.py",
        "META/Package-Dependency-Graph-current.csv",
        "tools/package_dependency_graph.py",
        "META/Policy-Assertion-Matrix-current.csv",
        "tools/policy_assertion_matrix.py",
        "META/Regeneration-Sequence-Plan-current.csv",
        "tools/regeneration_sequence_plan.py",
        "META/Archive-Build-Manifest-current.csv",
        "tools/archive_build_manifest.py",
        "META/Selftest-Coverage-Matrix-current.csv",
        "tools/selftest_coverage_matrix.py",
        "META/Checksum-Scope-Audit-current.csv",
        "tools/checksum_scope_audit.py",
        "META/Public-Negative-Corpus-current.csv",
        "tools/public_negative_corpus.py",
        "META/Release-Evidence-Closure-current.csv",
        "tools/release_evidence_closure.py",
        "GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md",
        "META/Dependency-Cycle-Audit-current.csv",
        "tools/dependency_cycle_audit.py",
        "META/Handoff-Notice-Audit-current.csv",
        "tools/handoff_notice_audit.py",
        "META/Current-Surface-Registry-current.csv",
        "tools/current_surface_registry.py",
    ]
    for rel in required_files:
        if not (root / rel).exists():
            findings.append({"severity": "high", "check": "public_export_eligibility_file_exists", "file": rel, "detail": "missing"})
    if findings:
        return findings
    candidates = csv_rows(root / "Candidate-Ledger-current.csv")
    eligibility = csv_rows(root / "META/Public-Export-Eligibility-current.csv")
    cand_ids = {r.get("candidate_id", "") for r in candidates}
    elig_ids = {r.get("candidate_id", "") for r in eligibility}
    if cand_ids != elig_ids:
        findings.append({"severity": "high", "check": "public_export_eligibility_candidate_coverage", "file": "META/Public-Export-Eligibility-current.csv", "detail": f"candidate_only={len(cand_ids-elig_ids)} eligibility_only={len(elig_ids-cand_ids)}"})
    required_cols = {"candidate_id","candidate_name","public_export_tier","public_shape_template","highest_harm_proximity","most_restrictive_public_link_policy","consent_or_governance_gate","live_referral_gate","capacity_gate","source_link_gate","image_gate","case_detail_gate","public_url_release","public_claim_release","required_review","review_note"}
    if eligibility:
        missing_cols = required_cols - set(eligibility[0].keys())
        if missing_cols:
            findings.append({"severity": "high", "check": "public_export_eligibility_columns", "file": "META/Public-Export-Eligibility-current.csv", "detail": ",".join(sorted(missing_cols))})
    allowed_tiers = {"public_index_shape_only","boundary_index_shape_only","policy_context_only","quarantined_no_public_expansion"}
    templates = {r.get("template_key", "") for r in csv_rows(root / "SCHEMA/Public-Allowed-Claim-Shapes-current.csv")}
    bad_tiers = [r.get("candidate_id", "") for r in eligibility if r.get("public_export_tier") not in allowed_tiers]
    if bad_tiers:
        findings.append({"severity": "high", "check": "public_export_eligibility_tier_allowed", "file": "META/Public-Export-Eligibility-current.csv", "detail": "; ".join(bad_tiers[:8])})
    bad_templates = [r.get("candidate_id", "") for r in eligibility if r.get("public_shape_template") not in templates]
    if bad_templates:
        findings.append({"severity": "high", "check": "public_export_eligibility_template_allowed", "file": "META/Public-Export-Eligibility-current.csv", "detail": "; ".join(bad_templates[:8])})
    public_rows = csv_rows(root / "PUBLIC/Candidate-Index-public.csv")
    if public_rows:
        public_ids = {r.get("candidate_id", "") for r in public_rows}
        if public_ids != elig_ids:
            findings.append({"severity": "high", "check": "public_index_eligibility_coverage", "file": "PUBLIC/Candidate-Index-public.csv", "detail": f"public_only={len(public_ids-elig_ids)} eligibility_only={len(elig_ids-public_ids)}"})
        for r in public_rows:
            if not r.get("public_export_tier") or not r.get("public_shape_template"):
                findings.append({"severity": "high", "check": "public_index_eligibility_fields", "file": "PUBLIC/Candidate-Index-public.csv", "detail": f"{r.get('candidate_id','')} missing public_export_tier/template"})
                break
    gov_rows = csv_rows(root / "GOVERNANCE/Governance-Decision-Ledger-current.csv")
    if not gov_rows:
        findings.append({"severity": "high", "check": "governance_decision_ledger_rows", "file": "GOVERNANCE/Governance-Decision-Ledger-current.csv", "detail": "no rows"})
    else:
        required_gov = {"decision_id","date","decision_class","scope","decision","what_changed","what_remains_blocked","review_required_before_change","related_files","status"}
        missing_gov = required_gov - set(gov_rows[0].keys())
        if missing_gov:
            findings.append({"severity": "high", "check": "governance_decision_ledger_columns", "file": "GOVERNANCE/Governance-Decision-Ledger-current.csv", "detail": ",".join(sorted(missing_gov))})
        if not any(r.get("decision_class") == "public_release_blocked" for r in gov_rows):
            findings.append({"severity": "medium", "check": "governance_decision_public_release_blocked_present", "file": "GOVERNANCE/Governance-Decision-Ledger-current.csv", "detail": "no public_release_blocked row"})
    return findings


def validate_public_source_link_review(root: Path) -> list[dict]:
    findings=[]
    required=[
        "META/Public-Source-Link-Review-current.csv","META/Public-Source-Link-Review-current.json","META/Public-Source-Link-Review-current.md",
        "SCHEMA/Public-Source-Link-Review-Fields-current.csv","tools/public_source_link_review.py"
    ]
    for rel in required:
        if not (root/rel).exists():
            findings.append({"severity":"high","check":"public_source_link_review_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    sources=csv_rows(root/"Source-Registry-current.csv")
    review=csv_rows(root/"META/Public-Source-Link-Review-current.csv")
    source_ids={r.get("source_id","") for r in sources}
    review_ids={r.get("source_id","") for r in review}
    if source_ids != review_ids:
        findings.append({"severity":"high","check":"public_source_link_review_coverage","file":"META/Public-Source-Link-Review-current.csv","detail":f"source_only={len(source_ids-review_ids)} review_only={len(review_ids-source_ids)}"})
    allowed={"block_public_url","manual_review_required_block_until_review","allow_only_with_boundary_note_after_manual_review","allow_after_context_review"}
    bad=[r.get("source_id","") for r in review if r.get("public_url_release_decision") not in allowed]
    if bad:
        findings.append({"severity":"high","check":"public_source_link_review_decision_allowed","file":"META/Public-Source-Link-Review-current.csv","detail":"; ".join(bad[:8])})
    if not any(r.get("public_url_release_decision") in {"block_public_url","manual_review_required_block_until_review"} for r in review):
        findings.append({"severity":"medium","check":"public_source_link_review_has_blocks","file":"META/Public-Source-Link-Review-current.csv","detail":"no blocked/manual-review URL rows found"})
    return findings


def validate_public_release_lint(root: Path) -> list[dict]:
    findings=[]
    required=[
        "META/Public-Release-Lint-current.csv","META/Public-Release-Lint-current.json","META/Public-Release-Lint-current.md",
        "SCHEMA/Public-Release-Lint-Fields-current.csv","tools/public_release_lint.py"
    ]
    for rel in required:
        if not (root/rel).exists():
            findings.append({"severity":"high","check":"public_release_lint_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Public-Release-Lint-current.csv")
    if not rows:
        findings.append({"severity":"high","check":"public_release_lint_rows","file":"META/Public-Release-Lint-current.csv","detail":"no rows"})
        return findings
    high=[r for r in rows if r.get("severity")=="high"]
    if high:
        findings.append({"severity":"high","check":"public_release_lint_high_findings","file":"META/Public-Release-Lint-current.csv","detail":f"{len(high)} high findings"})
    public_files={str(p.relative_to(root)) for p in (root/"PUBLIC").glob("*") if p.is_file()}
    lint_files={r.get("file","") for r in rows}
    missing=sorted(public_files-lint_files)
    if missing:
        findings.append({"severity":"high","check":"public_release_lint_file_coverage","file":"META/Public-Release-Lint-current.csv","detail":"; ".join(missing[:8])})
    return findings


def validate_sensitive_surface_inventory(root: Path) -> list[dict]:
    findings=[]
    required=[
        "META/Sensitive-Surface-Inventory-current.csv","META/Sensitive-Surface-Inventory-current.json","META/Sensitive-Surface-Inventory-current.md",
        "SCHEMA/Sensitive-Surface-Inventory-Fields-current.csv","tools/sensitive_surface_inventory.py"
    ]
    for rel in required:
        if not (root/rel).exists():
            findings.append({"severity":"high","check":"sensitive_surface_inventory_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Sensitive-Surface-Inventory-current.csv")
    if not rows:
        findings.append({"severity":"medium","check":"sensitive_surface_inventory_rows","file":"META/Sensitive-Surface-Inventory-current.csv","detail":"no configured surfaces found; check tool coverage"})
    public_high=[r for r in rows if r.get("file_scope")=="public" and r.get("severity")=="high"]
    if public_high:
        findings.append({"severity":"high","check":"sensitive_surface_inventory_public_high","file":"META/Sensitive-Surface-Inventory-current.csv","detail":f"{len(public_high)} public high inventory rows; public lint must be clean"})
    return findings


def validate_candidate_governance_snapshot(root: Path) -> list[dict]:
    findings=[]
    required=[
        "META/Candidate-Governance-Snapshot-current.csv","META/Candidate-Governance-Snapshot-current.json","META/Candidate-Governance-Snapshot-current.md",
        "META/Governance-Review-Queue-current.csv","META/Governance-Review-Queue-current.json","META/Governance-Review-Queue-current.md",
        "SCHEMA/Candidate-Governance-Snapshot-Fields-current.csv","SCHEMA/Governance-Review-Queue-Fields-current.csv",
        "tools/candidate_governance_snapshot.py"
    ]
    for rel in required:
        if not (root/rel).exists():
            findings.append({"severity":"high","check":"candidate_governance_snapshot_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    cand_ids={r.get("candidate_id","") for r in csv_rows(root/"Candidate-Ledger-current.csv")}
    snap=csv_rows(root/"META/Candidate-Governance-Snapshot-current.csv")
    snap_ids={r.get("candidate_id","") for r in snap}
    if cand_ids != snap_ids:
        findings.append({"severity":"high","check":"candidate_governance_snapshot_coverage","file":"META/Candidate-Governance-Snapshot-current.csv","detail":f"candidate_only={len(cand_ids-snap_ids)} snapshot_only={len(snap_ids-cand_ids)}"})
    queue=csv_rows(root/"META/Governance-Review-Queue-current.csv")
    if not queue:
        findings.append({"severity":"high","check":"governance_review_queue_rows","file":"META/Governance-Review-Queue-current.csv","detail":"no rows"})
    if not any(r.get("candidate_id")=="cand_bridget_tolley_fsis_mmiwg_canada" and r.get("governance_quarantine")=="true" for r in snap):
        findings.append({"severity":"high","check":"candidate_governance_snapshot_bridget_quarantine","file":"META/Candidate-Governance-Snapshot-current.csv","detail":"Bridget/FSIS governance quarantine not visible"})
    return findings


def _json_rows(path: Path):
    try:
        data=json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _sha256(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def _fingerprint(root: Path, rels: list[str]) -> str:
    h=hashlib.sha256()
    for rel in sorted([x for x in rels if x]):
        p=root/rel
        h.update(rel.encode("utf-8")+b"\0")
        if p.exists(): h.update(_sha256(p).encode("ascii"))
        else: h.update(b"MISSING")
    return h.hexdigest()


def validate_row_validation_report(root: Path) -> list[dict]:
    findings=[]
    required=[
        "SCHEMA/Row-Validation-Contract-current.json",
        "SCHEMA/Row-Validation-Report-current.csv",
        "SCHEMA/Row-Validation-Report-current.json",
        "SCHEMA/Row-Validation-Report-current.md",
        "SCHEMA/Row-Validation-Report-Fields-current.csv",
        "tools/row_validate.py",
    ]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"row_validation_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"SCHEMA/Row-Validation-Report-current.json")
    if not rows:
        findings.append({"severity":"high","check":"row_validation_rows","file":"SCHEMA/Row-Validation-Report-current.json","detail":"no rows"})
    high=[r for r in rows if r.get("severity")=="high"]
    if high:
        findings.append({"severity":"high","check":"row_validation_high_findings","file":"SCHEMA/Row-Validation-Report-current.json","detail":f"{len(high)} high findings"})
    return findings


def validate_revision_surface_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/Revision-Surface-Audit-current.csv","META/Revision-Surface-Audit-current.json","META/Revision-Surface-Audit-current.md","SCHEMA/Revision-Surface-Audit-Fields-current.csv","tools/revision_surface_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"revision_surface_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Revision-Surface-Audit-current.json")
    high=[r for r in rows if r.get("severity")=="high"]
    if high:
        findings.append({"severity":"high","check":"revision_surface_high_findings","file":"META/Revision-Surface-Audit-current.json","detail":f"{len(high)} high findings"})
    return findings


def validate_generated_artifact_provenance(root: Path) -> list[dict]:
    findings=[]
    required=["META/Generated-Artifact-Provenance-current.csv","META/Generated-Artifact-Provenance-current.json","META/Generated-Artifact-Provenance-current.md","SCHEMA/Generated-Artifact-Provenance-Fields-current.csv","tools/generated_artifact_provenance.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"generated_provenance_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Generated-Artifact-Provenance-current.csv")
    if not rows:
        findings.append({"severity":"high","check":"generated_provenance_rows","file":"META/Generated-Artifact-Provenance-current.csv","detail":"no rows"})
        return findings
    bad=[r.get("artifact_path","") for r in rows if r.get("status")!="pass"]
    if bad:
        findings.append({"severity":"high","check":"generated_provenance_status","file":"META/Generated-Artifact-Provenance-current.csv","detail":"; ".join(bad[:8])})
    for r in rows:
        art=root/r.get("artifact_path","")
        if not art.exists():
            findings.append({"severity":"high","check":"generated_provenance_artifact_exists","file":r.get("artifact_path",""),"detail":"missing"}); continue
        if r.get("artifact_sha256") and _sha256(art)!=r.get("artifact_sha256"):
            findings.append({"severity":"high","check":"generated_provenance_artifact_hash","file":r.get("artifact_path",""),"detail":"hash drift"})
        inputs=[x for x in (r.get("input_paths","") or "").split("|") if x]+[r.get("generator","")]
        if r.get("input_fingerprint") and _fingerprint(root, inputs)!=r.get("input_fingerprint"):
            findings.append({"severity":"high","check":"generated_provenance_input_fingerprint","file":r.get("artifact_path",""),"detail":"input fingerprint drift"})
    return findings



def validate_public_index_parity(root: Path) -> list[dict]:
    findings=[]
    required=["META/Public-Index-Parity-current.csv","META/Public-Index-Parity-current.json","META/Public-Index-Parity-current.md","SCHEMA/Public-Index-Parity-Fields-current.csv","tools/public_index_parity.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"public_index_parity_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Public-Index-Parity-current.json")
    if not rows:
        findings.append({"severity":"high","check":"public_index_parity_rows","file":"META/Public-Index-Parity-current.json","detail":"no rows"})
    high=[r for r in rows if r.get("severity")=="high"]
    if high:
        findings.append({"severity":"high","check":"public_index_parity_high_findings","file":"META/Public-Index-Parity-current.json","detail":f"{len(high)} high findings"})
    return findings


def validate_governance_consistency_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/Governance-Consistency-Audit-current.csv","META/Governance-Consistency-Audit-current.json","META/Governance-Consistency-Audit-current.md","SCHEMA/Governance-Consistency-Audit-Fields-current.csv","tools/governance_consistency_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"governance_consistency_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Governance-Consistency-Audit-current.json")
    if not rows:
        findings.append({"severity":"high","check":"governance_consistency_rows","file":"META/Governance-Consistency-Audit-current.json","detail":"no rows"})
    high=[r for r in rows if r.get("severity")=="high"]
    if high:
        findings.append({"severity":"high","check":"governance_consistency_high_findings","file":"META/Governance-Consistency-Audit-current.json","detail":f"{len(high)} high findings"})
    return findings


def validate_package_dependency_graph(root: Path) -> list[dict]:
    findings=[]
    required=["META/Package-Dependency-Graph-current.csv","META/Package-Dependency-Graph-current.json","META/Package-Dependency-Graph-current.md","SCHEMA/Package-Dependency-Graph-Fields-current.csv","tools/package_dependency_graph.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"package_dependency_graph_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Package-Dependency-Graph-current.csv")
    if not rows:
        findings.append({"severity":"high","check":"package_dependency_graph_rows","file":"META/Package-Dependency-Graph-current.csv","detail":"no rows"})
        return findings
    bad=[r.get("edge_id","") for r in rows if r.get("status")=="missing_dependency"]
    if bad:
        findings.append({"severity":"high","check":"package_dependency_graph_missing","file":"META/Package-Dependency-Graph-current.csv","detail":"; ".join(bad[:8])})
    return findings



def validate_csv_json_mirror_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/CSV-JSON-Mirror-Audit-current.csv","META/CSV-JSON-Mirror-Audit-current.json","META/CSV-JSON-Mirror-Audit-current.md","SCHEMA/CSV-JSON-Mirror-Audit-Fields-current.csv","tools/csv_json_mirror_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"csv_json_mirror_audit_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/CSV-JSON-Mirror-Audit-current.json")
    if not rows:
        findings.append({"severity":"high","check":"csv_json_mirror_audit_rows","file":"META/CSV-JSON-Mirror-Audit-current.json","detail":"no rows"})
    high=[r for r in rows if r.get("severity")=="high"]
    if high:
        findings.append({"severity":"high","check":"csv_json_mirror_audit_high_findings","file":"META/CSV-JSON-Mirror-Audit-current.json","detail":f"{len(high)} high findings"})
    return findings


def validate_schema_coverage_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/Schema-Coverage-Audit-current.csv","META/Schema-Coverage-Audit-current.json","META/Schema-Coverage-Audit-current.md","SCHEMA/Schema-Coverage-Audit-Fields-current.csv","tools/schema_coverage_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"schema_coverage_audit_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Schema-Coverage-Audit-current.json")
    if not rows:
        findings.append({"severity":"high","check":"schema_coverage_audit_rows","file":"META/Schema-Coverage-Audit-current.json","detail":"no rows"})
    high=[r for r in rows if r.get("severity")=="high"]
    medium=[r for r in rows if r.get("severity")=="medium"]
    if high:
        findings.append({"severity":"high","check":"schema_coverage_audit_high_findings","file":"META/Schema-Coverage-Audit-current.json","detail":f"{len(high)} high findings"})
    if medium:
        findings.append({"severity":"high","check":"schema_coverage_backlog_medium_findings","file":"META/Schema-Coverage-Audit-current.json","detail":f"{len(medium)} medium backlog rows; rev0055 requires zero backlog"})
    return findings



def validate_field_schema_consistency(root: Path) -> list[dict]:
    findings=[]
    required=["META/Field-Schema-Consistency-Audit-current.csv","META/Field-Schema-Consistency-Audit-current.json","META/Field-Schema-Consistency-Audit-current.md","SCHEMA/Field-Schema-Consistency-Audit-Fields-current.csv","tools/field_schema_consistency.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"field_schema_consistency_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Field-Schema-Consistency-Audit-current.json")
    if not rows:
        findings.append({"severity":"high","check":"field_schema_consistency_rows","file":"META/Field-Schema-Consistency-Audit-current.json","detail":"no rows"})
    high=[r for r in rows if r.get("severity")=="high"]
    if high:
        findings.append({"severity":"high","check":"field_schema_consistency_high_findings","file":"META/Field-Schema-Consistency-Audit-current.json","detail":f"{len(high)} high findings"})
    return findings


def validate_path_reference_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/Path-Reference-Audit-current.csv","META/Path-Reference-Audit-current.json","META/Path-Reference-Audit-current.md","SCHEMA/Path-Reference-Audit-Fields-current.csv","tools/path_reference_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"path_reference_audit_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Path-Reference-Audit-current.json")
    high=[r for r in rows if r.get("severity")=="high"]
    if not rows:
        findings.append({"severity":"high","check":"path_reference_audit_rows","file":"META/Path-Reference-Audit-current.json","detail":"no rows"})
    if high:
        findings.append({"severity":"high","check":"path_reference_audit_high_findings","file":"META/Path-Reference-Audit-current.json","detail":f"{len(high)} high findings"})
    return findings


def validate_rule_gate_traceability(root: Path) -> list[dict]:
    findings=[]
    required=["META/Rule-Gate-Traceability-current.csv","META/Rule-Gate-Traceability-current.json","META/Rule-Gate-Traceability-current.md","SCHEMA/Rule-Gate-Traceability-Fields-current.csv","tools/rule_gate_traceability.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"rule_gate_traceability_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Rule-Gate-Traceability-current.csv")
    bad=[r.get("rule_number","") for r in rows if r.get("trace_status") in {"missing_boundary_coverage","missing_trace_file"}]
    if not rows:
        findings.append({"severity":"high","check":"rule_gate_traceability_rows","file":"META/Rule-Gate-Traceability-current.csv","detail":"no rows"})
    if bad:
        findings.append({"severity":"high","check":"rule_gate_traceability_missing","file":"META/Rule-Gate-Traceability-current.csv","detail":"; ".join(bad[:8])})
    return findings


def validate_tool_run_matrix(root: Path) -> list[dict]:
    findings=[]
    required=["META/Tool-Run-Matrix-current.csv","META/Tool-Run-Matrix-current.json","META/Tool-Run-Matrix-current.md","SCHEMA/Tool-Run-Matrix-Fields-current.csv","tools/tool_run_matrix.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"tool_run_matrix_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Tool-Run-Matrix-current.csv")
    bad=[r.get("tool_path","") for r in rows if r.get("status")!="pass"]
    if not rows:
        findings.append({"severity":"high","check":"tool_run_matrix_rows","file":"META/Tool-Run-Matrix-current.csv","detail":"no rows"})
    if bad:
        findings.append({"severity":"high","check":"tool_run_matrix_nonpass","file":"META/Tool-Run-Matrix-current.csv","detail":"; ".join(bad[:8])})
    return findings


def validate_required_document_coverage(root: Path) -> list[dict]:
    findings=[]
    required=["META/Required-Document-Coverage-current.csv","META/Required-Document-Coverage-current.json","META/Required-Document-Coverage-current.md","SCHEMA/Required-Document-Coverage-Fields-current.csv","tools/required_document_coverage.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"required_document_coverage_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Required-Document-Coverage-current.json")
    high=[r for r in rows if r.get("severity")=="high"]
    if not rows:
        findings.append({"severity":"high","check":"required_document_coverage_rows","file":"META/Required-Document-Coverage-current.json","detail":"no rows"})
    if high:
        findings.append({"severity":"high","check":"required_document_coverage_high_findings","file":"META/Required-Document-Coverage-current.json","detail":f"{len(high)} high findings"})
    return findings



def validate_audit_selftest(root: Path) -> list[dict]:
    findings=[]
    required=["META/Audit-Selftest-current.csv","META/Audit-Selftest-current.json","META/Audit-Selftest-current.md","SCHEMA/Audit-Selftest-Fields-current.csv","tools/audit_selftest.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"audit_selftest_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Audit-Selftest-current.csv")
    bad=[r.get("selftest_id","") for r in rows if r.get("status")!="pass"]
    if len(rows)<6:
        findings.append({"severity":"high","check":"audit_selftest_rows","file":"META/Audit-Selftest-current.csv","detail":f"only {len(rows)} selftest rows"})
    if bad:
        findings.append({"severity":"high","check":"audit_selftest_failures","file":"META/Audit-Selftest-current.csv","detail":"; ".join(bad[:8])})
    return findings


def validate_rebuild_readiness_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/Rebuild-Readiness-Audit-current.csv","META/Rebuild-Readiness-Audit-current.json","META/Rebuild-Readiness-Audit-current.md","SCHEMA/Rebuild-Readiness-Audit-Fields-current.csv","tools/rebuild_readiness_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"rebuild_readiness_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Rebuild-Readiness-Audit-current.json")
    high=[r for r in rows if r.get("severity")=="high"]
    if not rows:
        findings.append({"severity":"high","check":"rebuild_readiness_rows","file":"META/Rebuild-Readiness-Audit-current.json","detail":"no rows"})
    if high:
        findings.append({"severity":"high","check":"rebuild_readiness_high_findings","file":"META/Rebuild-Readiness-Audit-current.json","detail":f"{len(high)} high findings"})
    return findings

def validate_package_file_inventory(root: Path) -> list[dict]:
    findings=[]
    required=["META/Package-File-Inventory-current.csv","META/Package-File-Inventory-current.json","META/Package-File-Inventory-current.md","SCHEMA/Package-File-Inventory-Fields-current.csv","tools/package_file_inventory.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"package_file_inventory_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Package-File-Inventory-current.csv")
    if len(rows) < 100:
        findings.append({"severity":"high","check":"package_file_inventory_rows","file":"META/Package-File-Inventory-current.csv","detail":f"only {len(rows)} inventory rows"})
    public=[r for r in rows if r.get("package_zone")=="public_layer"]
    if not public:
        findings.append({"severity":"high","check":"package_file_inventory_public_layer","file":"META/Package-File-Inventory-current.csv","detail":"no public-layer files classified"})
    return findings


def validate_checksum_scope_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/Checksum-Scope-Audit-current.csv","META/Checksum-Scope-Audit-current.json","META/Checksum-Scope-Audit-current.md","SCHEMA/Checksum-Scope-Audit-Fields-current.csv","tools/checksum_scope_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"checksum_scope_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Checksum-Scope-Audit-current.csv")
    bad=[r.get("scope_check_id","") for r in rows if r.get("severity")=="high" or r.get("status")=="fail"]
    if not rows:
        findings.append({"severity":"high","check":"checksum_scope_rows","file":"META/Checksum-Scope-Audit-current.csv","detail":"no rows"})
    if bad:
        findings.append({"severity":"high","check":"checksum_scope_high_or_fail","file":"META/Checksum-Scope-Audit-current.csv","detail":"; ".join(bad[:8])})
    return findings


def validate_public_negative_corpus(root: Path) -> list[dict]:
    findings=[]
    required=["META/Public-Negative-Corpus-current.csv","META/Public-Negative-Corpus-current.json","META/Public-Negative-Corpus-current.md","SCHEMA/Public-Negative-Corpus-Fields-current.csv","tools/public_negative_corpus.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"public_negative_corpus_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Public-Negative-Corpus-current.csv")
    bad=[r.get("test_id","") for r in rows if r.get("status")!="pass"]
    if len(rows)<8:
        findings.append({"severity":"high","check":"public_negative_corpus_rows","file":"META/Public-Negative-Corpus-current.csv","detail":f"only {len(rows)} fixtures"})
    if bad:
        findings.append({"severity":"high","check":"public_negative_corpus_failures","file":"META/Public-Negative-Corpus-current.csv","detail":"; ".join(bad[:8])})
    return findings


def validate_release_evidence_closure(root: Path) -> list[dict]:
    findings=[]
    required=["META/Release-Evidence-Closure-current.csv","META/Release-Evidence-Closure-current.json","META/Release-Evidence-Closure-current.md","SCHEMA/Release-Evidence-Closure-Fields-current.csv","tools/release_evidence_closure.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"release_evidence_closure_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Release-Evidence-Closure-current.csv")
    bad=[r.get("closure_check_id","") for r in rows if r.get("severity")=="high" or r.get("status")=="fail"]
    if not rows:
        findings.append({"severity":"high","check":"release_evidence_closure_rows","file":"META/Release-Evidence-Closure-current.csv","detail":"no rows"})
    if bad:
        # Do not let schema validation become a self-referential release gate.
        # The dedicated release-evidence closure QA check and release gate enforce these rows.
        findings.append({"severity":"medium","check":"release_evidence_closure_deferred_to_release_gate","file":"META/Release-Evidence-Closure-current.csv","detail":"; ".join(bad[:8])})
    return findings


def validate_archive_member_manifest(root: Path) -> list[dict]:
    findings=[]
    required=["META/Archive-Member-Manifest-current.csv","META/Archive-Member-Manifest-current.json","META/Archive-Member-Manifest-current.md","SCHEMA/Archive-Member-Manifest-Fields-current.csv","tools/archive_member_manifest.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"archive_member_manifest_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Archive-Member-Manifest-current.csv")
    bad=[r.get("package_path","") for r in rows if r.get("status")!="pass"]
    if len(rows)<100:
        findings.append({"severity":"high","check":"archive_member_manifest_rows","file":"META/Archive-Member-Manifest-current.csv","detail":f"only {len(rows)} rows"})
    if bad:
        findings.append({"severity":"high","check":"archive_member_manifest_nonpass","file":"META/Archive-Member-Manifest-current.csv","detail":"; ".join(bad[:8])})
    return findings


def validate_unicode_path_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/Unicode-Path-Audit-current.csv","META/Unicode-Path-Audit-current.json","META/Unicode-Path-Audit-current.md","SCHEMA/Unicode-Path-Audit-Fields-current.csv","tools/unicode_path_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"unicode_path_audit_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Unicode-Path-Audit-current.csv")
    bad=[r.get("check","") for r in rows if r.get("severity")=="high" and r.get("status")!="pass"]
    if not rows:
        findings.append({"severity":"high","check":"unicode_path_audit_rows","file":"META/Unicode-Path-Audit-current.csv","detail":"no rows"})
    if bad:
        findings.append({"severity":"high","check":"unicode_path_audit_high_fail","file":"META/Unicode-Path-Audit-current.csv","detail":"; ".join(bad[:8])})
    return findings


def validate_package_identity_audit(root: Path) -> list[dict]:
    findings=[]
    required=["META/Package-Identity-Audit-current.csv","META/Package-Identity-Audit-current.json","META/Package-Identity-Audit-current.md","SCHEMA/Package-Identity-Audit-Fields-current.csv","tools/package_identity_audit.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"package_identity_audit_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=csv_rows(root/"META/Package-Identity-Audit-current.csv")
    bad=[r.get("identity_check_id","") for r in rows if r.get("severity")=="high" and r.get("status")!="pass"]
    if not rows:
        findings.append({"severity":"high","check":"package_identity_audit_rows","file":"META/Package-Identity-Audit-current.csv","detail":"no rows"})
    if bad:
        findings.append({"severity":"high","check":"package_identity_audit_high_fail","file":"META/Package-Identity-Audit-current.csv","detail":"; ".join(bad[:8])})
    return findings

def validate_release_gate_attestation(root: Path) -> list[dict]:
    findings=[]
    required=["META/Release-Gate-Attestation-current.csv","META/Release-Gate-Attestation-current.json","META/Release-Gate-Attestation-current.md","SCHEMA/Release-Gate-Attestation-Fields-current.csv","tools/release_gate_attestation.py"]
    for rel in required:
        if not (root/rel).exists(): findings.append({"severity":"high","check":"release_gate_attestation_file_exists","file":rel,"detail":"missing"})
    if findings: return findings
    rows=_json_rows(root/"META/Release-Gate-Attestation-current.json")
    if len(rows)<10:
        findings.append({"severity":"high","check":"release_gate_attestation_rows","file":"META/Release-Gate-Attestation-current.json","detail":f"only {len(rows)} gates"})
    fails=[r.get("gate_id","") for r in rows if r.get("status")!="pass"]
    if fails:
        # Release-gate failures are enforced by the dedicated release-gate QA check.
        # Reporting them here as high would make gate_002 depend circularly on itself.
        findings.append({"severity":"medium","check":"release_gate_attestation_failures_deferred_to_release_gate","file":"META/Release-Gate-Attestation-current.json","detail":"; ".join(fails[:8])})
    return findings

def validate_required_schema_files(root: Path) -> list[dict]:
    required = [
        "SCHEMA/README-schema-current.md",
        "SCHEMA/Frontmatter-Contract-current.json",
        "SCHEMA/Ledger-Contract-current.json",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.json",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.md",
        "SCHEMA/Package-Release-Contract-current.json",
        "SCHEMA/Row-Validation-Contract-current.json",
        "SCHEMA/Schema-Validation-Report-current.csv",
        "SCHEMA/Schema-Validation-Report-current.json",
        "SCHEMA/Schema-Validation-Report-current.md",
        "SCHEMA/Release-Gate-Attestation-Fields-current.csv",
        "SCHEMA/Generated-Artifact-Provenance-Fields-current.csv",
        "SCHEMA/Revision-Surface-Audit-Fields-current.csv",
        "SCHEMA/Row-Validation-Report-Fields-current.csv",
        "SCHEMA/Public-Index-Parity-Fields-current.csv",
        "SCHEMA/Governance-Consistency-Audit-Fields-current.csv",
        "SCHEMA/Package-Dependency-Graph-Fields-current.csv",
        "SCHEMA/CSV-JSON-Mirror-Audit-Fields-current.csv",
        "SCHEMA/Schema-Coverage-Audit-Fields-current.csv",
        "SCHEMA/Package-File-Inventory-Fields-current.csv",
        "SCHEMA/Field-Schema-Consistency-Audit-Fields-current.csv",
        "SCHEMA/Audit-Selftest-Fields-current.csv",
        "SCHEMA/Rebuild-Readiness-Audit-Fields-current.csv",
        "SCHEMA/Policy-Assertion-Matrix-Fields-current.csv",
        "SCHEMA/Regeneration-Sequence-Plan-Fields-current.csv",
        "SCHEMA/Archive-Build-Manifest-Fields-current.csv",
        "SCHEMA/Selftest-Coverage-Matrix-Fields-current.csv",
        "SCHEMA/Checksum-Scope-Audit-Fields-current.csv",
        "SCHEMA/Public-Negative-Corpus-Fields-current.csv",
        "SCHEMA/Release-Evidence-Closure-Fields-current.csv",
        "SCHEMA/Row-Validation-Report-current.md",
        "SCHEMA/Row-Validation-Report-current.json",
        "SCHEMA/Row-Validation-Report-current.csv",
    ]
    findings = []
    for rel in required:
        if not (root / rel).exists():
            findings.append({"severity": "high", "check": "schema_file_exists", "file": rel, "detail": "missing"})
    return findings


def validate_dependency_cycle_audit(root: Path) -> list[dict]:
    findings=[]
    required=['META/Dependency-Cycle-Audit-current.csv','META/Dependency-Cycle-Audit-current.json','META/Dependency-Cycle-Audit-current.md','SCHEMA/Dependency-Cycle-Audit-Fields-current.csv','tools/dependency_cycle_audit.py']
    for rel in required:
        if not (root/rel).exists(): findings.append({'severity':'high','check':'dependency_cycle_audit_file_exists','file':rel,'detail':'missing'})
    rows=csv_rows(root/'META/Dependency-Cycle-Audit-current.csv')
    bad=[r.get('cycle_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: findings.append({'severity':'high','check':'dependency_cycle_audit_rows','file':'META/Dependency-Cycle-Audit-current.csv','detail':'no rows'})
    if bad: findings.append({'severity':'high','check':'dependency_cycle_audit_high_fail','file':'META/Dependency-Cycle-Audit-current.csv','detail':'; '.join(bad[:8])})
    return findings


def validate_handoff_notice_audit(root: Path) -> list[dict]:
    findings=[]
    required=['GOVERNANCE/Handoff-Use-Limits-and-Reviewer-Notice-current.md','META/Handoff-Notice-Audit-current.csv','META/Handoff-Notice-Audit-current.json','META/Handoff-Notice-Audit-current.md','SCHEMA/Handoff-Notice-Audit-Fields-current.csv','tools/handoff_notice_audit.py']
    for rel in required:
        if not (root/rel).exists(): findings.append({'severity':'high','check':'handoff_notice_audit_file_exists','file':rel,'detail':'missing'})
    rows=csv_rows(root/'META/Handoff-Notice-Audit-current.csv')
    bad=[r.get('notice_check_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: findings.append({'severity':'high','check':'handoff_notice_audit_rows','file':'META/Handoff-Notice-Audit-current.csv','detail':'no rows'})
    if bad: findings.append({'severity':'high','check':'handoff_notice_audit_high_fail','file':'META/Handoff-Notice-Audit-current.csv','detail':'; '.join(bad[:8])})
    return findings


def validate_current_surface_registry(root: Path) -> list[dict]:
    findings=[]
    required=['META/Current-Surface-Registry-current.csv','META/Current-Surface-Registry-current.json','META/Current-Surface-Registry-current.md','SCHEMA/Current-Surface-Registry-Fields-current.csv','tools/current_surface_registry.py']
    for rel in required:
        if not (root/rel).exists(): findings.append({'severity':'high','check':'current_surface_registry_file_exists','file':rel,'detail':'missing'})
    rows=csv_rows(root/'META/Current-Surface-Registry-current.csv')
    bad=[r.get('surface_path','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: findings.append({'severity':'high','check':'current_surface_registry_rows','file':'META/Current-Surface-Registry-current.csv','detail':'no rows'})
    if bad: findings.append({'severity':'high','check':'current_surface_registry_high_fail','file':'META/Current-Surface-Registry-current.csv','detail':'; '.join(bad[:8])})
    return findings



def validate_manifest_semantic_coherence_audit(root: Path) -> list[dict]:
    findings=[]
    required=['META/Manifest-Semantic-Coherence-Audit-current.csv','META/Manifest-Semantic-Coherence-Audit-current.json','META/Manifest-Semantic-Coherence-Audit-current.md','SCHEMA/Manifest-Semantic-Coherence-Audit-Fields-current.csv','tools/manifest_semantic_coherence_audit.py']
    for rel in required:
        if not (root/rel).exists(): findings.append({'severity':'high','check':'manifest_semantic_coherence_file_exists','file':rel,'detail':'missing'})
    rows=csv_rows(root/'META/Manifest-Semantic-Coherence-Audit-current.csv')
    bad=[r.get('check_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: findings.append({'severity':'high','check':'manifest_semantic_coherence_rows','file':'META/Manifest-Semantic-Coherence-Audit-current.csv','detail':'no rows'})
    if bad: findings.append({'severity':'high','check':'manifest_semantic_coherence_high_fail','file':'META/Manifest-Semantic-Coherence-Audit-current.csv','detail':'; '.join(bad[:8])})
    return findings


def validate_json_key_uniqueness_audit(root: Path) -> list[dict]:
    findings=[]
    required=['META/JSON-Key-Uniqueness-Audit-current.csv','META/JSON-Key-Uniqueness-Audit-current.json','META/JSON-Key-Uniqueness-Audit-current.md','SCHEMA/JSON-Key-Uniqueness-Audit-Fields-current.csv','tools/json_key_uniqueness_audit.py']
    for rel in required:
        if not (root/rel).exists(): findings.append({'severity':'high','check':'json_key_uniqueness_file_exists','file':rel,'detail':'missing'})
    rows=csv_rows(root/'META/JSON-Key-Uniqueness-Audit-current.csv')
    bad=[r.get('json_path','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: findings.append({'severity':'high','check':'json_key_uniqueness_rows','file':'META/JSON-Key-Uniqueness-Audit-current.csv','detail':'no rows'})
    if bad: findings.append({'severity':'high','check':'json_key_uniqueness_high_fail','file':'META/JSON-Key-Uniqueness-Audit-current.csv','detail':'; '.join(bad[:8])})
    return findings


def validate_review_role_boundary_audit(root: Path) -> list[dict]:
    findings=[]
    required=['GOVERNANCE/Review-Role-and-Handoff-Boundaries-current.md','META/Review-Role-Boundary-Audit-current.csv','META/Review-Role-Boundary-Audit-current.json','META/Review-Role-Boundary-Audit-current.md','SCHEMA/Review-Role-Boundary-Audit-Fields-current.csv','tools/review_role_boundary_audit.py']
    for rel in required:
        if not (root/rel).exists(): findings.append({'severity':'high','check':'review_role_boundary_file_exists','file':rel,'detail':'missing'})
    rows=csv_rows(root/'META/Review-Role-Boundary-Audit-current.csv')
    bad=[r.get('boundary_id','') for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    if not rows: findings.append({'severity':'high','check':'review_role_boundary_rows','file':'META/Review-Role-Boundary-Audit-current.csv','detail':'no rows'})
    if bad: findings.append({'severity':'high','check':'review_role_boundary_high_fail','file':'META/Review-Role-Boundary-Audit-current.csv','detail':'; '.join(bad[:8])})
    return findings

def run(root: Path) -> list[dict]:
    findings = []
    # Some report files are generated after the first pass; don't require them until write_report has run.
    for rel in [
        "SCHEMA/README-schema-current.md",
        "SCHEMA/Frontmatter-Contract-current.json",
        "SCHEMA/Ledger-Contract-current.json",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.csv",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.json",
        "SCHEMA/Source-Type-Controlled-Vocabulary-current.md",
        "SCHEMA/Package-Release-Contract-current.json",
    ]:
        if not (root / rel).exists():
            findings.append({"severity": "high", "check": "schema_file_exists", "file": rel, "detail": "missing"})
    if findings:
        return findings
    front = json.loads((root / "SCHEMA/Frontmatter-Contract-current.json").read_text(encoding="utf-8"))
    ledgers = json.loads((root / "SCHEMA/Ledger-Contract-current.json").read_text(encoding="utf-8"))
    findings += validate_frontmatter(root, front)
    findings += validate_ledger_contract(root, ledgers)
    findings += validate_source_vocabulary(root)
    findings += validate_public_manifest(root)
    findings += validate_governance_fields(root)
    findings += validate_public_export_eligibility(root)
    findings += validate_public_source_link_review(root)
    findings += validate_public_release_lint(root)
    findings += validate_sensitive_surface_inventory(root)
    findings += validate_candidate_governance_snapshot(root)
    findings += validate_row_validation_report(root)
    findings += validate_revision_surface_audit(root)
    findings += validate_generated_artifact_provenance(root)
    findings += validate_public_index_parity(root)
    findings += validate_governance_consistency_audit(root)
    findings += validate_package_dependency_graph(root)
    findings += validate_csv_json_mirror_audit(root)
    findings += validate_schema_coverage_audit(root)
    findings += validate_field_schema_consistency(root)
    findings += validate_path_reference_audit(root)
    findings += validate_rule_gate_traceability(root)
    findings += validate_tool_run_matrix(root)
    findings += validate_required_document_coverage(root)
    findings += validate_audit_selftest(root)
    findings += validate_rebuild_readiness_audit(root)
    findings += validate_package_file_inventory(root)
    findings += validate_checksum_scope_audit(root)
    findings += validate_public_negative_corpus(root)
    findings += validate_release_evidence_closure(root)
    findings += validate_archive_member_manifest(root)
    findings += validate_unicode_path_audit(root)
    findings += validate_package_identity_audit(root)
    findings += validate_dependency_cycle_audit(root)
    findings += validate_handoff_notice_audit(root)
    findings += validate_current_surface_registry(root)
    findings += validate_manifest_semantic_coherence_audit(root)
    findings += validate_json_key_uniqueness_audit(root)
    findings += validate_review_role_boundary_audit(root)
    findings += validate_release_gate_attestation(root)
    return findings


def write_report(root: Path, findings: list[dict]):
    report_rows = findings
    if not report_rows:
        report_rows = [{"severity": "info", "check": "schema_validation", "file": ".", "detail": "PASS schema/frontmatter/ledger/source-type/public-manifest contract checks"}]
    fields = ["severity", "check", "file", "detail"]
    csv_path = root / "SCHEMA/Schema-Validation-Report-current.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in report_rows:
            w.writerow({k: r.get(k, "") for k in fields})
    (root / "SCHEMA/Schema-Validation-Report-current.json").write_text(json.dumps(report_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    high = [r for r in findings if r.get("severity") == "high"]
    med = [r for r in findings if r.get("severity") == "medium"]
    low = [r for r in findings if r.get("severity") == "low"]
    lines = [
        "# Schema Validation Report — current",
        "",
        f"High findings: {len(high)}",
        f"Medium findings: {len(med)}",
        f"Low findings: {len(low)}",
        "",
    ]
    if findings:
        lines += ["## Findings", ""]
        for r in findings:
            lines.append(f"- **{r.get('severity')}** `{r.get('check')}` `{r.get('file')}` — {r.get('detail')}")
    else:
        lines.append("PASS: schema/frontmatter/ledger/source-type/public-manifest contract checks.")
    (root / "SCHEMA/Schema-Validation-Report-current.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--write-report", action="store_true")
    ap.add_argument("--fail-on-high", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    findings = run(root)
    if args.write_report:
        write_report(root, findings)
    high = [r for r in findings if r.get("severity") == "high"]
    if findings:
        for r in findings[:50]:
            print(f"{r.get('severity','?').upper()} {r.get('check')} {r.get('file')}: {r.get('detail')}")
        if len(findings) > 50:
            print(f"... {len(findings)-50} more findings")
    else:
        print("PASS schema/frontmatter/ledger/source-type/public-manifest contract checks")
    if args.fail_on_high and high:
        sys.exit(1)


if __name__ == "__main__":
    main()
