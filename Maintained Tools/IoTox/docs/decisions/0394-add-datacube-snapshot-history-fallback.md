# 0394 — Add datacube snapshot history fallback

Date: 2026-09-20

Status: accepted

## Context

The repository datacube must stay below 128,000,000 bytes. After the
founder-preview release trail landed, the clean exporter refused to package:

```text
mandatory datacube content is 183950180 bytes and exceeds the limit
```

The full Git bundle alone was about 122.5 MB, while the compressed current
source probe was about 27.8 MB. Optional founding cubes were not the problem;
full reachable history plus the source tree could not fit.

## Decision

Keep the committed source tree mandatory, but make the Git bundle history mode
adaptive:

```sh
IOTOX_DATACUBE_HISTORY_MODE=auto      # default
IOTOX_DATACUBE_HISTORY_MODE=full
IOTOX_DATACUBE_HISTORY_MODE=snapshot
```

`auto` first measures a full-history bundle and a compressed source probe. If
they cannot fit below the strict ceiling with reserved headroom, the exporter
creates a standalone source-snapshot Git repository from the exact clean commit
and bundles that instead. Every cube records:

- `git/HISTORY_MODE` as `full` or `snapshot`;
- `git/SOURCE_COMMIT` as the original repository commit represented by
  `repository/`; and
- manifest fields for full-history bundle bytes and compressed source-probe
  bytes.

The verifier requires the bundle, `HISTORY_MODE`, and `SOURCE_COMMIT`, verifies
the bundle, and rejects unknown history modes.

## Consequences

Datacubes remain cloneable and exact for source inspection under the hard size
ceiling. They no longer overclaim full history when history cannot fit. A
snapshot-mode cube is a conversation/recovery handoff for the exact source
state, not a replacement for the authoritative repository history.

Operators who need a full-history archive may set
`IOTOX_DATACUBE_HISTORY_MODE=full`, but the exporter will still fail if the
result exceeds the configured byte ceiling.

## Validation

- `bash -n tools/make-repository-datacube.sh`
- `tools/make-repository-datacube.sh`
- `tools/make-repository-datacube.sh --verify ARCHIVE`
