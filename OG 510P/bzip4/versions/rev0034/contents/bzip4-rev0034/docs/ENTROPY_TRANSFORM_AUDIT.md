# Entropy and inverse-transform terminal audit — rev0029

rev0029 audits the boundary between the constant BZ3 block envelope, the
arithmetic decoder, and the optional LZP and modified-RLE inverse transforms.
The valid BZ3v1 byte stream is unchanged. Malformed input now stops at the first
unavailable or contradictory byte instead of depending on a later CRC failure.

## Canonical parsed block envelope

The low-level block decoder consumes the same allocation-free `BlockEnvelope`
parser used by frame inspection and workspace planning. Declaration, original
size, payload bound, model bits, intermediate sizes, BWT input size, primary
index, and required workspace are checked once and returned as one value.

This removes a second hand-written interpretation of the wire header. Raw and
regular blocks are distinguished once. Regular blocks require a one-based BWT
primary index inside the transformed extent; `-1` remains the raw-block
sentinel.

## Bounded arithmetic underflow

The inherited arithmetic reader returned synthetic `0xff` values after input
ended. A tiny payload could therefore trigger work proportional to an
attacker-controlled declared output before eventual rejection. rev0029 records
input exhaustion and returns as soon as bootstrap or renormalization needs the
first missing byte.

Internal progress telemetry records entropy bytes consumed, complete output
symbols, and truncation state. It resets for every attempt and is an internal
deterministic test surface rather than a public ABI.

The fixed witness declares a 4 MiB model-0 output, a valid primary index, and
only four arithmetic bytes. Across seven runs:

- published rev0028 median: `0.544909787` seconds;
- rev0029 median: `0.000010692` seconds;
- rev0029 progress: four input bytes, zero complete output symbols, truncation.

Both variants reject the block. The timing is a malformed-work witness only.

## Exact LZP terminal

The LZP inverse accepts an explicit expected output extent and succeeds only
when the compressed transform stream is consumed exactly and that output extent
is produced exactly. It rejects:

- truncated marker escapes or match lengths;
- reserved `255` match-length components;
- non-backward references;
- match lengths crossing the output boundary; and
- trailing transform bytes after exact output.

Overlapping backward matches remain legal and retain original bytewise copy
semantics. When LZP is the final inverse transform, CRC accumulation remains
fused into this mandatory output pass.

## Exact modified-RLE terminal

The modified-RLE inverse requires its complete 32-byte selection bitmap, a
non-`255` terminal component for every selected run, exact output, and exact
input consumption. It rejects truncated bitmaps, unterminated runs,
output-crossing runs, and trailing transform bytes. CRC accumulation remains
fused into the final reconstruction pass.

A valid model-4 block was used to construct shorter descriptor/CRC prefixes that
the predecessor accepted while silently leaving transform bytes. rev0029 rejects
all of them as malformed.

Transform grammar failures map to `BZ3_ERR_MALFORMED_HEADER`; entropy exhaustion
maps to `BZ3_ERR_TRUNCATED_DATA`; an intact but wrong reconstruction maps to
`BZ3_ERR_CRC`.

## Compatible APM locality

The arithmetic model's 512 by 17 adaptive-probability rows are stored as
`[run_selector][context][probability]`. A symbol touches only one selector, so
its 256 by 17 plane is contiguous. The table remains 17,408 bytes and every
initial value, probability read, mutation order, and encoded byte is preserved.

The implementation also retains rev0028's explicit order-1 alias rule: current
and previous rows may be the same row, so all three probabilities are captured
before any cell is updated. The retained APM microbenchmark predates the final
integration of those two compatible refactors and is historical prototype
evidence, not a rev0029 final-binary speed claim.

## Regression surface

The `entropy_and_transform_terminal_contract` strict group exercises literal
and overlapping LZP streams, short outputs, invalid length components, literal
and selected modified-RLE streams, unterminated and output-crossing runs,
entropy underflow work, progress reset, valid decode, and the crafted model-4
shortened-descriptor witness. The separate alias group compares active and
pristine-oracle bytes over all normal transform models and reused state.

Machine-readable evidence is in:

- `evidence/entropy-transform-terminal-regression.json`;
- `evidence/entropy-underflow-failfast-benchmark.json`; and
- `evidence/entropy-apm-layout-benchmark.json`.
