# rev0053 learned-trace block bounds

This probe tests the score-path pruning idea on Q/K/V rows emitted by a tiny trained attention model.
It is not a public/pretrained trace and not a GPU/kernel timing claim.

The central question is whether block upper bounds computed from the observable key cache remain tight enough on learned traces to skip exact token QK score work.  The probe compares natural position blocks with key-PCA-sorted blocks and keeps an unsafe sampled-radius variant as a negative control.
