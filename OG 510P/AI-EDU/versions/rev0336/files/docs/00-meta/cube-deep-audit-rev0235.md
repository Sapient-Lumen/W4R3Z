# Cube deep audit rev0235: live-window drift and rollback execution

## Finding

Rev0234 closed the last-mile overreach gap between a decision board and a concrete change ticket. The next risky gap is later: a bounded ticket can still drift during the first live window if nobody names the window scope, stop triggers, rollback owner, and evidence readouts before use begins.

That is a more substantive risk than another registry problem. It is where a careful archive could still fail in practice: the public claim stays cautious, but the live service silently adds users, dates, source systems, prompts, data classes, vendor claims, or memory/tool behavior that the packet did not justify.

## What changed

Rev0235 adds `docs/30-operations/ft0181-live-window-stop-rollback-card.md` and wires it into lifecycle validation. A lifecycle row now carries a compact `live_window_control` object in addition to the post-decision change ticket. The object names window state, scope, allowed/prohibited behavior, stop triggers, rollback steps, evidence readouts, and public-claim freeze.

The no-real-data hint tutor row remains blocked. It can rehearse rollback, but it cannot start a live window, expand users, promote the lifecycle state, publish outcome language, add schema fields, or close `FT-0181`.

## Audit/refactor

The refactor target was lifecycle drift. Before this revision, `tools/check_service_lifecycle_decisions.py` knew that a lifecycle decision needed a board reference and change ticket, but it did not require an executable live-window control. Now it rejects lifecycle rows that lack a live-window object, fail to freeze public claims, omit stop triggers or rollback steps, or carry example-only evidence while pretending to have an active window.

A new `IFF8` failure class catches live-window drift: the scenario where a ticket is narrow but the first live window quietly expands cohort, time, tools, memory, data, or claims.

## Why this is priority work

The cube already has enough doctrine to say what is allowed. What it still needs is a way to stop a real pilot when the allowed thing changes shape. The live-window card is intentionally small because the operator should be able to act immediately: pause, roll back, suppress claim, quarantine, or complete the window without closure.

## Next risk

The next unresolved execution risk is owner availability. A perfect packet path still stalls if no teacher/service owner can supply a minimized `SRC2+` packet. The next pass should reduce owner burden further or prepare the fallback `AIEDU-SR-003` reminder workflow with the same window discipline.

## Boundary

Rev0235 does not import real pilot evidence and does not close `FT-0181`. It improves the chance that a future live pilot window can be stopped or rolled back before it turns into unreviewed expansion.
