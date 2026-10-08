# Wake from amnesia rev0072

Start with `docs/758-rev0072-summaryreceipt-importarchive-lineageprune.md`.

The current boundary chain is:

```text
handoff receipt/import/summary lineage -> summary receipt -> import archive -> lineage prune guard
```

The key invariant is that redacted public/operator/garden summary state may become compact, but contradiction memory and component digests must survive archive and prune.
