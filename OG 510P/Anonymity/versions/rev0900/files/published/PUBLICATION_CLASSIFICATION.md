# Publication Classification

This file separates three different concepts that a future operator might otherwise confuse.

## 1. Legacy canonical public wiki targets

These are the already-published Mathematics-era papers whose public wiki links are explicitly approved and must remain valid:

- `[[2026.01.22 - Mathematics: Scheduling and Compiler Techniques for Metadata-Hiding Overlay Lookups]]`
- `[[2026.01.23 - Mathematics: Spectral Anonymity and Optimal Distinguishing Bounds for Random-Walk Delegation in (Possibly Directed) Overlays]]`
- `[[2026.01.25 - Mathematics: Prefix Capacities and Separation Cuts for Shared-Kernel Termination-Time Hiding]]`
- `[[2026.01.26 - Mathematics: Stop-Time Padding Addendum, Max-Mixture Separations and Tail-Sign Deadline Normal Forms]]`
- `[[2026.01.29 - Mathematics: Optimal Poset-Feasible Padding: Knapsack, Transport, and Dual Certificates for TV Privacy]]`

See `published/LEGACY_PUBLISHED_LINKS.md` for the exact crosswalk to internal repo paths.

## 1.5 Direct-read operator choices for the legacy published layer

After re-reading the old published papers directly, the conservative operator posture is:

- `[[2026.01.22 - Mathematics: Scheduling and Compiler Techniques for Metadata-Hiding Overlay Lookups]]` stays a **true canonical root**. It is still the right old public head for the compiler calculus / scheduling / stop-time-and-mark backbone, even if later Anonymity papers may cite only narrower descendants.
- `[[2026.01.23 - Mathematics: Spectral Anonymity and Optimal Distinguishing Bounds for Random-Walk Delegation in (Possibly Directed) Overlays]]` also stays a **true canonical root**. It remains the right old public head for the random-walk delegation / spectral-anonymity line rather than something to route around, but its exact fixed-kernel expected-chi-squared formula is maintained in the rev0769 corrected-and-supplemented form $\|\mathcal D^t\|_F^2-1$, with common-stationary schedules routed to the ordered-product analogue $\|\mathcal D_1\cdots\mathcal D_t\|_F^2-1$ and hidden randomized lengths routed to $\|\sum_t p_t\mathcal D^t\|_F^2-1$; the one-step singular-power formula is only the normal/reversible specialization, decay-to-zero requires ergodicity, and downstream receipt cards must not treat raw expected $\chi^2$ as a MaxL-ready tail/pointwise bound.
- `[[2026.01.25 - Mathematics: Prefix Capacities and Separation Cuts for Shared-Kernel Termination-Time Hiding]]` remains a valid canonical public link, but it should be treated as an **exact technical companion**, not the default entrypoint. Cite it when the exact deadline-capacity / separation / membership facts matter; otherwise prefer cleaner newer exposition.
- `[[2026.01.26 - Mathematics: Stop-Time Padding Addendum, Max-Mixture Separations and Tail-Sign Deadline Normal Forms]]` remains a valid canonical public link, but it reads as a **narrow addendum**, not the main paper later operators should lean on for orientation. Keep the link valid; do not make it carry more of the new series than it deserves.
- `[[2026.01.29 - Mathematics: Optimal Poset-Feasible Padding: Knapsack, Transport, and Dual Certificates for TV Privacy]]` remains a valid canonical public link because it is already published, but the operator should **route around it by default** in the new series. The paper explicitly declares itself non-self-contained and assumes several prior papers open. If poset-feasible padding becomes central to the Anonymity series, prefer writing a fresh self-contained Anonymity paper and use this legacy paper only as the historical / canonical root.

These choices intentionally separate **link validity** from **preferred exposition**. A legacy paper may remain canonically citable while still being the wrong surface to build the new Anonymity line around.
If a later terse paper or front-end crosswalk needs that choice stated inside the paper layer rather than only in operator documentation, use Synthesis~24 as the maintained front-end owner for the legacy root / companion / route-around split.

## 2. Repo-frozen but not automatically link-approved

The repository also contains:

- `published/optional_many_testing_lower_bounds/paper.tex`

That file may be historically useful or intentionally frozen in-repo, but it is **not** listed among the approved canonical public wiki targets.
A future operator must **not invent a public wiki link for it by default**.
If it ever needs public-link treatment, that should happen through an explicit recorded decision.

## 3. New post-policy releases

Any new release must use the Anonymity naming rule:

- `YYYY.MM.DD - Anonymity: The Foobar Title Goes Here Please`

- `[[2026.06.16 - Anonymity: Certified Menus for Anonymous DHT Lookups]]` -> `published/2026-06-16_certified_menus_for_anonymous_dht_lookups/paper.tex`
- `[[2026.06.16 - Anonymity: Routing-Signature Compression for Many-Testing-Safe Anonymous DHT Tuning]]` -> `published/2026-06-16_routing_signature_compression_for_many_testing_safe_anonymous_dht_tuning/paper.tex`
- `[[2026.06.16 - Anonymity: Congestion-EQ]]` -> `published/2026-06-16_congestion_eq/paper.tex`
- `[[2026.06.16 - Anonymity: PSC-Q]]` -> `published/2026-06-16_psc_q/paper.tex`
- `[[2026.06.16 - Anonymity: W-Congestion-EQ]]` -> `published/2026-06-16_w_congestion_eq/paper.tex`
- `[[2026.06.16 - Anonymity: Calibration Recipes for Anonymous DHT Deployments]]` -> `published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/paper.tex`
- `[[2026.06.16 - Anonymity: State-Dependent Anonymity]]` -> `published/2026-06-16_state_dependent_anonymity/paper.tex`

These are the first seven post-policy Anonymity public heads. Certified Menus is backed by `published/2026-06-16_certified_menus_for_anonymous_dht_lookups/PUBLICATION_RECEIPT.json`; Routing-Signature Compression is backed by `published/2026-06-16_routing_signature_compression_for_many_testing_safe_anonymous_dht_tuning/PUBLICATION_RECEIPT.json`; Congestion-EQ is backed by `published/2026-06-16_congestion_eq/PUBLICATION_RECEIPT.json` and should be treated as the congestion-family theorem/accountant root before PSC-Q; PSC-Q is backed by `published/2026-06-16_psc_q/PUBLICATION_RECEIPT.json` as the mechanism spine; W-Congestion-EQ is backed by `published/2026-06-16_w_congestion_eq/PUBLICATION_RECEIPT.json` as the deterministic replay/checker spine, not as deployment-truth evidence. Calibration Recipes is backed by `published/2026-06-16_calibration_recipes_for_anonymous_dht_deployments/PUBLICATION_RECEIPT.json` as the calibration-support spine, with `calibration_recipe_packet` treated as nonmaterialized owner-map / series-spine route metadata in the current worked example. State-Dependent Anonymity is backed by `published/2026-06-16_state_dependent_anonymity/PUBLICATION_RECEIPT.json` as the state-family accountant root; its source-bound evidence card enforces the bit/nat unit conversion guard.

## Compact reentry aid

Use `published/CITATION_HEADS.md` when you need the short answer quickly.
Use this file when you need the fuller distinction and operator rules behind that answer.
