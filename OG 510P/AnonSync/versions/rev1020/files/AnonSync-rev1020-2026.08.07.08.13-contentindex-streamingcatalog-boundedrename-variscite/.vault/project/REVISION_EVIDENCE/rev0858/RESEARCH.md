# Rev0858 research notes

Research was used to challenge the inherited path and resource assumptions,
not to substitute for executable tests.

## JSON and parser limits

RFC 8259, section 9, explicitly permits implementations to set limits on input
text size, nesting depth, numeric range/precision, and string length/content.
It also requires UTF-8 for JSON exchanged outside a closed ecosystem and warns
that non-Unicode bit sequences produce unpredictable behavior.

Source:
https://www.rfc-editor.org/rfc/rfc8259.html

Implication for AnonSync: a resource ceiling is part of interoperable parser
policy, not an exceptional failure. Rev0858 applies this principle at the typed
manifest boundary. A later decoder revision should enforce counts while
parsing so rejected data is never first materialized as a large vector.

## Win32 portable names

Microsoft's “Naming Files, Paths, and Namespaces” documentation lists reserved
characters, prohibits trailing spaces/periods for portable shell behavior, and
states that `CON`, `PRN`, `AUX`, `NUL`, `COM1` through `COM9`, and `LPT1`
through `LPT9` remain reserved when followed by extensions. It also documents
ISO-8859-1 superscript digits 1, 2, and 3 as valid device-number spellings, for
example `COM¹`.

Source:
https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file

Implication for AnonSync: byte-valid UTF-8 is not sufficient for a
cross-platform path authority. Rev0858 adds the three superscript spellings.
This still does not solve all platform collision questions, such as Unicode
normalization, default case folding, or filesystem-specific equivalence.

## Unicode security

Unicode Technical Report 36 and Unicode Technical Standard 39 describe visual
spoofing, confusables, mixed-script identifiers, and the need for explicit
security profiles rather than assuming that well-formed Unicode is safe.

Sources:
https://www.unicode.org/reports/tr36/
https://www.unicode.org/reports/tr39/

Implication for AnonSync: current paths are canonical byte strings with strict
UTF-8 and a portable filename subset. They are not a human-identity profile.
Future UI and invitation surfaces should display script/confusable warnings
without silently changing the bytes used for object identity.

## Speculative next architecture

The strongest next step is a budget-aware manifest codec whose builder owns a
single admission token. Every array count and string length would consume that
token before allocation. The codec would produce either a fully frozen,
validated manifest plus exact usage evidence or no manifest at all. Running
that codec in a disposable worker would further contain parser and allocator
faults before the principal process receives transition authority.
