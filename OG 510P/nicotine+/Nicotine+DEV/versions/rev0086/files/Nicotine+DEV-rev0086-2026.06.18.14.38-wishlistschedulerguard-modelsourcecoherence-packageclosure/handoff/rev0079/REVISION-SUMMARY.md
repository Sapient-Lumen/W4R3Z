# rev0079 revision summary

Rev0079 deepens `SEARCH-AGAIN-EPOCH-01` without selecting a patch.

The core correction is that a network-thread acknowledgement cannot safely follow mere dequeue or admission mutation. Buddy and user searches are per-recipient server-message fan-outs, and current outgoing/packing helpers can silently stop or return without success information. A meaningful local acknowledgement must follow successful prepacking and network output ownership of the complete fan-out.

The model separately preserves the residual disconnect case: output-buffer ownership is not socket write or remote completion. Maintainers still need an explicit policy for a disconnect after acknowledgement, zero-result refreshes, replay, and stale-row presentation.

The cube refactor centralizes revision-specific authority in `data/current_revision_contract.json`; current package, runtime, and navigation audits now consume one list.

No upstream patch is selected. All generated content remains research-only.

## Validation

```text
research/model/source tests:  78/78 pass
source invariants:            35/35 pass
compile checks:               21/21 pass
upstream units:               60 passed, 1 skipped
packet authority:             187/187 pass
runtime adoption:             33/33 pass
selected patch:               none
```
