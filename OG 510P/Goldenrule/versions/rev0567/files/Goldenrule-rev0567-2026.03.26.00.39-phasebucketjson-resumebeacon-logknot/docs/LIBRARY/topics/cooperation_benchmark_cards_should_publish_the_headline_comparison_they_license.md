# Cooperation benchmark cards should publish the headline comparison they license

A compact cooperation benchmark card is useful only if it does more than describe the lane.
It should also say what **headline comparison** the retained result actually licenses.
Recent benchmark-documentation and evaluation-methodology work makes the compact archive rule clear:

- `RS-GR-074` introduces **BenchmarkCards** as a standardized way to document benchmark objectives, methodologies, data sources, and limitations so benchmark users can avoid misuse and misinterpretation.
- `RS-GR-075` argues that evaluation interpretation depends on the **objective**, **task**, and **operational context**, so the same score can mean different things under different comparison goals.
- `RS-GR-076` warns that common benchmark reporting can conflate different notions of performance, making benchmark results hard to interpret for downstream decisions.
- The standing cooperation sources already show that changing language, communication regime, visibility, or process capture can materially change the measured phenomenon (`RS-GR-053`, `RS-GR-055`, `RS-GR-063`, `RS-GR-067`).

## Minimum contract

Whenever a cooperation benchmark card is retained, publish two short claim-boundary fields:

1. **headline comparison licensed** — the exact comparison the card supports, such as “cold-start fresh-partner transfer within one counterpart class under no-chat full-information conditions”; 
2. **headline comparison not licensed** — at least one nearby but stronger claim the card does **not** support without extra justification, such as generalization from proxies to real humans, from same-partner continuation to fresh-partner transfer, or from one language lane to all language lanes;
3. whether the retained aggregate is **comparative** or only **descriptive** when multiple contract rows vary at once;
4. which card rows are intentionally being varied in the headline comparison and which are being held fixed;
5. and whether any pooled roll-up should be read as a convenience summary rather than as one unified cooperation claim.

## Implementor consequence

Treat the benchmark card as a **claim boundary**, not as metadata decoration.
A score may justify “better under this declared lane contract” while failing to justify “more cooperative in general.”
If multiple contract rows vary at once, the benchmark should be described as a lane bundle or family rather than collapsed into one generic headline.

## Archive consequence

Keep the retained object tiny.
One short “licensed / not licensed” pair on the card is enough.
That prevents future sessions from laundering richly different benchmark lanes into a stronger inheritor-facing cooperation claim than the evidence supports.
