# Rev0013 capture operator runbook

Start with `data/source_graph/source_capture_order.rev0013.json`.

For each target:

1. confirm the target is still in the queue;
2. create HTTP and redirect-chain sidecars;
3. if fetch succeeds, compute SHA-256 and byte count in private custody;
4. do not put raw payload bytes into the public bundle;
5. do not run OCR or named-entity recognition;
6. route the target to privacy preflight;
7. update rollback dependencies if any source mutation is observed;
8. leave all current-status claims blocked unless the status-proof bundle process opens separately.

An anomaly should create an anomaly sidecar, not an absence claim.

