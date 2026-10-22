# bzip4

## Compression that can fit the work around it

bzip4 develops a C++20 implementation of the bzip3 1.5.3 codec for a practical embedding problem: compress and restore carried materials without letting a codec consume the workspace, silently change the byte policy, or expose an unfinished destination. Its interesting contribution is the connection between compression, bounded parallel work and deliberate file publication, not a claim to have invented a better compression ratio.

The supplied rev0034 provides library interfaces and command-line tools. Named profiles separate the block partition that determines encoded bytes from the number of workers available to produce them. A small source capsule and a larger payload can therefore have different explicit speed/size policies, while a tighter memory budget reduces concurrency rather than quietly choosing a different compression.

## The inherited codec, deliberately partitioned

The [block encoder](versions/rev0034/contents/bzip4-rev0034/src/libbz3.cpp) conditionally keeps modified run-length encoding and LZP prediction when each reduces the intermediate data, applies the Burrows–Wheeler transform, then arithmetic coding. Blocks shorter than 64 bytes take a literal path. A larger block gives these transforms more material to work with, but also needs more workspace and leaves fewer independent blocks to schedule. The project studies that operational tradeoff while preserving the inherited block contract.

## Block policy and execution policy are different choices

The [profile registry](versions/rev0034/contents/bzip4-rev0034/src/profile.cpp) contains three versioned choices: 256 KiB requested blocks for small source capsules, 1 MiB for the general speed profile, and 2 MiB for the balanced profile. Each requests up to eight lanes under a 128 MiB default codec-workspace budget. A lane is a concurrently usable block workspace, not a promise that eight threads will be productive on every input.

The [resource planner](versions/rev0034/contents/bzip4-rev0034/src/resource_plan.cpp) first computes the effective block size and block count. It then admits no more lanes than the requested count, the available blocks, or the workspace budget can support. For nonempty input, if even one lane cannot fit, the named command rejects the operation before creating its output staging file.

This distinction makes reproducibility concrete. A profile fixes its requested block-size law; small inputs follow the codec's effective-size adjustment under that law. Runtime lane fitting does not repartition the input. The [profile policy](versions/rev0034/contents/bzip4-rev0034/docs/PROFILE_POLICY.md) requires a new identifier for a changed requested block size rather than silently redefining an existing profile.

For example, the carried regression uses 3,479,061 input bytes. The 1 MiB speed profile has four blocks and four useful lanes, not eight. The reader can inspect that plan before creating workers. The historical unqualified `compress INPUT OUTPUT` command still uses a different default, 16 MiB and one lane; it is not an alias for the named speed profile.

The charged budget covers codec workspace. It is not total process memory: thread stacks, allocator overhead, input/output infrastructure, page cache and the embedding application's other work still need room.

## Parallel work without unbounded completed output

The [retained parallel interface](versions/rev0034/contents/bzip4-rev0034/include/bzip4/parallel_codec.hpp) keeps workers and codec arenas across calls. Within a bounded batch, each active lane handles at most one block; completed workspace views are delivered in frame order before those arenas are reused. The design avoids making the whole corpus, or an accumulating queue of finished blocks, the unit of working memory.

The interface also spells out responsibilities that an embedder must honor. Range-backed readers must preserve stable bytes for the call and support concurrent reads unless serialized reads are selected. Sink views are borrowed only during the callback, and callbacks must not re-enter the same encoder. This is useful machinery for a long-lived host, not just a faster invocation of a disposable command.

## Inspect the envelope before paying for decode

The [frame scanner](versions/rev0034/contents/bzip4-rev0034/src/frame_source.cpp) reads the count-bearing header, walks block descriptors and validates bounded prefixes before decoded output is delivered. It checks whether the block count fits the input, whether record spans stay inside the source, whether cumulative decoded size exceeds the caller's limit, and whether trailing bytes are permitted.

The [block-envelope validator](versions/rev0034/contents/bzip4-rev0034/src/frame_envelope.cpp) checks model bits, intermediate lengths and the BWT index against the described transformed block. It accumulates the workspace actually required by the validated payload and output extents. A declared large block size need not force a declaration-sized decoder arena when the actual blocks support a smaller one.

These checks answer admission questions, not every decoding question in advance. The complete payload still has to decode correctly. The [profile-aware command path](versions/rev0034/contents/bzip4-rev0034/tools/bzip4_codec.cpp) combines preflight, profile compatibility, resource planning, decoding and output accounting before publication.

## Finished bytes and durable publication are separate events

The command opens its source through [a pinned descriptor](versions/rev0034/contents/bzip4-rev0034/src/pinned_file.cpp), uses position-based reads, and checks a fingerprint containing device, inode, size and modification/change times before committing the output. It does not repeatedly resolve a filename as if that guaranteed the same source. The fingerprint is a mutation check, not a cryptographic assertion that hostile concurrent writes are impossible.

