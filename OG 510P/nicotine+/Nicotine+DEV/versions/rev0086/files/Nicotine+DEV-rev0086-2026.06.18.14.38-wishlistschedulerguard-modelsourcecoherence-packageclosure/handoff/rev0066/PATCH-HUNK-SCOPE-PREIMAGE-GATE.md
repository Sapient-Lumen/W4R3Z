# rev0066 hunk-scope/preimage gate

This handoff note points reviewers to the hunk-level proof for the archived-source patch files.

Run:

```bash
python tools/probe_rev0066_patch_hunk_scope.py --source-zip /path/to/Nicotine-source.zip
```

Expected summary:

```text
status: pass
bundle patches: 12
file-scope rows: 15/15 pass
hunk preimage rows: 41/41 pass
marker rows: 30/30 pass
negative controls: 4/4 pass
```

Scope: archived-source proof for the uploaded source bundle only. This is not a live-current checkout proof.
