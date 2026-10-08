# Plugin list count summary (rev354)

`plugin list` was already legible after rev347, but it still made broad health inspection do extra work: you could read each per-plugin entry, yet you still had to mentally count how many plugins existed, how many were broken, and whether the tree was mostly loaded or mostly just available.

Rev354 keeps the change deliberately small and trust-first:

- `plugin list` now starts with a tiny count-aware prefix like `plugin list: 3 plugin(s) (1 error, 2 loaded)`
- the old per-plugin summary entries stay unchanged
- empty inventories now say `plugin list: 0 plugin(s)` instead of a vague `(none)`

That is not flashy UI work. It is just a better inspection loop. The command now answers both questions at once:

1. **What is here?**
2. **What is the overall shape of plugin health?**

That matters for both humans and future LLMs because it reduces one more tiny place where the repo made you reconstruct state by hand from otherwise honest details.
