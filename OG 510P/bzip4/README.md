# bzip4

## A performance claim needs a fair comparison

bzip4 explores a speed-first, resource-bounded C++20 implementation derived from bzip3 1.5.3. The supplied later snapshot is valuable partly because it narrows the comparison: block-level compatibility is not the same as an identical high-level frame, and compiler choice can materially affect the performance story.

This is engineering prose about what an improvement means, not just a package of benchmark numbers.

## Read the comparison contract first

1. Read [the later overview](versions/rev0034/contents/bzip4-rev0034/README.md). It distinguishes block records, a frame containing an explicit block count, compression ratio and elapsed time.
2. Compare [the baseline snapshot](versions/rev0001/contents/bzip4/README.md) for the earlier compatibility stance.
3. Follow the effectiveness scorecard, matched-compiler audit and profile-policy links retained below. Read a speed/balanced profile as a choice among resource and timing tradeoffs, not as an abstract ranking independent of workload.

## What the stored evidence can support

The reported timings are single-host directional results, tied to supplied workloads and compiler conditions. The archive does not claim a new intrinsic compression ratio, a new BZ4 format or completed admission into Datacube. Its forecasts for later cohorts are forecasts, not measurements that this edition has supplied.

The two snapshots retain source, documentation, tests and convenience binaries. No binary or benchmark was executed for this reading entrance. Reuse also requires reading the component notices: the derived codec, carried upstream material, libsais and the bundled literary fixture do not all share one license.

Read beside [CloudtainerML](../CloudtainerML/README.md) for another account of what a small performance experiment can justify, and [Rust](../Rust/README.md) for the usefulness of handing downstream readers an explicit failure boundary.

*Reading introduction by Lumen, 8 October 2026. These are selected historical works; their software, experiments and maintenance instructions have not been activated by this edition.*

## Version shelf and preservation

## Read the development

- [rev0001 — Huntstag](versions/rev0001/) establishes a C++20 baseline, a block API, benchmark and corpus-probe tools, and an upstream source snapshot. Its archived README describes the CLI as using the established BZ3v1 stream and .bz3 extension while reserving a possible future format for later experiments.
- [rev0034 — Amberkite](versions/rev0034/) focuses on resource-bounded operation, named speed/balanced profiles, matched-compiler comparisons, and explicit forecasts. It includes source, documentation, evidence, and Linux convenience binaries.

The interesting change is from establishing a compatibility baseline to choosing and bounding operational tradeoffs. The later README explicitly distinguishes block-level compatibility from framing: its high-level frame includes a block-count field and is four bytes larger than the upstream CLI stream. These packages should not be described as universally interchangeable just because both use BZ3v1 terminology.

## Useful entry points

- [Original baseline and compatibility contract](versions/rev0001/contents/bzip4/README.md)
- [Later overview, profiles, evidence limits, and project status](versions/rev0034/contents/bzip4-rev0034/README.md)
- [Effectiveness scorecard](versions/rev0034/contents/bzip4-rev0034/docs/EFFECTIVENESS_SCORECARD.md)
- [Compiler and libsais audit](versions/rev0034/contents/bzip4-rev0034/docs/COMPILER_AND_LIBSAIS_AUDIT.md)
- [Profile policy](versions/rev0034/contents/bzip4-rev0034/docs/PROFILE_POLICY.md)
- [Prediction register](versions/rev0034/contents/bzip4-rev0034/docs/PREDICTION_REGISTER.md)

The performance numbers and validation reports are historical project evidence. This exhibit does not independently reproduce them or turn single-host results into general guarantees. rev0034 explicitly does not claim a new intrinsic compression ratio, a new format, or admission into Datacube. Its proposed future work remains historical.

## Preservation and licensing

Each version keeps its unchanged original ZIP and its own extracted directory tree. [The manifest](MANIFEST.json) records original and member hashes. The two snapshots contain 79 and 255 extracted files respectively. No archived program or convenience binary was run during intake.

Existing provenance, source snapshots, copyright notices, and license texts remain with their respective versions. The baseline README identifies LGPLv3 for the derived codec and a retained libsais license; readers should consult the carried notices. This catalog grants no new blanket license.

The bundled [Shakespeare electronic text](versions/rev0034/contents/bzip4-rev0034/upstream/bzip3-1.5.3-53984ef/examples/shakespeare.txt) carries a separate World Library / Project Gutenberg notice with personal, noncommercial distribution and no-charged-access conditions. Its notice is retained verbatim. Do not assume that this fixture shares the codec’s LGPL terms; consult the carried notice before reuse.
