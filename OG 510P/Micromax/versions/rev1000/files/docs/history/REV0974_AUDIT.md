# Revision 0974 audit

## Priority judgment

Rev0973 bounded Micromax instruction dispatch but explicitly could not interrupt
one Python/native primitive. The first measured residual was severe and
plugin-reachable: `s-replace` could turn a 100,000-byte source and 3,000-byte
replacement into a projected 300,000,000-byte Python string during one hostcall.
The generic result budget rejected the value only after allocation.

The smallest honest correction is prospective geometry where geometry is exact,
plus bounded incremental construction where rendering is recursive. A process or
WebAssembly migration would be disproportionate for these deterministic
in-process operations and would still require the same limit at the hostcall
boundary.

## Severe or wasteful findings

| Finding | Consequence | Correction |
|---|---|---|
| Hostcall result limits were postconditions only | `s-replace`, `s-join`, split, or concatenation could allocate an oversized result before denial | Compute exact bytes/cells and fail before the allocating primitive |
| `to-str` and `s-format %s` recursively built ordinary Python strings | Repeated aliases amplified a small retained graph inside one dispatch | Use one bounded streaming renderer with UTF-8 accounting |
| `.` and `.s` delegated structured values to Python `print`/`repr` | Debugging words bypassed the new text ceiling and could consume/output unbounded text | Render first under the same ceiling; consume/print only after success |
| Generic result accounting called `str()` on arbitrary-size integers | The guard itself could do expensive decimal conversion or hit CPython's digit-limit exception | Use exact conversion only for small integers and a bit-length upper estimate for large ones |
| Several input checks created temporary UTF-8 byte strings | A defensive check duplicated caller text just to count it | Share an allocation-free UTF-8 counter with early-stop support |
| `s-format` created a specifier list and copied its argument slice | Defensive work allocated in proportion to request size before output was known | Stream format validation and index the existing stack until commit |
| A naive join preflight rescanned every shared alias | A denied defensive path could still spend repeated native traversal work | Cache at most 64 immutable string identities and stop on first proven overrun |
| A generic “memory budget registry” was tempting | Policy surface would grow without containing Python process memory | Keep exact preflight local to concrete constructors and document residual work |

## Boundary review

`host_limits.py` now owns safe effective result limits, exact/proven-lower-bound
UTF-8 measurement, prospective violation messages, and bounded-cost integer text
estimation. The existing generic changed-stack postcheck remains the final
fallback for all hostcalls.

`host_strings.py` adds preconditions only where output geometry is knowable:
concatenation, split, join, and replacement. Validation occurs before stack
mutation. Exact-fit results still succeed. `s-format` cannot know its final text
without rendering each value, so it writes into `BoundedTextBuilder` and restores
the complete request on resource denial.

`value_text.py` is the single renderer for `to-str`, `s-format`, `.`, and `.s`.
Every append reserves UTF-8 bytes before writing. Nested strings keep the existing
JSON-quoted representation; top-level `.` strings remain raw. Depth remains
bounded at the historical six-level presentation rule. This is output
construction control, not a deep object membrane.

A Linux subprocess test sets `RLIMIT_AS` to current virtual memory plus 128 MiB,
then asks for the 300 MB replacement. The operation returns a stable Micromax
budget error with all operands intact instead of attempting the projection.

## Research judgment

Python documents `str.replace`, `str.join`, and `str.split` as result-producing
string operations; it does not provide an output-allocation quota parameter.
Python also documents a configurable integer-to-decimal digit limit, which is a
useful warning that a resource guard should not depend on eagerly rendering a
large integer. MITRE CWE-770 describes allocation without limits or throttling as
a resource-exhaustion weakness. CPython's Unicode writer API provides a broader
implementation precedent for owned incremental construction, although Micromax
uses a pure-Python bounded builder.

Official sources checked 2026-07-18:

- https://docs.python.org/3/library/stdtypes.html
- https://docs.python.org/3/library/sys.html
- https://docs.python.org/3/c-api/unicode.html
- https://cwe.mitre.org/data/definitions/770.html

## Residual risk

- This is not a Python-process memory limit, hostile-code sandbox, syscall
  boundary, native-code fault boundary, or crash boundary.
- Existing input objects may already be large. Huge lists of empty strings,
  shrinking replacements, substring search, trimming, slicing, and case
  conversion can still require substantial traversal or constant-factor output.
- Map rendering still sorts keys and stringifies them before the bounded output
  is complete; capture a concrete failing graph before extending the renderer.
- The generic arbitrary hostcall budget remains a postcondition when prospective
  geometry is unavailable.
- Explicit nonpositive embedding limits disable the corresponding guard and
  transfer responsibility to the embedding.
- No complete repository-suite or universal memory-containment claim is made.

## Recommended next correction

Measure the strongest remaining single-dispatch path rather than adding a generic
resource bureaucracy. Good candidates are a huge empty-element join, map-key
rendering, or a nonmultiplicative native string traversal. Add an input/work
ceiling only when the measured journey identifies a stable owner; select process
or Wasm isolation only for a failure that cannot be bounded honestly in-process.
