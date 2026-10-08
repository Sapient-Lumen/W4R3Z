# Risk register — rev0067

| Risk | Current local pressure |
|---|---|
| Duplicate closure becomes final too early | `repairsettlement.py` requires joined publish/ACK/closure evidence |
| Restart loses contradiction evidence | `closurearchive.py` requires contradiction archive entries |
| Cleanup deletes protected evidence | `repairprune.py` forbids dropping witness/cooldown/contradiction/settlement memory |
| Replay or fork poisons local memory | all three lanes require sequence and previous-link checks |
| One family controls the story | all three lanes require family and path-family diversity |

Still unsolved: production persistence, live I2P transport, real remote semantics, Sybil resistance, and global finality.
