# rev0037 public-overlap update — U-123

Fresh overlap check retained the conservative classification: no exact direct public duplicate was captured for the specific chain of duplicate same-user/same-token download activation, active F-connection owner replacement, stale callback cleanup, and callback orphaning.

Public context retained:

- Nicotine+ Soulseek protocol documentation: `TransferRequest` carries a uint32 token; `FileTransferInit` uses the same token on the F connection. URL: https://nicotine-plus.org/doc/SLSKPROTOCOL.html
- Nicotine+ issue #653: transfer lifecycle / queued transfer adjacency, not the U-123 duplicate-token active-owner chain. URL: https://github.com/nicotine-plus/nicotine-plus/issues/653
- Nicotine+ release notes: current public hardening context around network-message bounds and peer-spoofing fixes, not a direct U-123 collision report in the captured result. URL: https://nicotine-plus.org/NEWS.html
- Nicotine+ homepage: project/current stable/RC context. URL: https://nicotine-plus.org/

Search strings captured this turn included:

```text
site:github.com/nicotine-plus/nicotine-plus duplicate transfer token active_users download timeout FileTransferInit
site:github.com/nicotine-plus/nicotine-plus "active_users" "FileTransferInit" "token"
site:github.com/nicotine-plus/nicotine-plus "TransferRequest" "FileTransferInit" "token"
Nicotine+ SLSKPROTOCOL TransferRequest FileTransferInit token
```
