# Risk register — rev0031

Open risks:

- Lease probing is still toy, local, and no-network.
- Probe-family labels are test hints, not measured I2P independence.
- Egress budgets are heuristic and do not prove metadata privacy.
- Repair debt scheduling is local policy, not global truth.
- Tombstone-first scheduling can be abused by tombstone spam if admission walls are weak.
- Auditmesh adds another fold surface rather than completing the larger declarative fold cleanup.
- No production database or durable repair queue exists.

Mitigation in this revision: pin the riskiest boundaries with deterministic tests before live transport or real storage exists.
