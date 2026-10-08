# Attention row compiler benchmark

rev0043 adds the missing workload between score-stream toys and real kernels: a
row-level QK/softmax/V attention benchmark. Every compiler sees the same
attention rows and is judged by both selector behavior and actual output error
against dense softmax attention.

This is still synthetic E2 evidence, not a kernel claim. Its purpose is to veto
compiler ideas that preserve Top-K indices but damage the attention output, or
that look cheap only because value reads/output error were not counted.
