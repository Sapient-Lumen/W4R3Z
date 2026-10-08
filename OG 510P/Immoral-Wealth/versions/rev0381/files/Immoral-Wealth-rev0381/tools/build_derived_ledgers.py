#!/usr/bin/env python3
"""Regenerate current operator surfaces, indexes, provenance audit, and manifest.

The build is deterministic for unchanged source files when REVISION-RECEIPT.json is
unchanged. SOURCE_DATE_EPOCH may override the receipt timestamp.
"""
from pathlib import Path
import collections, datetime, hashlib, json, os, re

ROOT=Path(__file__).resolve().parents[1]
REV=(ROOT/"VERSION").read_text(encoding="utf-8").strip()


def load(rel): return json.loads((ROOT/rel).read_text(encoding="utf-8"))
def dump(rel,obj): (ROOT/rel).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def build_timestamp():
    epoch=os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        return datetime.datetime.fromtimestamp(int(epoch),tz=datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
    receipt=load("REVISION-RECEIPT.json")
    if not receipt.get("generated_at"): raise RuntimeError("Receipt generated_at required for deterministic build")
    return receipt["generated_at"]

GEN=build_timestamp()

def actual_counts():
    schema=load("docs/20-program/scoreboard-schema.json")
    props=(((schema.get("properties") or {}).get("fields") or {}).get("properties") or {})
    fields=load("docs/00-meta/field-registry.json").get("fields",[])
    evidence=load("cases/EVIDENCE_LEDGER.json")
    return {
      "case_memo_count":len(list((ROOT/"cases").glob("*-case.md"))),
      "scoreboard_count":len(list((ROOT/"cases").glob("*-scoreboard.json"))),
      "source_count":len(load("SOURCES.json").get("sources",[])),
      "schema_field_count":len(props),
      "registered_unused_field_count":sum(1 for r in fields if r.get("lifecycle_status")=="registered_unused"),
      "evidence_edge_count":evidence.get("evidence_edge_count")
    }

def write_mechanical():
    evidence=load("cases/EVIDENCE_LEDGER.json"); verified=load("cases/VERIFIED_CLAIM_EDGE_LEDGER.json")
    rows=evidence.get("edge_rows",[]); vrows=verified.get("verified_claim_edges",[])
    by_quality=collections.Counter(r.get("evidence_quality","<missing>") for r in rows)
    by_case=collections.defaultdict(list)
    for r in rows: by_case[r.get("case_id")].append(r)
    pairs={(r.get("case_id"),r.get("source_id")) for r in rows}
    cms=[]
    for cid,rs in by_case.items():
        q=collections.Counter(r.get("evidence_quality","<missing>") for r in rs)
        cms.append({"case_id":cid,"mechanical_association_count":len(rs),"unique_source_count":len({r.get('source_id') for r in rs}),"unique_claim_path_count":len({r.get('claim_path') for r in rs}),"scoreboard_source_ids_row_count":q.get("scoreboard_source_ids",0),"verified_claim_edge_count":sum(1 for v in vrows if v.get("case_id")==cid)})
    cms.sort(key=lambda x:x["mechanical_association_count"],reverse=True)
    out={"revision_current":REV,"generated_at":GEN,"source_ledger":"cases/EVIDENCE_LEDGER.json","status":"derived_mechanical_routes_not_proof","counts":{"mechanical_association_count":len(rows),"unique_case_source_pair_count":len(pairs),"edge_rows_per_unique_case_source_pair":round(len(rows)/max(1,len(pairs)),3),"scoreboard_source_ids_row_count":by_quality.get("scoreboard_source_ids",0),"verified_claim_edge_count":len(vrows)},"evidence_quality_counts":dict(sorted(by_quality.items())),"top_cases_by_mechanical_associations":cms[:30],"verified_edge_pilot":"cases/VERIFIED_CLAIM_EDGE_LEDGER.json"}
    dump("cases/MECHANICAL_EVIDENCE_SUMMARY.json",out)
    lines=["---",f"revision_current: {REV}",f"generated_at: {GEN}","status: active","---","","# Mechanical evidence summary","",f"- mechanical_association_count: {len(rows)}",f"- unique_case_source_pair_count: {len(pairs)}",f"- locator_bound_evidence_record_count: {len(vrows)}","- semantics: mechanical associations are discovery and citation routes, not proof.","","## Top cases by mechanical associations",""]
    for r in cms[:30]: lines.append(f"- `{r['case_id']}`: {r['mechanical_association_count']} mechanical associations; {r['verified_claim_edge_count']} locator-bound evidence records")
    (ROOT/"cases/MECHANICAL_EVIDENCE_SUMMARY.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def write_backlog_md():
    d=load("cases/CLAIM_ATOM_BACKLOG.json")
    ranked=sorted([r for r in d.get("claim_atoms",[]) if isinstance(r.get("priority"),int)],key=lambda r:r["priority"])
    lines=["---","project: Immoral Wealth","status: claim_atom_backlog",f"revision_current: {REV}",f"generated_at: {GEN}","---","",f"# Claim atom backlog — {REV}","",f"The archive has **{d.get('verified_claim_edge_count')} locator-bound evidence records**. Claim atoms are open work units, not evidence or verdicts.","","## Top open atoms",""]
    for r in ranked: lines.append(f"{r['priority']}. `{r['claim_atom_id']}` — `{r['case_id']}` — {r['needed_edge']}")
    (ROOT/"cases/CLAIM_ATOM_BACKLOG.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def write_queue_md():
    d=load("docs/00-meta/high-risk-substantive-work-queue.json")
    lines=["---",f"revision_current: {REV}",f"generated_at: {GEN}","title: High-Risk Substantive Work Queue","status: active","---","","# High-risk substantive work queue","","Items are ranked by decisive certification risk. A listed source or task is not itself proof.",""]
    for r in d.get("work_items",[]): lines.append(f"{r['priority']}. `{r['work_item_id']}` — `{r['case_id']}` — {r['deliverable']}")
    (ROOT/"docs/00-meta/high-risk-substantive-work-queue.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def write_verified_md():
    d=load("cases/VERIFIED_CLAIM_EDGE_LEDGER.json"); rows=d.get("verified_claim_edges",[])
    cc=collections.Counter(r.get("case_id") for r in rows)
    lines=["---",f"revision_current: {REV}",f"generated_at: {GEN}","title: Locator-Bound Evidence Record Ledger","status: active_semantic_boundary","---","",f"# Locator-bound evidence record ledger — {REV}","",f"Historical filenames retain `VERIFIED_CLAIM_EDGE` for compatibility. The operator term is **locator-bound evidence records**.","",f"- record_count: {len(rows)}",f"- case_count: {len(cc)}","- independently reviewed records: 0",f"- contradict records: {collections.Counter(r.get("relationship_code") for r in rows).get("contradicts",0)}","- certified current cases: 0","- structural completeness is not substantive verification.","","## Cases with records",""]
    for cid,n in sorted(cc.items()): lines.append(f"- `{cid}`: {n}")
    lines += ["","## Current change","",f"Current revision: {REV}. Locator-bound records are regenerated from the live JSON ledger; certification remains separate from structural evidence."]
    (ROOT/"cases/VERIFIED_CLAIM_EDGE_LEDGER.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def write_report_quarantine():
    report_rows=[]; jm=mm=0; gen_counter=collections.Counter()
    for p in sorted((ROOT/"reports").glob("*")):
        if p.suffix not in [".json",".md"]: continue
        m=re.search(r"rev(\d{4})",p.name); filename_rev=f"rev{m.group(1)}" if m else None; declared=None; generated=None
        if p.suffix==".json":
            try:
                d=json.loads(p.read_text(encoding="utf-8")); declared=d.get("revision") or d.get("revision_current") or d.get("current_revision"); generated=d.get("generated_at")
            except Exception: declared="[json_parse_error]"
        else:
            txt=p.read_text(encoding="utf-8",errors="ignore")[:3000]
            r=re.search(r"(?m)^(?:revision|revision_current|current_revision):\s*(rev\d{4})",txt); declared=r.group(1) if r else None
            g=re.search(r"(?m)^generated_at:\s*([^\n]+)",txt); generated=g.group(1).strip() if g else None
        if generated: gen_counter[generated]+=1
        mismatch=bool(filename_rev and declared and filename_rev!=declared)
        if mismatch and p.suffix==".json": jm+=1
        if mismatch and p.suffix==".md": mm+=1
        report_rows.append({"path":f"reports/{p.name}","filename_revision":filename_rev,"declared_revision":declared,"generated_at":generated,"revision_mismatch":mismatch,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
    dump("docs/00-meta/report-provenance-quarantine.json",{"revision_current":REV,"generated_at":GEN,"status":"historical_report_provenance_quarantine","counts":{"report_file_count_scanned":len(report_rows),"json_revision_mismatch_count":jm,"markdown_revision_mismatch_count":mm,"shared_generated_at_2026_06_13T19_37_00Z_count":gen_counter.get("2026-06-13T19:37:00Z",0)},"all_report_rows":report_rows})

def write_index():
    counts=actual_counts(); all_files=sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file())
    dump("ARCHIVE_INDEX.json",{"project":"Immoral Wealth","revision_current":REV,"generated_at":GEN,"file_count":len(all_files),"current_counts":counts,"files":all_files})
    lines=["---",f"revision_current: {REV}",f"generated_at: {GEN}","status: archive_index","---","","# Archive index","",f"Current live counts: **{counts['case_memo_count']} case memos**, **{counts['scoreboard_count']} scoreboards**, **{counts['source_count']} sources**, **{counts['schema_field_count']} registered fields**, **{counts['registered_unused_field_count']} registered_unused fields**, and **{counts['evidence_edge_count']} mechanical evidence associations**.","","## Files"]
    lines += [f"- `{x}`" for x in all_files]
    (ROOT/"ARCHIVE_INDEX.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

def write_manifest():
    rows=[]
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file(): continue
        rel=str(p.relative_to(ROOT))
        if rel in {"MANIFEST.json","MANIFEST.sha256"}: continue
        raw=p.read_bytes(); rows.append({"path":rel,"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest()})
    dump("MANIFEST.json",{"revision":REV,"generated_utc":GEN,"policy":"all files except MANIFEST.json and MANIFEST.sha256; checksum authenticates MANIFEST.json","file_count":len(rows),"files":rows})
    (ROOT/"MANIFEST.sha256").write_text(f"{hashlib.sha256((ROOT/'MANIFEST.json').read_bytes()).hexdigest()}  MANIFEST.json\n",encoding="utf-8")

def main():
    write_mechanical(); write_backlog_md(); write_queue_md(); write_verified_md(); write_report_quarantine(); write_index(); write_manifest()
    print("Regenerated deterministic operator surfaces, index, provenance audit, and manifest.")

if __name__=="__main__": main()
