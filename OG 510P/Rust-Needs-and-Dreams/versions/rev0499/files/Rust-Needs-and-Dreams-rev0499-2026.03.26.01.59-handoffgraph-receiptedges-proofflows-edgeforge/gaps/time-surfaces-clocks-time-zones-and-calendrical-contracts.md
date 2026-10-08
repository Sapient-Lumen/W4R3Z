# Gap: time surfaces, clocks, time zones, calendars, and reviewable temporal contracts

Read this together with [`design/time-surface-lane-map.md`](../design/time-surface-lane-map.md), [`design/time-surface-pilot-program.md`](../design/time-surface-pilot-program.md), and [`proposals/epic-time-surface-kit.md`](../proposals/epic-time-surface-kit.md).

## What is missing
Rust has multiple strong date/time pieces, but the ecosystem still lacks a **portable way to publish what a temporal surface actually means**.

Today there is no standard way to say:
- whether an API is about a monotonic measurement (`Instant`-like), a wall clock (`SystemTime`-like), an absolute timestamp, a fixed-offset datetime, a civil datetime, or a time-zone-aware datetime,
- which time-zone database or zone-resolution strategy is assumed, embedded, delegated to the host, or absent,
- how daylight-saving gaps and folds are handled,
- whether formatting is locale-free wire formatting, user-facing localized formatting, or custom-calendar rendering,
- what precision / truncation / leap-second / out-of-range posture applies,
- how values map to SQL, Serde, logs, HTTP, message buses, and tabular engines,
- whether tests use real clocks, fake clocks, frozen clocks, or deterministic replay,
- and what evidence actually ran: DST vectors, gap/fold probes, round-trip parse/format vectors, DB/wire interop vectors, or fake-clock schedule vectors.

That gap matters because Rust’s time ecosystem is no longer a simple “pick one crate” situation.
Std already distinguishes monotonic `Instant` from non-monotonic `SystemTime`; Chrono, `time`, and Jiff expose materially different models for offsets, zones, and arithmetic; ICU4X adds localized formatting and custom calendars; and new adapter crates like `jiff-icu` and `jiff-sqlx` show that interop pressure is already real.

So the missing contribution is not another datetime crate.
It is a **reviewable time-surface layer** for publishing clock kind, timezone/calendar semantics, formatting/localization posture, storage/wire interop, and evidence honestly.

Sources:
- https://doc.rust-lang.org/std/time/struct.Instant.html
- https://doc.rust-lang.org/std/time/struct.SystemTime.html
- https://docs.rs/chrono
- https://docs.rs/time
- https://docs.rs/jiff
- https://docs.rs/jiff/latest/jiff/_documentation/platform/index.html
- https://docs.rs/icu_datetime/latest/icu_datetime/
- https://docs.rs/icu/latest/icu/calendar/enum.AnyCalendar.html
- https://crates.io/crates/jiff-icu
- https://crates.io/crates/jiff-sqlx
- https://dirkjan.ochtman.nl/writing/2026/01/09/reviewing-2025.html

## The current seam is awkward
Rust already has several real time subcultures, but their semantics do not line up cleanly:
- `std::time::Instant` is about monotonic measurement and is opaque / relative, while `SystemTime` is a wall-clock value that can go backward,
- Chrono exposes `Utc`, `Local`, and `FixedOffset`, and its docs explicitly steer normalization toward `FixedOffset` when parsing textual dates,
- the `time` crate exposes `OffsetDateTime`, `PrimitiveDateTime`, `UtcOffset`, and compile-time checked format descriptions, but its public model is still largely offset-centric,
- Jiff explicitly separates timestamps, civil values, and time-zone-aware values, supports IANA TZ data and DST-aware arithmetic, and documents platform-specific system-zone discovery,
- ICU4X exposes localized formatting of dates, times, and time zones plus runtime-selectable calendars,
- adapter crates like `jiff-icu` and `jiff-sqlx` now exist because users need bridges across formatting, calendar, and database lanes,
- and maintenance signals are shifting too: the current Chrono maintainer has publicly said they are inclined to wind down Chrono / Chrono-TZ and now feel comfortable recommending Jiff.

So the ecosystem is not missing *temporal primitives*.
It is missing the **artifact family that records which temporal model a public surface actually chose, what it assumes about zones/calendars/locales/storage, and what evidence checked those claims**.

Sources:
- https://doc.rust-lang.org/std/time/struct.Instant.html
- https://doc.rust-lang.org/std/time/struct.SystemTime.html
- https://docs.rs/chrono
- https://docs.rs/time/latest/time/format_description/index.html
- https://docs.rs/time/latest/time/macros/macro.format_description.html
- https://docs.rs/jiff
- https://docs.rs/jiff/latest/jiff/tz/struct.TimeZone.html
- https://docs.rs/jiff/latest/jiff/_documentation/platform/index.html
- https://docs.rs/icu_datetime/latest/icu_datetime/
- https://docs.rs/icu/latest/icu/calendar/enum.AnyCalendar.html
- https://crates.io/crates/jiff-icu
- https://crates.io/crates/jiff-sqlx
- https://dirkjan.ochtman.nl/writing/2026/01/09/reviewing-2025.html

