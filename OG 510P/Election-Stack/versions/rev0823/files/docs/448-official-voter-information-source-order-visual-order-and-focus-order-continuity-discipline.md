# 448 — Official voter-information source order, visual order, and focus-order continuity discipline

**Track:** Shared / Public surfaces

This document defines a bounded control for **official voter-information routes whose meaning depends on people encountering repeated blocks, featured answers, cards, action lanes, or grouped controls in a coherent order across visual layout, source order, and keyboard focus travel**.

It does **not** replace the underlying voter-question families in `292–343`.
It does **not** replace:
- `416`, which governs reflow, text scaling, and small-viewport survival,
- `417`, which governs keyboard navigation, focus visibility, and logical order,
- `418`, which governs screen-reader semantics, landmarks, labels, and live updates,
- `421`, which governs touch targets, hover-revealed content, and pointer operability,
- `442`, which governs section anchors and in-page navigation,
- `445`, which governs tabbed answer lanes and hidden-panel findability,
- `446`, which governs answer-bearing data tables and row/cell findability,
- or `447`, which governs card/collection disambiguation and answer-tile clarity.

It adds one narrow rule:
**if an official voter-information route changes the apparent order or priority of answer-bearing content through flex/grid placement, reversal, featured-slot promotion, or other layout reordering, the route should not let the visual order, source order, and focus order diverge enough that users encounter the official answer in different sequences depending on how they navigate.**

## Why this is a distinct surface

W3C’s current WCAG understanding guidance for **Meaningful Sequence** says that when presentation order affects meaning, there should be a programmatically determinable sequence that still makes sense. Its current **Focus Order** understanding guidance points maintainers to techniques that keep interactive elements in an order that follows sequences and relationships in the content. W3C’s current technique **C27** says authors should keep DOM order aligned with visual order because users of screen readers, magnifiers, and keyboards can be confused when those orders diverge. Its current technique **G59** says interactive elements should receive focus in an order that follows the sequences and relationships in the content. MDN’s current grid-accessibility guidance says visual reordering with grid does not change speech or tab order and cites the specification warning that authors should use these features only for visual, not logical, reordering. MDN’s current flexbox-ordering guidance likewise says `row-reverse`, `column-reverse`, and `order` change only the visual presentation while tabbing order and speech order continue to follow source. USWDS’s current layout-grid guidance matters because the grid system is mobile-first and powered by flexbox, while USWDS’s current order-token guidance makes explicit that teams can set the order of items in a flex container. (xref: `w3c_wcag22_meaningful_sequence_page`; xref: `w3c_wcag21_focus_order_page`; xref: `w3c_wcag21_c27_dom_order_visual_order_page`; xref: `w3c_wcag21_g59_interactive_elements_order_page`; xref: `mdn_css_grid_accessibility_page`; xref: `mdn_ordering_flex_items_page`; xref: `uswds_layout_grid_page`; xref: `uswds_order_tokens_page`)

That is enough to justify a compact control here.
A route may pass adjacent controls and still fail the public because:
- a “featured” answer card is moved visually to the top while its link remains late in source/focus order,
- a narrow layout stacks cards in one order while desktop visually promotes a different answer lane,
- a flex `row-reverse` or custom `order` utility makes a deadline-critical CTA appear first while keyboard and speech users still encounter it last,
- or a multi-column route looks orderly to a sighted mouse user while keyboard, magnifier, and assistive-technology users traverse the same content in a materially different sequence.

## This is not the same thing as card clarity, keyboard support, or screen-reader semantics

`447` asks whether repeated cards or tiles are distinct enough that users can tell which item controls.

`417` asks whether keyboard interaction and focus visibility are operable and intelligible.

`418` asks whether screen-reader semantics, labels, landmarks, and announcements remain sound.

`448` asks a different question:
**when the route’s layout system changes the apparent order of answer-bearing content, do visual order, source order, and focus travel remain coherent enough that the controlling official answer is encountered in the same meaningful sequence?**

A route may pass the earlier controls and still fail `448` if:
- every card has a good label, but CSS promotion makes the “current” card look first while DOM/focus order still hits it fourth,
- keyboard focus is visible on every element, but focus jumps through cards in an order that contradicts the page’s visual grouping,
- screen-reader labels are accurate, but the underlying source order presents the answer lane in a different sequence from the visual layout,
- or a responsive grid preserves all content while silently changing which answer lane appears topmost or adjacent to the governing heading.

## Sequence coherence matters whenever layout implies priority

This archive should treat sequence as part of the public answer surface whenever a route relies on:
- featured cards, “start here” tiles, or promoted action blocks,
- desktop-first sidebars that collapse above or below the main answer on smaller screens,
- flex/grid reversal or explicit order utilities,
- grouped office/contact/deadline lanes whose left-to-right or top-to-bottom arrangement implies recommendation or urgency,
- or component systems where visual placement is easier to change than source structure.

In those cases, the office should not assume that the visual arrangement is the answer.
If sequence carries meaning, then the meaningful sequence has to survive across the route’s actual navigation modes.

## Featured answers are especially risky when source order lags behind

A common failure mode is a route that visually promotes one answer block — for example, “Vote today,” “Use this office,” “Current deadline,” or “Important status update” — while leaving the promoted block late in DOM order because it was easier to move with CSS than to change the underlying markup.

