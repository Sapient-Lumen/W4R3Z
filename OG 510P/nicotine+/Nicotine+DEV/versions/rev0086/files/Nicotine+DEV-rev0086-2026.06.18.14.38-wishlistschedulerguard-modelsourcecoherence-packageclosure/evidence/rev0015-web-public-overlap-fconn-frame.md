# rev0015 public-overlap notes — F-CONN-FRAME-01 / U-164

## Targeted conclusion

Targeted public search did **not** find a direct public issue or PR for the exact fixed-width F-connection partial-fragment behavior: short `FileTransferInit` / `FileOffset` prefixes being consumed before the complete 4-byte or 8-byte frame is available, followed by possible resynchronization into a different token or offset.

## Exact negative / near-negative checks

```text
GitHub issues, nicotine-plus/nicotine-plus: "FileTransferInit" -> no direct issue result.
GitHub issues, nicotine-plus/nicotine-plus: "FileOffset" -> no direct issue result.
GitHub issues, nicotine-plus/nicotine-plus: "F connection" "partial" -> no direct issue result.
GitHub issues, nicotine-plus/nicotine-plus: "partial frame" "FileOffset" -> no direct issue result.
```

## Public adjacency that affects presentation

- Nicotine+ issue #2447 publicly reports transfers reaching near-complete or complete-looking states and then aborting/sticking. This is transfer-lifecycle symptom adjacency, not a direct U-164 match.
- Nicotine+ issue #1985 publicly reports `FileOffset`-adjacent upload I/O errors around large offsets. This is field/path adjacency, not a direct partial-fragment finding.
- Nicotine+ issues #2850 and #2853 publicly report `BufferError: Existing exports of data: object cannot be re-sized` in the network thread. The rev0015 corrected probe uses production-like logging that does not retain msg-content memoryviews, so U-164 is **not** presented as a BufferError claim; these issues are kept only as broad network-buffer robustness adjacency.
- Nicotine+ release notes contain multiple historical transfer/peer-connection robustness fixes. That keeps the item in transfer-robustness/public-adjacent presentation language.

## rev0015 classification

```text
classification: candidate no direct exact public match found / public-adjacent transfer robustness
strict decision: do not promote in rev0015
reason: verified behavior is useful hardening, but consequence is transfer/session reliability and availability; it does not outrank U-123, PB-01, or SEARCH-RESP-01.
```
