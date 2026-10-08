# Public trace KV group audit — rev0086

**Status:** pass_with_blockers

rev0085 moves the public trace gate from dense math alone toward cache-ownership semantics: a row bundle can now pass only if each query-head row carries a verified compact KV-head owner and head-count/group-size metadata. The audit rejects a forged GQA map even though the recomputed dense attention output is unchanged, which protects later sparse/cost claims from overcounting duplicated per-query K/V rows as independent KV-cache storage.

Rows checked: 12

Head→KV groups exercised: [{'head': 0, 'kv_head': 0}, {'head': 1, 'kv_head': 0}, {'head': 2, 'kv_head': 1}, {'head': 3, 'kv_head': 1}]

Correct GQA bundle accepted: True

Forged KV-map bundle rejected while dense math still matched: True
