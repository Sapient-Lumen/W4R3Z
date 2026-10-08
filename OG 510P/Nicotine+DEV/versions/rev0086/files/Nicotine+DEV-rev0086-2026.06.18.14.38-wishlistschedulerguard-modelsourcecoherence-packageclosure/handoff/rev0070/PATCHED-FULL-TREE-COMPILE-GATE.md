# rev0070 patched full-tree compile gate

Run from the cube root:

```bash
python tools/probe_rev0070_full_tree_compile_gate.py --source-zip /path/to/Nicotine-source.zip --validate-existing
```

Expected summary:

```text
status: pass
patch apply rows: 12/12 pass
full-tree compile rows: 439/439 pass
critical file hashes: 15/15 pass
```

This gate depends on the external uploaded source bundle. It does not embed source trees in the cube.
