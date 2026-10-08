# rev0082 refactor audit

The population frontier now separates three concepts that were previously easy to conflate:

1. `population_column_frontier_rows`: does any current counter answer a named threat column under familywise lower bounds?
2. `population_column_rescue_rows`: if not, is the failure certification-limited, mean-below but still upper-bound-rescuable, or current-counter-set deficient even by upper bound?
3. `summarize_population_column_rescue`: records the rescue distribution by hierarchy layer and threat axis.

This is a code-level refactor, not a new doctrine registry. It makes the next experimental choice executable: sample more only where an existing counter's mean/upper envelope justifies it; invent or repair policy where even the upper envelope is below the floor.

No new raw transition tables or replay traces were shipped. The audit consumes the compact rev0081 frontier table.
