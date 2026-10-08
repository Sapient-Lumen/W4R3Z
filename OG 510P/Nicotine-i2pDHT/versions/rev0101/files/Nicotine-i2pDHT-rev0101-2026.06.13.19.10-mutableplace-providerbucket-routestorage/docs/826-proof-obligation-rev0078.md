# Proof obligation rev0078

The local proof obligation is:

```text
summaryackledger + deliveryarchive + summaryprunefence
  -> summaryreplay
  -> ackclosure
  -> summaryexportfence
```

Each step must preserve exact boundary, component digests, sequence links, redaction memory, contradiction memory, and hard-negative pressure.
