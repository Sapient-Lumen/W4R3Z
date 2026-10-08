# Web references — rev0020

- Official Nicotine+ Soulseek protocol documentation: `https://nicotine-plus.org/doc/SLSKPROTOCOL.html`
  - Used for `Too many megabytes`, `QueueUpload`, `UploadDenied`, and legacy `TransferRequest` message context.
- Official Nicotine+ release notes: `https://nicotine-plus.org/NEWS.html`
  - Used for historical per-user upload queue limit in megabytes.
- Nicotine+ GitHub issue #1985: `https://github.com/nicotine-plus/nicotine-plus/issues/1985`
  - Used as large-upload / queue-limiter / `Too many megabytes` public-adjacent material, not a direct U-244 match.

Targeted searches did not find a direct public issue/PR/advisory for the exact candidate-size queue-admission invariant.
