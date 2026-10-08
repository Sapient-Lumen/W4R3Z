# Discount schedule and valuation rule are world contracts, not moral progress

Recent work adds another missing layer to Concord's future-facing worlds: **long-horizon outcomes depend not only on what agents do, but on how the institution mathematically values distant benefits and harms, including the discount schedule, capital treatment, and assumptions about demographic change or future bias**.

- `RS-GR-263` shows that updated U.S. federal discounting guidance lowered the central real discount rate from 3% to 2%, changed capital treatment, and thereby materially increased the weight assigned to long-lived harms and benefits; in the example discussed, that shift alone more than doubled the social cost of carbon.
- `RS-GR-264` shows that demographic change affects the social discounting problem itself rather than merely changing the political backdrop around it.
- `RS-GR-265` shows that the appropriate social discount rate in public investment depends on future bias and can alter equilibrium policy and investment choices.
- Together, these results warn that a benchmark can look more future-protective because the planner used a lower or declining discount rate, changed capital treatment, or adopted different demographic / future-bias assumptions — not because the underlying Golden-Rule disposition improved.

## Why this matters for Concord

A future-facing benchmark should not report "agents valued the future more" without publishing whether that change came from behavior, from the scoring rule, or from both.

There is a real institutional difference between:
1. a world evaluated with a constant higher discount rate;
2. a world evaluated with a lower constant rate;
3. a world evaluated with a declining long-run schedule;
4. a world where some harms are discounted conventionally but threshold breaches or rights violations are treated differently;
5. a world where the same behavior is reranked because demographic assumptions, capital treatment, or future-bias parameters changed.

Those are not calculator settings.
They change which futures count, how much they count, and whether a result reflects a different moral rule or merely a different valuation architecture.

## Minimal implementor handoff

If Concord adds long-horizon welfare, stewardship, climate, or investment lanes, publish at least:

1. the discount schedule used, including whether it is constant, declining, mixed, or category-specific;
2. any alternate valuation machinery such as shadow-price-of-capital treatment, threshold overrides, or non-discounted harm floors;
3. the demographic, growth, or future-bias assumptions that feed the valuation rule;
4. at least one sensitivity comparison where the action profile is held fixed and only the valuation rule changes;
5. whether headline results survive a same-behavior comparison under more than one plausible long-horizon valuation scheme.

Without that compact contract, future inheritors can mistake a different discount architecture for the same thing as stronger reciprocity or deeper intergenerational ethics.

