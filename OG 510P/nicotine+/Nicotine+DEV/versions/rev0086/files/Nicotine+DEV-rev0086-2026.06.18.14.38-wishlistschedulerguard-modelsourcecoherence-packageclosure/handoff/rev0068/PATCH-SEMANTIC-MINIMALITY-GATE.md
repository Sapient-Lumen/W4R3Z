# rev0068 handoff: patch semantic/minimality gate

Use this folder as the compact handoff entry for the rev0068 semantic/minimality layer.

Primary files:

```text
docs/PATCH-SEMANTIC-MINIMALITY-GATE-REV0068.md
docs/PATCH-SEMANTIC-COHERENCE-REFACTOR-REV0068.md
report_drafts/STRICT-PATCH-SEMANTIC-MINIMALITY-GATE-REV0068.md
tools/probe_rev0068_patch_semantic_minimality.py
data/rev0068_patch_semantic_summary.json
data/rev0068_patch_semantic_inventory.csv
data/rev0068_patch_semantic_marker_contract.csv
data/rev0068_patch_semantic_source_touched_files.csv
```

Helper:

```bash
python tools/probe_rev0068_patch_semantic_minimality.py --source-zip /path/to/Nicotine-source.zip --validate-existing
```

Full regeneration:

```bash
python tools/probe_rev0068_patch_semantic_minimality.py --source-zip /path/to/Nicotine-source.zip --write-data
```

Boundary:

```text
This is archived-source patch semantic support. It is not live-current upstream filing proof.
```
