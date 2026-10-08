# Repeated-round ledger — rev0019

One green round can be accidental. `roundledger.py` stores typed summaries across repeated local rounds so acceptance cannot come from one convenient surface while another surface is screaming.

The ledger joins:

```text
liveness/metadata budget
provider proof verdicts
witness-cache summary
round id and observation time
```

It can accept when the surfaces align, continue when witness/provider/liveness evidence is thin, stop when metadata budget is spent, and quarantine false-provider or witness-contradiction pressure.

This is not global consensus. It is local memory against repeated-round amnesia.
