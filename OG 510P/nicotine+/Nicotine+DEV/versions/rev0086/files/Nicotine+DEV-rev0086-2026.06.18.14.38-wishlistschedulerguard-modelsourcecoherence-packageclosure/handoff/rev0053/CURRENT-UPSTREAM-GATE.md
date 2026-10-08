# rev0053 current-upstream gate

This handoff layer is the bridge from cube-internal production-gated packets to current-upstream filing readiness.

```text
current checkout -> selected/native marker scan -> run seven fixed regressions -> update filing language -> only then file
```

Run:

```bash
python tools/probe_rev0053_current_upstream_gate.py --source-dir /path/to/current/nicotine-plus
```
