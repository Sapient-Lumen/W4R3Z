# rev0010 PB-01 public-overlap refresh

Classification: **candidate no direct public match found, but public/upstream adjacent**.

## Captured exact-match searches

- GitHub issues search for `"promoting to primary connection"`: no direct issue/PR result found in the captured search page.
- GitHub issues search for `"replace existing connection"`: no direct issue/PR result found in the captured search page.
- GitHub issues search for `"spoofed users"`: no direct issue result found in the captured search page.

## Public-adjacent material

- Official protocol docs document the modern direct/indirect PeerInit order and state that the PeerInit token is always zero; older `SendConnectToken` cross-checking is described as obsolete.
- PR #3287 publicly discusses peer connection message order and maintainer notes around PeerInit token being unused/zero.
- PR #866 publicly discusses handling PeerInit/PierceFireWall cases with no token.
- Issue #653 and issue #2978 are connection/transfer lifecycle adjacent, but not direct PB-01 primary-election reports.
- 3.3.11 RC notes mention broad spoofed-user upload prevention and distributed-search fixes; this keeps PB-01 from being presented as a clean novelty claim.

## Decision

PB-01 is eligible for the strict/front lane as a report-candidate because the concrete invariant reproduced across stable, release-candidate, and master lanes. It is **not** production-ready disclosure text because maintainer/private overlap and compatibility expectations for legitimate reconnect/fallback behavior remain unresolved.
