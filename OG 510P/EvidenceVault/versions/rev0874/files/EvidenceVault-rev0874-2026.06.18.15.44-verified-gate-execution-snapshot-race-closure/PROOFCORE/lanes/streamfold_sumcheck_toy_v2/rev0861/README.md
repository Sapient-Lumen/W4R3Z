# rev0861 loose payload locator lane

rev0861 closes the next practical recovery gap after rev0860. The rev0860 graft
engine can stage verified streamfold payload bytes only when the candidate root
already contains the exact canonical EvidenceVault paths. That is safe but too
brittle for real recovery: old caches, extracted evidence bundles, object-store
exports, or partial filesystem searches may contain the right bytes under loose
or renamed paths.

This lane adds `PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py`, an
exact byte-count/SHA-256 locator. It scans one or more real candidate roots
without following symlinks, finds expected `streamfold_sumcheck_toy_v2` payloads
by hash, and can stage a complete non-ambiguous match set back to canonical
paths in an isolated directory outside the overlay and outside all candidate
roots.

Current overlay state remains honest:

```text
full expected streamfold payloads: 17
minimum first recovery payloads:    4
canonical payload bytes present:    0
```

Operator examples:

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py --mode minimum --json

python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py \
  --candidate-root /path/to/cache-or-export \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-loose-minimum \
  --json
```

Staging is blocked unless every selected payload has exactly one match. Duplicate
hash matches are reported but not auto-resolved. This keeps recovery from silently
choosing one of several possible sources and gives the operator a concrete audit
trail to reduce the candidate root or choose a cleaner source.

Non-claims: this lane is not a rights grant, not a recovered payload bundle, not
a streamfold correctness proof, not a SNARK, not zero knowledge, and not succinct.
