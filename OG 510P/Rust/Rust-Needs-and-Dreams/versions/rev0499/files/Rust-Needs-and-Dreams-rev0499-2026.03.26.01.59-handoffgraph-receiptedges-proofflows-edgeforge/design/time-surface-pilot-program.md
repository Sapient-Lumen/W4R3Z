# Design: Time Surface Pilot Program

## Goal
Turn Time Surface Kit from a good conceptual map into a **ranked execution plan**.

Rust already has enough time machinery to prove the gap is real.
The next step is not more crate accumulation.
It is a pilot sequence that shows Rust projects can publish **reviewable temporal truth** across monotonic clocks, wall clocks, civil/offset forms, zoned DST-aware values, localized calendars, storage adapters, and fake clocks without pretending those lanes have already converged.

Read this together with:
- [`design/time-surface-kit.md`](./time-surface-kit.md)
- [`design/time-surface-lane-map.md`](./time-surface-lane-map.md)
- [`design/background-work-kit.md`](./background-work-kit.md)
- [`design/localization-surface-kit.md`](./localization-surface-kit.md)
- [`proposals/epic-time-surface-kit.md`](../proposals/epic-time-surface-kit.md)

## Why this needs its own design layer
The Time Surface Kit already defines the artifact family: surface/profile/vector/check/pack artifacts.

What it did **not** yet answer clearly enough is:
- which temporal lanes should be piloted first,
- which distinctions are worth locking in early,
- how to keep wall-clock capture separate from elapsed timing,
- how to keep zoned/DST semantics separate from localization/rendering semantics,
- how to keep storage adapters separate from core temporal models,
- and what counts as pilot success versus another datetime comparison blog post.

Without that layer, time-surface work risks two bad outcomes:
1. **temporal flattening** — the archive starts implying all time crates differ only in ergonomics or syntax;
2. **adapter theater** — one successful parse, SQL round-trip, or localized formatter demo impersonates evidence for broader clock, zone, or DST claims.

## Design principles
1. **Start from exact lane identity.** Every pilot should say which temporal lane it is proving.
2. **Keep clocks separate from datetimes.** Monotonic measurement, wall time, and human-facing datetimes are related but not interchangeable.
3. **Keep zoned semantics separate from localization.** DST-aware arithmetic and locale-aware rendering are adjacent, not identical.
4. **Treat tzdb source as public contract.** System, embedded, build-generated, and application-provided databases are not one posture.
5. **Treat storage and migration as their own lane.** Adapters are where semantic loss usually appears.
6. **Treat fake clocks as first-class.** Runtime-controlled or paused clocks are public testing behavior, not hidden implementation details.
7. **Prefer vectors that reveal lossiness.** DST gaps/folds, wall-versus-monotonic drift, locale fallback, precision loss, and adapter truncation matter more than feature matrices.
8. **Consumer handoffs must stay bounded.** Schedulers, DB layers, support docs, and migration guides should only claim the time-lane facts actually exported.

## Artifact family
### 1. `time-pilot-brief/v0`
Why this temporal lane is being piloted.

Should record:
- pilot id and summary
- lane family (`monotonic`, `wall-clock`, `civil-offset`, `zoned`, `localized`, `storage-adapter`, `fake-clock`, `migration`)
- why the lane matters now
- intended consumer(s)
- why the lane is tractable now

### 2. `time-lane-profile/v0`
The declared contract for the lane.

Should record:
- primary crate/type family
- clock or datetime posture
- tzdb/calendar/locale dependencies if relevant
- parse/format/storage assumptions
- ambiguity and precision rules
- adapter/lossiness notes
- explicit unsupported areas

### 3. `time-query-budget/v0`
The bounded questions the pilot must answer.

Should record:
- named semantic questions in scope
- required answer fields
- required uncertainty classes
- mandatory vector coverage
- explicit out-of-scope questions

### 4. `time-consumer-handoff/v0`
How a downstream consumer may reuse the pilot.

Should record:
- consumer class (`scheduler-review`, `db-review`, `protocol-review`, `localization-review`, `test-review`, `migration-review`, `support`)
- which artifacts are consumed directly
- which claims remain advisory only
- what the consumer must still verify independently

### 5. `time-pilot-scorecard/v0`
Decides whether widening is justified.

Should ask:
- did the pilot preserve lane identity honestly?
- did it make lossy adapters explicit?
- did it attach concrete vectors and reports?
- did at least one real consumer import it?
- did it avoid claiming universal time truth?

### 6. `time-pilot-pack/v0`
Bundle of:
- pilot brief
- lane profile
- query budget
- consumer handoff
- time-surface artifacts from the base kit
- scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Monotonic-versus-wall clock truth lane
**Why first**
- Std already provides the sharpest possible split between `Instant` and `SystemTime`.
- This pilot creates the baseline rule that elapsed timing and external timestamps must not be flattened.

