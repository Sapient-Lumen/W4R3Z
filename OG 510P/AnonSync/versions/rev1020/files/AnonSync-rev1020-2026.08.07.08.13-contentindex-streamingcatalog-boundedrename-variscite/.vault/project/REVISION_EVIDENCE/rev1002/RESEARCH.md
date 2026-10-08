# Rev1002 research note

Local copy scheduling and network framing are separate resource domains. Coupling them would make a tiny negotiated wire page multiply local disk turns, while permitting an adaptive chunk-sized local copy would reintroduce an unbounded owner-thread read at the four-terabyte ceiling. Rev1002 therefore uses a product-owned local range and a shared per-apply byte frontier, while preserving exact cryptographic checks at every reuse boundary.
