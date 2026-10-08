# Wake from amnesia — rev0066

The latest design seam is **repair publication after duplicate conflict**.

Remember:

- rev0065 staged the repair and started conflict cooldown;
- rev0066 does not let staged repair become a public write;
- repair publication readiness gets its own marker chain;
- repair ACKs get their own ledger;
- duplicate closure is accepted only if contradiction memory survives.

Current codename: `repairpublish-ackclosure-duplicatefinality`.
