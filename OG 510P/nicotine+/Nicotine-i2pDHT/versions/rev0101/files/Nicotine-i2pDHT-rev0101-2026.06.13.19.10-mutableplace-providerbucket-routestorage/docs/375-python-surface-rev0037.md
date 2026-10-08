# Python surface rev0037

The active Python additions are:

```text
serviceticket.ServiceTicketRequest
serviceticket.ServiceTicketCapsule
serviceticket.assess_service_ticket
servicereceipt.ServiceReceiptCapsule
servicereceipt.assess_service_receipt
ticketfold.audit_ticket_fold
```

The design keeps everything deterministic, signed, and transport-neutral. No
live router, SAM socket, or production persistence surface is introduced.
