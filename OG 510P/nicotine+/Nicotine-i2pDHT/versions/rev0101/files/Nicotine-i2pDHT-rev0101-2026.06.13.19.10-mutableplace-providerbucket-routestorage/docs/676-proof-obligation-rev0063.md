# Proof obligations — rev0063

rev0063 must show:

- late ACK after retry fence is accepted only as watch evidence;
- late ACK can abort retry settlement without erasing retry fence memory;
- retry-delivered conflicts with late original ACK;
- withdraw repair publication memory is separate from retry settlement;
- egress journal compaction quarantines dropped contradictions;
- current surfaces are pinned by lateackfold.
