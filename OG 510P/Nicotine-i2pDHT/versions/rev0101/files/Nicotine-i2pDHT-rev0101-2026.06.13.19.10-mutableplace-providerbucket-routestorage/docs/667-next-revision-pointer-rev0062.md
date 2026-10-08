# Next revision pointer — rev0062

Suggested next revision: **rev0063 `lateack-retrysettle-egressjournal`**.

Suggested focus:

```text
late ACK arrival after retry fence,
retry result settlement,
withdraw/repair publication memory,
and egress-journal compaction that preserves contradictions.
```

Hard questions:

- What happens when a late ACK arrives after a retry has been fenced but before retry delivery settles?
- How should retry attempts settle independently from original sends without hiding lineage?
- When can a withdraw repair become terminal?
- Which evidence can be compacted once original send and retry send both have terminal states?
