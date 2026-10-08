# Design: Time Surface Lane Map (monotonic clocks, wall clocks, civil/offset forms, zoned DST-aware values, localized calendars, storage adapters, and fake clocks)

## Goal
Make the archive more precise about **what kind of temporal claim is actually being made**.

Rust's time ecosystem is much stronger than its public conversations often admit, but the phrase "datetime support" still hides too much.
A `std::time::Instant` timeout, a `SystemTime` filesystem timestamp, a `time::OffsetDateTime` wire value, a Jiff `Zoned` with IANA/DST semantics, an ICU4X localized calendar formatter, a `jiff-sqlx` database bridge, and a Tokio paused clock in tests are **different but connected** lanes.

The worthy contribution here is therefore not another datetime engine, one more formatting DSL, or a fake universal time badge.
It is a **portable lane map and evidence boundary** that lets tools say which temporal lane they occupy, what assumptions attach to it, where adapters are lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/time-surface-kit.md`](./time-surface-kit.md)
- [`design/time-surface-pilot-program.md`](./time-surface-pilot-program.md)
- [`design/background-work-kit.md`](./background-work-kit.md)
- [`design/localization-surface-kit.md`](./localization-surface-kit.md)
- [`proposals/epic-time-surface-kit.md`](../proposals/epic-time-surface-kit.md)

## Why this note is needed now
The current ecosystem signals line up around one conclusion: Rust needs a better **time-surface contract**, not just more date/time crates.

- Std keeps the two foundational clock lanes sharply distinct. `Instant` is a monotonically nondecreasing, opaque measurement useful only with `Duration`, but its docs also warn it is not guaranteed to be steady and that hardware, virtualization, or OS bugs can still violate monotonicity. `SystemTime` is explicitly not monotonic and is for talking to external entities like the filesystem and other processes.
  https://doc.rust-lang.org/std/time/struct.Instant.html
  https://doc.rust-lang.org/std/time/struct.SystemTime.html
- The `time` crate still represents an important offset/wire-format lane. Its features keep formatting, parsing, `local-offset`, `serde`, and `serde-human-readable` explicit, and its `format_description` module keeps well-known versus macro-built format descriptions explicit.
  https://docs.rs/time/latest/time/
  https://docs.rs/time/latest/time/format_description/index.html
- Jiff makes the zoned/DST-aware lane unusually legible. Its docs center zone-aware values, and its comparison and platform docs explain automatic TZDB integration, Windows bundling of the database, and CLDR-backed Windows-to-IANA mapping for local-zone discovery.
  https://docs.rs/jiff
  https://docs.rs/jiff/latest/jiff/_documentation/comparison/index.html
  https://docs.rs/jiff/latest/jiff/_documentation/platform/index.html
- Chrono and Chrono-TZ remain important, but they make a different claim. Chrono does not ship timezone data by default, while Chrono-TZ generates `TimeZone` implementations from the IANA database in a build script and exposes compile-time-built zone values.
  https://docs.rs/chrono
  https://docs.rs/chrono-tz
  https://docs.rs/chrono-tz/latest/chrono_tz/enum.Tz.html
- ICU4X keeps the localization/calendar lane explicit. `icu_datetime` focuses on localized formatting of dates, times, and time zones, and its field-set model keeps date, time, and zone choices first-class instead of hiding them behind one locale string.
  https://docs.rs/icu_datetime/latest/icu_datetime/
  https://docs.rs/icu_datetime/latest/icu_datetime/fieldsets/index.html
- Adapter pressure is already real. `jiff-sqlx` exists because SQLx integration needs a separate boundary today, and `jiff-icu` exists because zone-aware values and localized rendering are adjacent but distinct lanes.
  https://docs.rs/jiff-sqlx/latest/jiff_sqlx/
  https://docs.rs/jiff-icu/latest/jiff_icu/
- Deterministic/fake-clock semantics are also their own lane. Tokio's `time` module is runtime-bound, and its paused/advanced test-clock APIs explicitly warn about auto-advance behavior and timer processing limits.
  https://docs.rs/tokio/latest/tokio/time/index.html
  https://docs.rs/tokio/latest/tokio/time/fn.pause.html
  https://docs.rs/tokio/latest/tokio/time/fn.advance.html
- Maintenance signals are shifting, which raises the value of migration-aware lane mapping. Dirkjan Ochtman wrote in January 2026 that they are inclined to wind down Chrono and Chrono-TZ and now feel comfortable recommending Jiff.
  https://dirkjan.ochtman.nl/writing/2026/01/09/reviewing-2025.html

## The lane map

### Lane 1 — Monotonic elapsed/timeout lane
**What it is**
- Opaque monotonic-ish clocks for durations, deadlines, intervals, retries, and latency measurement.
- `std::time::Instant`, runtime-bound timer APIs, and timeout logic built around elapsed time rather than wall time.

**Why it matters**
- This is the cleanest lane for benchmarking, latency budgets, backoff, and timeout reasoning.
- It must stay distinct from user-visible timestamps and scheduler-facing civil time.

**What the archive should preserve**
- monotonicity claim (`guaranteed`, `best-effort`, `runtime-controlled`),
- opacity versus epoch anchoring,
- overflow/saturation posture,
- suspend/virtualization caveats,
- and runtime ownership of timer behavior.

**What it should not pretend**
- that elapsed time is a human timestamp,
- that monotonic means steady,
- or that a paused test clock is the same thing as a real system clock.

### Lane 2 — Wall-clock / external timestamp lane
**What it is**
- System-clock values used for filesystems, other processes, logs, and protocol anchors.
- `SystemTime` and APIs that deliberately cross into host/external chronology.

**Why it matters**
- This is where clock drift, NTP adjustment, and backwards movement become part of the public contract.
- External timestamps often need epoch conversion, comparison failure handling, or loss notes.

**What the archive should preserve**
- monotonicity absence,
- epoch anchor,
- external-authority posture,
- comparison failure or drift handling,
- and host-clock assumptions.

**What it should not pretend**
- that wall-clock capture is good enough for timeout logic,
- that file timestamps imply event order,
- or that host clocks are interchangeable across machines.

### Lane 3 — Civil / offset-only / wire-format lane
**What it is**
- Values for human-legible dates/times or fixed-offset datetimes without full geographic-zone semantics.
- `time`-crate offset/civil forms, compile-time format descriptions, and explicit parse/format lanes.

**Why it matters**
- This lane is often the most appropriate for protocols and storage that do not retain full zone identity.
- It is also where feature gating, human-readable versus binary serde, and compile-time formatting posture matter.

**What the archive should preserve**
- civil versus offset distinction,
- formatting/parsing feature posture,
- human-readable versus binary serialization,
- local-offset acquisition posture,
- and precision/range/truncation rules.

**What it should not pretend**
- that a fixed offset is a geographic time zone,
- that format strings imply locale-aware rendering,
- or that RFC3339-like output proves DST-aware arithmetic.

### Lane 4 — Zoned / IANA / DST-aware lane
**What it is**
- Time values that intentionally combine exact instants with geographic-zone rules.
- Jiff, Chrono plus Chrono-TZ, and other TZDB-aware stacks.

**Why it matters**
- This is the lane where DST gaps/folds, zone database freshness, host-zone discovery, and ambiguous-local-time policy become unavoidable.
- The ecosystem already contains materially different answers here: system TZDB, embedded TZDB, build-generated zones, and CLDR-backed local-zone mapping.

**What the archive should preserve**
- tzdb source (`system`, `embedded`, `build-generated`, `application-provided`),
- gap/fold posture,
- local-zone discovery posture,
- update/freshness risk,
- and DST-aware arithmetic expectations.

**What it should not pretend**
- that all zoned libraries make the same freshness and discovery tradeoffs,
- that fixed-offset values retain enough information for later civil scheduling,
- or that compile-time-built zones and host-zone lookups are interchangeable.

### Lane 5 — Localized calendar / locale-rendering lane
**What it is**
- User-facing date/time/zone rendering with locale and calendar semantics.
- ICU4X field sets, localized zone names, runtime-selectable calendars, and `jiff-icu`-style bridges.

**Why it matters**
- This lane answers a different question than wire formatting: what should a user in a locale or calendar system actually see?
- It also introduces data requirements and fallbacks that protocol-oriented crates often do not carry.

**What the archive should preserve**
- locale source and negotiation,
- calendar system,
- field-set or skeleton choice,
- timezone display kind,
- and CLDR/ICU data requirements.

**What it should not pretend**
- that localized rendering is merely pretty formatting,
- that locale-aware output and protocol output are one lane,
- or that user-facing zone names are available without extra data.

### Lane 6 — Storage / adapter / migration lane
**What it is**
- Bridges into SQL, serde, HTTP, logs, analytics, and migrations between crate families.
- `jiff-sqlx`, serde feature choices, and Chrono/`time`/Jiff conversion boundaries.

**Why it matters**
- This is where semantic loss usually happens.
- Zone identity, calendar context, precision, and even ambiguity decisions often disappear when values cross process or storage boundaries.

**What the archive should preserve**
- retained versus lost information,
- adapter family,
- database/protocol constraints,
- migration assumptions,
- and round-trip guarantee level.

**What it should not pretend**
- that successful parse/format round-trips preserve civil intent,
- that SQL adapters are semantically neutral,
- or that one migration guide is enough for all time stacks.

### Lane 7 — Deterministic / fake-clock lane
**What it is**
- Controlled clocks for tests, simulation, replay, and runtime-scoped scheduling experiments.
- Tokio paused/advanced clocks and adjacent fake-clock mechanisms.

**Why it matters**
- This lane changes what time even means during testing.
- It affects timeout behavior, scheduler fairness, ordering assumptions, and what evidence a test can legitimately claim.

**What the archive should preserve**
- runtime ownership,
- pause/advance policy,
- auto-advance behavior,
- external-I/O caveats,
- and whether the clock is replayable, manually driven, or merely frozen.

**What it should not pretend**
- that fake-clock tests prove wall-clock behavior,
- that advancing time guarantees all timers have been processed,
- or that deterministic scheduling is implied by having a mock clock.

## Adapter rules
A lane map becomes useful only if it names **lossy boundaries**.
The archive should therefore treat these as first-class adapter classes:

1. **monotonic ↔ wall-clock**
   - gains or loses epoch anchoring, drift exposure, and external-authority posture.
2. **wall-clock ↔ civil/offset**
   - adds or removes parsing/formatting commitments and fixed-offset retention rules.
3. **offset/civil ↔ zoned**
   - gains or loses TZDB source, DST gap/fold semantics, and local-zone discovery posture.
4. **zoned ↔ localized calendar rendering**
   - gains or loses locale, field-set, calendar, and zone-display data requirements.
5. **temporal values ↔ storage/wire adapters**
   - may lose zone identity, calendar context, precision, or ambiguity choices.
6. **real clocks ↔ fake clocks**
   - changes runtime ownership, timer advancement semantics, and what evidence counts as real-world behavior.

## What should change elsewhere in the archive
- **Time Surface Kit** should remain the base artifact family, but it should now cite this lane map as the rule for what must stay separate.
- **Background Work Kit** should import only the time lanes it actually consumes: deadlines, recurrences, civil schedules, fake clocks, and storage receipts are not one thing.
- **Localization Surface Kit** should import locale/calendar rendering facts rather than re-owning time-zone and clock semantics.
- **Replay Kit** should import deterministic/fake-clock lane truth rather than redefining time behavior itself.
- **Dataset / protocol / database stacks** should import storage-lane artifacts instead of narrating their own hidden temporal semantics.

## Strategic conclusion
The archive should now treat **Time Surface Kit** as a sharper frontier seam than it was before:
- lane maps should keep **monotonic**, **wall-clock**, **civil/offset**, **zoned/DST-aware**, **localized/calendar**, **storage/migration**, and **fake-clock** work distinct;
- pilot programs should prove those lanes separately before speaking about "Rust time support" in general;
- downstream consumers should import only the lane facts they can honestly reuse.

The worthy contribution here is therefore a thin `cargo timesurf` / `time-pack/v0` layer whose lane profiles, adapter reports, vector reports, and consumer handoffs make temporal behavior reviewable without forcing one universal time abstraction.
