# Risk register — rev0063

Risks made executable:

- late ACK silently erases retry fence memory;
- retry-delivered marker coexists with late original ACK;
- withdraw repair becomes terminal because live egress looked ready;
- journal compaction drops contradiction evidence;
- replay/fork/previous-link drift in late ACK, retry settlement, withdraw repair, or journal entries;
- low family/path diversity masquerades as settled evidence.
