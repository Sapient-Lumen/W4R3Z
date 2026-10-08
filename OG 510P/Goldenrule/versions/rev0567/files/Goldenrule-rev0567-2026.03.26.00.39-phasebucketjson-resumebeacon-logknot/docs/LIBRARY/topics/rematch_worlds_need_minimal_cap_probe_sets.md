# Rematch worlds need minimal cap-probe sets

Key idea:
- Once the final low-delta choice has collapsed to two anchors and a scalar hazard-normalized margin `rho`, future inheritors should not rescan the whole published cap range just to classify how the winner path behaves.
- In the current proxy, two cap probes are **provably insufficient** to distinguish all four strict winner-path classes.
- The three caps `{10, 20, 10000}` are sufficient and minimal.

What changed here:
- The archive already had the exact threshold curve `tau(c)` and the four strict trajectory classes.
- This pass compresses that into a finite diagnostic contract:
  - any two cap probes can realize at most three strict winner signatures because, once `tau(a)` and `tau(b)` are ordered, one mixed pattern is impossible,
  - so four strict classes require at least three probes,
  - and the signature on caps `(10, 20, 10000)` already separates every class: `MMM`, `SMM`, `SMS`, `SSS`.

Why it matters:
- This is tighter than saying “endpoint checks are risky.” It says endpoint checks are structurally incapable of recovering the full path class.
- It also gives future inheritors a compact operational rule: probe cap `20`, then `10`, then `10000` only if needed.

Planning consequence:
- Future rematch-world archives should publish a minimal finite probe set whenever a continuous threshold path has already been reduced to a small number of qualitative classes.
- That keeps handoff logic compact while still being exact.

Pointers:
- report: `artifacts/reports/rematch_proxy_delta_minimal_cap_probe_snapshot_20260306.md`
- builder: `scripts/report/build_rematch_proxy_delta_minimal_cap_probe_snapshot.py`
- validator: `scripts/test/check_rematch_delta_minimal_cap_probes.py`