## Why the archive now needs an explicit lane map
The base gap was already correct, but it still left one flattening hazard: too much of the ecosystem can be described as if "time support" were one lane.

The archive now needs to keep at least these lanes separate:
- **monotonic elapsed/timeout clocks** (`Instant`, runtime timers),
- **wall-clock / external timestamps** (`SystemTime`, file/process metadata),
- **civil or offset-only forms** (`time`-style parse/format and offset lanes),
- **zoned / IANA / DST-aware forms** (Jiff, Chrono plus Chrono-TZ, and explicit tzdb-source posture),
- **localized calendar / locale rendering** (ICU4X and `jiff-icu` style bridges),
- **storage / adapter / migration lanes** (`jiff-sqlx`, Serde/SQL/log/protocol retention and loss),
- **deterministic / fake-clock lanes** (Tokio paused/advanced test time and adjacent runtime-controlled clocks).

That distinction is no longer theoretical. Tokio's docs make runtime-controlled paused/advanced time explicit; Chrono documents that timezone data is not shipped by default; Chrono-TZ documents build-generated zones; Jiff documents automatic TZDB integration and Windows embedding; ICU4X documents localized field-set-driven formatting; and `jiff-sqlx` documents its separate bridge posture.

Sources:
- https://docs.rs/tokio/latest/tokio/time/index.html
- https://docs.rs/tokio/latest/tokio/time/fn.pause.html
- https://docs.rs/tokio/latest/tokio/time/fn.advance.html
- https://docs.rs/chrono
- https://docs.rs/chrono-tz
- https://docs.rs/jiff/latest/jiff/_documentation/platform/index.html
- https://docs.rs/icu_datetime/latest/icu_datetime/
- https://docs.rs/jiff-sqlx/latest/jiff_sqlx/

## Why this matters
This gap matters because time semantics cut across many high-value Rust systems at once:
1. **timeouts, retries, and latency measurement** — monotonic and wall-clock time are not interchangeable;
2. **scheduling and calendaring** — civil time, time zones, DST gaps/folds, and recurrence semantics leak everywhere;
3. **storage and interop** — SQL / JSON / HTTP / logs / analytics stacks routinely lose zone or calendar intent unless it is published explicitly;
4. **localized user interfaces** — user-facing formatting and custom-calendar rendering are different from protocol formatting;
5. **deterministic testing and replay** — fake/frozen clocks and deterministic time advancement are part of the public support boundary, not just test internals;
6. **migration risk** — moving from Chrono or `time` to Jiff / ICU-backed stacks is not just a type-alias change; it changes semantics.

A worthy contribution here is therefore not a new formatting DSL or another “easy datetime” API.
It is a way to treat **time surfaces as reviewable ecosystem infrastructure**.

Sources:
- https://doc.rust-lang.org/std/time/struct.Instant.html
- https://doc.rust-lang.org/std/time/struct.SystemTime.html
- https://docs.rs/chrono
- https://docs.rs/time
- https://docs.rs/jiff/latest/jiff/_documentation/comparison/index.html
- https://docs.rs/icu_datetime/latest/icu_datetime/
- https://crates.io/crates/jiff-icu
- https://crates.io/crates/jiff-sqlx

## What “good” looks like
A worthy contribution here is **not** one fake universal datetime badge.
It is a shared time-surface boundary:
- one `time-surface/v0` describing the top-level temporal family and intended use,
- one `clock-kind-profile/v0` describing monotonic / wall / logical / fake clock posture, precision, and host/runtime assumptions,
- one `civil-zone-profile/v0` describing timestamp / civil / offset / zoned semantics, DST gap/fold handling, and timezone-data sourcing,
- one `calendar-locale-profile/v0` describing calendar system, localized formatting posture, locale negotiation, and user-facing rendering assumptions,
- one `time-storage-profile/v0` describing SQL / Serde / log / wire / analytics mappings, truncation, and round-trip guarantees,
- one `time-adapter-profile/v0` describing bridges between `std::time`, Chrono, `time`, Jiff, ICU4X, and storage adapters,
- one `time-vector-set/v0` describing DST, parse/format, round-trip, fake-clock, and DB/wire vectors,
- one `time-check-report/v0` recording which vectors actually ran,
- and one `time-pack/v0` bundle for docs, CI, migration notes, fixtures, and archaeology.

That would let Rust teams reason about time choices with **explicit artifacts** instead of a brittle mix of README advice, type signatures, and bug folklore.

## Non-goals
This gap should not be used to:
- replace existing datetime crates,
- define one canonical calendar or timezone library,
- collapse monotonic timing, wall-clock timestamps, civil/offset forms, zoned scheduling, localized formatting, storage adapters, and fake-clock lanes into one fake manifest,
- or pretend that DST / leap-second / localization semantics can be solved by a single conversion function.

The job is smaller and sharper:
**make temporal surfaces legible, honest, and checkable across clocks, zones, calendars, formatting, persistence, and evidence.**
