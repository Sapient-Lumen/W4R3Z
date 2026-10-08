# rev0270 authority handoff and vault dry-run refactor

## What changed

rev0270 moves the first-artifact path from prepared packet status to a single execution handoff. The new handoff binds the human branch-decision template, private custody precommit, exact reviewer-first message bytes, response-disposition playbook, failed-gate shell, and six-artifact workbook before any external action can be treated as authorized.

## Risk fixed

The risky failure mode after rev0267 was symbolic readiness: a packet, route matrix, failed-gate shell, and playbook could all exist while no one could tell, in one place, whether the operator had authority, private roots, and current hashes. That kind of gap tends to produce either indefinite hesitation or accidental overclaiming.

rev0270 therefore adds:

- `examples/authority-handoff-vault-dry-run-rev0270-reviewer-first-nosend.json`
- `examples/signed-authority-public-shell-rev0270-template.json`
- `docs/30-transition/rev0270-authority-handoff-and-vault-dryrun.md`
- `tools/audit_rev0270_authority_handoff_vault.py`

## Operational rule

The next real progress is not another doctrine surface. It is one of these:

1. signed no-send/defer/stop authority,
2. signed reviewer-first authority plus private roots and send-time hash/locator recheck,
3. signed retarget authority, or
4. a failed gate recorded without pretending to be live evidence.

No branch decision exists in this release. No private vault root is selected. No external party has been contacted. The dry-run does not authorize send, transport, response-clock start, custody, intake, import, recognition, welfare finding, reviewer appointment, or live-floor effect.
