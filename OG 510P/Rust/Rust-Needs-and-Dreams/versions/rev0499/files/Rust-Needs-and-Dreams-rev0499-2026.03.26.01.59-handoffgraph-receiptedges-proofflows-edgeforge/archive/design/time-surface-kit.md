# Design: Time Surface Kit (`cargo timesurf`, `time-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **time surfaces** in Rust: clock kind, timestamp/civil/zoned semantics, timezone and DST posture, locale/calendar rendering, storage/wire mappings, deterministic-test posture, and the evidence that those claims were actually checked.

This should help answer questions like:
- is this API measuring elapsed time, reading wall time, representing a precise instant, or representing a user-facing civil schedule,
- what timezone rules and database source are assumed,
- how DST gaps/folds and offset-only values are handled,
- whether formatting is wire-oriented or locale-aware,
- how values round-trip through Serde, SQL, logs, and protocols,
- and what fake-clock or deterministic-test support actually exists.

It should **not** replace datetime crates, schedulers, or localization engines.
It should make temporal semantics reviewable and comparable.

Read this together with:
- [`design/time-surface-lane-map.md`](./time-surface-lane-map.md)
- [`design/time-surface-pilot-program.md`](./time-surface-pilot-program.md)
- [`design/background-work-kit.md`](./background-work-kit.md)
- [`design/localization-surface-kit.md`](./localization-surface-kit.md)
- [`proposals/epic-time-surface-kit.md`](../proposals/epic-time-surface-kit.md)

## References (signals)
- `Instant` is monotonic-ish / nondecreasing and opaque, but its docs also warn that hardware, virtualization, or OS bugs can break monotonic guarantees and that some APIs saturate to zero instead of panicking.
  https://doc.rust-lang.org/std/time/struct.Instant.html
- `SystemTime` is explicitly not monotonic and can go backward.
  https://doc.rust-lang.org/std/time/struct.SystemTime.html
- Chrono’s docs center `Utc`, `Local`, and `FixedOffset`, and describe normalizing other zones into `FixedOffset` for parsed text.
  https://docs.rs/chrono
- The `time` crate exposes `OffsetDateTime`, `UtcOffset`, and feature-gated formatting/parsing plus compile-time `format_description!` support.
  https://docs.rs/time
  https://docs.rs/time/latest/time/format_description/index.html
  https://docs.rs/time/latest/time/macros/macro.format_description.html
- Jiff explicitly supports the IANA Time Zone Database, DST-aware arithmetic, and separates timestamps, civil values, and zoned values.
  https://docs.rs/jiff
- Jiff also documents concrete platform-specific system-zone discovery, including CLDR-based Windows-to-IANA mapping.
  https://docs.rs/jiff/latest/jiff/_documentation/platform/index.html
- ICU4X provides localized formatting of dates/times/zones and runtime-selectable calendars.
  https://docs.rs/icu_datetime/latest/icu_datetime/
  https://docs.rs/icu/latest/icu/calendar/enum.AnyCalendar.html
- `jiff-icu` and `jiff-sqlx` are current evidence that interop bridges are already becoming their own lane.
  https://crates.io/crates/jiff-icu
  https://crates.io/crates/jiff-sqlx
- Dirkjan Ochtman’s 2026 maintenance review says they are inclined to wind down Chrono and Chrono-TZ and now feel comfortable recommending Jiff.
  https://dirkjan.ochtman.nl/writing/2026/01/09/reviewing-2025.html

## Conceptual model
Time Surface Kit assumes that “time support” is not one thing.
It is at least seven separable lanes, now made explicit in [`design/time-surface-lane-map.md`](./time-surface-lane-map.md):
1. **monotonic elapsed/timeout** — opaque duration-bearing clocks and runtime timer lanes;
2. **wall-clock / external timestamp** — host/system times used for filesystems, logs, and other processes;
3. **civil / offset / wire format** — fixed-offset and parse/format-heavy lanes that are not the same as geographic-zone semantics;
4. **zoned / IANA / DST-aware** — time values coupled to zone databases, local-zone discovery, and ambiguity handling;
5. **localized calendar / locale rendering** — user-facing formatting, field-set choice, zone-name display, and custom calendars;
6. **storage / adapter / migration** — SQL/Serde/log/protocol bridges and retained-versus-lost temporal meaning;
7. **deterministic / fake-clock** — runtime-controlled testing, replay, and paused/advanced clock semantics.

