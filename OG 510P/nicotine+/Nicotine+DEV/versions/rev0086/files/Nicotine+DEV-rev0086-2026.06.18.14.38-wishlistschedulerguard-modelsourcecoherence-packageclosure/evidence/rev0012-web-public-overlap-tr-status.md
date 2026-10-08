# rev0012 public-overlap refresh — TR-STATUS-01

Scope: U-158 (`UploadFailed` / `UploadDenied`) and U-166 (`PlaceInQueueResponse`).

## Classification

- U-158: **public-adjacent, no direct public match found in this pass for the exact claimed-username + virtual-path status-binding invariant.**
- U-166: **public-adjacent and low standalone value.** Queue-position/request traffic and upload-list performance have public overlap; the exact arbitrary `PlaceInQueueResponse` queue-position update is not worth a separate strict report without a stronger state consequence.

## Public material captured

1. Official Nicotine+ Soulseek protocol docs define the relevant message shapes:
   - `PlaceInQueueResponse`: `string filename`, `uint32 place`.
   - `UploadFailed`: `string filename`.
   - `UploadDenied`: `string filename`, `string reason`.
   - The same docs also explain that `UploadFailed` can cause the recipient to re-queue the download, which makes the local abort/retry side effect protocol-relevant.
   - URL: https://nicotine-plus.org/doc/SLSKPROTOCOL.html

2. Nicotine+ issue #3199 / release-note overlap:
   - Issue #3199 describes severe slowness/freezing while another user is downloading a large amount of files.
   - Nicotine+ 3.3.8 release notes list #3199 and include “Optimized upload queue position requests.”
   - This is adjacent to queue-position traffic and U-166, but it is not a direct report of arbitrary claimed-username `PlaceInQueueResponse` queue-position mutation.
   - URLs: https://github.com/nicotine-plus/nicotine-plus/issues/3199 and https://nicotine-plus.org/NEWS.html

3. Soulseek.NET issue #604:
   - Discusses `UploadFailed` causing the peer to immediately re-queue/restart and `UploadDenied` being required to abort/cancel a download.
   - This is strong semantic adjacency for U-158, because it confirms the status messages are understood publicly as transfer-control signals with retry/abort consequences.
   - It is not a Nicotine+ report of claimed-username/virtual-path source binding.
   - URL: https://github.com/jpdillingham/Soulseek.NET/issues/604

4. Soulseek.NET issue #668:
   - Discusses odd behavior around SoulseekQt sending `UploadDenied` for a file that no longer exists, and downstream handling confusion.
   - This is adjacent to `UploadDenied` status semantics and transfer cleanup but not a direct username/path provenance report.
   - URL: https://github.com/jpdillingham/Soulseek.NET/issues/668

5. Nicotine+ 3.3.11 RC release notes:
   - Broadly adjacent because they mention preventing uploads from going through to spoofed users and peers sometimes being told our username is theirs.
   - This keeps U-158 from being described as “cleanly novel,” especially because its most meaningful threat story depends on source/identity binding.
   - URL: https://nicotine-plus.org/NEWS.html

## Rev0012 decision

Do **not** promote U-158/U-166 as a third strict finding in this revision.

Reasoning:

- The handler-level proof is real and consistent across all lanes.
- U-158’s strongest impact, closing/requeueing an active download with `UploadFailed`, becomes meaningfully adversarial when paired with PB-01-style peer/source binding gaps.
- U-166 is mostly UI/queue-position state and should be a regression/supporting test, not a standalone report.
- Public material already discusses `UploadFailed`/`UploadDenied` semantics and queue-position/request performance enough that the novelty should remain cautious.

Recommended cube treatment:

- Canonical family: `TR-STATUS-01 transfer status message provenance`.
- Canonical row: U-158.
- Subcase/support: U-166.
- Cross-dependency: PB-01 peer-source binding and U-123 transfer lifecycle provenance.
