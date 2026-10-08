# Assignment-scope surface checklist

- Identify one authoritative public path for precinct / district / jurisdiction assignment and one fallback help path.
- State the bounded public input basis clearly enough that a voter can tell whether the answer came from an address lookup, a voter-record lookup, or another public path.
- Return the precinct label or identifier, the relevant districts/jurisdictions, and the authoritative local-election-office routing answer in the same surface family.
- Distinguish assignment facts from downstream polling-place or ballot-style answers; do not force voters to infer precinct or district scope from a sample ballot alone.
- Publish explicit correction notices when precinct assignment, district assignment, or special-election scope changes because of address correction, reassignment, or boundary updates.
- Check parity across assignment lookup, polling-place lookup, ballot-style/sample-ballot surfaces, special-election pages, elected-official pages, and help scripts.
- Treat silent precinct-code changes, district-label swaps, and hidden address-correction effects as explicit superseding events, not background database edits.
- Publish accessible and translated versions where required, plus a fallback contact path when the primary lookup fails.
- Do not publish internal geocoding rules, full GIS logic, or unnecessary voter-record details when a bounded public answer plus pointer will do.
- Record `last_verified_at` and the latest correction/advisory notice pointer.