That is a bounded public-surface problem because:
- sighted mouse users may see the promoted answer first,
- keyboard users may tab to it only after traversing less important cards,
- screen-reader users may hear it in a different sequence from the visible page,
- and magnifier users may experience focus travel that appears to jump unpredictably around the screen.

When the route relies on a featured answer lane, the archive should expect the office to review whether the featured placement is merely cosmetic or whether the meaningful sequence itself has drifted.

## Responsive wrapping and reversal can silently rewrite the perceived scan path

USWDS’s current grid guidance, MDN’s current grid-accessibility guidance, and MDN’s current flex-ordering guidance together matter because official public routes are often laid out with responsive flex/grid systems whose wrapping, reversal, or explicit order classes can make desktop and mobile users perceive different priorities from the same markup. (xref: `uswds_layout_grid_page`; xref: `mdn_css_grid_accessibility_page`; xref: `mdn_ordering_flex_items_page`)

For this archive, that means a route should review not only whether content survives on narrow screens, but also whether the **answer sequence** still makes sense when:
- two columns become one,
- a sidebar drops below the main content,
- a featured card moves from first visual position to later stacked position,
- a reverse-direction layout is used to “fix” presentation,
- or explicit `order` values are used to reposition items without changing the source.

## What the office should be able to say publicly

For a bounded public record, an office should be able to say:
- whether the route uses any flex/grid/order-based visual reordering at all,
- which answer-bearing blocks are sequence-sensitive,
- whether featured/promoted blocks remain early enough in source and focus order to match their apparent priority,
- whether desktop and narrow layouts were reviewed for sequence drift,
- and whether the office intentionally avoided logical meaning that exists only in visual placement.

The archive does **not** need individualized tab traces, screen recordings of named users, or exhaustive telemetry to support this claim.
It needs a compact statement that the sequence-sensitive route was checked and that the meaningful order stayed coherent.

## Evidence posture and recommended digests

This surface should stay **digest-first** and route-bounded.
Good public evidence is a compact posture statement plus any necessary cross-reference to the adjacent card/tab/table/reflow controls.

Recommended digest names:
- **Sequence Continuity Surface Digest (SCSD):** digest of the bounded source/visual/focus sequence posture for the route.
- **Featured Order Review Digest (FORD):** optional digest for routes that promote one answer lane or “start here” card above peers.
- **Responsive Sequence Drift Digest (RSDD):** optional digest for routes whose stacked/wrapped layouts required explicit review.

## What belongs in the public scan-order payload

Keep the payload **small, route-aware, and sequence-focused**.

Recommended top-level fields:
- stable `surface_id`
- `jurisdiction_id` / election scope
- `scan_order_surface_label`
- `delivery_role_note`
- `covered_surface_refs[]`
- `official_source_anchors[]`
- `reviewed_route_variants[]`
- `source_vs_visual_order_note`
- `focus_order_note`
- `featured_or_promoted_block_note`
- `layout_reordering_controls_note`
- `narrow_layout_sequence_note`
- `help_or_overview_escape_note`
- `last_verified_at`
- supersedes / superseded-by pointers

Do **not** publish by default:
- named-user keyboard traces,
- raw session replay,
- individualized assistive-technology recordings,
- exhaustive DOM snapshots for every breakpoint,
- or speculative UX interpretation beyond the bounded sequence question.

## Verification questions for third parties

A verifier, journalist, observer, or court should be able to answer:
- Did the office identify whether this route uses visual reordering, reversal, or featured promotion that affects answer sequence?
- If one answer lane appears visually first or “recommended,” is it encountered in a coherent place in source order and focus travel too?
- Did the office review both desktop and narrow layouts for sequence drift rather than only checking that content still exists?
- Are adjacent controls (`447`, `445`, `446`, `417`, `418`) enough here, or is there a distinct source/visual/focus order problem that required its own bounded review?
- Did the office preserve a compact public record of sequence review without retaining individualized browsing exhaust?

## How this fits the family map

Source order, visual order, and focus-order continuity is **not** a new underlying voter-question family bucket.
It is a delivery-layer control over official routes that already answer substantive voter questions elsewhere in the stack.

This document only says that, if an official voter-information route uses layout or promotion choices that change the apparent order of answer-bearing content, the route should keep source order, visible order, and focus travel coherent enough that the public does not receive different answer sequences depending on navigation mode.

## Minimal artifacts in this archive

- Template payload: `artifacts/templates/official-voter-information-scan-order-surface-payload.json`
- Operator checklist: `artifacts/checklists/official-voter-information-scan-order-surface-checklist.md`

## Sources (pinned IDs / lockfile IDs)

- W3C WAI: Understanding SC 1.3.2 Meaningful Sequence (xref: `w3c_wcag22_meaningful_sequence_page`)
- W3C WAI: Understanding SC 2.4.3 Focus Order (xref: `w3c_wcag21_focus_order_page`)
- W3C WAI Technique C27: DOM order matches visual order (xref: `w3c_wcag21_c27_dom_order_visual_order_page`)
- W3C WAI Technique G59: interactive elements follow content sequence (xref: `w3c_wcag21_g59_interactive_elements_order_page`)
- MDN: Grid layout and accessibility (xref: `mdn_css_grid_accessibility_page`)
- MDN: Ordering flex items (xref: `mdn_ordering_flex_items_page`)
- USWDS: Layout grid (xref: `uswds_layout_grid_page`)
- USWDS: Order tokens (xref: `uswds_order_tokens_page`)
