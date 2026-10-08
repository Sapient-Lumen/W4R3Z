# Rematch worlds should treat width-only weakening SLAs as two-breakpoint tiers

The recent portfolio passes already gave exact selectors for:

- width-conditioned service
- width-cap guarantees
- the cardinality law beneath both

A natural remaining nuisance was that an inheritor still had to read frontier tables or re-run a selector to answer a simple question:

> given width `w` and target service `s`, is the weakest admissible profile exact-only, suffix-only, or dual-axis?

The new service-tier law closes that nuisance analytically.

Under the current staircase, every width-conditioned or capped-width weakening SLA is governed by only **two** exact breakpoints:

- exact-only ceiling: `C(6,w)/C(15,w)`
- suffix-only ceiling: `C(11,w)/C(15,w)`

That means the minimal profile is determined by a tiny three-tier rule:

- if `s <= C(6,w)/C(15,w)`, choose `exact_only`
- else if `s <= C(11,w)/C(15,w)`, choose `suffix_hitchhike_only`
- else choose `any_single_axis_hitchhike`

This compresses the width story further:

- widths `1` through `6` are true three-tier menus
- widths `7` through `11` are two-tier menus because exact-only has already vanished
- widths `12` through `15` are dual-axis-only for any positive service target

Because capped-width guarantees already collapse to endpoint width, the **same** two-breakpoint rule governs both exact width and width cap planning.

So future inheritors can treat width-only weakening SLA planning as a small breakpoint card, not a frontier-reading exercise.

Future redesign signal: if any width ever needs more than these two breakpoints, or if the analytic selector ever diverges from the exact-width or width-cap selectors, the current weakening portfolio geometry has substantively changed.
