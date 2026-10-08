# High-priority / high-quality document

Status as of rev0034: **3 promoted report-candidates**, **0 production-ready disclosure texts**.

This document is intentionally strict. A promoted report-candidate is not a claim of code execution, not a polished external advisory, and not a request to submit a PR. It means the item has enough current-source evidence, public-overlap checking, bounded impact, and reproducible local proof to deserve the front lane.

## Promoted report-candidates

1. **U-123** — duplicate peer-supplied download transfer tokens can orphan a later F-connection transfer session after a stale first timeout.
2. **PB-01 / U-168 + U-176** — peer connection primary election can be replaced or promoted without source/generation binding.
3. **SEARCH-RESP-01 / U-163** — `FileSearchResponse` acceptance is token-centered and not bound to requested search source/scope.

## Rev0034 strict decision

**FLAC-LEADING-ID3V2-DURATION-PRELUDE-01 / U-139** is verified, but it is not promoted.

The witness proves that stable/3.3.x duration-only `.flac` share scanning can read, decode, and apply a leading ID3v2 mapped text frame before native FLAC duration extraction. Master no longer applies the mapped ID3 field when `tags=False` and avoids the full large mapped-frame body read in the witness, although it still traverses the leading ID3 envelope.

This remains audited backlog because it is local media-parser hardening, public/upstream-adjacent TinyTag behavior, and partially fixed in master. It is weaker than the existing peer/protocol binding candidates.

## Audited hardening retained outside strict lane

| Packet | Latest proof revision | Decision |
|---|---:|---|
| FLAC-LEADING-ID3V2-DURATION-PRELUDE-01 / U-139 | rev0034 | Verified local FLAC leading-ID3v2 duration-only prelude behavior; master partially fixed; not strict-promoted. |
| FLAC-STREAMINFO-BLOCK-BUDGET-01 / U-127 | rev0033 | Verified local FLAC STREAMINFO fixed-block materialization budget; not strict-promoted. |
| MP4-M4A-ATOM-BUDGET-01 / U-125 | rev0032 | Verified local MP4 atom-leaf materialization budget; not strict-promoted. |
| OGG-CONTINUATION-ACCUM-01 / U-124 | rev0031 | Verified local Ogg continuation-packet assembly budget; not strict-promoted. |
| WMA-ASF-TINYSTEP-01 / U-273 | rev0030 | Verified local WMA/ASF object-size progress behavior; not strict-promoted. |
| FILE-ATTRIBUTE-BUDGET-01 / U-199 | rev0029 | Verified per-file attribute-count semantic-budget behavior; not strict-promoted. |
| SEARCH-SEND-POLICY-01 / U-174 + U-247 | rev0028 | Verified search send/geoblock/plugin policy behavior; not strict-promoted. |
| DISTRIB-PARENT-FANOUT-01 / U-173 + U-187 + U-216 + U-214 | rev0027 | Verified distributed parent/child fanout and branch-root hardening; not strict-promoted. |
| ROOM-SERVER-STATE-01 / U-111 + U-92 | rev0026 | Verified room/list count-mismatch parser and UI-state hardening; not strict-promoted. |
| PROTO-FRAME-PARSER-01 / U-137 + U-175 | rev0025 | Verified parser/frame hardening; not strict-promoted. |
| TRANSFER-CONTROL-PATH-BUDGET-01 / U-271 + U-274 + U-256 | rev0024 | Verified transfer-control path budget/echo behavior; not strict-promoted. |
| DOWNLOAD-INCOMPLETE-PROVENANCE-01 / U-226 + U-230 + U-250 + U-253 | rev0023 | Verified incomplete-file provenance and file-entry support; not strict-promoted. |
| TRANSFER-COMPLETE-LIFETIME-01 / U-269 | rev0022 | Verified completed-upload socket/slot lifetime behavior; not strict-promoted. |
| SHARE-SCAN-CACHE-01 / U-248 | rev0021 | Verified but public-overlap/known; not strict-promoted. |
| UPLOAD-QUEUE-POLICY-01 / U-244 | rev0020 | Verified upload queue candidate-size accounting behavior; not strict-promoted. |
| TRANSFER-EOF-01 / U-251 | rev0019 | Verified upload short-read/EOF lifecycle behavior; not strict-promoted. |
| TRANSFER-SIZE-PROVENANCE-01 / U-69 + U-107 + U-198 | rev0018 | Verified transfer size/opened-file/read-clamp chain; not strict-promoted. |
| PENDING-CONN-BUDGET-01 / U-181 | rev0017 | Verified pending connection message buffering; not strict-promoted. |
| ADDR-CONNECT-01 / U-145 + U-171 | rev0016 | Verified address-policy behavior; not strict-promoted. |
| F-CONN-FRAME-01 / U-164 | rev0015 | Verified fixed-width F-frame fragment behavior; not strict-promoted. |
| FOLDER-RESP-01 / U-167 | rev0014 | Verified folder response binding/parser-ordering behavior; not strict-promoted. |
| TR-STATUS-01 / U-158 + U-166 | rev0012 | Verified transfer status provenance behavior; not strict-promoted. |

Detailed packet docs remain in `docs/*-REV####.md`; this strict document should stay a front-lane index, not a second backlog.
