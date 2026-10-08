# Field execution risk burndown — rev0332

| Risk | Prior state | rev0332 change | Remaining test |
|---|---|---|---|
| Reviewed packet does not match run instructions | owner-review hashes omitted `COACH-PROMPT.md`, `RUN-CHECKLIST.md`, `CYCLE-RUN-SHEET.md`, and the discovery card | owner review now hash-locks those run-defining files before any result receipt | a real owner review must occur and then the result recorder must reject post-review prompt drift |
| Entry readiness permits local prompt edits | readiness checked owner plan, logs, and readout but not generation-time prompt/run hashes | added `run-definition-hash-stable` entry check comparing manifest hashes and owner-plan prompt SHA | run a real packet only after the owner chooses the problem and the generated files remain stable |
| Operator patches instead of regenerating | a local operator could fix wording in the prompt or run sheet after readiness, breaking provenance | docs and router language now say regenerate if run-defining instructions change | field operator must resist local hotfixes after owner plan completion |
| Control growth displaces field work | the defect could have produced another registry layer | reused readiness, owner-review, and result-recorder path; no new schema or validator family | next change should follow a real field event or another reproducible defect |

## Current unblocker

Hold one real discovery conversation, complete one local owner plan, and run at most one feasibility
cycle. Do not treat a hash-stable generated packet as evidence that a cycle occurred.
