# Prune replay resistance

`prunereplay.py` treats repair-prune replay as its own restart-generation surface.  An old prune marker must not be reusable after restart to justify forgetting archive evidence, contradiction memory, or the prune marker itself.

The lane rejects restart-generation rollback, replay, sequence fork, previous-link mismatch, component digest drift, boundary drift, memory drops, hard negatives, and low family/path diversity.

Design guess: **prune replay is not proof of absence; it is a demand that archive memory still be present**.
