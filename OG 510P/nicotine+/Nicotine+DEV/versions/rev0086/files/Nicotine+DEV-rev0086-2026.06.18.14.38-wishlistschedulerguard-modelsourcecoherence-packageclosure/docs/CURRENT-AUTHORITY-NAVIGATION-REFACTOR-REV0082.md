# Current authority navigation refactor — rev0082

Current authority now points to two Search Again packets instead of the rev0081 combined packet.

The navigation contract requires:

```text
ordinary and wishlist current-disposition documents
source-backed consumer closure and evidence-reuse contract
current deterministic ZIP contract and tools
rev0082 probe outputs, packet snapshot, public context, and handoff
```

It forbids the combined rev0081 disposition and probe from being presented as current authority. Historical evidence remains available and indexed rather than deleted.
