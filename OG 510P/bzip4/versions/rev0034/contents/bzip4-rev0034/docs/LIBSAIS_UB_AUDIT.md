# libsais signed-marker undefined-behavior audit

The active amalgamation is pinned with bzip3 1.5.3. The pristine upstream copy
under `upstream/` remains untouched and is compiled as a renamed byte oracle.
The active `src/libsais.h` carries two narrow defined-arithmetic repairs.

## rev0021 sign-bit construction

GCC UndefinedBehaviorSanitizer reported signed left shifts into bit 31. The
imported code converted a Boolean to signed 32-bit and shifted it by
`SAINT_BIT - 1` to manufacture either zero or `INT32_MIN`.

That bit pattern is intentional, but signed `1 << 31` is undefined in C and
C++. The active copy replaced all 48 instances with:

```text
condition ? SAINT_MIN : 0
```

This preserves the same two-result marker function without a signed shift.

## rev0028 suffix-group marker transfer

The rev0028 entropy regression reached a separate UBSan witness in
`libsais_partial_sorting_gather_lms_suffixes_32s_4k`. Five expressions used:

```text
(s - SUFFIX_GROUP_MARKER) & ~SUFFIX_GROUP_MARKER
```

`SUFFIX_GROUP_MARKER` is bit 30. Some legal temporary suffix entries carry the
sign marker in bit 31. Subtracting bit 30 in signed `int32_t` can therefore
underflow before the mask is applied, even though the algorithm intends modulo
32-bit marker manipulation.

The active copy now converts the value to `uint32_t`, performs the subtraction
and mask there, and copies the resulting 32 bits back into the signed slot with
`memcpy`. This preserves the intended bit transition without relying on signed
overflow or an out-of-range unsigned-to-signed conversion.

The dedicated regression deliberately exercises the 32-bit 4k LMS gather path,
all four normal transform models, and active-versus-pristine encoded-byte
identity. GCC ASan/UBSan passes with `halt_on_error=1` after the repair.

## Oracle boundary

The pristine C oracle is compiled without UBSan instrumentation because its
purpose is exact comparison with unmodified upstream source. It remains under
AddressSanitizer. The active C++ codec, frame wrapper, tools, and tests remain
under AddressSanitizer and UndefinedBehaviorSanitizer. Valid encoded bytes are
required to remain identical to the oracle.

## rev0033 branchless compaction decrement

The new multi-megabyte resource-planning regression reached a third imported
UBSan witness in `libsais_compact_unique_and_nonunique_lms_suffixes_32s`.
The branchless compactor unconditionally evaluated five stores of the form:

```text
SAr[r] = p - 1;
r -= p > 0;
```

For nonpositive marker entries, the right-side store is not retained because
`r` is not decremented, but the subtraction is still evaluated. A legal
temporary `SAINT_MIN` marker therefore performed `INT32_MIN - 1` in signed
arithmetic before the dead value was overwritten.

The active copy now performs all five decrements modulo `uint32_t` and restores
the result bits with `memcpy`. This preserves the imported two's-complement bit
transition and branchless layout while removing signed overflow and avoiding an
out-of-range unsigned-to-signed conversion. The pristine upstream oracle remains
unchanged.

The regression uses a 3 MiB-plus payload that reaches this compaction path,
requires active-versus-pristine frame byte identity, exact reconstruction, and
GCC ASan/UBSan with `halt_on_error=1`.
