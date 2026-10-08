# Traffic-analysis mitigations checklist

**Track:** Shared (cross-cutting)


## Client/Server protocol
- [ ] Request/response sizes do not depend on ballot selections.
- [ ] Constant outer envelope size (or discrete buckets independent of vote content).
- [ ] Error messages are normalized and size-stabilized.

## Network behavior
- [ ] Optional batching and timestamp equalization enabled for high-risk elections.
- [ ] Multi-ingress submission supported; retries do not leak vote content.
- [ ] No publication of IPs, user agents, TLS identifiers, or fine-grained timing.

## Validation
- [ ] Run packet-capture tests across representative flows (cast/spoil/invalid) and confirm indistinguishability targets.
