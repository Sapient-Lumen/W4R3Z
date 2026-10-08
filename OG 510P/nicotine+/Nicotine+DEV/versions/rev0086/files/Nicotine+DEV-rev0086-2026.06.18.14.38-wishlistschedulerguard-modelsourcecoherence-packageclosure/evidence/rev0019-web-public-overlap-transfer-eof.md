# Public-overlap review — TRANSFER-EOF-01 / U-251 — rev0019

Classification:

```text
candidate no direct exact public match found / public upload-stuck-completion adjacent
```

## Exact/narrow searches attempted

The archive records these searches as negative or non-direct:

```text
site:github.com/nicotine-plus/nicotine-plus/issues upload stuck 99% completed upload socket open Nicotine+
site:github.com/nicotine-plus/nicotine-plus/issues upload EOF short read uploaded size Nicotine+
site:github.com/nicotine-plus/nicotine-plus/issues FileOffset upload aborted 99% Nicotine+
site:github.com/nicotine-plus/nicotine-plus/issues UploadFailed upload stuck file transfer Nicotine+
Nicotine+ GitHub upload stuck 99%
Nicotine+ uploads stuck completed transfer issue
Nicotine+ issue upload aborts 99% transfer
Nicotine+ GitHub UploadFailed transfer stuck
```

The searches surfaced public transfer-stuck/completion/cancellation symptoms, but not a direct report for the exact local opened-file short-read/EOF plus exact-completion-gate invariant.

## Adjacent public material found

```text
- Nicotine+ issue #2447: reports uploads listed as complete locally while recipients see aborts near 99%.
- Nicotine+ issue #784 / PR #786: public history around uploads being cancelled and avoiding stuck upload state.
- Nicotine+ issue #1563: user-facing desire to requeue transfers stopped by connection/timeouts.
- Nicotine+ NEWS: repeated transfer stuck/cancelled/queue fixes across releases.
- Nicotine+ protocol docs: UploadFailed semantics and F-connection/FileOffset flow make incorrect abort/timeout behavior user-visible and confusing.
```

## Decision impact

The overlap is enough to avoid novelty overclaiming. U-251 is verified and worth regression coverage, but remains in audited backlog rather than becoming a strict report candidate.
