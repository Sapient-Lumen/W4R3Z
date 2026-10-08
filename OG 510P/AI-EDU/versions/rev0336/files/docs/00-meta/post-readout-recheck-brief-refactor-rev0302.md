# rev0302 post-readout recheck brief refactor

## What changed

`rev0302` compresses the next risky seam in `FT-0181`: after a human records a
bounded post-readout action dispatch and its due/recheck date arrives, the archive
previously emitted the dense `owner-post-readout-recheck` command directly. That
was safe, but it left a high-drop-off step exactly where the operator must choose
between no new owner context, new owner context held outside the archive, owner
action complete without closure, or route blocked.

New helper:

```bash
make owner-post-readout-recheck-brief \
  ACTION=scratch/.../post-readout-action.json \
  AS_OF_DATE=YYYY-MM-DD
```

`make owner-field-work` may now safely prepare this brief when the router selects
`PREPARE-POST-READOUT-RECHECK-BRIEF`. It reruns the router and stops at the
human-owned recheck-recording boundary.

## What the brief does

The brief validates one scratch-local `post-readout-action.json`, hash-checks the
source dispatch, confirms that `AS_OF_DATE` is on or after `due_or_recheck_date`,
and emits a one-screen handoff with bounded `owner-post-readout-recheck` command
skeletons for exactly these outcomes:

| Recheck outcome | Meaning |
|---|---|
| `no_new_owner_context` | Nothing new came back; preserve the dispatch/recheck history and stop live. |
| `new_owner_context_available` | New owner context exists outside the archive; hold it out and route through context receipt before intake. |
| `owner_action_complete_no_closure` | Owner-held action completed locally but does not authorize closure or public/service/lifecycle movement. |
| `route_blocked_no_owner` | The owner route is unavailable or blocked; preserve the block and keep `FT-0181` live. |

The `new_owner_context_available` command skeleton requires
`NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE=1` so the brief cannot smuggle raw context,
owner answers, contact details, public-language text, learner rows, protected facts,
or security payloads into a local recheck record.

## Boundary

The brief is not a recheck. It is not owner context, context receipt, intake,
evidence, SRC2+ acceptance, custody evidence, public-summary support, service-record
mutation, lifecycle movement, owner-action completion, or closure.

The refactor reduces operator drop-off at the due-date seam while preserving the
rule that only a human can record the recheck and only a real returned context file
can enter the next intake loop through the post-readout context receipt gate.
