# Current-web marker coherence refactor — rev0054

rev0054 separates five concepts that were easy to over-merge:

```text
1. archived source anchors from rev0051
2. selected literal marker scans from rev0053/rev0054
3. full current checkout proof
4. fixed-behavior regression proof
5. public path traversal/release-note overlap
```

The main audit result is that current web marker triage is useful but insufficient. It cannot retire or file packets by itself.

Notable split: PB-01 has a web-visible legacy fallback phrase about keeping an established primary connection, but rev0054 does not treat this as the selected PB-01 fix. The selected invariant also requires rejecting/holding later direct replacements and preventing generic secondary promotion over an established primary while preserving fallback compatibility.
