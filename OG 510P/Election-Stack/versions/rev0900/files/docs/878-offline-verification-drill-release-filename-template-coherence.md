# 878. Offline verification drill release-filename template coherence

**Track:** Shared (Release engineering and offline verification)
**Status:** rev0856 stale-drill-command repair

## Problem fixed

The offline verification drill plan was regenerated for current archive versions, but its ZIP-verification commands still inherited an old concrete carrier example from rev0846. That was dangerous because the drill plan is exactly the place an offline reviewer copies commands from when checking a release ZIP.

A stale carrier name can waste reviewer time, point a maintainer at the wrong archive, or create false confidence that the current release was verified when the command actually names an older revision.

## rev0856 change

`tools/release_go_no_go_pack.py` now emits a current-revision filename template instead of a stale historical codename:

```text
The-Election-Stack-rev####-YYYY.MM.DD.HH.MM-codename.zip
```

`scripts/check_release_go_no_go_pack.py` now rejects offline drill plans that do not mention the current revision prefix or that carry stale historical release ZIP examples.

## Boundary

The filename template is operator guidance only. The ZIP verifier and manifest checks remain the evidence-bearing controls; filename coherence is not signer authentication, certification, legal advice, live-pilot authorization, or proof of current voter instruction.
