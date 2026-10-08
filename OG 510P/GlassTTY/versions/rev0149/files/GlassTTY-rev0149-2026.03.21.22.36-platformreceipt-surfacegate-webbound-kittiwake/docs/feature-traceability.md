# Feature traceability

A feature theme is not complete when it has a nice description. It becomes implementable when it is traceable.

## Traceability chain

Every major feature or theme should be explainable in this order:

1. **theme**
   - example: structured browser state
2. **affected workflows**
   - example: composer-read, latest-turn-read, generation-read
3. **state families**
   - example: composer, turn, generation
4. **action/outcome implications**
   - example: write and submit must emit outcomes
5. **evidence expectations**
   - example: state snapshot, workflow proof, support bundle, route/history witness when needed
6. **support-truth effect**
   - example: lets a surface move from investigated to experimental for one workflow on one lane
7. **release claim**
   - example: can or cannot be said in STATUS/support matrix

## Themes that need this treatment now
- multi-surface adapter support
- structured browser state
- drift detection and maintenance
- support truth and release gates
- agent-capable operation
- navigation truth and browser-history witnesses
- fused control-plane review surfaces
- workflow expansion beyond the minimum set

## Rule for future docs
If a new feature idea cannot be traced through workflows, state, evidence, and support truth, it is still at the concept stage and should be written as such.
