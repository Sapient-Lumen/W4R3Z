# rev0063 trace packet speed envelope

This experiment is not a new sparse-attention algorithm. It is an upper-bound test for the rev0062 native Q/K/V replay lane.

The benchmark uses the local tiny-trained Q/K/V trace packet and supplies an exact Top-p 0.96 support mask as an oracle side input. The native path still computes every QK score and every softmax weight, but it pays zero selector/search cost and accumulates only the oracle-selected values. This answers a narrow question: if selector optimization were magically free, would sparse value accumulation have native CPU headroom against dense attention on this local trace?

The result is non-promotional by design. The support mask is selected from full-score oracle knowledge, all QK scores are still computed, score storage/materialization remains required, and this is not a public/pretrained or GPU/fused-kernel trace.
