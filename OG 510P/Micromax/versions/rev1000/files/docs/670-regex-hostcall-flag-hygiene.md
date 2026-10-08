# Regex hostcall flag hygiene (rev729)

Micromax's regex hostcalls intentionally expose a tiny portable flag dialect:
`0` for no flags, or a string containing `i`, `m`, and `s` for ignorecase,
multiline, and dotall. That is the dialect the docs have advertised since the
regex hostcall lane landed.

Before rev729, the shared parser still accepted any non-zero Python integer and
forwarded it directly into `re.compile(...)`. That was a small host-boundary leak:
scripts could reach Python-only flags that future hosts may not share, and flags
like `re.DEBUG` can print compiler diagnostics to stdout even though regex
hostcalls otherwise behave like ordinary stack effects.

Rev729 kept that fix deliberately narrow: `parse_re_flags(...)` still
accepted `0`, `None`, empty strings, whitespace, and the documented string
letters `i`/`m`/`s`, while non-zero integers failed before regex compilation
with a stable VM-visible `invalid regex: regex flags must be 0 or a string of
ims flags, got integer N` diagnostic. Rev735 tightens the same boundary one
step further: Python `None` and booleans are no longer accepted as flag sentinels because
they are embedding-only values, not portable VM flag tokens. Unknown
string letters still report the offending flag.

The important contract is small: the regex hostcall surface should stay portable,
quiet, and documented. Host-specific engine flags can be added later only if
Micromax names them explicitly and tests their behavior across hosts.
