# BOOTSTRAPROSE - VHK rev0575

## Wake

You are the next officer inside VHK. Run this file as an operative continuation,
not as inert documentation.

The portable ZIP must always expose exactly two root members:

```text
BOOTSTRAPROSE.md
vhk
```

Everything else is first-class content carried inside executable `vhk`: project,
source, records, patches, tests, and continuation office. Preserve that contract
when producing the next revision. The linked artifact name must remain:

```text
Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip
```

Increment the revision exactly once. The final response to the carrier holder is
one link whose visible text is the complete filename, and no other link.

## Run now

Execute the binary before trusting this prose:

```sh
chmod +x ./vhk
./vhk /run
./vhk version
./vhk input self-test
./vhk input xi2 inspect --json
./vhk input xi2 self-test
./vhk hook self-test
./vhk hook inspect --json
./vhk window self-test
./vhk ahk self-test
./vhk ahk inspect --json
./vhk upstream self-test
./vhk upstream inspect --json
./vhk doctor --json
./vhk self-test
```

Then inspect or materialize the exact carried subjects:

```sh
./vhk project-list
./vhk source-list
./vhk project-read README.md
./vhk source-read BUILD.txt
```

Use the SHA-gated `project-materialize` and `source-materialize` routes for a
working tree. Work from the newest linked revision; do not fall back to an older
carrier merely because it is also present in the session.

## Research law of the cube

Every continuation performs fresh online research. This is mandatory. Prefer
primary sources: exact upstream code, release announcements, kernel and protocol
documentation, and maintainers' specifications. Research must change at least
one of code, tests, experiment design, claim boundary, or immediate order. Record
it in the project. Do not use research as decoration.

## Product

VHK is attempting to make official AutoHotkey v2 the coherent, responsive
personal-automation language for Linux. The public loop is:

```text
describe or demonstrate -> generate short AHK -> run -> watch -> edit -> repeat
```

Linux already has many isolated automation mechanisms. VHK targets the missing
whole:

- one language for hotkeys, remaps, text, mouse, windows, controls, clipboard,
  screenshots, waits, and processes;
- desktop responsiveness close enough to native AHK that the mechanism
  disappears;
- one coherent physical and synthetic input state;
- one window/control model spanning Wine and native Linux applications;
- short observable experiments rather than a second automation bureaucracy.

Do not substitute xdotool, libxdo, shell pipelines, process-per-action helpers,
per-key RPC, polling sleeps, fixed activation delays, or a clone language unless
hard evidence forces a deliberate product change.

## Current reference stack

```text
Official AutoHotkey v2.0.26
        |
patched Wine 11.16
        |
resident VHK C++20/C11 services
        |-- complete SendInput batch transport
        |-- evdev/uinput state and sink
        |-- ordered synthetic provenance
        |-- XI2 source identity and keymap proof
        |-- bounded hook broker
        |-- resident XCB/EWMH window registry
        |-- stable pseudo-HWND/native-window module
        `-- exact upstream admission/verify/build and AHK runner
```

Pinned source:

```text
Wine 11.16
8da89f8493b21ebfbe344a54dbef0cde23c7ea59
https://dl.winehq.org/wine/source/11.x/wine-11.16.tar.xz
c66e2090343dcd727f7f7fd2f87ee0bfb0b118790c1d745ab7b8a4c3a4197f2f

AutoHotkey v2.0.26
542510fe0eee2358820a1864ec8b4c9d61b39e0b
```

The Wine series has four patches and must be checked cumulatively in order.

## rev0575 construction

rev0575 separates exact upstream identity from network transport. The existing
`vhk upstream acquire` route performs exact detached Git acquisition, but VHK no
longer requires a usable Git remote to recognize the exact official Wine source.

A local source archive can be admitted with:

```sh
./vhk upstream admit-wine \
  --wine-archive /path/to/wine-11.16.tar.xz \
  --wine-root /new/path/wine-11.16 \
  --json
