# 420 — Official voter-information motion, animation, auto-advancing content, and interruption-safe fail-open discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes that must remain readable and usable when a voter is distracted, motion-sensitive, vestibular-sensitive, cognitively overloaded, or simply trying to read the current answer without the page sliding, shimmering, counting down, auto-rotating, scrolling away, or otherwise moving under them**:
reduced-motion handling,
auto-moving content controls,
non-essential interaction-triggered animation limits,
and a still, user-controllable answer/help lane for urgent public information.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `305`, which governs the authoritative office/help route,
- `403`, which governs progressive-enhancement and JS-dependency survival,
- `404`, which governs cache freshness and stale-answer eviction,
- `408`, which governs overload/queue-page degraded-answer continuity,
- `417`, which governs keyboard navigation and visible focus,
- `418`, which governs nonvisual structure and announced updates,
- or `419`, which governs contrast, non-color cues, and visible state legibility.

It adds one narrow rule:
**if an official voter-information page uses motion or automatic change to present status, urgency, or attention cues, the office should keep the current first-party answer/help lane stable enough to read, should honor reduced-motion preferences for non-essential movement, and should not make pause/stop/manual control the voter’s burden only after the page has already started moving.**

## Why this is a distinct surface

The EAC’s current **Effective Design for the Administration of Federal Elections** treats online voter-information materials as a core election responsibility and says election materials should be clear, understandable, accessible, and usable. Digital.gov’s current digital-first public-experience requirements say public websites and digital services should be accessible to people of diverse abilities. W3C’s current understanding guidance for **Pause, Stop, Hide** says moving, blinking, scrolling, and auto-updating visual content that starts automatically is the core concern of that criterion. W3C’s current understanding guidance for **Animation from Interactions** says some users experience distraction or nausea from animated content, distinguishes automatic animation from interaction-triggered animation, and says teams can avoid unnecessary animation, provide a way to turn off non-essential animation, or use reduced-motion preferences. MDN’s current `prefers-reduced-motion` reference says the media feature exists to detect whether a user has enabled a device setting to minimize non-essential motion and that interfaces can remove, reduce, or replace motion-based animations accordingly. WAI’s current carousel-authoring example says auto-rotation should pause on reduced-motion preference, focus, or hover and remain manually controllable with a visible start/stop control. (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`; xref: `digital_gov_requirements_digital_first_public_experience_page`; xref: `w3c_wcag21_pause_stop_hide_page`; xref: `w3c_wcag21_animation_from_interactions_page`; xref: `mdn_prefers_reduced_motion_media_feature_page`; xref: `w3c_wai_aria_apg_carousel_tablist_example_page`)

That is enough to justify a compact control here.
A page can be current, fast enough, keyboard reachable, screen-reader understandable, and visually legible, yet still fail first contact because the answer is embedded in a rotating hero, the warning banner keeps sliding, the status panel auto-refreshes and jumps, the map pans/parallaxes during scrolling, the countdown pulses or flips continuously, or a skeleton/shimmer placeholder keeps moving while the actual answer remains hard to hold in view.

## This is not the same thing as freshness or screen-reader review

`404` asks whether the page is serving the **current** official answer instead of stale cached state.

`418` asks whether changes, labels, structure, and status are understandable nonvisually.

`420` asks a different question:
**even when the content is current and technically announced, can a voter read and act on it without automatic motion, auto-advancing content, or interaction-triggered animation making the answer lane physically uncomfortable, distracting, or unstable?**

A route may pass `404` and `418` and still fail `420` if:
- the urgent notice rotates away before an ordinary reader can finish it,
- a countdown or animated progress strip is the main urgency cue,
- scroll-linked or parallax effects move surrounding content in non-essential ways,
- lookup results or cards animate dramatically on every keystroke or state change,
- or auto-updating panels interrupt reading without an obvious pause, stop, or stable summary path.

## Motion is allowed; motion-critical meaning is not

This document does **not** ban all animation.
It bans dependence on non-essential motion or automatic change **as the price of safely reading the answer**.

For this archive, that means:
- keep motion as optional polish rather than the only carrier of urgency or state,
- give users a stable way to read the authoritative answer without racing a carousel, ticker, shimmering placeholder, or moving map,
- honor reduced-motion preferences for non-essential movement,
- and make the default public-answer path manually controllable whenever automatic motion would otherwise compete with comprehension.

This matters especially for election pages where teams may use animation to imply “new,” “urgent,” “happening now,” “refreshing,” or “look here first.”
Those meanings need a stable text summary and a controllable presentation path.

## Auto-updating content is an integrity problem when it interrupts reading

Election instructions often contain deadline-sensitive state:
site hours,
queue advisories,
status updates,
registration deadlines,
mail-ballot cure windows,
or polling-place changes.

The practical rule here is simple:
- if content updates automatically, keep the current answer lane readable long enough to understand,
- do not replace the entire answer lane with motion-first “live” theater,
- and preserve a stable, current text summary plus a visible office/help fallback.

This does not demand zero live behavior.
It demands that live behavior not turn “current” information into an unstable reading target.

## Pause, stop, hide, or disable should be obvious when movement starts automatically

For this archive, `420` should explicitly review:
- carousels, rotating notices, hero banners, and slide shows,
- scrolling tickers, marquees, pulsing warning treatments, and animated countdowns,
- skeletons, shimmer loaders, and looping placeholders that occupy the answer lane,
- scroll-linked or interaction-triggered non-essential motion,
- map/list synchronization that moves or re-centers unexpectedly,
- and auto-refresh/update patterns that shift focus or replace visible content while a voter is reading.

When automatic movement exists, the route should expose an obvious manual control or a still-by-default path rather than assuming every voter can tolerate or out-read the motion.

## Keep the same authoritative answer across motion variants

Reduced-motion variants, paused carousels, static snapshots, or no-animation modes MAY change presentation.
They should **not** silently change the underlying authoritative answer or hide warnings, deadlines, or fallback instructions that remain visible only in the animated/default rendering.

This composes directly with `406`.
Different presentation variants may justify different visual behaviors.
They do **not** justify answer drift.

## Minimal motion-state taxonomy

A small taxonomy is enough:

1. **Reduced-motion preference state** — non-essential motion respects user/device reduced-motion preference.
2. **Auto-moving content control state** — automatically moving, blinking, scrolling, or auto-updating content can be paused, stopped, hidden, or disabled where needed.
3. **Interaction-triggered motion state** — non-essential animation started by scrolling, hovering, focusing, filtering, or other interaction can be suppressed or reduced.
4. **Stable answer-lane state** — the current official answer/help lane remains readable without racing movement or repeated layout shifts.
5. **Interruption-safe update state** — live or auto-updating content does not replace or destabilize the answer while the voter is reading.
6. **Visual answer lane available without motion** — the current official answer/help route remains materially understandable in a still, user-controllable presentation.

## Preserve bounded reconstruction, not user-condition telemetry

What matters here is bounded reconstruction of the office’s motion-safety posture:
- which critical routes were reviewed,
- whether reduced-motion handling was checked,
- whether auto-moving content had visible pause/stop/manual controls,
- whether interaction-triggered motion stayed non-essential,
- whether the answer lane remained stable during updates,
- and when the route was last reviewed.

Do **not** preserve individualized medical or disability inferences, motion-sensitivity guesses, raw gaze/session telemetry, or exhaustive video capture of every rendering path when bounded public-answer reconstruction is sufficient.

## Suggested payload fields

The payload for this surface can stay small.
Suggested fields include:

- `surface_id`
- `jurisdiction_id`
- `motion_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `critical_answer_routes[]`
- `reviewed_motion_state_paths[]`
- `reduced_motion_preference_note`
- `auto_moving_content_control_note`
- `interaction_triggered_motion_note`
- `stable_answer_lane_note`
- `auto_update_and_interruption_note`
- `countdown_timer_and_urgency_presentation_note`
- `carousel_marquee_and_rotating_notice_note`
- `same_answer_across_motion_variants_note`
- `motion_state_classes[]`
- `motion_trace_policy{}`
- `routing_fallback_uri`
- `routing_fallback_phone`
- `latest_notice_uri`
- `last_verified_at`
- `supersedes`
- `superseded_by`

## Verification prompts that fit this surface

- Can a voter read the current answer/help lane without it rotating, shimmering, scrolling away, or repeatedly re-centering itself?
- If content starts moving automatically, is there an obvious pause, stop, hide, or still/manual path?
- Does the route honor reduced-motion preference for non-essential movement?
- Are countdowns, live indicators, and urgency cues still understandable as stable text or labels rather than motion-only emphasis?
- Do interaction-triggered animations stay non-essential, and can they be reduced or disabled when needed?
- If the main route becomes distracting or unstable, is there still a plainly visible first-party office/help fallback?

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-motion-surface-payload.json`
- Operator quickcheck: `artifacts/checklists/official-voter-information-motion-surface-checklist.md`

## Sources to keep pinned

Keep the lockfile entries for:
- EAC: Effective Design for the Administration of Federal Elections (xref: `eac_effective_design_for_the_administration_of_federal_elections_page`)
- Digital.gov: Requirements for a digital-first public experience (xref: `digital_gov_requirements_digital_first_public_experience_page`)
- W3C WAI: Understanding SC 2.2.2 Pause, Stop, Hide (xref: `w3c_wcag21_pause_stop_hide_page`)
- W3C WAI: Understanding SC 2.3.3 Animation from Interactions (xref: `w3c_wcag21_animation_from_interactions_page`)
- MDN: `prefers-reduced-motion` media feature (xref: `mdn_prefers_reduced_motion_media_feature_page`)
- WAI-ARIA APG: Carousel example with slide controls (xref: `w3c_wai_aria_apg_carousel_tablist_example_page`)