The kit should preserve these distinctions even when one crate spans several of them.

## Artifact family

### 1) `time-surface/v0`
Top-level declaration for a public temporal surface.

Fields:
- package / crate / module id
- surface id and version
- intended use classes (`elapsed-measurement`, `deadline-timeout`, `protocol-timestamp`, `civil-schedule`, `localized-rendering`, `database-roundtrip`, `mixed`)
- primary public types
- supported runtimes / targets where relevant
- related adapter ids
- documentation and evidence pointers

### 2) `clock-kind-profile/v0`
Describe clock source semantics.

Fields:
- clock kind (`monotonic`, `wall`, `logical`, `fake`, `externally-provided`, `mixed`)
- opacity / anchoring (`opaque-relative`, `unix-epoch`, `calendar-anchored`, `runtime-defined`)
- monotonicity claim (`guaranteed`, `best-effort`, `not-monotonic`, `test-controlled`)
- precision / resolution / truncation notes
- overflow / saturation / panic posture
- runtime / OS assumptions
- fake-clock controls (freeze, advance, jump, inject)

### 3) `civil-zone-profile/v0`
Describe temporal representation and zone semantics.

Fields:
- value model (`timestamp`, `civil`, `offset`, `zoned`, `recurrence`, `mixed`)
- timezone support (`none`, `fixed-offset-only`, `host-local`, `IANA`, `custom`, `mixed`)
- timezone data source (`system-tzdb`, `embedded-tzdb`, `icu`, `host-api`, `application-provided`, `none`)
- DST gap posture (`reject`, `earliest`, `latest`, `caller-selects`, `not-applicable`)
- DST fold posture (`earliest`, `latest`, `ambiguous`, `caller-selects`, `not-applicable`)
- arithmetic semantics (`duration-only`, `calendar-aware`, `DST-aware`, `mixed`)
- leap-second / range / invalid-local-time notes
- local-zone discovery posture

### 4) `calendar-locale-profile/v0`
Describe rendering / localization / calendar semantics.

Fields:
- calendar support (`iso8601-only`, `gregorian-localized`, `runtime-selectable`, `custom`)
- locale source / negotiation (`explicit`, `system-default`, `fallback-chain`, `none`)
- formatting classes (`wire`, `human-readable`, `localized`, `pattern-driven`, `mixed`)
- parsing posture (`strict`, `lenient`, `wire-only`, `localized-input`, `mixed`)
- timezone display kinds used (`offset`, `generic-name`, `location-name`, `mixed`)
- CLDR / ICU / custom data requirements
- compile-time formatting support notes

### 5) `time-storage-profile/v0`
Describe persistence and interop mappings.

Fields:
- serialization formats (`rfc3339`, `unix-seconds`, `unix-nanos`, `sql-timestamp`, `custom`, `mixed`)
- retained semantics (`instant-only`, `offset-retained`, `zone-retained`, `calendar-retained`, `lossy`)
- DB adapters / protocol adapters used
- truncation / precision loss rules
- null / default / sentinel-time posture
- round-trip guarantee level (`lossless`, `lossy-but-documented`, `best-effort`, `unknown`)
- migration notes between crate families

### 6) `time-adapter-profile/v0`
Describe bridges between temporal ecosystems.

Fields:
- source and destination type families
- semantic mapping (exact, lossy, partial, requires-extra-context)
- lost information (zone, locale, calendar, precision, ambiguity choice)
- added assumptions (host tzdb, ICU data, SQL driver behavior, local zone lookup)
- feature / dependency / runtime requirements
- migration guidance

### 7) `time-vector-set/v0`
Collection of executable vectors.

Vector classes:
- monotonic / wall-clock behavior vectors
- DST gap and fold vectors
- parse / format round-trip vectors
- locale / calendar rendering vectors
- SQL / Serde / HTTP / log round-trip vectors
- precision / truncation vectors
- fake-clock / deterministic scheduling vectors
- migration parity vectors between crate families

### 8) `time-check-report/v0`
Results of running declared vectors.

Fields:
- vector ids executed
- environment (OS, tzdb source/version if known, locale data source, Rust toolchain, target)
- adapter versions used
- outcomes (`pass`, `fail`, `unsupported`, `inconclusive`, `skipped`)
- failure classes (`gap-fold-mismatch`, `precision-loss`, `zone-loss`, `calendar-loss`, `clock-behavior-mismatch`, `other`)
- log / fixture attachments

