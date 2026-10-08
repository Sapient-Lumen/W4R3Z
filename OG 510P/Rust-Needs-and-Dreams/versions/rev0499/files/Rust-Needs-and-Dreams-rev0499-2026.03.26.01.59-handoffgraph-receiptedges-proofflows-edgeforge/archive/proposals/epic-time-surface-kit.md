# Epic proposal: Time Surface Kit

Read this together with [`design/time-surface-lane-map.md`](../design/time-surface-lane-map.md), [`design/time-surface-pilot-program.md`](../design/time-surface-pilot-program.md), and [`design/time-surface-kit.md`](../design/time-surface-kit.md).

## Thesis
One of the more worthy ecosystem contributions in Rust now would be a **portable review layer for time surfaces**.

Rust programs constantly cross boundaries between monotonic measurement, wall-clock timestamps, civil scheduling, time-zone-aware datetimes, localized rendering, and persistence. But today those semantics are usually published only through type names, crate choice, and scattered bug lore.

Rust does not need one more datetime crate nearly as much as it needs a boring, explicit `time-pack/v0`.

## Why now
The timing is unusually good:
- std already makes a sharp distinction between monotonic `Instant` and non-monotonic `SystemTime`;
- Chrono, `time`, and Jiff now represent materially different ecosystem lanes instead of one settled consensus;
- Jiff has made IANA-zone / DST-aware / host-zone discovery support much more legible and is already growing adapter crates;
- ICU4X makes custom calendars and localized date/time formatting a first-class Rust lane;
- adapter crates such as `jiff-icu` and `jiff-sqlx` are evidence that interop is becoming a first-class problem;
- and the current Chrono maintainer has publicly said they are inclined to wind down Chrono and Chrono-TZ while recommending Jiff.

That means the next major time seam is visible before it has converged.
This is exactly when a reviewable contract is more valuable than another implementation.

Sources:
- https://doc.rust-lang.org/std/time/struct.Instant.html
- https://doc.rust-lang.org/std/time/struct.SystemTime.html
- https://docs.rs/chrono
- https://docs.rs/time
- https://docs.rs/jiff
- https://docs.rs/icu_datetime/latest/icu_datetime/
- https://crates.io/crates/jiff-icu
- https://crates.io/crates/jiff-sqlx
- https://dirkjan.ochtman.nl/writing/2026/01/09/reviewing-2025.html

## Why the archive now needs a lane-oriented rollout
The epic was already directionally right, but it still needed a sharper execution rule: **time should be piloted by lane, not by crate family**.

The archive now needs to prove at least seven adjacent but non-equivalent lanes separately:
1. monotonic elapsed/timeout clocks,
2. wall-clock/external timestamps,
3. civil/offset and wire-format lanes,
4. zoned/IANA/DST-aware lanes,
5. localized calendar/locale rendering,
6. storage/adapter/migration bridges,
7. deterministic/fake-clock runtime control.

That is why this revision adds both [`design/time-surface-lane-map.md`](../design/time-surface-lane-map.md) and [`design/time-surface-pilot-program.md`](../design/time-surface-pilot-program.md): the worthy contribution is not another crate comparison or one giant datetime matrix, but a ranked rollout whose pilots preserve lane identity and expose lossiness.

## What should be built
A first credible version should ship:
1. `time-surface/v0`, `clock-kind-profile/v0`, `civil-zone-profile/v0`, `calendar-locale-profile/v0`, `time-storage-profile/v0`, `time-adapter-profile/v0`, `time-vector-set/v0`, `time-check-report/v0`, and `time-pack/v0`
2. one std pilot distinguishing monotonic measurement from wall-clock capture
3. one Jiff / timezone-aware pilot with DST gap/fold vectors
4. one storage/wire pilot covering RFC 3339 / Unix timestamp / SQL round-trips
5. one localized calendar/rendering pilot using ICU4X or `jiff-icu`
6. one fake-clock / deterministic-test pilot
7. docs and CI that make zone loss, precision loss, locale assumptions, and clock behavior visible

The winning version is compact, semantic, and boundary-aware.
It should make temporal semantics legible together rather than canonizing one crate family.

## Initial pilots
- **Clock lane** — distinguish elapsed timing from wall-clock capture explicitly
- **Zone lane** — publish DST gap/fold and tzdb-source semantics honestly
- **Persistence lane** — show exactly what SQL / Serde / HTTP / log forms retain or lose
- **Localization lane** — show when ICU/calendar/locale data is required for user-facing rendering
- **Fake-clock lane** — make runtime-controlled paused/advanced time explicit before replay/test consumers overclaim it
- **Migration lane** — record semantic differences when moving between Chrono / `time` / Jiff / ICU-backed forms

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document clock, zone, calendar/locale, storage, and evidence vocabulary
2. **v0.2 zone + storage pilots**
   - ship at least one DST-aware pilot and one SQL/wire round-trip pilot
   - show how lossy and lossless lanes differ in artifacts
3. **v0.3 localization + fake-clock depth**
   - add localized rendering and deterministic-test evidence
   - capture host-dependent vs embedded-data differences explicitly
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one identical time stack

## Success metrics
- Library authors can review clock, zone, calendar, and storage assumptions without reconstructing them from type aliases and docs.
- Applications can distinguish user-facing civil time from protocol timestamps and elapsed measurements.
- Migrations between Chrono / `time` / Jiff / ICU-backed lanes become diffable instead of surprising.
- DB / protocol / analytics integrations can publish what zone/calendar/precision information is preserved or lost.
- Deterministic-test and fake-clock support becomes an attachable capability instead of a hidden test-only convenience.

## Archive fit
This proposal fills a real gap in the archive:
- **Runtime Capability Kit** handles clock authority as a capability,
- **Background Work Kit** handles durable job / schedule execution,
- **Localization Surface Kit** handles broader message and locale workflows,
- **Dataset Surface Kit** handles table / columnar data contracts,
- **Replay Kit** handles deterministic replay infrastructure.

But none of those is the portable contract for **clock kind, zoned/civil semantics, locale/calendar rendering, storage/wire mappings, and attachable temporal evidence**.
Time Surface Kit is the missing substrate above Rust’s increasingly fragmented and increasingly important time ecosystem.
