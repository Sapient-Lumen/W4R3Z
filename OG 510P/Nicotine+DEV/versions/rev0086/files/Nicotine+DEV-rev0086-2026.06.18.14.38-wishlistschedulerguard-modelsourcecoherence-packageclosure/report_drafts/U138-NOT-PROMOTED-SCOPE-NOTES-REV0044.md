# U-138 not-promoted scope notes — rev0044

This is intentionally not a production disclosure report.

## Summary

The previously deferred **U-138 / general ID3v2 advertised-frame materialization** row is too broad for strict/front promotion. The MP3 share-scanner duration path in Nicotine+ uses TinyTag with `tags=False, duration=True`; the rev0044 witness shows that this path skips the leading ID3v2 body before MPEG duration scanning and does not read a mapped text-frame payload as one advertised body.

The generic tag-enabled TinyTag ID3v2 parser still reads mapped frame bodies with `fh.read(frame_size)`. That behavior may be worth upstream parser-hardening discussion, but rev0044 does not have a Nicotine+ strict/front caller path that justifies a maintainer-ready packet.

## Artifact status

```text
production-ready report: no
selected patch: no
fixed-behavior regression: no
current-behavior boundary witness: yes
```

## Recommended wording for future use

Do not describe U-138 as "Nicotine+ share scanner reads arbitrary ID3v2 frame bodies for MP3 duration." Rev0044 evidence does not support that claim.

A narrower, supportable sentence is:

```text
TinyTag's tags-enabled ID3v2 parser reads mapped text-frame bodies according to advertised frame size, but Nicotine+'s MP3 share-scanner duration-only path does not enable that parsing mode.
```
