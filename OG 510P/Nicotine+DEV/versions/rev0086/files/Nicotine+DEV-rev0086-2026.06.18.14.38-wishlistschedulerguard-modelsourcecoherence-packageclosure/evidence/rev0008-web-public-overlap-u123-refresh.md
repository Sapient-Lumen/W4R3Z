# rev0008 public-overlap refresh for U-123

Status: **candidate no direct public match found; public transfer-lifecycle adjacent**.

## Queries captured this pass

```text
site:github.com/nicotine-plus/nicotine-plus "duplicate" "TransferRequest" token
site:github.com/nicotine-plus/nicotine-plus "active_users" "token" "download"
site:github.com/nicotine-plus/nicotine-plus "FileTransferInit" "token" "active_users"
site:github.com/nicotine-plus/nicotine-plus "Download" "token" "timed out"
github.com/nicotine-plus/nicotine-plus "FileTransferInit" "TransferRequest"
github.com/nicotine-plus/nicotine-plus "unknown token" "FileTransferInit"
github.com/nicotine-plus/nicotine-plus "transfer token" "FileTransferInit"
github.com/nicotine-plus/nicotine-plus "TransferRequest" "queued" "token"
"duplicate token" "Soulseek" "TransferRequest"
"FileTransferInit" "Soulseek" "token" "duplicate"
"TransferRequest" "same token" "Soulseek"
"FileTransferInit" "active_users" "Nicotine+"
```

## Relevant public overlap

- Nicotine+ issue #653 discusses transfer connection initiation around unallowed/queued transfer responses and includes token/connection timing logs. This is adjacent transfer-lifecycle history, not a direct duplicate-token stale-timeout report.
- Soulseek.NET issue #668 discusses odd cleanup around `UploadDenied` and transfer connection behavior when a file no longer exists. This is adjacent client interoperability/cleanup context, not the U-123 invariant.
- Nicotine+ protocol documentation states that `FileTransferInit` uses the same token previously included in `TransferRequest`, and that the peer establishes an F connection after the transfer request/response flow.
- 3.3.11 RC notes mention broad spoofed-user upload prevention and network-message hardening. This is upstream-adjacent context, not direct evidence that U-123 is fixed.

## Classification

Do not write “new vulnerability, nobody has seen this.” Write:

```text
No direct public match found for duplicate peer-supplied download TransferRequest token + stale first timeout deleting the later F-connection session mapping. Public transfer-lifecycle and spoofed-user/upload context exists.
```
