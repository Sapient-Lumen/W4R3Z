# rev0082 deterministic ZIP contract self-test

Status: **pass**

```text
contract checks:          8/8
malformed archives:       4/4 rejected
repeat build:             byte-identical
valid tree/content audit: pass
```

Rejected mutations: duplicate raw member, case-folding collision, parent traversal, and an extra directory entry.
