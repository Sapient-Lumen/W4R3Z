# Archive Zip Chronology Card

Compact chronology audit for sibling revision zips: record whether the external package lane stays timestamp-monotone across revisions, whether “latest by revision” matches “latest by timestamp,” and why archive head authority must still prefer revision labels when the two orderings differ historically.

## Headline findings

- The authoritative head by revision is `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`, while the latest zip by timestamp is `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`; same_head=True.
- Sibling zip chronology has 0 adjacent revision/timestamp inversions, so revision order is timestamp-monotone across unique revisions.
- Duplicate revision labels still number 1; authority therefore stays rule-based: prefer highest revision label for archive head; use timestamp only to order multiple zips that share the same revision label.

## Current live root

- root_name: `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal`
- revision_label: `rev0565`
- timestamp: `2026.03.25.23.58`

## Head comparison

- latest_by_revision: `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`
- latest_by_timestamp: `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`
- revision_and_timestamp_heads_match: `True`
- authority_rule: `prefer highest revision label for archive head; use timestamp only to order multiple zips that share the same revision label`

## Adjacent revision/timestamp inversions

- No adjacent revision/timestamp inversions were found across the unique revision heads.

## Duplicate revision labels

- `rev0562` appears 2 times: `Goldenrule-rev0562-2026.03.25.19.13-localrootsfetch-pruneladder.zip`, `Goldenrule-rev0562-2026.03.25.23.12-userspacerustup-livebridge.zip`

## Steward command

- audit_command: `python3 scripts/tools/audit_archive_zip_chronology.py`

## Tail by revision

- `rev0560` @ `2026.03.24.05.13` — `Goldenrule-rev0560-2026.03.24.05.13-proofbudget-citationbytes.zip`
- `rev0561` @ `2026.03.25.22.47` — `Goldenrule-rev0561-2026.03.25.22.47-rustupdetour-shadowcomeback.zip`
- `rev0562` @ `2026.03.25.23.12` — `Goldenrule-rev0562-2026.03.25.23.12-userspacerustup-livebridge.zip`
- `rev0563` @ `2026.03.25.23.23` — `Goldenrule-rev0563-2026.03.25.23.23-registryonlysurface-fetchtripwire.zip`
- `rev0564` @ `2026.03.25.23.43` — `Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip`
- `rev0565` @ `2026.03.25.23.58` — `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`
- `rev0566` @ `2026.03.26.00.24` — `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`

## Tail by timestamp

- `rev0560` @ `2026.03.24.05.13` — `Goldenrule-rev0560-2026.03.24.05.13-proofbudget-citationbytes.zip`
- `rev0562` @ `2026.03.25.19.13` — `Goldenrule-rev0562-2026.03.25.19.13-localrootsfetch-pruneladder.zip`
- `rev0561` @ `2026.03.25.22.47` — `Goldenrule-rev0561-2026.03.25.22.47-rustupdetour-shadowcomeback.zip`
- `rev0562` @ `2026.03.25.23.12` — `Goldenrule-rev0562-2026.03.25.23.12-userspacerustup-livebridge.zip`
- `rev0563` @ `2026.03.25.23.23` — `Goldenrule-rev0563-2026.03.25.23.23-registryonlysurface-fetchtripwire.zip`
- `rev0564` @ `2026.03.25.23.43` — `Goldenrule-rev0564-2026.03.25.23.43-procmacrofirst-nativenulltripwire.zip`
- `rev0565` @ `2026.03.25.23.58` — `Goldenrule-rev0565-2026.03.25.23.58-offlineproofladder-cachetruth-nightsignal.zip`
- `rev0566` @ `2026.03.26.00.24` — `Goldenrule-rev0566-2026.03.26.00.24-lockedofflinetriage-resumecompass-logknot.zip`
