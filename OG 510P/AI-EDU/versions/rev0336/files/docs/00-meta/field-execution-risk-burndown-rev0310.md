# rev0310 field execution risk burndown

| Risk | rev0310 control | Residual boundary |
|---|---|---|
| A terminal readout dispatch preserves the source lane but carries a mismatched next evidence ask. | `owner_post_readout_action_integrity_error()` now requires `next_evidence_ask_class` to match the dispatch lane map. | The next ask is still only a class label; real owner context must return through the field lane. |
| A dispatch carries a public-language action not justified by the readout disposition. | The guard and recorder now require `public_language_action` to match the dispatch lane map. | The archive still cannot publish, suppress, or revise public language from local dispatch alone. |
| Optional CLI overrides create drift before a human sees it. | `record_ft0181_post_readout_action.py` blocks mismatched owner-action, next-ask, and public-language classes before writing scratch output. | Human review and later recheck/context receipt gates remain required. |
| The cube spends another pass on bureaucracy. | The pass changes one recorder, one shared guard, and one validator regression, plus focused release docs only. | Next work should keep reducing post-readout tail risk rather than adding registries. |

`FT-0181` remains live. This pass does not contact an owner, import a real CSV,
accept `SRC2+`, authorize a real active-change window, upgrade or suppress a
public claim, mutate service records, or close the followthrough.
