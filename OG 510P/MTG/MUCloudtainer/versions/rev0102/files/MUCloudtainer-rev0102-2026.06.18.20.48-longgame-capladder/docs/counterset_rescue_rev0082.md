# rev0082 counter-set rescue envelope

rev0081 showed that every threat-column frontier failed its familywise lower-bound answer test. The remaining risk was interpretive: a failed frontier could mean either that more seed-disjoint evidence might certify an existing counter, or that the current two-counter population is too narrow even under optimistic upper bounds.

rev0082 classifies each of the 36 rev0081 threat-column rows with a rescue label:

- `certification_limited_existing_counter_candidate`: the best existing counter has mean score at or above 0.50, but the familywise lower bound is still below 0.50.
- `mean_below_threshold_but_upper_bound_allows_rescue`: the best existing counter's point estimate is below 0.50, but the upper bound still leaves possible rescue.
- `current_counter_set_deficient_even_by_upper_bound`: even the best existing counter's upper bound is below 0.50, so another policy/deck repair should outrank more sampling for that cell.

Results: 0 rows certify an existing counter, 21 are certification-limited, 14 are below-mean but upper-bound-rescuable, and 1 fine cell is current-counter-set-deficient even by upper bound. The deficient cell is the by-size/life `counter40_vs_threat40`, starting-life 20, library-aware closure threat column. Mandatory global/by-life/by-size layers are not yet upper-bound-impossible; they remain failed, but the next work should separate targeted counter-policy invention from brute-force sampling.
