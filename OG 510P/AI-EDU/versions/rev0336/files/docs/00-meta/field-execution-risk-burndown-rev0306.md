# rev0306 field execution risk burndown

| Risk | rev0306 control | Residual boundary |
|---|---|---|
| Checker scratch CSV is mistaken for a returned owner reply. | Returned CSV guard blocks `scratch/checks`, `scratch/releases`, legacy scratch lanes, and check/smoke/test/fixture path components. | Real returned CSVs still need to live outside the archive or under `scratch/field/ft0181`. |
| Broad `SCRATCH=scratch` debug scan sees checker or release scratch. | Field router firebreak now ignores exact `checks` and `releases` scratch lanes as well as prefix-named fixture lanes. | Operators should still use the default field lane unless intentionally debugging. |
| The returned-reply path grows doctrine instead of execution. | No schema, branch family, or registry family was added; the pass changes shared guards, regressions, and short audit docs only. | The actual blocker remains outside the archive: real owner send/return/review. |
| Direct intake becomes the ordinary path. | README/START_HERE/AGENTS continue to direct real returns through `make owner-field-next CSV=...` first. | Direct tools remain for repair/debug and must stay bounded. |

`FT-0181` remains live. This pass does not contact an owner, import a real CSV,
accept `SRC2+`, authorize a live window, upgrade a public claim, or close the
followthrough.
