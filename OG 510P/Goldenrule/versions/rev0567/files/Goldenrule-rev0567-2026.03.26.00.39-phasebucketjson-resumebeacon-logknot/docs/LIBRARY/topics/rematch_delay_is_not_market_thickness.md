# Rematch Delay Is Not Market Thickness

The archive now has enough local evidence and outside literature to draw a sharper boundary around the current leave/rematch proxy:

> A sweep over rematch delay is **not** the same thing as a sweep over matching-market efficiency.

## What the local proxy now says clearly

The derived report in `artifacts/reports/rematch_proxy_matching_friction_snapshot_20260306.{md,json}` checks a narrow but useful property of the current proxy.

Across five salient policies (`CCEEE`, `CCDDE`, `always_c`, `courteous_firm`, and `DCECC`) and all three extortion shares:

- `overall_avg_payoff` is monotone in delay,
- i.e. every tested cell satisfies `delay=0 >= delay=1 >= delay=2`,
- so in the current proxy, delay behaves as a **one-sided tax** on productive time.

That is helpful because it tells the inheritor exactly what this proxy is doing.
It is **not** yet a full market model.

## What the literature adds

Two recent lines sharpen the interpretation.

- `RS-GR-013` (Bester & Sákovics, 2024) studies an anonymous matching market where matched pairs play an infinitely repeated Prisoner's Dilemma. Lower matching frictions have **two opposing effects** there: they make it easier to escape punishment after cheating, but they also increase the share of agents who end up in productive cooperative relationships.
- `RS-GR-014` (Premo & Brown, 2019) shows in a spatial IPD setting that the opportunity cost of walking away rises with **higher error** and **lower density**.

Put together with the local proxy result, this gives a clean implementor lesson:

- the current proxy captures the **cost-of-leaving** side,
- but it does not yet capture the full **market-thickness / search-difficulty** side.

## Why the distinction matters

If a future report says “lower friction helped cooperation,” there are at least two different underlying mechanisms that could be doing the work:

1. fewer dead rounds while searching,
2. more favorable steady-state assortment because more agents stay matched in productive relationships.

The current proxy only gives us mechanism `1` directly.
That means it is a good diagnostic for delay taxes, but it should not be overinterpreted as a complete model of competition or matching efficiency.

## Practical handoff for the inheritor

1. Keep rematch delay / search delay as an explicit world field.
2. Add a **separate** market-thickness or matching-efficiency parameter in the first endogenous rematch world.
3. Track the steady-state share of agents who are matched versus currently searching.
4. Treat claims that only vary delay in the exogenous-pool proxy as **diagnostic**, not yet general matching-market claims.

## Compact interpretation

The proxy already taught the archive that delay is a real tax.
This refinement says something just as important:

> delay tax and market thickness are related, but they are not interchangeable.
