# Closure archive restart memory

`closurearchive.py` makes repair settlement sticky across restart without letting it become global truth.

The archive must include settlement memory and contradiction memory. A soft note alone is not enough. A settlement archive entry without contradiction carriage is treated as dangerous because it can make later prune logic think the conflict is safely gone.

The archive lane rejects replay, rollback, same-sequence forks, previous-link mismatch, boundary drift, digest drift, hard-negative pressure, and missing contradiction evidence.

This is a small local model for a future database/journal boundary: archive writes are not cleanup; they are protocol memory.

closure archive needle.
