# CELL-319 — No-Exp Oscillator Attention Proxy

Priority: P1

Status: coded-native-frontier

Question: When exponentials/global reductions are charged, can no-exp cosine/synchronization-style attention be competitive without losing tails?

Cheap first run: Run REV0032_OSCILLATOR_ATTENTION_PROXY_SMOKE.json; inspect target mass vs exp/cost/tail miss.

Metrics: target_mass, entropy, cost, exp_ops, tail_miss, score

Required baselines: softmax_exp, relu_noexp, cosine_relu_proxy, oscillator_pow4_proxy, topk_softmax_k8

Stop condition: Keep P1 unless no-exp methods survive tail-needle and alias-decoy guards.
