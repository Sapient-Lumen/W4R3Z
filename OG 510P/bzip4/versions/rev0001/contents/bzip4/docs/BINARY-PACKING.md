# Binary packing direction

The binary goal has two independent pieces:

1. produce a smaller reversible representation of a C++ executable;
2. reinflate and execute it safely in a constrained environment.

They should be designed and benchmarked separately. A strong binary transform does not require a self-extracting launcher, and a launcher should not dictate the compression format prematurely.

## Phase 1 — reversible binary transform

Start with ELF analysis on Linux because the intended environments use GCC-built C++ binaries.

Potential lanes:

- ELF/program/section headers and layout metadata;
- executable code;
- read-only constants and string tables;
- writable initialized data;
- relocations and dynamic linking metadata;
- symbols and debug sections;
- zero-filled or alignment padding;
- embedded compressed resources, which should usually bypass recompression.

Potential reversible transforms:

- section extraction with an exact layout map;
- delta coding sorted addresses and relocation offsets;
- branch/call target normalization for relative machine-code operands;
- grouping function bodies or sections across related binary versions;
- string-table front coding and suffix sharing;
- zero/padding run representation;
- architecture-specific transforms guarded by machine type and strict bounds checks.

Do not call stripping an optimization of the same lossless problem. Stripping can be offered separately, but it changes the original binary and may remove debugging or dynamic-linking information.

## Phase 2 — execution strategies

### External unpacker

A small installed `bzip4-run` executable reads a packed file, verifies it, materializes the original, and executes it. This keeps packed files data-only and makes updating the decoder easier.

### Self-extracting image

A launcher stub and packed payload are combined. This is convenient but adds a fixed size overhead, complicates signing, and makes every packed binary carry decoder code.

### Temporary-file execution

Write to a secure private temporary file, apply exact mode bits, execute, then remove. This is broadly understandable but may fail on `noexec` filesystems, consumes temporary storage, and creates cleanup/race concerns. Use exclusive creation, restrictive permissions, and verified content.

### In-memory execution on Linux

A future Linux launcher can investigate `memfd_create` plus `fexecve`/`execveat`, subject to kernel and libc availability. This avoids a named disk file but still requires careful descriptor flags, sealing, executable-memory policy, and fallback behavior. It is a platform feature, not a portable assumption.

## Security requirements

- Authenticate or at minimum strongly hash the reconstructed executable before launch.
- Treat all packed metadata as hostile: check integer overflow, lengths, references, and decompression budgets.
- Enforce maximum output size before allocation.
- Never map writable and executable memory simultaneously when avoidable.
- Preserve or explicitly override permissions, interpreter, arguments, environment, and working directory.
- Avoid following attacker-controlled symlinks in temporary paths.
- Make cleanup robust across signals and failed execution.
- Do not silently execute when verification fails.
- Fuzz the unpacker and transform decoder independently of the compressor.

## Measurements

For constrained use, report:

- packed payload size;
- launcher/stub size and total deployed size;
- peak unpack memory;
- temporary storage requirement;
- cold and warm startup latency;
- time until the original program begins;
- supported kernel/libc/architecture matrix;
- behavior on `noexec`, read-only, and low-space environments;
- whether the reconstructed binary hash exactly matches the original.

## rev0001 status

No binary transform or launcher is implemented. The current codec can compress a binary as ordinary bytes, and the research plan intentionally avoids claiming that generic BZ3v1 compression is an executable packer.
