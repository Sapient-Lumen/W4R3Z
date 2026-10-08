# rev0089 priority reconsideration

Priority moved from more population volume to policy/evidence identity.

Why: rev0080 already eliminated the size/fine underpower blocker, and rev0087-rev0088 hardened adaptive candidate gating. The next failure that could invalidate a long chain of conclusions is code drift: a policy name such as `counter_guard` or `threat_surge` can continue to exist while its behavior changes. Without a runtime replay contract, old rows could be interpreted under new semantics.

Chosen action: add deterministic replay plus policy runtime digests before adding another counter candidate. This is higher leverage than more doctrine because it can fail on concrete stored rows and protects every later promotion gate.

Next likely priority: move from sampled replay to a compact sentinel set chosen from high-leverage cells: worst-LCB columns, mechanism-flip pairs, and any future promotable cells.
