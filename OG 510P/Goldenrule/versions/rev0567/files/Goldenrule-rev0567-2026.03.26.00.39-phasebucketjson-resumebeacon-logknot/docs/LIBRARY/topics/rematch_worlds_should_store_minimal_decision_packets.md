# Rematch worlds should store minimal decision packets

The archive now has enough structure that future sessions do **not** need to keep bulky rematch decision traces every time a two-anchor choice is revisited.

The current family `10/20/50/100` proxy now supports a smaller rule:

- if declared weights or direct projective coordinates `(B,H)` are available, store one direct oracle packet;
- if the decision must be diagnosed from black-box winner symbols, store the smallest probe packet matched to the actual question;
- and only escalate to the full fixed `[10,20,10000]` checked-cap packet when exact tie-cap identification or the full checked-cap path really matters.

That matters because archive growth should follow **evidence sufficiency**, not habit.

The new executable packet surface lives at `scripts/analysis/rematch_proxy_delta_decision_packet.py`. It gives the inheritor six compact modes:

- `oracle_coordinates`
- `oracle_weights`
- `probe_robustness_fixed`
- `probe_robustness_adaptive`
- `probe_strict_adaptive`
- `probe_exact_checked_cap_path`

The compact storage rule is now straightforward.

First, direct packets dominate black-box packets whenever declarations are available. A stored `(B,H)` packet answers every currently supported question with zero probes and is leaner than duplicating the full eight-weight vector when those declarations already live elsewhere in the archive.

Second, black-box packets should be chosen by question, not by maximalism. A robustness-only handoff should not automatically store a three-cap exact-path record. Open strict-class diagnosis should use the adaptive `10000 -> (10 after M, 20 after S)` packet unless tie-cap identification is part of the task.

Third, tie-cap identification is a real escalation trigger. The adaptive strict classifier is sufficient for the four open strict classes, but exact boundary ties still require the fixed checked-cap signature on `[10,20,10000]`.

Pointers:
- packet report: `artifacts/reports/rematch_proxy_delta_decision_packet_snapshot_20260307.md`
- packet builder: `scripts/report/build_rematch_proxy_delta_decision_packet_snapshot.py`
- packet script: `scripts/analysis/rematch_proxy_delta_decision_packet.py`
- validator: `scripts/test/check_rematch_delta_decision_packets.py`