### 9) `time-pack/v0`
Bundle format:
- `time-surface/v0`
- one or more `clock-kind-profile/v0`
- one or more `civil-zone-profile/v0`
- zero or more `calendar-locale-profile/v0`
- one or more `time-storage-profile/v0`
- zero or more `time-adapter-profile/v0`
- one `time-vector-set/v0`
- one or more `time-check-report/v0`
- raw fixtures / DST cases / locale snapshots / DB round-trip evidence / migration notes

## Reference UX: `cargo timesurf`
- `cargo timesurf inspect`
  - discover likely clock kinds, crate families, adapters, Serde/SQL features, and formatting lanes
- `cargo timesurf check`
  - run declared vectors and emit `time-check-report/v0`
- `cargo timesurf diff <A> <B>`
  - compare two packs or versions and explain semantic drift
- `cargo timesurf doctor`
  - explain likely ambiguity points: offset-vs-zone loss, DST edge handling, fake-clock absence, lossy DB mappings
- `cargo timesurf pack`
  - bundle a `time-pack/v0`

`cargo timesurf` should begin as an orchestrator / validator / packer. It should avoid becoming a new datetime engine or localization runtime.

## Default policy
- **Clock kind must be explicit.**
- **Elapsed/timeout clocks and wall clocks stay distinct.**
- **Offset-only and zone-aware values stay distinct.**
- **User-facing localization stays distinct from wire formatting.**
- **Storage/migration adapters must publish lossiness.**
- **Fake-clock and deterministic-test posture are first-class.**
- **Unsupported, host-dependent, or lossy outcomes are valid outcomes.**

## What the kit should provide to others
- **Application authors:** a way to state whether APIs expect elapsed time, deadlines, wall time, civil scheduling, or localized rendering.
- **Library authors:** a way to publish DST / zone / locale / storage assumptions without baking in one ecosystem monopoly.
- **DB / protocol / analytics teams:** an explicit place to record timestamp precision, retained zone intent, and round-trip limits.
- **Migration work:** a way to compare Chrono, `time`, Jiff, and ICU-backed lanes honestly.
- **Deterministic-test tooling:** a place to attach fake-clock and replay evidence.

## Overlap boundaries
- **Not Runtime Capability Kit:** that kit owns whether clock authority exists at all; Time Surface Kit owns the semantics once a clock/time API is used.
- **Not Background Work Kit:** that kit owns durable scheduling/execution semantics; this kit owns the temporal value and clock semantics those systems rely on.
- **Not Localization Surface Kit:** that kit owns messages/catalogs/locale-negotiation more broadly; this kit owns date/time/calendar/timezone rendering semantics specifically.
- **Not Dataset Surface Kit:** that kit owns table/columnar contracts; this kit owns the semantics of temporal values that may be stored there.
- **Not Diagnostic Surface Kit:** that kit owns error/reporting style; this kit owns time meaning and evidence.

## Hard problems (explicitly scoped)
1. **Leap seconds and platform drift**
   - v0 should allow “unsupported / host-defined / out of scope” without forcing fake certainty.
2. **Host timezone discovery variance**
   - the kit should record source and strategy, not pretend every platform is equivalent.
3. **Localization depth**
   - ICU-backed rendering is richer than offset formatting; the kit should preserve that richness without forcing ICU everywhere.
4. **Semantic migration**
   - moving between Chrono / `time` / Jiff / ICU-backed lanes is often lossy or assumption-heavy.
5. **Testing realism**
   - fake clocks, deterministic replay, and real wall clocks all tell different truths; the kit should preserve which was actually used.

## Evaluation plan
Pilot on:
1. one std-based timeout / retry / latency crate using `Instant` and `SystemTime`,
2. one protocol / DB crate publishing RFC 3339 or Unix timestamp mappings,
3. one Jiff-based application surface with IANA-zone and DST-aware arithmetic,
4. one localized UI lane using ICU4X or `jiff-icu`,
5. one fake-clock / deterministic-test harness.

Success bar:
- projects can publish temporal assumptions without inventing their own schema,
- reviewers can tell wall-clock, monotonic, civil, offset, zoned, and localized lanes apart,
- DST / storage / migration loss becomes visible before production,
- and the ecosystem gets a reusable boundary above today’s fragmented time stack without flattening meaningful differences.
