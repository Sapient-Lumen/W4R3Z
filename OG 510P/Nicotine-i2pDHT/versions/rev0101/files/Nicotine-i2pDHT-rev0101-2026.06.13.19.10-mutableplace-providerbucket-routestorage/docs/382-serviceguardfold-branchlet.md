# Serviceguardfold branchlet audit

rev0037 has two active service lanes:

1. ticketlane / servicereceipt, which grants exact-scope work and records what
   happened;
2. serviceannounce / ingressgate, which controls how services are exposed and
   how inbound requests reach the ticket lane.

`serviceguardfold.py` pins the second lane without deleting the first. It also
uses the same foldmap, foldregistry, and surfaceledger spine so the cube does not
hide current risk-first code behind unindexed branchlets.

Audit stance: branchlets may coexist, but they must be visible from docs,
public pointers, head registry, tests, and active ledgers.
