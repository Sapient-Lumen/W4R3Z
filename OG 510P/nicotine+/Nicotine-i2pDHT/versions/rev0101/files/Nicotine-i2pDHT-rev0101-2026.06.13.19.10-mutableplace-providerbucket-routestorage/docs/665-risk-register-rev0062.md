# Risk register — rev0062

| Risk | Current pressure |
|---|---|
| terminal ACK and retry both plausible | `ackrepairjoin.py` quarantines ACK/repair conflict |
| missing ACK becomes blind resend | delivery repair + rollback probe + live egress + retry fence |
| retry idempotency reuses original idempotency | join and fence reject collision |
| remote commit appears after missing ACK | rollback/live-egress/join quarantines remote commit pressure |
| prune deletes repair evidence | `repairpruneguard.py` retains repair debt |
| branchlet ancestry becomes invisible | `egressrepairfold.py` pins branchlet archive and active fold |
| restart reuses retry permission | `retryfence.py` requires previous-linked markers |

Still unsolved: real networking, real storage, real clocks, real malicious I2P behavior, real DHT churn, real privacy, and production cryptography.