**Primary artifacts**
- `time-surface/v0`
- `clock-kind-profile/v0`
- vectors for monotonic saturation/overflow behavior, epoch conversion, external timestamp comparison, and drift/error posture

**Primary consumers**
- retry/timeout reviewers
- protocol/logging consumers
- support and docs consumers

### 2) Zoned / DST / tzdb-source lane
**Why second**
- This is where real semantic divergence appears fastest.
- Jiff, Chrono, and Chrono-TZ already prove that zoned time involves database source, ambiguity policy, and local-zone discovery choices.

**Primary artifacts**
- `civil-zone-profile/v0`
- `time-adapter-profile/v0`
- vectors for DST gaps/folds, local-zone discovery, tzdb freshness assumptions, and zone-retention loss

**Primary consumers**
- scheduling reviewers
- migration reviewers
- support consumers

### 3) Civil / offset / wire-format lane
**Why third**
- Protocols and persisted payloads often need offset/civil forms without importing full zone logic.
- The `time` crate already gives strong evidence for explicit formatting/parsing and human-readable/binary serde distinctions.

**Primary artifacts**
- `civil-zone-profile/v0`
- `time-storage-profile/v0`
- vectors for parse/format round-trips, precision/truncation, human-readable versus binary serialization, and local-offset acquisition posture

**Primary consumers**
- protocol reviewers
- API/library maintainers
- docs and support consumers

### 4) Storage / adapter lane
**Why fourth**
- This lane proves whether the archive can talk honestly about what survives persistence and transport.
- `jiff-sqlx` is already explicit that a separate bridge exists because trait placement and dependency layering matter.

**Primary artifacts**
- `time-storage-profile/v0`
- `time-adapter-profile/v0`
- `time-check-report/v0`
- vectors for SQL, serde, log, and HTTP-style representations plus retained-versus-lost semantics

**Primary consumers**
- database reviewers
- analytics/platform consumers
- migration consumers

### 5) Localized calendar / locale-rendering lane
**Why fifth**
- This lane should arrive only after non-localized temporal semantics are already explicit.
- ICU4X and `jiff-icu` already provide enough substrate to prove locale, calendar, and zone-display claims separately.

**Primary artifacts**
- `calendar-locale-profile/v0`
- `time-adapter-profile/v0`
- vectors for locale negotiation, calendar selection, zone-name rendering, and fallback behavior

**Primary consumers**
- UI/product reviewers
- localization teams
- docs/support consumers

### 6) Deterministic / fake-clock lane
**Why sixth**
- This lane is powerful but easy to overclaim.
- Tokio's docs already show that pausing and advancing time is runtime-scoped and comes with auto-advance and timer-processing caveats.

**Primary artifacts**
- `clock-kind-profile/v0`
- `time-vector-set/v0`
- `time-check-report/v0`
- vectors for pause, advance, auto-advance boundaries, blocking-I/O caveats, and timeout behavior under a controlled clock

**Primary consumers**
- test/replay reviewers
- async/runtime consumers
- incident/debug consumers

### 7) Migration lane
**Why seventh**
- This lane becomes credible only after the other lanes are individually legible.
- Current maintenance signals make it timely, but migration guidance should import real lane artifacts rather than guess from crate names.

**Primary artifacts**
- `time-adapter-profile/v0`
- `time-consumer-handoff/v0`
- vectors for Chrono → Jiff, Chrono-TZ → Jiff, and `time` ↔ Jiff semantic deltas where possible

**Primary consumers**
- maintainers planning upgrades
- ecosystem atlas/adoption consumers
- support/documentation consumers

## Graduation criteria
A time-surface pilot should graduate only when it has:
1. an explicit pilot brief;
2. a lane profile naming the temporal lane under review;
3. a bounded query budget with named vectors;
4. at least one consumer-handoff artifact;
5. concrete check reports or attached evidence;
6. a scorecard showing the pilot remained lane-specific and did not claim universal time truth.

## Anti-goals
- one giant temporal manifest that erases clocks, civil values, zoned values, localization, storage, and fake-clock differences;
- narrating every datetime crate as a semantic superset of the others;
- using one parse/format or SQL demo as proof of DST or scheduling correctness;
- treating locale rendering as a cosmetic layer over protocol formatting;
- widening to background-work or replay megastacks before the time lanes are individually explicit.

## Why this is an ecosystem contribution
Rust already has strong temporal libraries.
What it still lacks is a compact, reviewable way to say **which time lane a public surface actually occupies, what evidence checked it, and how much downstream consumers may safely infer**.

That is a better contribution than yet another crate claiming to solve time once and for all.
