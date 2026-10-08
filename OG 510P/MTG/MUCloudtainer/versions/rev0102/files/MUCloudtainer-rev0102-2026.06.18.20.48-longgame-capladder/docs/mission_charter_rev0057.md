# Mission charter — rev0057

## Purpose

MUC-5 exists to discover and verify local strategic theory in a tiny hidden-information Magic-like microgame.

It should be judged by whether it can produce claims that are:

```text
public-observation safe
legality exact
replayable
seed-disjoint retestable
terminal-clean
C++-shadow checked where applicable
human-explainable
```

## Non-purpose

MUC-5 is not a generic Magic engine and should not chase full card coverage before it can explain its first replicated claim.

## Current north star

Turn `cf34_counter_wall vs pub_threat_overlord` from a replicated scoreboard fact into an explained local theory. The most likely explanation after rev0057 is endurance/decking: the target's 60-card counter/Jace shell survives and interacts until the opponent's 40-card Overlord shell draws out.

## Claim standard

A claim is not mature until it has:

```text
score and confidence interval
terminal mechanism distribution
replay sample pass count
C++ shadow status
seed-family provenance
same-deck or same-pilot control where relevant
human-readable claim card
```
