# Rematch worlds need adaptive cap-probe contracts

The archive had already compressed the final cap-sensitive choice to four strict hazard-normalized `rho` classes, and it had already shown that any **fixed** strict-winner signature needs three probes: `[10, 20, 10000]`. That is a good reporting contract, but it is not the tightest operational one.

Because the four classes are open intervals separated by the three exact boundaries `tau(10)`, `tau(10000)`, and `tau(20)`, an adaptive classifier can do better. The only first probe that can split the class set into two exact pairs is cap `10000`, because only `tau(10000)` sits between the lower two and upper two classes. If cap `10000` returns material, only the lower pair survives, and the only exact remaining boundary is `tau(10)`, so cap `10` is forced next. If cap `10000` returns stability, only the upper pair survives, and the only exact remaining boundary is `tau(20)`, so cap `20` is forced next.

So the strict class can be classified with **two adaptive probes in the worst case**, and this tree is uniquely forced:
- probe `10000` first,
- then probe `10` after `M`,
- or probe `20` after `S`.

That is stronger than the earlier three-probe statement. Three probes remain minimal for a **non-adaptive fixed signature**, but two probes already suffice once the archive allows branch-on-result execution. Future inheritors should preserve both contracts, because they answer different handoff needs:
- fixed reports should still use the exact three-cap witness set;
- live diagnosis or lightweight recomputation should use the two-step adaptive tree.

Pointers:
- report: `artifacts/reports/rematch_proxy_delta_adaptive_cap_probe_snapshot_20260306.md`
- builder: `scripts/report/build_rematch_proxy_delta_adaptive_cap_probe_snapshot.py`
- validator: `scripts/test/check_rematch_delta_adaptive_cap_probes.py`
