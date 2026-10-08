# rev0022 web public-overlap notes — TRANSFER-COMPLETE-LIFETIME-01 / U-269

Status: **candidate no direct exact public match found / public-adjacent**.

## What was searched

Representative targeted searches:

```text
site:github.com/nicotine-plus/nicotine-plus "Completed upload" "99%" upload stuck
site:github.com/nicotine-plus/nicotine-plus "upload" "stuck" "socket"
site:github.com/nicotine-plus/nicotine-plus "file-upload-progress" "bytes_sent"
site:github.com/nicotine-plus/nicotine-plus "all bytes" "upload" "socket" "Nicotine+"
site:github.com/nicotine-plus/nicotine-plus "UploadFile" "sentbytes"
site:github.com/nicotine-plus/nicotine-plus "completed upload connections" "socket"
```

## Public-adjacent material found

```text
Nicotine+ #2447
  Public reports of uploader seeing 100% complete while the downloader sees abort/99%, and reports of uploads reaching 100% while still taking time to move on.

Nicotine+ #3162
  Public wrong-upload/stat behavior around upload progress and large-file transfer errors.

Nicotine+ #784
  Public reports of random uploads becoming cancelled.

Nicotine+ #1563
  Public request to automatically retry uploads stopped by connection errors/timeouts.

Nicotine+ protocol docs
  FileTransferInit uses the token from TransferRequest; FileOffset starts the F upload flow; UploadFailed is sent when an active upload file connection closes.
```

## Direct match assessment

I did **not** find a public issue/PR/advisory naming the exact invariant now proved in rev0022:

```text
completed advertised-size upload remains active, and invalid post-completion F input is discarded but refreshes conn.last_active so generic idle cleanup does not close the completed upload slot.
```

Because the public upload-completion/stuck/cancelled symptoms are strong adjacent overlap, the cube does **not** mark this as clean novelty or promote it strict.
