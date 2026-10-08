# CELL-155 — K-Forcing Joint Next-k Student

Priority: **P1**  
Status: **candidate**

## Question

Can a tiny student learn a joint next-k distribution better than independent greedy future heads?

## Cheap first run

No runnable probe yet; start with teacher bigram/PCFG and tiny MLP/Transformer student.

## Metrics

- joint distribution error
- diversity
- speed proxy
- teacher KL

## Stop condition

If joint sampling gives no diversity/quality benefit over independent heads, keep as decoding note.
