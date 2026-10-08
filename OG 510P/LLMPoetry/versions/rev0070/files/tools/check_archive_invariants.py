#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

REV_CTOR = re.compile(r"^do_rev\d{4}(?:_[A-Za-z0-9_-]+)?\.py$")

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})

def main(root="."):
    root=Path(root)
    checks=[]
    try:
        state=json.loads((root/"STATE.json").read_text(encoding="utf-8"))
        inv=json.loads((root/"ARCHIVE_INVARIANTS.json").read_text(encoding="utf-8"))
        add(checks,"archive_invariants_revision_current",inv.get("revision")==state.get("revision"),inv.get("revision"))
        add(checks,"archive_invariants_head_current",inv.get("current_head")==state.get("current_head"),inv.get("current_head"))
        add(checks,"archive_invariants_updated_at_current",inv.get("updated_at")==state.get("updated_at"),inv.get("updated_at"))
    except Exception as exc:
        state={}; inv={}
        add(checks,"archive_invariants_parse",False,exc)
    add(checks,"no_source_seed_dir",not (root/"source_seed").exists())
    add(checks,"no_embedded_fable_poem_dir",not (root/"specimens/Fable-Claude-F5P").exists())
    add(checks,"seed_receipt_present",(root/"seed/SEED_INPUT_RECEIPT.json").exists())
    add(checks,"seed_digest_present",(root/"docs/20-seed/SEED_DOCTRINE_DIGEST.md").exists())
    add(checks,"pruned_paths_present",(root/"PRUNED_TRANSIENT.paths").exists())
    constructors=[p.name for p in root.iterdir() if p.is_file() and REV_CTOR.fullmatch(p.name)]
    add(checks,"no_parent_dependent_revision_constructors",not constructors,constructors)
    symlinks=[p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_symlink()]
    add(checks,"no_release_tree_symlinks",not symlinks,symlinks[:20])
    try:
        spec=json.loads((root/"registries/specimen_registry.json").read_text(encoding="utf-8"))
        add(checks,"specimen_text_false",spec.get("embedded_text") is False and all(s.get("embedded_text") is False for s in spec.get("specimens",[])))
        add(checks,"specimen_count_15",len(spec.get("specimens",[]))==15)
    except Exception as exc:
        add(checks,"specimen_registry_parse",False,exc)
    try:
        from release_tree import MANIFEST_EXCLUDE, collect_files
        collect_files(root,exclude=MANIFEST_EXCLUDE)
        add(checks,"shared_release_tree_policy_accepts_cube",True)
    except Exception as exc:
        add(checks,"shared_release_tree_policy_accepts_cube",False,exc)
    ok=all(c["ok"] for c in checks)
    print(json.dumps({"ok":ok,"checks":checks,"failed":[c for c in checks if not c["ok"]]},indent=2))
    return 0 if ok else 1

if __name__=="__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv)>1 else "."))
