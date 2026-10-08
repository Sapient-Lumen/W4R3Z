# Rematch worlds need question-targeted probe contracts

The archive had accumulated several different “minimal” probe results for the final family-`10/20/50/100` two-anchor choice, but they were minimal for **different questions**.

That distinction matters.

If the inheritor needs the **exact strict path shape** as the additional-budget cap changes, the archive still needs the full strict-path machinery:
- fixed ex-post record: `[10, 20, 10000]`;
- live exact diagnosis: `10000 -> (10 or 20)`.

But if the real handoff question is only **whether added budget can ever overturn the choice**, then the tail boundary `tau(10000)` is wasted effort. It only splits the two already cap-sensitive strict subclasses.

So the archive should route probe work by question:
- exact strict-path portable record -> `[10, 20, 10000]`;
- exact strict-path live diagnosis -> probe `10000` first, then `10` after `M` or `20` after `S`;
- overturn-risk portable record -> `[10, 20]`;
- overturn-risk live diagnosis with fastest robust-material certificate -> `10`, then `20` only if needed;
- overturn-risk live diagnosis with fastest robust-stability certificate -> `20`, then `10` only if needed.

The important operational consequence is simple:
- do **not** default to the three-cap strict signature when the question is only overturn risk;
- reserve cap `10000` for the narrower task of separating the two cap-sensitive strict subclasses.

That keeps the archive leaner and keeps future recomputation matched to the real decision being made.

Pointers:
- report: `artifacts/reports/rematch_proxy_delta_question_targeted_probe_snapshot_20260306.md`
- builder: `scripts/report/build_rematch_proxy_delta_question_targeted_probe_snapshot.py`
- validator: `scripts/test/check_rematch_delta_question_targeted_probes.py`
