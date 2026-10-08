# Field execution risk burndown rev0272

## Current riskiest failure

The riskiest internal failure after the send-log gate is an open-ended response
clock. If the local first-contact or re-ask due date can drift, the cube can avoid
both real owner intake and a clean `NO_OWNER_PACKET` result while still appearing
active.

Rev0272 reduces that risk by bounding clocks in the field tools instead of in
prose.

## Burndown table

| Risk | Before rev0272 | Rev0272 correction | Still not solved |
|---|---|---|---|
| First-contact clock can be stretched | `owner-send-log` accepted any due date on or after sent date. | First owner response clock cannot exceed seven days from sent date. | The archive cannot prove external delivery. |
| Packet return date can silently overroute | Router accepted far-future packet return dates when building send-log commands. | Router clamps missing, past, or overlong return dates to the bounded first-contact clock. | Operator still has to send or adapt externally. |
| Re-ask can become a second long wait | Contact-status clock only checked order, not max duration. | Re-ask and no-owner-packet clocks are capped at three days. | Owner may still answer late outside the local clock. |
| No-owner status can obscure its source clock | No-owner-packet status could cite a source re-ask but carry different sent/due dates. | No-owner-packet sent and due dates must match the source `REASK_AWAITING_REPLY` status. | A real returned CSV still needs intake if it arrives. |
| Bureaucracy can replace field completion | More audit prose could look like progress. | Change is concentrated in existing router, send-log, contact-status, guards, and validators. | The next real move remains external. |

## Refactored surface family

The owner-contact path now has a bounded local state machine:

- first contact: packet plus send log, seven-day maximum response clock;
- first wait: `SENT_AWAITING_REPLY`, sourced from verified `send-log.json`;
- clarification: at most one `REASK_AWAITING_REPLY`, three-day maximum clock;
- terminal local field result: matching-clock `NO_OWNER_PACKET` if no viable CSV
  arrives;
- evidence path: only a plausible returned CSV routed through intake can move
  toward workbench review.

This is a refactor of the execution family, not a new doctrine branch.

## Completion risk that remains

The owner route may still fail. That is acceptable. A bounded `NO_OWNER_PACKET`
after one clarification is a substantive field result; indefinite waiting, a
broader export request, a copied owner email, or a new registry is not.
