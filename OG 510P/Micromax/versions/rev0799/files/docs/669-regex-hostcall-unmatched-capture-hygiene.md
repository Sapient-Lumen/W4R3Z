# Regex hostcall unmatched-capture hygiene (rev728)

Micromax's regex hostcalls expose match maps from `re.search` and `re.findall`:
`start`, `end`, the full matched `group`, positional `groups`, and optional
`groupdict` entries for named captures. Those maps are small enough to be useful
from scripts and future UIs, so they need to preserve the difference between
three distinct states:

- a capture matched real text, such as `"abc"`
- a capture participated but matched the empty string, `""`
- an optional capture did not participate at all

Before rev728, the hostcall layer used `str(...)` for every positional and named
capture. Python reports an unmatched optional capture as `None`, so Micromax
turned absence into the literal text `"None"`. That was misleading in two ways:
it made absence indistinguishable from user text that actually matched those four
characters, and it drifted from the VM's normal false/absent sentinel, `0`.

Rev728 keeps the fix intentionally narrow. `re.search` and `re.findall` match
maps now convert unmatched positional and named captures to `0`; captures that
really matched an empty string remain `""`; ordinary captures remain strings;
and the full-match `group` remains a string because a returned match always has a
whole-match span. Replacement hostcalls and editor replacement behavior are not
changed.

The important contract is small: match maps should not turn missing captures into
plausible text. If a future host implements the same `mx.regex` feature, this
absence/empty/text distinction should remain visible.