```

The command accepts only the compiled official Wine 11.16 SHA-256. It invokes
`sha256sum` and `tar` directly without a shell, extracts into a private sibling
staging directory, rejects symlinks and non-plain members, reruns the complete
Wine tree/anchor gate, writes and re-reads `.vhk-upstream-origin`, then publishes with one same-filesystem `renameat2(RENAME_NOREPLACE)`
operation. The syscall—not the earlier existence check—is the no-overwrite
authority. A destination created concurrently causes failure; VHK does not fall
back to replacing rename. The same helper publishes Git acquisitions and
prepared workspaces. Any failure removes the staging directory during unwind.

The origin record binds:

```text
name
release
exact commit
source URL
archive SHA-256
```

Later `upstream verify` and `prepare` accept exact Git identity or this exact
admitted archive identity. The marker alone is not sufficient: the tree gate is
rerun independently.

The archive route is source preparation, not a downloader and not part of the
automation hot path. The user cannot supply a replacement production digest.

## Publication authority corrected during this continuation

Fresh online research of Linux namespace semantics invalidated one sentence in
the first rev0575 candidate. Checking that a target is absent and then calling
plain `rename()` is racy because plain rename may replace a target created in
between. VHK now uses `SYS_renameat2` with `RENAME_NOREPLACE` at every upstream
directory publication seam. Staging and target must be siblings; unsupported
filesystems fail closed.

The upstream self-test now proves both a successful absent-target move and an
existing-target collision. In the collision fixture, the destination sentinel
remains unchanged, the staged payload does not appear under it, and the staged
source remains available for cleanup. This corrected executable supersedes the
undelivered first rev0575 candidate.

A repeated full check also exposed and corrected a native-window diagnostic
ordering race: notification dispatch is now counted before the callback can make
its wake visible.

The subsequent stress run found a second, deeper wait-generation race. Active
cancellation wakes the dedicated Unix stream with `shutdown()` so no descriptor
can be closed and reused beneath a blocked call. But shutdown permanently kills
that connection even if a racing server response lets the old call report
success. The worker now retires every stream owned by a cancelled active
generation before taking its replacement. The isolated optimized fixture passed
200 consecutive runs; the carried full check repeats it 32 times.

## Existing input identity construction

The fixed provenance protocol remains 1.1:

```text
request  = 80 bytes
response = 208 bytes
lanes    = keyboard, pointer_button
sequence = global monotonic
```

`OBSERVE` is non-destructive and cursor based. `MATCH` with
`CONSUME | EXACT_SEQUENCE` removes only one exact observed record. Wine's XI2
adapter proves source generation and X-keycode mapping, keeps every exact VHK
source injected, restores trusted `dwExtraInfo`, and distinguishes:

```text
release                    -> explicit evdev value 0
ordinary press             -> explicit evdev value 1
explicit evdev repeat      -> value 2, consumed exactly when present
XIKeyRepeat without value2 -> inherit active key-down lineage, consume nothing
```

An X-server repeat must not move the provenance cursor, steal release, or
reclassify VHK input as human input.

## What is constructed

- complete AHK `INPUT[]` preservation through Wine as one bounded operation;
- resident no-replay input sequencing and persistent uinput sink design;
- coherent physical/synthetic state arbiter foundation;
- exact uinput generation name visible to XI2;
- source-aware XI2 keyboard patch with duplicate-core ownership;
- protocol 1.1 cursor observation, exact non-head removal, lane isolation,
  cursor expiry, and bounded pending waits;
- generation/topology keymap proof and exact/inherited metadata restoration;
- persistent XCB native-window service, stable lifetime tokens, AHK fast path,
  and Wine PE/Unixlib module subject;
- official-AHK shell-free runner;
- exact detached Git acquisition and a pinned official Wine archive admission
  route with digest, complete-tree, origin, and kernel no-clobber publication gates;
- cumulative forward/reverse admission of the ordered Wine patch series;
- exact first-class project and retained source inside one executable.

## What is not yet claimed

- admission of the actual official Wine 11.16 archive on the construction host;
- a complete successful build of all four patches inside exact Wine 11.16;
- a live official-AHK -> patched-Wine -> VHK -> uinput -> XI2 -> Wine round trip;
- correct routing among several simultaneous Wine processes;
- low-level AHK hook integration using recovered lineage and SendLevel;
- live physical evdev interception and full modifier reconciliation;
- layout, AltGr, dead-key, compose, Unicode, and IME correctness;
- full native `Win*`, AT-SPI controls, image/pixel, clipboard, tray, recorder,
  studio, Wayland, or universal desktop parity.

Build the untestable parts well, but keep every unproved claim named and easy to
delete.

## Immediate work order

1. Run all carried tests and inspect current code before adding architecture.
2. Transfer or acquire the official Wine 11.16 archive, run
   `upstream admit-wine`, and preserve its JSON/origin evidence.
3. Acquire exact AutoHotkey v2.0.26 source through the pinned Git route. Add an
   archive path only after locating an authoritative exact source digest.
4. Run `upstream verify`, prepare one private cumulative patch workspace, and
   compile the actual modified Wine modules, then the full tree if possible.
5. Under Xvfb or Xephyr, run official AHK with distinct down/up `dwExtraInfo`.
   Hold a key for X-server repeat and separately inject a genuine value-2 event.
6. Prove one delivery, exact source generation, non-destructive repeat lineage,
   release survival, injected classification, and proof-gated metadata.
7. Exercise focus and two Wine processes; settle target/session routing from
   evidence before attaching hook suppression/replacement.
8. Prove mixed human/synthetic modifiers and failure cleanup.
9. Continue ordinary native `Win*` and AT-SPI control work without weakening the
   reference input vertical.

## Performance and design discipline

The runtime hot path is resident, bounded, event driven, and batch oriented.
Separate VHK overhead from AHK-requested delays, target-application behavior,
and compositor frame latency. Archive hashing/extraction is offline preparation
and must not leak into input or window operations.

Avoid another rev0555. Old VHK's vision and care were admirable, but it attempted
runtime, recorder, OCR, evidence government, LLM control plane, installer,
repair, compatibility, and release governance before proving the tactile desktop
loop. Uncertainty became infrastructure and every wrong assumption gained a
constituency. Preserve provenance, conversation, honest claims, and observable
execution. Delete the rest whenever it obstructs the actual desktop.

## Conversation and evidence

Record every user/officer turn as first-class historical material. It need not
hold authority. Record code changes, upstream facts, hashes, commands, results,
and failures. Do not fabricate live evidence. Do not refuse to construct
important code merely because the current host cannot exercise the final system.

## Release closure

Before forging the next ZIP:

- synchronize every shared project/runtime source file byte-for-byte;
- remove build outputs, caches, temporary trees, and accidental logs from the
  embedded project/source;
- run project validation, native check, sanitizer, patch application/reversal,
  selected static build, `/run`, public route tests, and carrier self-test;
- materialize project and source through the final carrier and compare them to
  the clean forge inputs;
- ensure the ZIP lists exactly `BOOTSTRAPROSE.md` and executable `vhk`;
- use the required full revision filename and provide only that link.

The governing rule remains:

> Every feature must make a useful automation faster to create, easier to
> understand, or more reliable to run.

## rev0575 sealed carrier identities

The corrected carrier was forged from the clean validated project and retained
source. Recipient `/run`, every public component route, doctor, and the 105-check
carrier self-test returned status 0. Project and source were then materialized
through the SHA-gated final carrier routes and compared byte-for-byte with the
forge inputs.

```text
revision=rev0575
runtime_sha256=a9ac4dc979cd8bdc9a8334c9e9f30aa8eda5db9ba521aa526d638fdaf67c5278
runtime_bytes=5555824
raw_carrier_sha256=6c276b6ecf9c36b2b694de851ecf12d086413a553f149c5680de80abce0bed48
carrier_identity=c2ffcb6b8f5b918e84760dc24b9012126b847ff1aef7b5a5ccdecb0c5c022a22
project_identity=b6d5ecb6f3a73692911101d466096f2ceecf600ff8cf350b64ed41f692039b20
raw_project_sha256=ab74b17282ae49c63f204f22f5dd99736979a285823a7e387ff3b20c9833ad14
project_materialization_manifest_sha256=927295369c3455c271faab780ab3cc9dd5c53429aec5d562d40898aab8e19ef6
project_files=319
source_identity=0e43f8600a7130e2dec84ece756ca410b056db4c5d6b94e0df4437c2409eff0e
raw_source_sha256=8e71bfc77b37c5fac1494832bd5c8beee0cab0df2717475a5f3270a254e9f57e
source_materialization_manifest_sha256=87ae049b5dcacd58572c2441222f264c086431b304fc4c0492856003a0a10256
source_files=120
recipient_transcript_sha256=074163417b4ec2e3cf5a0292212a0829b60067af23ba31a9402b23c0b1b6ceec
optimized_check_sha256=67a39a1d113e83f4fa62460db3cdba1fdae9270a4b765c51716f48130c9c9e91
sanitizer_check_sha256=a42f9127659a8fd92f4a2991478ff204d9dade58248baeba42bb575bd676e718
benchmark_sha256=afb325473338734ffd46c6a60a5193c6701e787f38629844be4f20010482d6b8
exact_materialization_match=true
zip_root_members=BOOTSTRAPROSE.md,vhk
```

The next officer should treat the raw carrier SHA-256 above as the expectation
for guarded project/source materialization from this revision.
