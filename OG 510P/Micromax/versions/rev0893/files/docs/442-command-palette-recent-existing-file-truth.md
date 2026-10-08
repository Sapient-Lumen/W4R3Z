Rev500 note: command-palette `Recent Files` rows now also keep explicit `existing file` disk truth when Micromax is allowed to inspect the target, so ordinary saved MRU entries stop being the one remaining class that says neither `existing file` nor `new file`.

# Command-palette recent-file existing-file truth (rev500)

Micromax already had the nearby honest surfaces:

- `recentfile` rows already reused exact MRU metadata like recency, active/open state, dirty/readonly flags, and current cursor position
- missing remembered paths already appended `new file`, and missing-path MRU rows already also appended `current buffer` / `switch buffer` or `empty buffer @ 1:0`
- adjacent `openpath` file rows already reused the capability-gated `existing file` / `new file` dialect for saved versus missing file targets

But one first-class execution seam still lagged behind that model: once a remembered recent path still existed on disk, the `recentfile` row still stopped at `section=... | detail` plus maybe one live-buffer action cue. That kept navigation context visible, but it still hid one boring, important distinction right where trust matters most:

- a closed saved recent file really is an `existing file`
- an open saved recent file is still an `existing file` even if Enter also means `current buffer` or `switch buffer`
- the saved-file case should not be the one remaining recent-file class that says neither `existing file` nor `new file`

Rev500 keeps the fix tiny and local to `_command_palette_recent_file_row(...)`:

- reuse the same capability-gated disk-truth check for `recentfile` rows too
- append `existing file` when Micromax is allowed to inspect the remembered path and it still exists on disk
- keep the newer missing-file and live-buffer action cues intact, so rows can still layer `new file`, `current buffer`, `switch buffer`, or `empty buffer @ 1:0` as needed

The intent is simple: once Micromax is already allowed to confirm that one visible recent-file row still points at a real saved target, it should say `existing file` before Enter instead of leaving the safest ordinary case implied.
