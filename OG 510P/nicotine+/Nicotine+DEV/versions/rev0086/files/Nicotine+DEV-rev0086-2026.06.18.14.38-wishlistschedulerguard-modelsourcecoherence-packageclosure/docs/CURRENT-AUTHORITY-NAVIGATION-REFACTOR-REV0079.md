# Current authority and navigation refactor — rev0079

## Problem

The active package and runtime audits each maintained their own revision-specific lists. In rev0078, the package contract held 36 required paths, four status outputs, and five CSV outputs, while the runtime contract repeated all six current scripts. Nine revision-specific path strings had to be edited across those contracts.

This is a quiet but serious cube failure mode: a new probe or document can become current in the README while one validator still checks the prior revision. Each validator may remain green because it is internally consistent with its own stale list.

## Refactor

`data/current_revision_contract.json` is now the sole machine-readable owner of:

```text
current revision
primary packet
open-first authority paths
current navigation files
current scripts
required status outputs
required nonempty CSV outputs
required navigation mentions
forbidden stale navigation targets
```

`tools/audit_current_navigation.py` validates that contract and emits a hash/size inventory. `tools/audit_current_package.py` and `tools/audit_cube_runtime_adoption.py` now consume the same contract instead of duplicating current path lists.

Historical documents and scripts remain unchanged. The refactor changes current authority, not evidence history.

## Failure modes now caught

```text
README points to the prior disposition
START-HERE omits the current machine authority
queue names a stale probe
runtime audit forgets a newly active script
package audit validates a different revision than the ledger
revision-specific authority path survives a revision rollover
current authority target is missing, unsafe, duplicated, or a symlink
```

## Scope and limitation

This does not make every historical status phrase disappear. The current packet ledger still overrides historical filenames and prose. The revision contract only determines which documents and tools are current navigation authorities.
## Active helper exception corrected

The content-addressed source locator is imported by every current source-backed probe. It was nevertheless omitted from the active runtime contract and carried a private `sha256_path()` implementation. Rev0079 moves it onto `tools/cube_runtime.py` and adds it to the current-script authority.

```text
current contracted scripts:                 6 -> 8
helper definitions measured:              159 -> 158
helper definition bytes:               67,393 -> 67,167
exact redundant function bytes:        39,968 -> 39,742
current runtime-adoption checks:          33/33 pass
```

The historical duplicate inventory remains evidence; this change removes one live exception rather than rewriting old probes.

