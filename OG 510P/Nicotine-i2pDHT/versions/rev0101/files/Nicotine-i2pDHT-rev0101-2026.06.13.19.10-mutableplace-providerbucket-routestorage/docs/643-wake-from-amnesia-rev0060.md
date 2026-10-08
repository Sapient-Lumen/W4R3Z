# Wake from amnesia rev0060

Start here after memory loss:

1. rev0059 ended with settlement store, tomb-repair join, and canary join.
2. rev0060 asks whether a canary-ready edge can become a future live write.
3. Answer: only through `livesendgate`, then `deliverywitness`, then `sendfence`.
4. All three are still no-network design/test surfaces.
