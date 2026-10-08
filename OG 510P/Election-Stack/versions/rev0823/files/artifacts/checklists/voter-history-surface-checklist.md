# Voter-history surface checklist

- Identify one authoritative public path for voter history / participation-record lookup and one fallback help path.
- State whether the surface is expected to show posted participation immediately, after Election Day, after county upload, after canvass, or after another bounded official step.
- Distinguish live ballot-status answers from posted participation-history answers; do not force voters to infer “my vote counted” from a stale tracking page alone.
- Return only bounded participation facts needed for the public answer, such as election date, voting method, county, or primary-ballot label where applicable.
- Publish explicit correction notices when posted participation history is delayed, corrected, removed because of a public correction, or temporarily unavailable.
- Check parity across the voter portal, ballot-status/help pages, office contact directories, FAQs, and hotline/help scripts.
- Treat changed participation method/county/party fields and posting-window updates as explicit superseding events, not silent edits.
- Publish accessible and translated versions where required, plus a fallback contact path when the primary lookup fails.
- Do not publish ballot selections, ballot images, pollbook scans, or unnecessary voter-file details when a bounded public answer plus pointer will do.
- Record `last_verified_at`, the posting-lag note, and the latest correction/advisory notice pointer.
