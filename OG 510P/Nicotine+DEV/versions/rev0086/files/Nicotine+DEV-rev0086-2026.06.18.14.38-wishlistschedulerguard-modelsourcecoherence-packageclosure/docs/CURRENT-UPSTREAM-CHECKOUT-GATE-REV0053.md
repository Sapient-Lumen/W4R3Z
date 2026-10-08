# Current-upstream checkout gate — rev0053

rev0053 continues from the official rev0052 package and does **not** promote a new private packet.

rev0052 made every filing field explicit, but still left the top pre-filing blocker unresolved:

```text
fresh current upstream checkout -> classify native/equivalent fixes -> run seven fixed-regression gates -> update/retire/hold packets
```

The build container could not resolve `github.com`, so rev0053 could not perform that checkout locally. Instead, it adds a portable checkout-gate harness and makes the current-source decision explicit rather than silently relying on archived source anchors or web snippets.

```text
strict report-candidates: 7
production-gated maintainer packets: 7
production-ready disclosure texts in cube: 7
new private packets in rev0053: 0
current checkout completed in container: no
portable checkout harness added: yes
archived rev0003 marker scan rows: 21
```

Run:

```bash
python tools/probe_rev0053_current_upstream_gate.py
python tools/probe_rev0053_current_upstream_gate.py --source-zip /path/to/Nicotine-source.zip --expect-archived-baseline
python tools/probe_rev0053_current_upstream_gate.py --source-dir /path/to/fresh/current/nicotine-plus
```

The helper is conservative. Marker scans are only a triage signal; final filing status still requires running the seven fixed-behavior regressions against current source.

---

## Rev0055 source-use clarification

The uploaded `Nicotine-source(1).zip` is an external archived-source input and is being used. rev0055 records its hash, validates rev0051 anchors against it, reruns the rev0053 source-zip marker scan against it, and reruns the rev0046 selected patch stack on extracted source lanes.

The remaining "fresh current checkout" language refers only to live-current external filing requirements. It does not mean the uploaded source bundle was absent or unused.

