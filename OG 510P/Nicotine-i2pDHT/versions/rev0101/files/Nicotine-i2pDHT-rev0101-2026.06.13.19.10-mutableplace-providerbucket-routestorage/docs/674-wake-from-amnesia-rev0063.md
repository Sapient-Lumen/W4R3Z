# Wake from amnesia — rev0063

rev0063 asks: what if the original ACK arrives late after we already fenced retry?

Answer: do not erase anything. Keep the late ACK as scoped evidence, settle retry independently, and journal the contradiction if both paths appear terminal.

Remember:

```text
late ACK evidence is not terminal truth
retry settlement is not original-send settlement
withdraw repair has its own publication memory
compaction must preserve contradictions
```
