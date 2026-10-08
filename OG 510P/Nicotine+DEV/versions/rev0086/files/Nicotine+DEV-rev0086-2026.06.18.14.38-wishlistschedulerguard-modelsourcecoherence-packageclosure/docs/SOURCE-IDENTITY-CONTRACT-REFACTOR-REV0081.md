# Source identity contract refactor — rev0081

## Failure mode

The cube had overlapping current authorities for bundle digest, archive layout, lane heads, and public refs. Independent consumers could pass while silently attributing executable evidence to different source identities.

## Single authority

`data/current_source_contract.json` now owns:

```text
source ZIP SHA-256
source-tree, archive, and Git prefixes
archive member for every lane
exact bundled lane heads
content-addressed source discovery patterns
observed public refs and the executable-proxy relationship
```

`tools/source_bundle_locator.py` exports compatibility values by loading this contract. `data/current_source_history_contract.json` references it instead of duplicating digest, Git suffix, or executable head. The superseded parallel contract is required to be absent.

## Executable guard

`tools/audit_current_source_contract.py` validates the uploaded bundle, all three nested lane archives, worktree heads, locator exports, current-tool identity de-duplication, and five deliberate mutants covering digest, lane, archive, public-head, and parallel-authority drift.

```text
source-contract checks: 42/42 pass
source-history checks:  41/41 pass
historical claims:       15
```

## Scope boundary

Public master was observed at `a96406e7aa285a3fb2a3e35900686d164a22bf02`. The executable proxy in the supplied bundle is `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`. The intervening visible commits do not alter the reviewed search flow, but whole-tree executable claims remain scoped to the bundled proxy.
