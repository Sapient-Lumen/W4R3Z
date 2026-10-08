# Proof obligations — rev0030

Current toy proof obligations:

- Negative-space reports must not accept absence when positive evidence exists for the same target/request.
- Negative-space reports must quarantine responder forks and family floods.
- Peerbook entrance views must reject channel monoculture and contact-lease forks.
- Peer delta sketches must reject bad/expired/forked/monoculture summaries and respect local delta budgets.
- Key crisis memory must reject rollback, quarantine same-sequence forks, and gate risky keyed operations.
- Key crisis fold must keep rev0030 visible while preserving rev0029 foldseal regression.
- Bootstrap join must not advance when peerbook, live-probe/live-smoke, absence, or egress pressure disagrees.
- Key-crisis recovery must not drop checkpointed hard-negative facts.
- Delta repair must preserve tombstone-first pressure until exact repair arrives.

These are deterministic local fixtures, not production security proofs.
