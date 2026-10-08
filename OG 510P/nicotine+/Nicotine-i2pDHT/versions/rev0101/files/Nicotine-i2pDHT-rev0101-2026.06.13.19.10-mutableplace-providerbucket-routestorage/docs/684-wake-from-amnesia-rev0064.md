# Wake from amnesia — rev0064

You are in the public-edge retry/ACK/repair line. rev0063 introduced late ACK handling after retry fencing, retry/withdraw settlement, withdraw repair, and egress journal compaction. rev0064 asks what happens next: can we stage another publication, trust idempotency, or repair duplicate delivery?

Answer: only locally, only with exact-boundary evidence, and only after remote witness pressure when duplicate delivery is possible.
