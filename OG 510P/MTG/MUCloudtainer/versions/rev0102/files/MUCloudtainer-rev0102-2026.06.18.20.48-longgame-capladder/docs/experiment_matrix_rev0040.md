# rev0040 experiment matrix additions

| Experiment | Status | Question |
|---|---:|---|
| Hybrid selector matched audit | added | Does behavior + limited votes + diversity + ranker prior keep union-best actions better than older selectors? |
| C++ transition shadow on hybrid branch traffic | passed | Does new branch-heavy traffic remain parity-clean against the C++ transition microkernel? |
| Selector stress on high-action/high-margin frames | next | Can we find frames where budget choice actually matters? |
| Adaptive hybrid branch racing | next | Can extra rollouts be spent only on top contenders after hybrid selection? |

rev0040 result: all three selectors tied in the smoke panel, so the next matrix should intentionally target harder frames.
