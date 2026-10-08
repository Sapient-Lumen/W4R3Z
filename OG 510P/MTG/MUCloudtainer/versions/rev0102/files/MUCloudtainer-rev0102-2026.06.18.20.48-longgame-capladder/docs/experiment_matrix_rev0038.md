# rev0038 experiment matrix

| Axis | rev0038 setting | Why |
|---|---|---|
| Frame sampler | public-policy disagreement | Spend branch budget on contested decisions |
| Screener policies | counter/threat/patient/code/outcome | Diverse public-safe voters |
| Branching | full menu for small frames, budgeted subset for larger frames | Avoid skipping high-action frames entirely |
| Rollouts per selected action | 2 | Smoke-scale cost control |
| Branch max decisions | 320 | Avoid endless labels and expose truncation explicitly |
| C++ check | transition shadow for branch and payoff traffic | Keep C++ parity close to new workloads |
| Model | Ridge linear public action ranker | Keep model simple until labels improve |
| Payoff gate | promotion + statistical + replay + C++ shadow | Archive rows without overclaiming |

Open experiment questions:

```text
Does disagreement screening increase decisive labels per branch rollout?
Do screen-voted actions include best branched actions more often than behavior choices?
Do screeners merely recreate their own biases, or expose genuinely useful alternatives?
Can a matched-label audit compare screened vs unscreened on identical situations?
```
