# Fixture lab

Fixture-lab should now be treated as one part of GlassTTY's broader drift and support program.

## Old mental model
Fixture-lab was mainly a place to debug selectors and content-script behavior.

## New mental model
Fixture-lab is:
- a baseline generator
- a drift detector
- an adapter development workbench
- a support-truth artifact source

## What fixture captures should help answer

- what compose and latest-turn structures looked like
- how receiver candidates were ranked
- which cues an adapter relied on
- what changed between two captures
- whether a workflow failure is likely adapter drift, frame drift, route drift, or missing evidence

## Relation to support work

Every official surface should eventually have:
- baseline fixture captures
- comparison artifacts over time
- notes about the fragile cues those captures reveal
- a path from fixture evidence to support-tier updates

## Important rule

Do not keep fixture-lab isolated from the main product story. A multi-surface browser bridge needs fixture and drift infrastructure to stay alive.
