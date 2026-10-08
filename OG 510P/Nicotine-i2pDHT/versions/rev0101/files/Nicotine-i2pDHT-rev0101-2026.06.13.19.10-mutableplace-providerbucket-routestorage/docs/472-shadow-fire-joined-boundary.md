# Shadow-fire joined boundary

`shadowfire.py` joins the risky public bridge chain:

```text
bridge epoch
+ key receipt lane
+ subjective policy firebreak
+ authority receipt mesh
+ announcement repair when closing/withdrawing
+ hard-negative scan
```

The module is intentionally conservative. It rejects quarantined components, mismatched expected public/closed state, missing close repair, low evidence diversity, and live hard-negative pressure. It can accept with watch when policy or key receipts are explicitly watch-bearing.

The design target is not a central bridge authority. The target is a local side-effect gate where a public bridge cannot keep advertising itself through stale, replayed, or half-rotated evidence.
