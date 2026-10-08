# rev0006 public-overlap notes — Batch 02 peer/source binding

This file records what rev0006 used to avoid duplicating public work. It is not a complete proof of novelty.

## Public/upstream overlap that affects wording

- Nicotine+ 3.3.11 RC1 release notes mention network-message size caps and spoofed-user upload prevention. That directly affects how U-169 and the broader peer/transfer-binding family should be presented.
- The official Soulseek protocol documentation confirms several relevant message shapes: `PierceFireWall` uses a token from `ConnectToPeer`; direct `PeerInit` notes the token is ignored; `UploadFailed` carries filename only; `UploadDenied` carries filename and reason; `FileTransferInit` carries a token from `TransferRequest`.
- GitHub issue searches for exact strings such as `PeerInit replace`, `FileTransferInit token`, `UserInfoResponse`, and `pending PeerInit` did not surface direct Nicotine+ issue hits in the captured search pages, but connection/transfer issues are public-adjacent.
- U-217 is partially upstream-changed in master source via `AddAllowedResponse(UserInfoResponse, username)`, so it is not a clean fresh finding against future source lanes.

## rev0006 working classifications

| id | rev0006 public-overlap class | practical meaning |
|---|---|---|
| U-123 | candidate-no-direct-public-found / source-public-code-visible | Best microrepro-first candidate, but novelty still provisional. |
| U-158 | public-adjacent not direct | Transfer-status behavior exists publicly; exact username/path binding not found in captured pages. |
| U-165 | public-adjacent / protocol-history-overlap | Old token/connection-flow context exists; not a clean nobody-mentioned claim. |
| U-168 | upstream-overlap / spoofed-user-adjacent | Exact direct PeerInit replace not found; spoofed-user upload fix overlaps the theme. |
| U-171 | public-adjacent not direct | Connection/address issues exist; arbitrary address-class policy is not proven direct-public. |
| U-176 | candidate-no-direct-public-found / upstream-theme-adjacent | Promising but requires dynamic state-machine proof. |
| U-181 | candidate-no-direct-public-found / connection-troubleshooting-adjacent | No direct hit in captured searches; needs resource measurement. |
| U-217 | upstream-partially-fixed / residual-candidate | Master implements username-keyed allowed response gate; only residual generation/source binding remains. |
| U-169 | upstream-in-flight / adjacent-public | 3.3.11 RC spoofed-user upload fix makes this unsuitable as clean fresh. |