The [atomic writer](versions/rev0034/contents/bzip4-rev0034/src/atomic_file.cpp) creates an exclusive staging file in the destination directory, writes and synchronizes it, closes it, renames it into place, then synchronizes the directory. A failure before rename leaves staging cleanup rather than a published partial file. A failure in the final directory sync is different: rename has already published the destination, although durability was not confirmed. The implementation records publication before that final step and does not pretend an error means nothing changed.

That boundary matters to a caller deciding whether to retry. It is also part of why the project cannot be understood through codec throughput alone: getting a compressed byte sequence and responsibly replacing a file are connected but distinct operations.

## Compatibility and the meaning of “better”

At a fixed block partition, the [carried comparison](versions/rev0034/contents/bzip4-rev0034/docs/EFFECTIVENESS_SCORECARD.md) reports identical block records to the pristine bzip3 1.5.3 oracle. Its high-level frame is not identical to the upstream CLI stream: bzip4 uses the 13-byte, count-bearing envelope of upstream's separate high-level API, four bytes longer than the CLI header. The [frame audit](versions/rev0034/contents/bzip4-rev0034/docs/UPSTREAM_FRAME_AUDIT.md) explains why the two envelopes share a name without sharing a parser contract. Shared BZ3v1 terminology does not make the complete files universally interchangeable.

The frame also does not record the profile name. [Profile compatibility](versions/rev0034/contents/bzip4-rev0034/src/profile.cpp) compares the frame's block size with the profile's effective-size law; it cannot establish which name an encoder intended. Multiple profiles can converge on a small input. An embedding carrier must bind the intended profile and build identity separately, alongside content identities and limits.

The scorecard's 546,406,400-byte witness illustrates a real choice. Its 1 MiB result was 33.11% larger than the 16 MiB compressed result, yet preserved 97.93% of the bytes saved by that larger-block policy. Those are different denominators, not competing truths. A requirement such as “80% as effective” needs to specify the metric.

The [matched-compiler audit](versions/rev0034/contents/bzip4-rev0034/docs/COMPILER_AND_LIBSAIS_AUDIT.md) likewise corrects an earlier comparison that mixed build settings. Its three-round, single-host matrix reports lower elapsed time for bzip4 under matched GCC and Clang builds, but compiler choice itself changes the result materially. These are historical measurements of named configurations, not an intrinsic or universal speed percentage. The large-block experiment that exceeded 300 seconds of decode time is retained as a reason not to turn every ratio improvement into an automatic operational setting.

## A codec ready to study is not an admitted carrier feature

The later [overview](versions/rev0034/contents/bzip4-rev0034/README.md) records an intended Datacube role, while explicitly stating that the inspected Datacube rev0117 still used `none-v1`. Admission would require source space, retained notices, authenticated profile/build identity, stored and plaintext hashes, resource limits, unsupported-reader behavior and carrier-level verification. The codec's own profiles do not implement that integration merely by using Datacube names.

Read [rev0001](versions/rev0001/contents/bzip4/README.md) for the baseline, then the planner, file boundary and scorecard above for what the later work changes. Read beside [CloudtainerML](../CloudtainerML/README.md) for experiments whose costs and information access define their meaning, and [BrowserRT](../BrowserRT/README.md) for another implementation where an error after publication cannot be treated as an untouched destination. Their mechanisms differ; the shared question is what the caller is entitled to conclude.

## Version shelf and preservation

- [rev0001 — Huntstag](versions/rev0001/) establishes the C++20 baseline, block API, benchmark and corpus-probe tools, with an upstream source snapshot.
- [rev0034 — Amberkite](versions/rev0034/) adds the resource/profile account developed above, source, historical evidence and Linux convenience binaries. The [prediction register](versions/rev0034/contents/bzip4-rev0034/docs/PREDICTION_REGISTER.md) keeps later forecasts distinct from supplied measurements.

### Preservation and licensing

Each version keeps its unchanged original ZIP and its own extracted directory tree. [The manifest](MANIFEST.json) records original and member hashes. The two snapshots contain 79 and 255 extracted files respectively. No archived program or convenience binary was run during intake.

Existing provenance, source snapshots, copyright notices, and license texts remain with their respective versions. The baseline README identifies LGPLv3 for the derived codec and a retained libsais license; readers should consult the carried notices. See the [current owner declaration](../../LEGAL-NOTICE.txt).

The bundled [Shakespeare electronic text](versions/rev0034/contents/bzip4-rev0034/upstream/bzip3-1.5.3-53984ef/examples/shakespeare.txt) carries a separate World Library / Project Gutenberg notice with personal, noncommercial distribution and no-charged-access conditions. Its notice is retained verbatim. Do not assume that this fixture shares the codec’s LGPL terms; consult the carried notice before reuse.
