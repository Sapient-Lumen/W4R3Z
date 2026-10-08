# Claim provenance and runtime profile-index refactor — rev0322

Rev0322 targets the next risky edge after rev0321. The archive could emit profile-backed answer packets, but it still risked two failures: runtime code repeatedly joining duplicated profile surfaces, and answer packets carrying source IDs without binding those sources to the actual decision claims being made.

## Substantive change

`tools/answer_case.py` now emits claim packets for every selected route. Each selected route must expose, at minimum:

- route classification;
- policy category-error blocking;
- accountable-actor assignment;
- remedy default move and blocked move;
- source-currentness claim when the route depends on a volatile source.

Each claim packet carries a claim type, route id, claim text, supporting profile field, and source IDs. This makes it harder for an answer to look well-cited while only dragging along a source list.

## Runtime refactor

Added `tools/build_route_profile_index.py` and `docs/00-meta/route-profile-index.json`. The route profile index is a generated runtime narrow waist that joins live route records to remedy, policy-action, and actor-accountability profiles. The individual profile surfaces remain authoritative, but answer emission now uses the checked index rather than rejoining those surfaces at runtime.

Added `tools/audit_route_profile_index.py`. It blocks the release if the runtime index drifts from any live route, remedy, policy-action, actor-accountability, source-currentness, source, path, or axis field.

Added `tools/audit_claim_provenance.py`. It invokes `tools/answer_case.py` across all active golden cases and blocks the release if a selected route lacks required claim types, cites unsupported sources, omits primary sources from claim packets, or loses currentness claim support.

## Machine result

- Route profile index entries: 155
- Route profile index drift: 0
- Claim-bearing answer packets: 122
- Claim route instances: 610
- Claim packets: 2735
- Required claim-type recall: 2551/2551
- Claim source-edge recall: 17703/17703
- Currentness claim recall: 295/295
- Complete claim-packet answers: 122/122

## What this deliberately does not do

Rev0322 does not add routes, cases, axes, or doctrine just to increase registry counts. It also does not pretend to solve final precedence, current-law advice, or quantitative fiscal modeling. The point is narrower: make the runtime answer layer less wasteful and make emitted claims traceable enough that later final-answer logic has something real to test.

## Next riskiest frontier

The next high-value pass should add a precedence resolver that turns selected candidate routes into an ordered disposition when routes conflict. The resolver should be tested against cases where no-go rules, protected floors, actor accountability, source-currentness, and ordinary revenue classification compete in the same scenario.
