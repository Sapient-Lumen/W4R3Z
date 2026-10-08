# Canonical sparse compiler benchmark — rev0041

A single score-stream generator feeds several hard-mask compilers: fixed threshold, Top-p, hybrid threshold/Top-K, block-index with certification, temporal GVR with certification, and exact heap Top-K.

The purpose is to stop comparing unrelated synthetic toys. Every compiler sees the same rows and reports exactness, certification, fallback, candidate count, score reads, candidate reads, pass count, comparison estimate, cost proxy, and regret.
