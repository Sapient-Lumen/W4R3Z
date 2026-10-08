# Public path traversal watch — rev0049

Rev0049 records already-public path-joining/path-traversal work as public context only.

## Observed public items

| Row | Public source | Cube decision |
| --- | --- | --- |
| PUBLIC-PATH-JOIN-PR-3781 | `https://github.com/nicotine-plus/nicotine-plus/pull/3781` | Public-watch-only; do not open a private packet from stale local source. |
| PUBLIC-PATH-JOIN-PR-3723 | `https://github.com/nicotine-plus/nicotine-plus/pull/3723` | Historical public context; keep separate from private strict packets. |

## Boundary

The public path traversal work concerns local destination path joining and path component normalization. It is separate from:

- U-123 download transfer-session active-owner collision.
- PB-01 peer primary-election / secondary-promotion compatibility.
- FileSearchResponse source-admission/source-snapshot binding.
- FileSearchResponse parser-internal prefix/result-list materialization budgets.

## Decision

No private path traversal packet is opened in rev0049. The next valid way to revisit this area is a newer-source audit, not a private report derived from public PR text.
