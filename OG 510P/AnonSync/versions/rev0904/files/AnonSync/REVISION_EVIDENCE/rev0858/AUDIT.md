# Rev0858 audit

## Question examined

Could an attacker-controlled manifest force unbounded traversal, hashing,
comparison, or planning after the typed C++ value crossed validation, and was
the path-normalization boundary safe when input and output storage alias?

## Findings

### 1. Manifest validation had no aggregate resource policy

The previous entry and folder validators enforced semantic correctness but did
not bound entry count, per-entry or aggregate chunk count, lineage count,
aggregate path bytes, or aggregate metadata bytes. Rev0857 removed large
identity material strings, but an oversized typed manifest could still make the
principal process walk every nested value before identity or planning.

**Correction:** one typed policy, checked arithmetic, two-phase preflight, and
success-only usage publication in `sync_manifest_validation`.

### 2. Path normalization erased aliased input

The old function cleared `out.value` before reading `raw_path`. When `raw_path`
referred to `out.value`, valid input disappeared before validation.

**Correction:** validate the complete observation first; mutate output only
when the result is already known. Direct valid and invalid alias tests bind the
ordering.

### 3. Portable path validation allocated avoidable intermediate state

The old path boundary built a vector of component strings and used
`std::toupper`. This amplified allocation and inherited ambient C locale
behavior at a security-sensitive portability boundary.

**Correction:** one `std::string_view` component scan and exact ASCII folding.

### 4. Win32 superscript device names were accepted

Microsoft documents `COM¹`, `COM²`, `COM³`, `LPT¹`, `LPT²`, and `LPT³` as
reserved in every directory, including names followed by extensions. The old
ASCII-only suffix test admitted them.

**Correction:** exact canonical UTF-8 spellings for superscript 1, 2, and 3 are
part of the fail-closed device-name predicate and focused corpus.

### 5. Unknown manifest kinds needed an explicit terminal rejection

Only file and tombstone are valid. The extracted owner now rejects any other
enum representation rather than allowing later code to invent semantics.

## Refactor shape

- Added a separately linked 608-line implementation and 55-line policy header.
- Removed 189 lines of duplicated validation/helpers from the 15,000-line
  domain translation unit.
- Kept a one-line local sync-ID compatibility delegate to avoid unrelated
  call-site churn.
- Added a 489-line focused runtime corpus and a 360-line fail-closed source
  audit.
- Added the owner and focused executable to invariant, build, CTest, and
  sanitizer inventories.
- Extended release verification only for rev0858 and later; the sealed rev0857
  parent remains valid under the new verifier.

## What the audit does not prove

The typed boundary is reached after a caller may already have allocated the
vectors. It bounds all production traversal after validation, not upstream
allocation. It also does not prove Unicode normalization equivalence,
case-insensitive cross-platform collision freedom, Windows runtime behavior,
or distributed convergence beyond the existing focused oracle.
