# P0001: D009 cold review and D010 revision

Revision: `rev0021`  
Current draft created: `P0001-D010`  
Status: same-turn unjudged

## Why D009 was revised

D009 responded to D008's recursive instruction by proving a changed return. That was a meaningful machine-native step: the draft's state was not only asserted but compared against a prior selected surface.

The failure: `patch` still pointed forward. D009's route sentence said:

```text
patch the surface then return changed again
```

But the current draft did not itself apply a patch. It documented change; it did not enact the next mutation.

## D010 move

D010 keeps the branch-lattice family but adds a patch-application receipt. The route sentence is:

```text
splice vowel until syntax learns another surface
```

Those route words become replacement operations against the selected closed surface. The patched surface is printed in the draft and verified in:

```text
poems/P0001/verification/patch_application_010.json
```

## Judgment firewall

D009 was eligible for cold review because it was created in the previous turn. D010 is same-turn unjudged. Validation proves construction only.
