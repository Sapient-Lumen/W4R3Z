# Current public context — rev0049

Observed 2026-06-15.

| Source | Observed | Cube effect |
| --- | --- | --- |
| Nicotine+ homepage | Stable 3.3.10 is listed, and testers are asked to test the 3.3.11 release candidate. | Keep source-refresh recommendation before external filing. |
| Nicotine+ NEWS | 3.3.11 RC1 includes broad correction language for network caps, upload spoofing, username identity, distributed search, and empty-room search. | Retain the seven narrower packet-specific gates; do not retire on broad wording alone. |
| GitHub 3.3.11 milestone | One open safe-path/path-traversal item observed, 97% complete. | Add public-watch gate instead of opening a private row. |
| GitHub PR #3781 | Open `safe_path_join()` path traversal/path component safety work. | Keep path joining separate from private handoff. |
