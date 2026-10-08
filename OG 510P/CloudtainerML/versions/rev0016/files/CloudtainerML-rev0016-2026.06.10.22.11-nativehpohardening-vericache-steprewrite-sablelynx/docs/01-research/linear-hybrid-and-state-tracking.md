# Linear, hybrid, and state-tracking lane

Core sources: `SRC-0005` through `SRC-0014`, `SRC-0051`, `SRC-0054`, `SRC-0060`.

## Main hypothesis cluster

Pure recurrence is efficient but can hit a content-addressed recall cliff. Full attention is expressive but memory-hungry. Hybrids may win by spending attention only where direct retrieval is necessary.

## Candidate tests

- associative recall capacity boundary;
- key collision and repeated-key corrections;
- attention-vs-recurrence routing over sequence chunks;
- exact state tracking from generated action sequences;
- complex vs real recurrent states;
- score-level recurrence signals added to attention logits.
