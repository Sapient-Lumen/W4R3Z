# Priority reconsideration — rev0059

The riskiest unfinished work is now narrower than it was in rev0058.

## Before rev0059

The main risk was whether the replicated `cf34_counter_wall` edge was a pilot edge or a deck/size/endurance edge.

## After rev0059

The main risk is the life-20 contradiction:

```text
rev0059 A-D block: life-20 A and B tied at 0.700.
rev0059 life-20 stress: A beat B by +0.4583.
cumulative life-20 A/B: A leads B by +0.3452 over 84 games per arm.
```

So the next high-value work is not a broader registry.  It is a seed forensic pass over life-20 A/B games: compare early draw timing, Jace Brainstorm/Fateseal use, counter density, Overlord mode, and library trajectory in the seeds where B_pilot_swap_size_skew wins.
